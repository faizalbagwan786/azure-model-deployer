import subprocess
import logging

logger = logging.getLogger(__name__)

class AzureClient:
    def login(self):
        """Ensures the Azure CLI context is active."""
        try:
            # check=True will raise CalledProcessError if exit code != 0
            subprocess.run(["az", "account", "show"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            logger.error("Azure CLI not authenticated. Run 'az login' or check CI credentials.")
            raise

    def push_image(self, acr_name, image_tag):
        """Authenticates with ACR and pushes the image."""
        logger.info(f"Pushing image to ACR: {acr_name}")
        try:
            subprocess.run(["az", "acr", "login", "--name", acr_name], check=True, capture_output=True)
            subprocess.run(["docker", "push", image_tag], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to push image: {e}")
            raise

    def deploy_container_app(self, resource_group, env_name, app_name, image_tag, cpu, memory, min_replicas, max_replicas, env_vars, port):
        """Wraps 'az containerapp up' to deploy or update the service."""
        
        cmd = [
            "az", "containerapp", "up",
            "--name", app_name,
            "--resource-group", resource_group,
            "--environment", env_name,
            "--image", image_tag,
            "--cpu", str(cpu),
            "--memory", memory,
            "--target-port", str(port),
            "--ingress", "external"
        ]

        if min_replicas is not None:
            cmd.extend(["--min-replicas", str(min_replicas)])
        if max_replicas is not None:
            cmd.extend(["--max-replicas", str(max_replicas)])

        if env_vars:
            cmd.append("--env-vars")
            cmd.extend([f"{k}={v}" for k, v in env_vars.items()])

        try:
            # Run deployment
            subprocess.run(cmd, check=True)
            
            # Retrieve FQDN
            result = subprocess.run(
                [
                    "az", "containerapp", "show", 
                    "--name", app_name, 
                    "--resource-group", resource_group, 
                    "--query", "properties.configuration.ingress.fqdn", 
                    "--output", "tsv"
                ],
                capture_output=True, text=True, check=True
            )
            
            fqdn = result.stdout.strip()
            return f"https://{fqdn}"
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Deployment failed for {app_name}. Check Azure logs.")
            raise