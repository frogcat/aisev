from fastapi.testclient import TestClient
from src.main import app
from src.db.define_tables import Dataset, engine
from sqlalchemy.orm import sessionmaker

client = TestClient(app)


def test_qualitative_datasets():
    response = client.get("/qualitative_datasets")
    assert response.status_code == 200
    data = response.json()
    assert "qualitative_datasets" in data
    assert isinstance(data["qualitative_datasets"], list)
    for item in data["qualitative_datasets"]:
        assert "id" in item
        assert "name" in item
        assert "perspective" in item
        assert "contents" in item


def test_create_qualitative_dataset():
    post_data = {
        "name": "サンプル質問",
        "criterion": "有害情報の出力制御",
        "contents": [
            "質問その１",
            "質問その２",
            "質問その３"
        ]
    }
    response = client.post("/qualitative_dataset", json=post_data)
    assert response.status_code == 200
    data = response.json()
    assert "datasets" in data
    assert isinstance(data["datasets"], list)
    assert len(data["datasets"]) > 0
    for ds in data["datasets"]:
        assert "id" in ds
        assert "name" in ds
        assert "type" in ds
        assert ds["name"].startswith("サンプル")
        assert ds["type"] == "qualitative"


def test_delete_qualitative_datasets():
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    ds = Dataset(name="test_ds_delete_qual",
                 data_content=b"A", type="qualitative")
    session.add(ds)
    session.commit()
    ds_id = ds.id
    session.close()

    del_response = client.delete(f"/qualitative_datasets/{ds_id}")
    assert del_response.status_code == 200
    assert del_response.json() == {"result": True}

    del_response2 = client.delete("/qualitative_datasets/9999999")
    assert del_response2.status_code == 404
    assert del_response2.json()["detail"] == "Qualitative datasets not found"


def test_get_qualitative_dataset():
    # First create test data
    post_data = {
        "name": "取得テスト用質問",
        "criterion": "有害情報の出力制御",
        "contents": ["質問A", "質問B"]
    }
    post_response = client.post("/qualitative_dataset", json=post_data)
    assert post_response.status_code == 200
    ds = post_response.json()["datasets"][0]
    ds_id = ds["id"]

    # --- Retrieve with existing ID ---
    get_response = client.get(f"/qualitative_datasets/{ds_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == ds_id
    assert data["name"] == "取得テスト用質問"
    assert data["perspective"] == "有害情報の出力制御"
    # Modify contents format to match actual response
    assert isinstance(data["contents"], list)
    assert len(data["contents"]) == 2
    # Verify that each element in contents is in object format
    for i, content in enumerate(data["contents"]):
        assert "id" in content
        assert "text" in content
        assert isinstance(content["id"], int)
        assert isinstance(content["text"], str)
    # Verify text content is correct
    content_texts = [content["text"] for content in data["contents"]]
    assert "質問A" in content_texts
    assert "質問B" in content_texts

    # --- Retrieve with non-existent ID ---
    get_response_404 = client.get("/qualitative_datasets/9999999")
    assert get_response_404.status_code == 404
    assert get_response_404.json()["detail"] == "Qualitative dataset not found"


def test_get_qualitative_datasets_by_evaluation_id():
    # 1. Create qualitative dataset
    post_data = {
        "name": "評価ID取得テスト用質問",
        "criterion": "有害情報の出力制御",
        "contents": ["質問X", "質問Y"]
    }
    post_response = client.post("/qualitative_dataset", json=post_data)
    assert post_response.status_code == 200
    ds = post_response.json()["datasets"][0]
    ds_id = ds["id"]

    # 2. Create evaluation definition (include above qualitative dataset in criteria)
    eval_data = {
        "evaluationName": "APIテスト評価_定性取得",
        "criteria": [
            {
                "criterion": "有害情報の出力制御",
                "quantitative": {
                    "checked": False,
                    "datasets": [],
                    "percentage": 0,
                    "text": ""
                },
                "qualitative": {
                    "checked": True,
                    "questions": [ds_id],
                    "percentage": 100
                }
            }
        ]
    }
    eval_response = client.post("/evaluation", json=eval_data)
    assert eval_response.status_code == 200
    evaluation_id = eval_response.json()["evaluation_id"]
    assert isinstance(evaluation_id, int)

    # 3. Retrieve by evaluation ID
    get_response = client.get(
        f"/qualitative_datasets/by_evaluation/{evaluation_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert isinstance(data["qualitative_datasets"], list)
    assert any(item["id"] == ds_id for item in data["qualitative_datasets"])

    # 4. Retrieve with non-existent evaluation ID
    get_response_404 = client.get(
        "/qualitative_datasets/by_evaluation/9999999")
    assert get_response_404.status_code == 404
    assert get_response_404.json(
    )["detail"] == "Qualitative datasets not found for the given evaluation_id"
