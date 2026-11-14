"""
Example: Multi-modal Vision Chat using OpenAI SDK format.
Works with SmolVLM, Qwen2-VL, and Llama 3.2 Vision.
"""

import os
from openai import OpenAI

BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:8080/v1")
API_KEY = os.getenv("OPENAI_API_KEY", "your_secret_api_key_here")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

def vision_demo():
    image_url = "https://images.pexels.com/photos/20787/pexels-photo.jpg"
    print(f"Analyzing Image from: {image_url}...")

    response = client.chat.completions.create(
        model="HuggingFaceTB/SmolVLM-500M-Instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is shown in this picture? Describe it concisely."},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        max_tokens=100
    )

    print("\n✅ Vision Result:")
    print(response.choices[0].message.content)

if __name__ == "__main__":
    vision_demo()

