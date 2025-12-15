
# Standard and third-party imports
import os
import torch
import requests
import logging
from io import BytesIO
from PIL import Image

# FastAPI and dependencies
from fastapi import FastAPI, HTTPException, Request, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from transformers import AutoModelForImageTextToText, AutoModelForVision2Seq, AutoProcessor, pipeline
from slowapi import Limiter
from slowapi.util import get_remote_address


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("model_server")


# Initialize FastAPI app and rate limiter
app = FastAPI(title="SmolVLM Server")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter



# API Key security setup
API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("API_KEY", "default-insecure-key-change-me")
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Dependency to enforce API key authentication
async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(status_code=403, detail="Could not validate credentials")



# Model configuration from environment
MODEL_ID = os.getenv("HF_MODEL_ID", "HuggingFaceTB/SmolVLM-500M-Instruct")
TASK_TYPE = os.getenv("TASK_TYPE", "vlm")

logger.info(f"Initializing model: {MODEL_ID} [{TASK_TYPE}]")

# Placeholders for model, processor, and generator
model = None
processor = None
generator = None

# Load the appropriate model and processor/generator based on the task type
try:
    if TASK_TYPE == "vlm":
        processor = AutoProcessor.from_pretrained(MODEL_ID)
        try:
            # Try to load as ImageTextToText model (for newer VLMs)
            model = AutoModelForImageTextToText.from_pretrained(
                MODEL_ID,
                torch_dtype=torch.float32,
                _attn_implementation="eager",
                low_cpu_mem_usage=True
            )
        except Exception:
            # Fallback to Vision2Seq model (for older VLMs)
            model = AutoModelForVision2Seq.from_pretrained(
                MODEL_ID,
                torch_dtype=torch.float32,
                _attn_implementation="eager",
                low_cpu_mem_usage=True
            )
    else:
        # Text generation pipeline
        generator = pipeline(TASK_TYPE, model=MODEL_ID)
    logger.info("Model loaded successfully!")
except Exception as e:
    logger.critical(f"FAILED TO LOAD MODEL: {e}")



# Request schema for inference endpoint
class InferenceRequest(BaseModel):
    text: str = Field(..., max_length=1000, title="Input Text") 
    image_url: str = None
    max_length: int = Field(50, le=512, title="Max New Tokens") 


# Health check endpoint to verify model readiness
@app.get("/health")
def health():
    if (TASK_TYPE == "vlm" and model is None) or (TASK_TYPE != "vlm" and generator is None):
        return {"status": "unhealthy", "detail": "Model not loaded"}
    return {"status": "healthy", "model": MODEL_ID}



# Inference endpoint for text and VLM tasks
@app.post("/predict", dependencies=[Depends(get_api_key)])
@limiter.limit("10/minute")
def predict(request: Request, payload: InferenceRequest):
    try:
        if TASK_TYPE == "vlm":
            # Vision-Language Model inference
            if not payload.image_url:
                raise HTTPException(status_code=400, detail="Image URL is required for VLM.")
            try:
                # Download and validate image
                resp = requests.get(payload.image_url, stream=True, timeout=5) 
                resp.raise_for_status()
                if len(resp.content) > 5 * 1024 * 1024:
                    raise HTTPException(status_code=400, detail="Image too large (Max 5MB)")
                image = Image.open(BytesIO(resp.content))
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to download image: {str(e)}")
            if image.mode != "RGB":
                image = image.convert("RGB")
            # Resize image for efficiency
            image.thumbnail((512, 512))
            # Prepare prompt for vision-language model
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image"},
                        {"type": "text", "text": payload.text}
                    ]
                },
            ]
            prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
            inputs = processor(text=prompt, images=[image], return_tensors="pt")
            with torch.no_grad():
                output = model.generate(**inputs, max_new_tokens=payload.max_length)
            generated_text = processor.batch_decode(output, skip_special_tokens=True)
            return {"result": generated_text[0]}
        else:
            # Text generation inference
            if generator is None:
                raise HTTPException(status_code=503, detail="Model not ready")
            result = generator(
                payload.text, 
                max_length=payload.max_length, 
                num_return_sequences=1
            )
            return {"result": result}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Inference error: {e}")
        raise HTTPException(status_code=500, detail=str(e))