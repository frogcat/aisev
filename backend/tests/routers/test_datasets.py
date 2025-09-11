from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_datasets():
    response = client.get("/datasets")
    assert response.status_code == 200
    data = response.json()
    assert "datasets" in data
    assert isinstance(data["datasets"], list)
    for item in data["datasets"]:
        assert "id" in item
        assert "name" in item


def test_custom_datasets():
    response = client.get("/custom_datasets")
    assert response.status_code == 200
    data = response.json()
    assert "custom_datasets" in data
    assert isinstance(data["custom_datasets"], list)
    for item in data["custom_datasets"]:
        assert "id" in item
        assert "name" in item


def test_register_dataset():
    data = """ID,text,output,meta,meta-mlmc,ten_perspective\nid1, text1, output1, {\"key\": \"value\"}, {\"key\": \"value-mlmc\"}, perspective1\nid2, text2, output2, {\"key\": \"value\"}, {\"key\": \"value-mlmc\"}, perspective2\n"""
    name = "test_import_data"

    files = {"file": ("test.csv", data, "text/csv")}
    data_form = {"datasetName": name}

    response = client.post("/datasets/register", files=files, data=data_form)

    assert response.status_code == 200
    res = response.json()
    assert "id" in res
    assert "name" in res
    assert res.get("name") == name


def test_get_datasets_by_ids():
    # Register datasets
    data1 = """ID,text,output,meta,meta-mlmc,ten_perspective\nid1, text1, output1, {\"key\": \"value\"}, {\"key\": \"value-mlmc\"}, perspective1\n"""
    data2 = """ID,text,output,meta,meta-mlmc,ten_perspective\nid2, text2, output2, {\"key\": \"value2\"}, {\"key\": \"value-mlmc2\"}, perspective2\n"""
    files1 = {"file": ("test1.csv", data1, "text/csv")}
    files2 = {"file": ("test2.csv", data2, "text/csv")}
    data_form1 = {"datasetName": "ds1"}
    data_form2 = {"datasetName": "ds2"}
    res1 = client.post("/datasets/register", files=files1, data=data_form1)
    res2 = client.post("/datasets/register", files=files2, data=data_form2)
    assert res1.status_code == 200
    assert res2.status_code == 200
    id1 = res1.json()["id"]
    id2 = res2.json()["id"]

    # Get IDs
    response = client.post("/datasets/by_ids", json={"ids": [id1, id2]})
    assert response.status_code == 200
    data = response.json()
    assert "datasets" in data
    ids = [d["id"] for d in data["datasets"]]
    assert id1 in ids and id2 in ids

    # Empty list
    response = client.post("/datasets/by_ids", json={"ids": []})
    assert response.status_code == 200
    assert response.json()["datasets"] == []

    # non-existed IDs
    response = client.post("/datasets/by_ids", json={"ids": [-999]})
    assert response.status_code == 200
    assert response.json()["datasets"] == []
