"""
Example: Real-time token streaming with ChatGPT-style typewriter effect.
Demonstrates Server-Sent Events (SSE) streaming compatibility.
"""

import os
import sys
import time
from openai import OpenAI

BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:8080/v1")
API_KEY = os.getenv("OPENAI_API_KEY", "your_secret_api_key_here")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

def streaming_demo():
    prompt = "Write a Python function to compute Fibonacci numbers with memoization and explain it."
    print(f"User: {prompt}\n")
    print("Assistant: ", end="", flush=True)

    stream = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        max_tokens=300
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            sys.stdout.write(delta)
            sys.stdout.flush()
    print("\n\n✅ Stream completed successfully.")

if __name__ == "__main__":
    streaming_demo()

