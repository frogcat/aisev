from src.manager.quantitative_dataset_manager import QuantitativeDatasetService
from src.db.define_tables import Dataset, EvaluationPerspective
from src.manager.dataset_manager import DatasetManager
import pickle


def test_add_from_json_quantitative(session, setup_perspectives):
    """
    Test if quantitative data is correctly added to Dataset table by QuantitativeDatasetService.add_from_json
    """
    perspective = EvaluationPerspective(perspective_name="perspective1")
    session.add(perspective)
    session.commit()
    data = {
        "name": "quant1",
        "criterion": "perspective1",
        "contents": [
            {"q": "Q1", "a": 1},
            {"q": "Q2", "a": 2}
        ]
    }
    added = QuantitativeDatasetService.add_from_json(session, data)
    assert len(added) == 1
    ds = session.query(Dataset).filter_by(name="quant1").first()
    assert ds is not None
    assert ds.type == "quantitative"
    assert pickle.loads(ds.data_content) == data["contents"]
    assert ds.evaluation_perspective_id == perspective.id


def test_get_all_quantitative(session, setup_perspectives):
    """
    Test that QuantitativeDatasetService.get_all can retrieve only data with type quantitative
    """
    perspective = EvaluationPerspective(perspective_name="perspective2")
    session.add(perspective)
    session.commit()
    ds1 = Dataset(name="quant2", data_content=pickle.dumps(
        [{"q": "Q3", "a": 3}]), evaluation_perspective_id=perspective.id, type="quantitative")
    ds2 = Dataset(name="qual1", data_content=pickle.dumps(
        [{"q": "Q4", "a": "A4"}]), evaluation_perspective_id=perspective.id, type="qualitative")
    session.add_all([ds1, ds2])
    session.commit()
    nan_sample =             {
                "name": "混合スコアラーデータセット",
                "data": """ID,text,output,ans0,ans1,ans2,requirement,ten_perspective,scorer
mix1,混合質問1,A,選択肢1,選択肢2,選択肢3,要件1,ロバスト性,multiple_choice
mix2,混合質問2,回答2,,,,要件2,ロバスト性,requirement
mix3,混合質問3,回答3,,,,要件3,データ品質,model_graded_qa"""
            }
    DatasetManager.register_dataset(session, nan_sample["name"], nan_sample["data"])
    results = QuantitativeDatasetService.get_all(session)
    assert any(d["name"] == "quant2" for d in results)
    assert all(d["name"] != "qual1" for d in results)
    assert all(d["name"] != "mix1" for d in results)


def test_delete_by_id_quantitative(session):
    """
    Test that only quantitative data is deleted by QuantitativeDatasetService.delete_by_id
    - When specifying non-existing ID or qualitative data ID, 0 items are deleted
    """
    perspective = EvaluationPerspective(perspective_name="perspective3")
    session.add(perspective)
    session.commit()
    ds_quant = Dataset(name="quant3", data_content=b"Q5",
                       evaluation_perspective_id=perspective.id, type="quantitative")
    ds_qual = Dataset(name="qual2", data_content=b"Q6",
                      evaluation_perspective_id=perspective.id, type="qualitative")
    session.add_all([ds_quant, ds_qual])
    session.commit()
    quant_id = ds_quant.id
    qual_id = ds_qual.id
    # --- Delete quantitative data ---
    deleted_count = QuantitativeDatasetService.delete_by_id(session, quant_id)
    assert deleted_count == 1
    assert session.query(Dataset).filter_by(id=quant_id).first() is None
    # --- Qualitative data should not be deleted ---
    deleted_count2 = QuantitativeDatasetService.delete_by_id(session, qual_id)
    assert deleted_count2 == 0
    still_exists = session.query(Dataset).filter_by(id=qual_id).first()
    assert still_exists is not None
    # --- Non-existing ID ---
    deleted_count3 = QuantitativeDatasetService.delete_by_id(session, -999)
    assert deleted_count3 == 0

def test_quantitative_add_from_json(session):
    """
    Test if quantitative data is correctly added to Dataset table by QuantitativeDatasetService.add_from_json
    """
    perspective = EvaluationPerspective(perspective_name="perspective1")
    session.add(perspective)
    session.commit()
    data = {
        "name": "quant1",
        "criterion": "perspective1",
        "contents": [
            {"q": "Q1", "a": 1},
            {"q": "Q2", "a": 2}
        ]
    }
    added = QuantitativeDatasetService.add_from_json(session, data)
    assert len(added) == 1
    ds = session.query(Dataset).filter_by(name="quant1").first()
    assert ds is not None
    assert ds.type == "quantitative"
    assert pickle.loads(ds.data_content) == data["contents"]
    assert ds.evaluation_perspective_id == perspective.id
    session.close()


def test_quantitative_get_all(session):
    """
    Test that QuantitativeDatasetService.get_all can retrieve only data with type quantitative
    """
    perspective = EvaluationPerspective(perspective_name="perspective2")
    session.add(perspective)
    session.commit()
    ds1 = Dataset(name="quant2", data_content=pickle.dumps(
        [{"q": "Q3", "a": 3}]), evaluation_perspective_id=perspective.id, type="quantitative")
    ds2 = Dataset(name="qual1", data_content=pickle.dumps(
        [{"q": "Q4", "a": "A4"}]), evaluation_perspective_id=perspective.id, type="qualitative")
    session.add_all([ds1, ds2])
    session.commit()
    results = QuantitativeDatasetService.get_all(session)
    assert any(d["name"] == "quant2" for d in results)
    assert all(d["name"] != "qual1" for d in results)
    session.close()


def test_quantitative_delete_by_id(session):
    """
    Test that only quantitative data is deleted by QuantitativeDatasetService.delete_by_id
    - When specifying non-existing ID or qualitative data ID, 0 items are deleted
    """
    perspective = EvaluationPerspective(perspective_name="perspective3")
    session.add(perspective)
    session.commit()
    ds_quant = Dataset(name="quant3", data_content=b"Q5",
                       evaluation_perspective_id=perspective.id, type="quantitative")
    ds_qual = Dataset(name="qual2", data_content=b"Q6",
                      evaluation_perspective_id=perspective.id, type="qualitative")
    session.add_all([ds_quant, ds_qual])
    session.commit()
    quant_id = ds_quant.id
    qual_id = ds_qual.id
    # --- Delete quantitative data ---
    deleted_count = QuantitativeDatasetService.delete_by_id(session, quant_id)
    assert deleted_count == 1
    assert session.query(Dataset).filter_by(id=quant_id).first() is None
    # --- Qualitative data should not be deleted ---
    deleted_count2 = QuantitativeDatasetService.delete_by_id(session, qual_id)
    assert deleted_count2 == 0
    still_exists = session.query(Dataset).filter_by(id=qual_id).first()
    assert still_exists is not None
    # --- Non-existing ID ---
    deleted_count3 = QuantitativeDatasetService.delete_by_id(session, -999)
    assert deleted_count3 == 0
    session.close()