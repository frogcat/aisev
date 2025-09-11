from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)



def test_create_ai_model():
    payload = {
        "name": "test-model",
        "url": "http://localhost/api",
        "apiKey": "dummy-key",
        "promptFormat": "{prompt}",
        "type": "both"
    }
    response = client.post("/ai_models", json=payload)
    assert response.status_code in (200, 201)
    data = response.json()
    assert "ai_model" in data
    model = data["ai_model"]
    assert model["name"] == payload["name"]
    assert model["url"] == payload["url"]
    assert model["apiKey"] == payload["apiKey"]
    assert model["promptFormat"] == payload["promptFormat"]
    assert model["type"] == payload["type"]

def test_update_ai_model():
    # First create a model
    payload = {
        "name": "update-test-model",
        "url": "http://localhost/api/update",
        "apiKey": "update-key",
        "promptFormat": "{prompt}",
        "type": "both"
    }
    create_resp = client.post("/ai_models", json=payload)
    assert create_resp.status_code in (200, 201)
    model_id = create_resp.json()["ai_model"]["id"]

    # Data for update
    update_payload = {
        "name": "updated-model",
        "url": "http://localhost/api/updated",
        "apiKey": "updated-key",
        "promptFormat": "<prompt>",
        "type": "both"
    }
    update_resp = client.put(f"/ai_models/{model_id}", json=update_payload)
    assert update_resp.status_code == 200
    updated = update_resp.json()["ai_model"]
    assert updated["name"] == update_payload["name"]
    assert updated["url"] == update_payload["url"]
    assert updated["apiKey"] == update_payload["apiKey"]
    assert updated["promptFormat"] == update_payload["promptFormat"]
    assert updated["type"] == update_payload["type"]

def test_delete_ai_model():
    # First create a model
    payload = {
        "name": "delete-test-model",
        "url": "http://localhost/api/delete",
        "apiKey": "delete-key",
        "promptFormat": "{prompt}",
        "type": "both"
    }
    create_resp = client.post("/ai_models", json=payload)
    assert create_resp.status_code in (200, 201)
    model_id = create_resp.json()["ai_model"]["id"]

    # Delete the model
    delete_resp = client.delete(f"/ai_models/{model_id}")
    assert delete_resp.status_code == 200
    data = delete_resp.json()
    assert data["result"] is True

    # Getting after deletion should return 404
    get_resp = client.get(f"/ai_models/{model_id}")
    assert get_resp.status_code == 404


def test_list_ai_models():
    response = client.get("/ai_models")
    assert response.status_code == 200
    data = response.json()
    assert "ai_models" in data
    assert isinstance(data["ai_models"], list)
    # Optionally, check structure of first item if list is not empty
    if data["ai_models"]:
        model = data["ai_models"][0]
        assert set(["id", "name", "url", "apiKey", "promptFormat", "type"]).issubset(model.keys())