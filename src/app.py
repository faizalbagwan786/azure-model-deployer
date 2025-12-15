import os
import torch
import requests
import logging
from io import BytesIO
from PIL import Image
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
# FIX: Import the new ImageTextToText class for SmolVLM2
from transformers import AutoModelForImageTextToText, AutoModelForVision2Seq, AutoProcessor, pipeline
from slowapi import Limiter
from slowapi.util import get_remote_address

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("model_server")

app = FastAPI(title="SmolVLM Server")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Configuration
MODEL_ID = os.getenv("HF_MODEL_ID", "HuggingFaceTB/SmolVLM-500M-Instruct")
TASK_TYPE = os.getenv("TASK_TYPE", "vlm")

logger.info(f"Initializing model: {MODEL_ID} [{TASK_TYPE}]")

model = None
processor = None
generator = None

# Model Loading
try:
    if TASK_TYPE == "vlm":
        processor = AutoProcessor.from_pretrained(MODEL_ID)
        
        # UNIVERSAL LOADER: Try the new class first (for 2.2B), fall back to old (for older models)
        try:
            logger.info("Attempting to load with AutoModelForImageTextToText (New Standard)...")
            model = AutoModelForImageTextToText.from_pretrained(
                MODEL_ID,
                torch_dtype=torch.float32,
                _attn_implementation="eager",
                low_cpu_mem_usage=True
            )
        except Exception as e:
            logger.warning(f"New loader failed ({e}), falling back to AutoModelForVision2Seq...")
            model = AutoModelForVision2Seq.from_pretrained(
                MODEL_ID,
                torch_dtype=torch.float32,
                _attn_implementation="eager",
                low_cpu_mem_usage=True
            )
            
    else:
        generator = pipeline(TASK_TYPE, model=MODEL_ID)
    logger.info("Model loaded successfully!")
except Exception as e:
    logger.critical(f"FAILED TO LOAD MODEL: {e}")

class InferenceRequest(BaseModel):
    text: str
    image_url: str = None
    max_length: int = 50

@app.get("/health")
def health():
    if (TASK_TYPE == "vlm" and model is None) or (TASK_TYPE != "vlm" and generator is None):
        return {"status": "unhealthy", "detail": "Model not loaded"}
    return {"status": "healthy", "model": MODEL_ID}

@app.post("/predict")
@limiter.limit("10/minute")
def predict(request: Request, payload: InferenceRequest):
    try:
        # VLM Logic
        if TASK_TYPE == "vlm":
            if not payload.image_url:
                raise HTTPException(status_code=400, detail="Image URL is required for VLM.")

            # Download
            try:
                resp = requests.get(payload.image_url, stream=True, timeout=10)
                resp.raise_for_status()
                image = Image.open(BytesIO(resp.content))
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to download image: {str(e)}")

            if image.mode != "RGB":
                image = image.convert("RGB")

            # Create Prompt Template
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

            # Generate
            with torch.no_grad():
                output = model.generate(**inputs, max_new_tokens=payload.max_length)
            
            generated_text = processor.batch_decode(output, skip_special_tokens=True)
            return {"result": generated_text[0]}

        # Text Logic
        else:
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