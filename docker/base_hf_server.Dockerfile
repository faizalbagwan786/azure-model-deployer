FROM python:3.9-slim

WORKDIR /app

# Install dependencies
# Using --no-cache-dir to keep image size small
RUN pip install --no-cache-dir fastapi uvicorn transformers torch

COPY app.py /app/app.py

# Default port 8080
EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]