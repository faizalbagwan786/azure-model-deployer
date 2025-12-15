docker-compose up --build -d
curl -X 'POST' \
  'http://localhost:8081/predict' \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: SetYourOwnSecretKeyHere' \
  -d '{
  "text": "Describe this image",
  "image_url": "[https://images.pexels.com/photos/20787/pexels-photo.jpg](https://images.pexels.com/photos/20787/pexels-photo.jpg)",
  "max_length": 100
}'

# Azure Model Deployer 🚀

> **Production-ready, secure, and flexible model deployment for text and vision models on Azure or locally.**

---

## Overview

Welcome! This project lets you deploy and run both text (GPT-2) and vision-language (SmolVLM) models with ease. You can switch between small and large models by changing a single config value—no code edits needed. Security and reliability are built in.

---

## ✨ Features

- **Universal Model Support:**
  - Auto-detects and runs either `SmolVLM-500M` or `SmolVLM2-2.2B`.
- **Security First:**
  - 🔐 **API Key Auth:** All endpoints require an `X-API-Key` header.
  - 🛡️ **Crash Prevention:** Strict limits on text length and token count.
  - 🚦 **Rate Limiting:** 10 requests/minute per client.
- **Easy Local Development:**
  - `docker-compose` spins up both models on different ports for easy testing.

---

## 🚀 Quickstart

### 1. Environment Setup

Create a `.env` file in the project root (copy from `.env.example` if available):

```ini
# Set your own strong API key!
API_KEY=SetYourOwnSecretKeyHere

# Choose your model:
# For the fast/small version:
# HF_MODEL_ID=HuggingFaceTB/SmolVLM-500M-Instruct
# For the smart/large version:
HF_MODEL_ID=HuggingFaceTB/SmolVLM2-2.2B-Instruct

# System settings
TASK_TYPE=vlm
MAX_TOKENS=128
```

### 2. Start the Server

Build and launch everything with:

```bash
docker-compose up --build -d
```

- **GPT-2 (Text):** http://localhost:8080
- **SmolVLM (Vision):** http://localhost:8081

---

## 🧪 Testing the API

**PowerShell Example:**

```powershell
Invoke-RestMethod -Uri "http://localhost:8081/predict" `
  -Method Post `
  -Headers @{"X-API-Key"="SetYourOwnSecretKeyHere"} `
  -ContentType "application/json" `
  -Body '{"text": "Describe this image", "image_url": "https://images.pexels.com/photos/20787/pexels-photo.jpg", "max_length": 100}'
```

**Curl Example (Linux/Azure):**

```bash
curl -X POST \
  http://localhost:8081/predict \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: SetYourOwnSecretKeyHere' \
  -d '{
    "text": "Describe this image",
    "image_url": "https://images.pexels.com/photos/20787/pexels-photo.jpg",
    "max_length": 100
  }'
```

---

## 🔄 Switching Models

1. Open your `.env` file.
2. Change the `HF_MODEL_ID` value to the desired model.
3. Run `docker-compose up -d` to restart with the new model.

---

## ☁️ Azure Deployment Notes

- **Memory:** The 2.2B model requires at least 8GB RAM. The 500M model works with less.
- **Secrets:** The `.env` file is not included for security. Set environment variables manually in the Azure portal when deploying.

---

## 🙌 Need Help?

Open an issue or reach out if you have questions or need support!