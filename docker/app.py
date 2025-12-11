import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("model_server")

app = FastAPI(title="Hugging Face Model Server")

# Configuration
MODEL_ID = os.getenv("HF_MODEL_ID", "gpt2")
TASK_TYPE = os.getenv("TASK_TYPE", "text-generation")

logger.info(f"Initializing model: {MODEL_ID} [{TASK_TYPE}]")

# Global model handler
generator = None

try:
    generator = pipeline(TASK_TYPE, model=MODEL_ID)
    logger.info("Model loaded successfully.")
except Exception as e:
    logger.critical(f"Failed to load model: {e}")
    # We don't exit here so the container stays alive for debugging, 
    # but the health check will fail.

class InferenceRequest(BaseModel):
    text: str
    max_length: int = 50

@app.get("/health")
def health_check():
    if generator is None:
        return {"status": "unhealthy", "reason": "Model failed to load"}
    return {"status": "healthy", "model": MODEL_ID}

@app.post("/predict")
def predict(payload: InferenceRequest):
    if generator is None:
        raise HTTPException(status_code=503, detail="Model service is not ready")
    
    try:
        # Generate response
        result = generator(
            payload.text, 
            max_length=payload.max_length, 
            num_return_sequences=1
        )
        return {"result": result}
    except Exception as e:
        logger.error(f"Inference error: {e}")
        raise HTTPException(status_code=500, detail="Inference failed")