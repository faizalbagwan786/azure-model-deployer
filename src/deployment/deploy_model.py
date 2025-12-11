import os
import json
import argparse
import logging
import sys
from azure_client import AzureClient
from build_image import build_docker_image

# Configure standard logging format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def load_config(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {path}: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Azure Model Deployment Automation")
    parser.add_argument("--model-key", required=True, help="Model identifier (e.g., gpt2-small)")
    parser.add_argument("--env", required=True, help="Target environment (dev, stage, prod)")
    args = parser.parse_args()

    # Calculate project root relative to this script
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    model_config_path = os.path.join(base_dir, "config", "models", f"{args.model_key}.json")
    env_config_path = os.path.join(base_dir, "config", "environments", f"{args.env}.json")

    # Load configurations
    model_config = load_config(model_config_path)
    env_config = load_config(env_config_path)

    # Resolve resource naming
    acr_name = env_config["acr_name"]
    image_tag_suffix = model_config.get("image_tag_suffix", "latest")
    app_base_name = env_config["container_app_base_name"]
    
    # Construct full image tag: <registry>.azurecr.io/<app>-<model>:<tag>
    full_image_tag = f"{acr_name}.azurecr.io/{app_base_name}-{args.model_key}:{image_tag_suffix}"
    
    az = AzureClient()
    az.login()

    # 1. Build Image
    logger.info(f"Starting build for {full_image_tag}...")
    docker_context = os.path.join(base_dir, "docker")
    dockerfile_path = os.path.join(docker_context, "base_hf_server.Dockerfile")
    
    build_docker_image(docker_context, dockerfile_path, full_image_tag)

    # 2. Push to ACR
    az.push_image(acr_name, full_image_tag)

    # 3. Deploy to Container Apps
    app_name = f"{app_base_name}-{args.model_key}"
    env_vars = model_config.get("environment_variables", {})

    logger.info(f"Deploying {app_name} to {env_config['resource_group']}...")
    
    app_url = az.deploy_container_app(
        resource_group=env_config["resource_group"],
        env_name=env_config["container_app_env_name"],
        app_name=app_name,
        image_tag=full_image_tag,
        cpu=env_config["cpu"],
        memory=env_config["memory"],
        min_replicas=env_config.get("min_replicas"),
        max_replicas=env_config.get("max_replicas"),
        env_vars=env_vars,
        port=model_config["port"]
    )
    
    # Write output for GitHub Actions (Modern Syntax)
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"app_url={app_url}\n")
    else:
        logger.info(f"Deployment URL: {app_url}")

if __name__ == "__main__":
    main()