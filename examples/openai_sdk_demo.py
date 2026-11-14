"""
Example: Drop-in replacement for OpenAI SDK using your Private Azure AI Gateway.
Run this directly with the official 'openai' library!
pip install openai
"""

import os
from openai import OpenAI

# Point to your local server or deployed Azure Container App
BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:8080/v1")
API_KEY = os.getenv("OPENAI_API_KEY", "your_secret_api_key_here")

# Initialize official OpenAI client
client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)

def chat_demo():
    print(f"Connecting to Private Gateway: {BASE_URL}...")
    
    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-1.5B-Instruct", # or "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
        messages=[
            {"role": "system", "content": "You are an expert cloud architect and senior software engineer."},
            {"role": "user", "content": "Explain why Scale-to-Zero on Azure saves 90% cloud costs in 2 sentences."}
        ],
        temperature=0.7,
        max_tokens=150
    )

    print("\n✅ Response Received:")
    print(response.choices[0].message.content)
    print("\n📊 Token Usage:", response.usage)

if __name__ == "__main__":
    chat_demo()

