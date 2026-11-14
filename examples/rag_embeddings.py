"""
Example: Generate vector embeddings for RAG (Retrieval-Augmented Generation)
using your Private Azure AI Gateway and the official OpenAI SDK.
"""

import os
from openai import OpenAI

BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:8080/v1")
API_KEY = os.getenv("OPENAI_API_KEY", "your_secret_api_key_here")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

def embeddings_demo():
    texts = [
        "Azure Container Apps supports scale-to-zero microservices.",
        "OpenAI compatible endpoints simplify migrating from proprietary models.",
        "DeepSeek and Qwen offer powerful self-hosted open reasoning."
    ]

    print("Generating vector embeddings for RAG search...")
    response = client.embeddings.create(
        model="BAAI/bge-small-en-v1.5",
        input=texts
    )

    for item in response.data:
        print(f"✅ Text index {item.index}: Vector dimension = {len(item.embedding)} floats")

if __name__ == "__main__":
    embeddings_demo()

