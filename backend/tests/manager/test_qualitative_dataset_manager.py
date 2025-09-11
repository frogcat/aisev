import pickle
import pytest
from src.manager.qualitative_dataset_manager import QualitativeDatasetService
from src.manager.quantitative_dataset_manager import QuantitativeDatasetService
from src.db.define_tables import Dataset, EvaluationPerspective, DatasetCustomMapping


def test_add_from_json(session, setup_perspectives):
    """
    Test if qualitative data is correctly added to Dataset table by QualitativeDatasetService.add_from_json
    - Multiple contents are added
    - name, data_content, type, evaluation_perspective_id are correct
    - Can be restored with pickle
    - IDs within contents are unique
    - 2 items are added
    """
    # Register "公平性と包摂性" as perspective
    perspective = EvaluationPerspective(perspective_name="公平性と包摂性")
    session.add(perspective)
    session.commit()
    # Sample JSON
    data = {
        "name": "質問セットA",
        "criterion": "公平性と包摂性",
        "contents": [
            "質問1: あなたの好きな色は何ですか？",
            "質問2: あなたの趣味は何ですか？"
        ]
    }
    data2 = {
        "name": "質問セットA",
        "criterion": "公平性と包摂性",
        "contents": [
            {"id": 1, "text": "質問1: あなたの好きな色は何ですか？"},
            {"id": 2, "text": "質問2: あなたの趣味は何ですか？"}
        ]
    }
    # Execute
    added = QualitativeDatasetService.add_from_json(session, data)
    added2 = QualitativeDatasetService.add_from_json(session, data2)
    # 2 items are added
    all_added = added + added2
    assert len(all_added) == 2
    # Get from DB
    db_ds_list = session.query(Dataset).filter(Dataset.id.in_([ds.id for ds in all_added])).all()
    assert len(db_ds_list) == 2
    for db_ds in db_ds_list:
        assert db_ds is not None
        assert db_ds.name == "質問セットA"
        assert db_ds.type == "qualitative"
        # Contents can be restored with pickle
        contents = pickle.loads(db_ds.data_content)
        assert isinstance(contents, list)
        for item in contents:
            assert "id" in item and "text" in item
        # Check uniqueness of IDs (within each dataset)
        ids = [item["id"] for item in contents]
        assert len(ids) == len(set(ids)), "contents内のidが一意であること"
        # evaluation_perspective_idが正しい
        perspective_db = session.query(EvaluationPerspective).filter_by(
            perspective_name="公平性と包摂性").first()
        assert db_ds.evaluation_perspective_id == perspective_db.id
    # Dataset IDs should be unique
    ids = [ds.id for ds in all_added]
    assert len(ids) == len(set(ids)), "DatasetのIDが一意であること"
    session.close()


def test_add_from_json_invalid_perspective(session, setup_perspectives):
    """
    Test that ValueError occurs when criterion does not exist
    """
    data = {
        "name": "質問セットB",
        "criterion": "存在しない観点",
        "contents": ["質問X"]
    }
    with pytest.raises(ValueError) as e:
        QualitativeDatasetService.add_from_json(session, data)
    assert "EvaluationPerspective with name 存在しない観点 not found" in str(e.value)


def test_add_from_json_empty_contents(session, setup_perspectives):
    """
    Test that data can be added even when contents is an empty list
    """
    data = {
        "name": "質問セットC",
        "criterion": "公平性と包摂性",
        "contents": []
    }
    added = QualitativeDatasetService.add_from_json(session, data)
    assert len(added) == 1
    ds = added[0]
    db_ds = session.query(Dataset).filter_by(id=ds.id).first()
    assert db_ds is not None
    assert pickle.loads(db_ds.data_content) == []


def test_delete_by_id(session):
    """
    Test that only qualitative data is deleted by QualitativeDatasetService.delete_by_id
    - When specifying ID of existing qualitative data, 1 item is deleted
    - When specifying non-existing ID or quantitative data ID, 0 items are deleted
    - After deletion, the corresponding data does not exist in DB
    """
    # Add qualitative data
    ds_qual = Dataset(name="qual1", data_content=b"Q1", type="qualitative")
    ds_quant = Dataset(name="quant1", data_content=b"Q2", type="quantitative")
    session.add_all([ds_qual, ds_quant])
    session.commit()
    qual_id = ds_qual.id
    quant_id = ds_quant.id

    # --- Delete qualitative data ---
    deleted_count = QualitativeDatasetService.delete_by_id(session, qual_id)
    assert deleted_count == 1, "qualitativeデータが1件削除されること"
    # Being missing from the DB
    deleted = session.query(Dataset).filter_by(id=qual_id).first()
    assert deleted is None, "削除後、qualitativeデータがDBに存在しない"

    # --- Quantitative data should not be deleted ---
    deleted_count2 = QualitativeDatasetService.delete_by_id(session, quant_id)
    assert deleted_count2 == 0, "quantitativeデータは削除されないこと"
    still_exists = session.query(Dataset).filter_by(id=quant_id).first()
    assert still_exists is not None, "quantitativeデータはDBに残っていること"

    # --- Non-existing ID ---
    deleted_count3 = QualitativeDatasetService.delete_by_id(session, -999)
    assert deleted_count3 == 0, "存在しないIDでは0件削除となること"
    session.close()


def test_get_by_id(session, setup_perspectives):
    """
    Test if qualitative data with specified ID can be correctly retrieved by QualitativeDatasetService.get_by_id
    - When specifying ID of existing qualitative data, correct content is returned as dict
    - When ID does not exist, None is returned
    - When specifying quantitative data ID, None is also returned
    """
    # Add qualitative data
    perspective = session.query(EvaluationPerspective).filter_by(
        perspective_name="公平性と包摂性").first()
    contents = [
        {"id": 1, "text": "質問A"},
        {"id": 2, "text": "質問B"}
    ]
    ds_qual = Dataset(name="qual_get", data_content=pickle.dumps(
        contents), type="qualitative", evaluation_perspective_id=perspective.id)
    ds_quant = Dataset(name="quant_get", data_content=pickle.dumps(
        [1, 2, 3]), type="quantitative")
    session.add_all([ds_qual, ds_quant])
    session.commit()
    qual_id = ds_qual.id
    quant_id = ds_quant.id

    # --- Existing qualitative data ---
    result = QualitativeDatasetService.get_by_id(session, qual_id)
    assert result is not None
    assert result["id"] == qual_id
    assert result["name"] == "qual_get"
    assert result["perspective"] == "公平性と包摂性"
    assert result["contents"] == contents

    # --- Non-existing ID ---
    result_none = QualitativeDatasetService.get_by_id(session, -999)
    assert result_none is None

    # --- Quantitative data ID ---
    result_quant = QualitativeDatasetService.get_by_id(session, quant_id)
    assert result_quant is None
    session.close()


def test_get_by_evaluation_id_with_evaluation_model(session, setup_perspectives):
    """
    Test QualitativeDatasetService.get_by_evaluation_id when using Evaluation model
    - Associated qualitative data can be correctly retrieved
    - Empty list when evaluation_id does not exist
    - Empty list when associated data is only quantitative
    """
    import pickle
    from src.db.define_tables import Evaluation
    from src.manager.qualitative_dataset_manager import QualitativeDatasetService

    # --- Preparation: evaluation, mapping, dataset(qualitative) ---
    evaluation = Evaluation(name="評価A", custom_datasets_id=101)
    session.add(evaluation)
    session.commit()
    # qualitative data
    contents = {"q1": "question1", "q2": "question2"}
    ds_qual = Dataset(name="qual_ds_eval", data_content=pickle.dumps(
        contents), type="qualitative")
    session.add(ds_qual)
    session.commit()
    # Get perspective (use existing one created by setup_perspectives)
    perspective = session.query(EvaluationPerspective).first()
    # mapping
    mapping = DatasetCustomMapping(
        custom_datasets_id=101, dataset_id=ds_qual.id, perspective_id=perspective.id)
    session.add(mapping)
    session.commit()

    # --- Get qualitative data ---
    result = QualitativeDatasetService.get_by_evaluation_id(
        session, evaluation.id)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == ds_qual.id
    assert result[0]["name"] == "qual_ds_eval"
    assert result[0]["contents"] == contents

    # --- Non-existing evaluation_id ---
    result_none = QualitativeDatasetService.get_by_evaluation_id(session, -999)
    assert result_none == []

    # --- Case with only quantitative data ---
    evaluation2 = Evaluation(name="評価B", custom_datasets_id=202)
    session.add(evaluation2)
    session.commit()
    ds_quant = Dataset(name="quant_ds_eval", data_content=pickle.dumps(
        [1, 2, 3]), type="quantitative")
    session.add(ds_quant)
    session.commit()
    mapping2 = DatasetCustomMapping(
        custom_datasets_id=202, dataset_id=ds_quant.id, perspective_id=perspective.id)
    session.add(mapping2)
    session.commit()
    result_quant = QualitativeDatasetService.get_by_evaluation_id(
        session, evaluation2.id)
    assert result_quant == []
    session.close()
