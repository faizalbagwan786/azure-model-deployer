import os
import json
import argparse
import logging
import sys
from typing import Optional, Dict
from pydantic import BaseModel, Field, ValidationError

# Add deployment directory to sys.path to allow relative imports when run directly
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

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
    min_replicas: Optional[int] = 0
    max_replicas: Optional[int] = 3
    scale_to_zero: Optional[bool] = True
    idle_timeout_seconds: Optional[int] = 300

class ModelConfig(BaseModel):
    model_key: str
    huggingface_model_id: str
    task_type: str = "chat"
    image_tag_suffix: str = "latest"
    port: int = 8080
    environment_variables: Dict[str, str] = {}

def load_config(path, model_class):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return model_class(**data)
    except (FileNotFoundError, ValidationError, json.JSONDecodeError) as e:
        logger.error(f"Config Validation Error in {path}: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Deploy Private AI Gateway to Azure Container Apps")
    parser.add_argument("--model-key", required=True, help="Filename key in config/models/ without .json")
    parser.add_argument("--env", required=True, help="Environment key in config/environments/ without .json")
    parser.add_argument("--dockerfile", default="docker/base_hf_server.Dockerfile", help="Path to Dockerfile (e.g. docker/gpu_hf_server.Dockerfile)")
    args = parser.parse_args()

    # Define Project Root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Load & Validate Configs
    model_config_path = os.path.join(base_dir, f"config/models/{args.model_key}.json")
    env_config_path = os.path.join(base_dir, f"config/environments/{args.env}.json")

    model_config = load_config(model_config_path, ModelConfig)
    env_config = load_config(env_config_path, EnvironmentConfig)

    # Naming
    full_image_tag = f"{env_config.acr_name}.azurecr.io/{env_config.container_app_base_name}-{args.model_key}:{model_config.image_tag_suffix}"

    az = AzureClient()
    az.login()

    # 1. Build Image (Context = Root)
    logger.info(f"Building {full_image_tag} using {args.dockerfile}...")
    dockerfile_path = os.path.join(base_dir, args.dockerfile) if not os.path.isabs(args.dockerfile) else args.dockerfile
    build_docker_image(base_dir, dockerfile_path, full_image_tag)

    # 2. Push to ACR
    az.push_image(env_config.acr_name, full_image_tag)

    # 3. Deploy to Azure Container Apps (with Scale-to-Zero if min_replicas=0)
    logger.info(f"Deploying to Azure Container Apps (Scale-to-Zero: {env_config.min_replicas == 0})...")
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

    logger.info(f"🚀 Success! Your Private OpenAI API is live at: {app_url}/v1")

if __name__ == "__main__":
    main()
