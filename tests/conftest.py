import os
import sys
import pytest

# Ensure root and src are in path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(root_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Set test environment variables BEFORE importing app
os.environ["TEST_MODE"] = "true"
os.environ["API_KEY"] = "test-secret-key-123"
os.environ["TASK_TYPE"] = "chat"
os.environ["HF_MODEL_ID"] = "Qwen/Qwen2.5-1.5B-Instruct"

from app import app
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
