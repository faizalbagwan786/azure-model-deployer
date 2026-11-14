def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "endpoints" in data

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_web_playground_endpoint(client):
    response = client.get("/chat")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Private Azure AI Gateway" in response.text

def test_v1_models_without_auth(client):
    response = client.get("/v1/models")
    assert response.status_code == 401

def test_v1_models_with_bearer_auth(client):
    response = client.get(
        "/v1/models",
        headers={"Authorization": "Bearer test-secret-key-123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    assert len(data["data"]) >= 1

def test_v1_models_with_x_api_key_auth(client):
    response = client.get(
        "/v1/models",
        headers={"X-API-Key": "test-secret-key-123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"

def test_chat_completions_missing_auth(client):
    payload = {
        "messages": [{"role": "user", "content": "Hello"}]
    }
    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 401

def test_chat_completions_invalid_auth(client):
    payload = {
        "messages": [{"role": "user", "content": "Hello"}]
    }
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer wrong-key"},
        json=payload
    )
    assert response.status_code == 401

def test_chat_completions_valid_mock(client):
    payload = {
        "messages": [{"role": "user", "content": "Explain scale to zero"}]
    }
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer test-secret-key-123"},
        json=payload
    )
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "chat.completion"
    assert "choices" in data
    assert len(data["choices"]) > 0

def test_embeddings_endpoint(client):
    payload = {
        "input": "Search query for semantic vector embeddings"
    }
    response = client.post(
        "/v1/embeddings",
        headers={"Authorization": "Bearer test-secret-key-123"},
        json=payload
    )
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    assert len(data["data"]) > 0
