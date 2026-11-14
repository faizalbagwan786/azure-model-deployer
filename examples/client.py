"""
Example Python client demonstrating how to call the Azure AI Model Deployer endpoint.
Works with both local Docker endpoints and deployed Azure Container Apps.
"""

import os
import requests

API_URL = os.getenv("API_URL", "http://localhost:8081/predict")
API_KEY = os.getenv("API_KEY", "your_api_key_here")

def test_vlm_prediction():
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    payload = {
        "text": "What is depicted in this image? Provide a brief 1-sentence description.",
        "image_url": "https://images.pexels.com/photos/20787/pexels-photo.jpg",
        "max_length": 64
    }

    print(f"Calling endpoint: {API_URL}")
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ Success! Response:")
        print(data.get("result"))
    else:
        print(f"\n❌ Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    test_vlm_prediction()

