# Azure Model Deployer (Local)

## Start
docker-compose build --no-cache
docker-compose up -d

## Test GPT2
curl -X POST http://localhost:8080/predict \
  -H "X-API-Key: sk_local_2f9c4ad8b71e4ce0b5d9e3fc847a1f92" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello"}'

## Test SmolVLM
curl -X POST http://localhost:8081/predict \
  -H "X-API-Key: sk_local_2f9c4ad8b71e4ce0b5d9e3fc847a1f92" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Describe the image",
    "image_url": "https://images.pexels.com/photos/20787/pexels-photo.jpg"
  }'
