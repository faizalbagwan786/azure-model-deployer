import os
import json
import argparse
import logging
import sys
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Dict

from azure_client import AzureClient
from build_image import build_docker_image

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# SECURITY: Validation Models 
class EnvironmentConfig(BaseModel):
    name: str = Field(..., pattern=r"^[a-z0-9-]+$")
    subscription_id: str
    resource_group: str = Field(..., pattern=r"^[a-z0-9-]+$")
    location: str
    acr_name: str = Field(..., pattern=r"^[a-z0-9]+$")
    container_app_env_name: str
    container_app_base_name: str
    cpu: float
    memory: str
    min_replicas: Optional[int] = 1
    max_replicas: Optional[int] = 3

class ModelConfig(BaseModel):
    model_key: str
    huggingface_model_id: str
    task_type: str = "text-generation"
    image_tag_suffix: str = "latest"
    port: int = 8080
    environment_variables: Dict[str, str] = {}

def load_config(path, model_class):
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        return model_class(**data) # Validate immediately
    except (FileNotFoundError, ValidationError, json.JSONDecodeError) as e:
        logger.error(f"Config Validation Error in {path}: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-key", required=True)
    parser.add_argument("--env", required=True)
    args = parser.parse_args()

    # Define Project Root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Load & Validate Configs
    model_config = load_config(os.path.join(base_dir, f"config/models/{args.model_key}.json"), ModelConfig)
    env_config = load_config(os.path.join(base_dir, f"config/environments/{args.env}.json"), EnvironmentConfig)

    # Naming
    full_image_tag = f"{env_config.acr_name}.azurecr.io/{env_config.container_app_base_name}-{args.model_key}:{model_config.image_tag_suffix}"
    
    az = AzureClient()
    az.login()

    # 1. Build Image (Context = Root)
    logger.info(f"Building {full_image_tag}...")
    dockerfile_path = os.path.join(base_dir, "docker", "base_hf_server.Dockerfile")
    # Fix: Use base_dir as context so we can COPY src/
    build_docker_image(base_dir, dockerfile_path, full_image_tag)

    # 2. Push
    az.push_image(env_config.acr_name, full_image_tag)

    # 3. Deploy
    logger.info(f"Deploying...")
    app_url = az.deploy_container_app(
        resource_group=env_config.resource_group,
        env_name=env_config.container_app_env_name,
        app_name=f"{env_config.container_app_base_name}-{args.model_key}",
        image_tag=full_image_tag,
        cpu=env_config.cpu,
        memory=env_config.memory,
        min_replicas=env_config.min_replicas,
        max_replicas=env_config.max_replicas,
        env_vars=model_config.environment_variables,
        port=model_config.port
    )
    
    logger.info(f"🚀 Success! Deployment URL: {app_url}")

if __name__ == "__main__":
    main()