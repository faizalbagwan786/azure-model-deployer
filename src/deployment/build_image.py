import subprocess
import logging

logger = logging.getLogger(__name__)

def build_docker_image(context_path, dockerfile_path, image_tag):
    """Wraps docker build command."""
    
    cmd = [
        "docker", "build",
        "-t", image_tag,
        "-f", dockerfile_path,
        context_path
    ]

    try:
        subprocess.run(cmd, check=True)
        logger.info(f"Successfully built: {image_tag}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Docker build failed. Ensure Docker is running. Error: {e}")
        raise