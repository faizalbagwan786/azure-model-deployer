import os
import glob
import sys
import pytest

# Ensure deployment code can be imported
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(root_dir, "src", "deployment"))

from deploy_model import load_config, EnvironmentConfig, ModelConfig

def test_validate_all_environment_configs():
    env_dir = os.path.join(root_dir, "config", "environments")
    files = glob.glob(os.path.join(env_dir, "*.json"))
    assert len(files) >= 3, "Expected dev, staging, prod configs"
    for f in files:
        config = load_config(f, EnvironmentConfig)
        assert config.name is not None
        assert config.cpu > 0
        assert config.memory.endswith("Gi") or config.memory.endswith("Mi")
        assert config.min_replicas >= 0

def test_validate_all_model_configs():
    models_dir = os.path.join(root_dir, "config", "models")
    files = glob.glob(os.path.join(models_dir, "*.json"))
    assert len(files) >= 4, "Expected modern 2025/2026 models"
    for f in files:
        config = load_config(f, ModelConfig)
        assert config.model_key is not None
        assert len(config.huggingface_model_id) > 0
        assert config.port > 0
