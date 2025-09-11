from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# Mock DB setup/teardown can be added if needed

def test_list_quantitative_datasets():
    response = client.get("/quantitative_datasets")
    assert response.status_code == 200
    assert "quantitative_datasets" in response.json()

def test_create_quantitative_dataset(monkeypatch):
    # Patch QuantitativeDatasetService.add_from_json to return a mock
    class MockDS:
        def __init__(self, id, name, type):
            self.id = id
            self.name = name
            self.type = type
    monkeypatch.setattr(
        "src.manager.quantitative_dataset_manager.QuantitativeDatasetService.add_from_json",
        lambda db, body: [MockDS(1, "test", "typeA")]
    )
    response = client.post("/quantitative_dataset", json={"name": "test", "type": "typeA"})
    assert response.status_code == 200
    data = response.json()
    assert "datasets" in data
    assert data["datasets"][0]["name"] == "test"

def test_delete_quantitative_datasets(monkeypatch):
    monkeypatch.setattr(
        "src.manager.quantitative_dataset_manager.QuantitativeDatasetService.delete_by_id",
        lambda db, dataset_id: True
    )
    response = client.delete("/quantitative_datasets/1")
    assert response.status_code == 200
    assert response.json()["result"] is True

def test_delete_quantitative_datasets_not_found(monkeypatch):
    monkeypatch.setattr(
        "src.manager.quantitative_dataset_manager.QuantitativeDatasetService.delete_by_id",
        lambda db, dataset_id: False
    )
    response = client.delete("/quantitative_datasets/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Quantitative datasets not found"
