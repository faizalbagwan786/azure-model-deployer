# Standard and third-party imports
import os
import time
import uuid
import json
import logging
from io import BytesIO
from typing import List, Optional, Union, Dict, Any
from threading import Thread

import requests
from PIL import Image

# FastAPI & Starlette
from fastapi import FastAPI, HTTPException, Request, Security, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from pydantic import BaseModel, Field

# Rate Limiting
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Graceful / Lazy ML Framework Imports
try:
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoModelForImageTextToText,
        AutoModelForVision2Seq,
        AutoProcessor,
        AutoTokenizer,
        TextIteratorStreamer
    )
    ML_AVAILABLE = True
except ImportError:
    torch = None
    ML_AVAILABLE = False

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("azure_ai_gateway")

# Test Mode & Device detection
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"
if torch is not None and torch.cuda.is_available() and not TEST_MODE:
    DEVICE = "cuda"
else:
    DEVICE = "cpu"

logger.info(f"⚡ Device initialized: {DEVICE.upper()} (ML Libraries Available: {ML_AVAILABLE}, Test Mode: {TEST_MODE})")

# Environment variables
API_KEY = os.getenv("API_KEY", "").strip()
MODEL_ID = os.getenv("HF_MODEL_ID", "Qwen/Qwen2.5-1.5B-Instruct")
TASK_TYPE = os.getenv("TASK_TYPE", "chat")
MAX_TOKENS_DEFAULT = int(os.getenv("MAX_TOKENS", "512"))
ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS", "*").split(",")

if not API_KEY or API_KEY in ["default-insecure-key-change-me", "YOUR_OWN_SECURE_KEY_HERE"]:
    logger.warning("⚠️  SECURITY WARNING: API_KEY is using a default or empty value. Set a strong secret key in production.")

# Initialize FastAPI App
app = FastAPI(
    title="Private Azure AI Gateway",
    description="Drop-in OpenAI-compatible API server running open-source models with Scale-to-Zero cloud support.",
    version="2.1.0"
)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "message": "Rate limit exceeded. Default limit is 60 requests per minute.",
                "type": "requests",
                "code": "rate_limit_exceeded"
            }
        }
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dual Auth: Supports both `Authorization: Bearer <key>` and `X-API-Key: <key>`
bearer_auth = HTTPBearer(auto_error=False)
header_auth = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(
    bearer: Optional[HTTPAuthorizationCredentials] = Security(bearer_auth),
    x_key: Optional[str] = Security(header_auth)
):
    token = None
    if bearer and bearer.credentials:
        token = bearer.credentials.strip()
    elif x_key:
        token = x_key.strip()

    if not API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server API_KEY environment variable is not configured."
        )

    if token == API_KEY:
        return token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": {
                "message": "Incorrect or missing API key. Provide via 'Authorization: Bearer <key>' or 'X-API-Key: <key>'",
                "type": "invalid_request_error",
                "code": "invalid_api_key"
            }
        }
    )

# Model Globals
model = None
tokenizer = None
processor = None
embeddings_model = None

if ML_AVAILABLE and not TEST_MODE:
    logger.info(f"Loading Model: {MODEL_ID} [Task Type: {TASK_TYPE}]...")
    try:
        torch_dtype = torch.float16 if DEVICE == "cuda" else torch.float32

        if TASK_TYPE == "vlm":
            processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
            try:
                model = AutoModelForImageTextToText.from_pretrained(
                    MODEL_ID,
                    torch_dtype=torch_dtype,
                    _attn_implementation="eager",
                    low_cpu_mem_usage=True,
                    trust_remote_code=True
                )
            except Exception:
                model = AutoModelForVision2Seq.from_pretrained(
                    MODEL_ID,
                    torch_dtype=torch_dtype,
                    _attn_implementation="eager",
                    low_cpu_mem_usage=True,
                    trust_remote_code=True
                )
            if DEVICE == "cuda":
                model = model.to(DEVICE)
        elif TASK_TYPE == "embeddings":
            from transformers import AutoModel
            tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
            embeddings_model = AutoModel.from_pretrained(MODEL_ID, torch_dtype=torch_dtype, trust_remote_code=True)
            if DEVICE == "cuda":
                embeddings_model = embeddings_model.to(DEVICE)
        else:
            # Standard Chat / Causal LM (Qwen, DeepSeek, Llama, Mistral)
            tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_ID,
                torch_dtype=torch_dtype,
                low_cpu_mem_usage=True,
                trust_remote_code=True
            )
            if DEVICE == "cuda":
                model = model.to(DEVICE)

        logger.info("✅ Model loaded successfully into memory!")
    except Exception as e:
        logger.critical(f"❌ Failed to load model weights: {e}")
elif not ML_AVAILABLE:
    logger.warning("ℹ️ Running in mock/testing mode: 'torch' or 'transformers' not installed locally. Run via Docker for full neural model execution.")
else:
    logger.info("🧪 TEST_MODE=true: Skipping heavy HuggingFace model download.")

# =========================================================================
# OPENAI SPECIFICATION PYDANTIC SCHEMAS
# =========================================================================

class ChatMessage(BaseModel):
    role: str
    content: Union[str, List[Dict[str, Any]]]
    name: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = Field(None, description="Model ID")
    messages: List[ChatMessage]
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(0.9, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(MAX_TOKENS_DEFAULT, le=4096)
    stream: Optional[bool] = False

class EmbeddingRequest(BaseModel):
    input: Union[str, List[str]]
    model: Optional[str] = None

class LegacyInferenceRequest(BaseModel):
    text: str = Field(..., max_length=2000)
    image_url: Optional[str] = None
    max_length: Optional[int] = MAX_TOKENS_DEFAULT

# =========================================================================
# BUILT-IN WEB CHAT PLAYGROUND (/chat)
# =========================================================================

PLAYGROUND_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Private AI Gateway — Chat Playground</title>
  <style>
    :root { --bg: #090b10; --card: #131722; --border: #232b3e; --accent: #0078d4; --text: #f1f5f9; --muted: #94a3b8; }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background: var(--bg); color: var(--text); display: flex; flex-direction: column; height: 100vh; }
    header { background: var(--card); border-bottom: 1px solid var(--border); padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; }
    .title { font-weight: 700; font-size: 1.1rem; color: #fff; display: flex; align-items: center; gap: 8px; }
    .badge { background: rgba(0, 120, 212, 0.2); color: #38bdf8; font-size: 0.75rem; padding: 4px 10px; border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.4); }
    .settings { display: flex; gap: 12px; align-items: center; }
    input[type="password"], input[type="text"] { background: #0b0e14; border: 1px solid var(--border); color: #fff; padding: 8px 12px; border-radius: 6px; font-size: 0.85rem; outline: none; }
    #chat-container { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 16px; max-width: 900px; margin: 0 auto; width: 100%; }
    .msg { display: flex; flex-direction: column; padding: 14px 18px; border-radius: 10px; max-width: 80%; line-height: 1.5; font-size: 0.95rem; }
    .msg.user { align-self: flex-end; background: var(--accent); color: #fff; border-bottom-right-radius: 2px; }
    .msg.assistant { align-self: flex-start; background: var(--card); border: 1px solid var(--border); border-bottom-left-radius: 2px; }
    .meta { font-size: 0.7rem; color: var(--muted); margin-bottom: 4px; }
    footer { background: var(--card); border-top: 1px solid var(--border); padding: 16px 24px; }
    .input-bar { max-width: 900px; margin: 0 auto; display: flex; gap: 12px; }
    textarea { flex: 1; background: #0b0e14; border: 1px solid var(--border); color: #fff; padding: 12px; border-radius: 8px; resize: none; height: 52px; font-size: 0.95rem; outline: none; }
    button { background: var(--accent); color: #fff; border: none; padding: 0 24px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.2s; }
    button:hover { background: #0086ee; }
  </style>
</head>
<body>
  <header>
    <div class="title">
      <span>Private Azure AI Gateway</span>
      <span class="badge">OpenAI /v1 Compatible</span>
    </div>
    <div class="settings">
      <input type="password" id="apiKey" placeholder="Bearer API Key (sk-...)" value="sk-private-azure-key-12345">
    </div>
  </header>
  <div id="chat-container">
    <div class="msg assistant">
      <div class="meta">AI GATEWAY</div>
      <div>Hello! Your private OpenAI-compatible gateway is online and ready. Ask me anything or test token streaming below.</div>
    </div>
  </div>
  <footer>
    <div class="input-bar">
      <textarea id="promptInput" placeholder="Send a message (Shift+Enter for newline)..."></textarea>
      <button id="sendBtn" onclick="sendMessage()">Send</button>
    </div>
  </footer>
  <script>
    const chat = document.getElementById('chat-container');
    const input = document.getElementById('promptInput');
    input.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } });

    async function sendMessage() {
      const text = input.value.trim();
      const key = document.getElementById('apiKey').value.trim();
      if (!text) return;
      input.value = '';

      const userMsg = document.createElement('div');
      userMsg.className = 'msg user';
      userMsg.innerHTML = '<div class="meta">YOU</div>' + text.replace(/\\n/g, '<br>');
      chat.appendChild(userMsg);
      chat.scrollTop = chat.scrollHeight;

      const botMsg = document.createElement('div');
      botMsg.className = 'msg assistant';
      botMsg.innerHTML = '<div class="meta">AI GATEWAY</div><div class="content"><i>Thinking...</i></div>';
      chat.appendChild(botMsg);
      chat.scrollTop = chat.scrollHeight;

      try {
        const resp = await fetch('/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + key
          },
          body: JSON.stringify({
            messages: [{ role: 'user', content: text }],
            stream: true,
            max_tokens: 512
          })
        });

        if (!resp.ok) {
          const err = await resp.json();
          botMsg.querySelector('.content').innerText = 'Error: ' + (err.detail || JSON.stringify(err));
          return;
        }

        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        let contentEl = botMsg.querySelector('.content');
        contentEl.innerText = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value);
          const lines = chunk.split('\\n');
          for (const line of lines) {
            if (line.startsWith('data: ') && line !== 'data: [DONE]') {
              try {
                const parsed = JSON.parse(line.replace('data: ', ''));
                const delta = parsed.choices[0]?.delta?.content || '';
                contentEl.innerText += delta;
                chat.scrollTop = chat.scrollHeight;
              } catch (e) {}
            }
          }
        }
      } catch (e) {
        botMsg.querySelector('.content').innerText = 'Connection Error: ' + e.message;
      }
    }
  </script>
</body>
</html>
"""

@app.get("/chat", response_class=HTMLResponse, tags=["Playground"])
def web_chat_playground():
    """Interactive ChatGPT-like web playground to test the deployed AI gateway directly in a browser."""
    return HTMLResponse(content=PLAYGROUND_HTML, status_code=200)

# =========================================================================
# OPENAI COMPATIBLE ENDPOINTS
# =========================================================================

@app.get("/", tags=["Info"])
def root():
    return {
        "status": "online",
        "service": "Private Azure AI Gateway",
        "compatibility": "OpenAI API v1 Spec",
        "active_model": MODEL_ID,
        "task_type": TASK_TYPE,
        "device": DEVICE,
        "endpoints": {
            "playground": "/chat",
            "chat_completions": "/v1/chat/completions",
            "models": "/v1/models",
            "embeddings": "/v1/embeddings",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health", tags=["Health"])
def health():
    if TEST_MODE or not ML_AVAILABLE:
        return {"status": "healthy", "model": MODEL_ID, "device": DEVICE, "task_type": TASK_TYPE}

    is_ready = False
    if TASK_TYPE == "vlm" and model is not None and processor is not None:
        is_ready = True
    elif TASK_TYPE == "embeddings" and embeddings_model is not None and tokenizer is not None:
        is_ready = True
    elif TASK_TYPE in ["chat", "text-generation"] and model is not None and tokenizer is not None:
        is_ready = True

    if not is_ready:
        return JSONResponse(status_code=503, content={"status": "unhealthy", "detail": "Model is not initialized."})
    return {"status": "healthy", "model": MODEL_ID, "device": DEVICE, "task_type": TASK_TYPE}

@app.get("/v1/models", dependencies=[Depends(verify_api_key)], tags=["OpenAI Compatible"])
def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": MODEL_ID,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "azure-private-cloud",
                "permission": [],
                "root": MODEL_ID,
                "parent": None
            }
        ]
    }

@app.post("/v1/chat/completions", dependencies=[Depends(verify_api_key)], tags=["OpenAI Compatible"])
@limiter.limit("60/minute")
def chat_completions(request: Request, payload: ChatCompletionRequest):
    request_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    created_ts = int(time.time())

    # TEST MODE / MOCK EXECUTION (When running outside Docker without heavy weights)
    if TEST_MODE or not ML_AVAILABLE:
        if payload.stream:
            def mock_stream():
                chunk = {"id": request_id, "object": "chat.completion.chunk", "created": created_ts, "model": MODEL_ID, "choices": [{"index": 0, "delta": {"content": "Private AI Gateway stream chunk."}, "finish_reason": None}]}
                yield f"data: {json.dumps(chunk)}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(mock_stream(), media_type="text/event-stream")
        return {
            "id": request_id,
            "object": "chat.completion",
            "created": created_ts,
            "model": MODEL_ID,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "Private AI Gateway response output."}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10}
        }

    # 1. VISION MULTI-MODAL PIPELINE
    if TASK_TYPE == "vlm":
        image_url = None
        user_prompt = ""

        for msg in payload.messages:
            if isinstance(msg.content, list):
                for part in msg.content:
                    if part.get("type") == "image_url":
                        image_url = part.get("image_url", {}).get("url")
                    elif part.get("type") == "text":
                        user_prompt += part.get("text", "")
            elif isinstance(msg.content, str):
                user_prompt += msg.content + "\n"

        if not image_url:
            raise HTTPException(status_code=400, detail="Multimodal request requires an image_url part.")

        try:
            resp = requests.get(image_url, stream=True, timeout=10)
            resp.raise_for_status()
            image = Image.open(BytesIO(resp.content)).convert("RGB")
            image.thumbnail((512, 512))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch image: {str(e)}")

        conv = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": user_prompt.strip()}]}]
        prompt_text = processor.apply_chat_template(conv, add_generation_prompt=True)
        inputs = processor(text=prompt_text, images=[image], return_tensors="pt")
        if DEVICE == "cuda":
            inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

        with torch.no_grad():
            output_tokens = model.generate(**inputs, max_new_tokens=payload.max_tokens)
        
        reply_text = processor.batch_decode(output_tokens, skip_special_tokens=True)[0]

        return {
            "id": request_id,
            "object": "chat.completion",
            "created": created_ts,
            "model": MODEL_ID,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": reply_text},
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(inputs.get("input_ids", [[]])[0]),
                "completion_tokens": len(output_tokens[0]),
                "total_tokens": len(inputs.get("input_ids", [[]])[0]) + len(output_tokens[0])
            }
        }

    # 2. STANDARD CHAT & STREAMING (DeepSeek / Qwen / Llama)
    if not tokenizer or not model:
        raise HTTPException(status_code=503, detail="Model is not ready.")

    messages_payload = [{"role": m.role, "content": m.content if isinstance(m.content, str) else str(m.content)} for m in payload.messages]
    
    try:
        formatted_prompt = tokenizer.apply_chat_template(messages_payload, tokenize=False, add_generation_prompt=True)
    except Exception:
        formatted_prompt = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in messages_payload]) + "\nASSISTANT:"

    inputs = tokenizer(formatted_prompt, return_tensors="pt")
    if DEVICE == "cuda":
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    prompt_tokens_count = len(inputs["input_ids"][0])

    # Safe sampling vs greedy kwargs
    gen_kwargs = {
        **inputs,
        "max_new_tokens": payload.max_tokens,
    }
    if payload.temperature and payload.temperature > 0.05:
        gen_kwargs["do_sample"] = True
        gen_kwargs["temperature"] = payload.temperature
        gen_kwargs["top_p"] = payload.top_p
    else:
        gen_kwargs["do_sample"] = False

    # STREAMING RESPONSE
    if payload.stream:
        streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
        gen_kwargs["streamer"] = streamer

        thread = Thread(target=model.generate, kwargs=gen_kwargs)
        thread.start()

        def event_stream():
            for new_token in streamer:
                chunk = {
                    "id": request_id,
                    "object": "chat.completion.chunk",
                    "created": created_ts,
                    "model": MODEL_ID,
                    "choices": [{"index": 0, "delta": {"content": new_token}, "finish_reason": None}]
                }
                yield f"data: {json.dumps(chunk)}\n\n"

            finish_chunk = {
                "id": request_id,
                "object": "chat.completion.chunk",
                "created": created_ts,
                "model": MODEL_ID,
                "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
            }
            yield f"data: {json.dumps(finish_chunk)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    # NON-STREAMING RESPONSE
    with torch.no_grad():
        output = model.generate(**gen_kwargs)

    generated_tokens = output[0][prompt_tokens_count:]
    completion_text = tokenizer.decode(generated_tokens, skip_special_tokens=True)

    return {
        "id": request_id,
        "object": "chat.completion",
        "created": created_ts,
        "model": MODEL_ID,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": completion_text.strip()},
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens_count,
            "completion_tokens": len(generated_tokens),
            "total_tokens": prompt_tokens_count + len(generated_tokens)
        }
    }

# =========================================================================
# OPENAI COMPATIBLE EMBEDDINGS (FOR RAG APPS)
# =========================================================================

@app.post("/v1/embeddings", dependencies=[Depends(verify_api_key)], tags=["OpenAI Compatible"])
def embeddings(request: Request, payload: EmbeddingRequest):
    if TEST_MODE or not ML_AVAILABLE:
        return {
            "object": "list",
            "data": [{"object": "embedding", "embedding": [0.01] * 384, "index": 0}],
            "model": MODEL_ID,
            "usage": {"prompt_tokens": 4, "total_tokens": 4}
        }

    if not embeddings_model or not tokenizer:
        raise HTTPException(status_code=503, detail="Embeddings model not configured. Set TASK_TYPE=embeddings.")

    inputs_list = [payload.input] if isinstance(payload.input, str) else payload.input
    encoded = tokenizer(inputs_list, padding=True, truncation=True, return_tensors="pt")
    if DEVICE == "cuda":
        encoded = {k: v.to(DEVICE) for k, v in encoded.items()}

    with torch.no_grad():
        model_output = embeddings_model(**encoded)
        attention_mask = encoded['attention_mask']
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        vectors = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        vectors = torch.nn.functional.normalize(vectors, p=2, dim=1).tolist()

    data_items = [{"object": "embedding", "embedding": vec, "index": i} for i, vec in enumerate(vectors)]

    return {
        "object": "list",
        "data": data_items,
        "model": MODEL_ID,
        "usage": {
            "prompt_tokens": sum(len(x) for x in encoded['input_ids']),
            "total_tokens": sum(len(x) for x in encoded['input_ids'])
        }
    }

# =========================================================================
# LEGACY / PREDICT ENDPOINT (BACKWARD COMPATIBILITY)
# =========================================================================

@app.post("/predict", dependencies=[Depends(verify_api_key)], tags=["Legacy"])
def legacy_predict(request: Request, payload: LegacyInferenceRequest):
    chat_payload = ChatCompletionRequest(
        messages=[ChatMessage(role="user", content=payload.text)],
        max_tokens=payload.max_length,
        stream=False
    )
    result = chat_completions(request, chat_payload)
    return {
        "result": result["choices"][0]["message"]["content"],
        "model": MODEL_ID,
        "device": DEVICE
    }
