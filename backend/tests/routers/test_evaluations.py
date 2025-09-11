from fastapi.testclient import TestClient
from src.main import app
from src.db.define_tables import Dataset, engine
from sqlalchemy.orm import sessionmaker

client = TestClient(app)


def test_evaluations():
    response = client.get("/evaluations")
    assert response.status_code == 200
    data = response.json()
    assert "evaluations" in data
    assert isinstance(data["evaluations"], list)
    assert len(data["evaluations"]) > 0
    for item in data["evaluations"]:
        assert "id" in item
        assert "name" in item
        assert "createdAt" in item
        assert "usedDatasets" in item


def test_create_evaluation():
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    ds = Dataset(name="test_ds_create", data_content=b"A", type="quantitative")
    session.add(ds)
    session.commit()
    ds_id = ds.id
    session.close()

    eval_data = {
        "evaluationName": "APIテスト評価POST",
        "criteria": [
            {
                "criterion": "テスト観点POST",
                "quantitative": {
                    "checked": True,
                    "datasets": [ds_id],
                    "percentage": 100,
                    "text": "テストプロンプトPOST"
                },
                "qualitative": {
                    "checked": False,
                    "questions": [],
                    "percentage": 0
                }
            }
        ]
    }
    response = client.post("/evaluation", json=eval_data)
    assert response.status_code == 200
    eval_id = response.json()["evaluation_id"]
    assert isinstance(eval_id, int)


def test_delete_evaluation():
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    ds = Dataset(name="test_ds_delete", data_content=b"A", type="quantitative")
    session.add(ds)
    session.commit()
    ds_id = ds.id
    session.close()

    eval_data = {
        "evaluationName": "APIテスト評価DELETE",
        "criteria": [
            {
                "criterion": "テスト観点DELETE",
                "quantitative": {
                    "checked": True,
                    "datasets": [ds_id],
                    "percentage": 100,
                    "text": "テストプロンプトDELETE"
                },
                "qualitative": {
                    "checked": False,
                    "questions": [],
                    "percentage": 0
                }
            }
        ]
    }
    response = client.post("/evaluation", json=eval_data)
    assert response.status_code == 200
    eval_id = response.json()["evaluation_id"]
    assert isinstance(eval_id, int)

    del_response = client.delete(f"/evaluation/{eval_id}")
    assert del_response.status_code == 200
    assert del_response.json() == {"result": True}

    del_response2 = client.delete("/evaluation/9999999")
    assert del_response2.status_code == 404
    assert del_response2.json()["detail"] == "Evaluation not found"
