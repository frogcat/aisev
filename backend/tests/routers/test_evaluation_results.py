import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.db.define_tables import EvaluationResult, Evaluation, AIModel, CustomDatasets
from src.db.session import get_db
from datetime import date
from src.db.define_tables import Dataset, EvaluationPerspective, DatasetCustomMapping
from unittest.mock import patch
import pandas as pd
import pickle

client = TestClient(app)


def setup_test_data(db):
    # Create evaluation perspective
    eval_persp = EvaluationPerspective(perspective_name="有害情報の出力制御")
    db.add(eval_persp)
    db.commit()

    # Create CSV data (matching DatasetManager format)
    csv_data = """ID,text,output,meta,meta-mlmc,ten_perspective
id1,test input 1,test target 1,{"key": "value"},{"key": "value-mlmc"},有害情報の出力制御
id2,test input 2,test target 2,{"key": "value2"},{"key": "value-mlmc2"},有害情報の出力制御"""

    # Create dataset using DatasetManager
    from src.manager.dataset_manager import DatasetManager
    dataset = DatasetManager.register_dataset(db, "データセットA", csv_data)

    # Create custom dataset
    custom_dataset = CustomDatasets(name="カスタムデータセットA")
    db.add(custom_dataset)
    db.commit()

    # Mapping between dataset and custom dataset
    mapping = DatasetCustomMapping(
        dataset_id=dataset.id,
        custom_datasets_id=custom_dataset.id,
        perspective_id=eval_persp.id,
        prompt="ダミープロンプト",
        percentage=100
    )
    db.add(mapping)
    db.commit()

    evaluation = Evaluation(
        name="評価A",
        created_date=date(2024, 6, 1),
        custom_datasets_id=custom_dataset.id
    )
    db.add(evaluation)
    db.commit()

    ai_model_target = AIModel(
        name="ターゲットモデル",
        model_name="gpt-4o-mini",
        url="http://target-model",
        api_key="dummy",
        api_request_format={},
        type="target"
    )
    ai_model_evaluator = AIModel(
        name="評価モデル",
        model_name="gpt-4o",
        url="http://eval-model",
        api_key="dummy",
        api_request_format={},
        type="eval"
    )
    db.add_all([ai_model_target, ai_model_evaluator])
    db.commit()

    return evaluation, ai_model_target, ai_model_evaluator, dataset


@pytest.fixture
def db_session():
    db = next(get_db())
    yield db
    db.rollback()
    db.close()


@pytest.fixture
def test_data(db_session):
    return setup_test_data(db_session)


def test_create_evaluation_result(test_data):
    evaluation, ai_model_target, ai_model_evaluator, dataset = test_data
    req = {
        "name": "結果1",
        "evaluation_id": evaluation.id,
        "target_ai_model_id": ai_model_target.id,
        "evaluator_ai_model_id": ai_model_evaluator.id,
        "quantitative_eval_state": "running",
        "quantitative_results": None,
        "qualitative_results": None
    }
    res = client.post("/evaluation_result/", json=req)
    assert res.status_code == 200
    result_id = res.json()
    assert isinstance(result_id, int)
    # Check status to verify it returns "running"
    status = client.get(f"/evaluation_results/{result_id}/status")
    assert status.status_code == 200
    assert status.json() == "running"


@patch('src.inspect.inspect_common.register_in_inspect_ai')
@patch('src.inspect.eval_datasets.new_eval_by_ten_perspective')
def test_exec_quantitative_evaluation(mock_eval, mock_register, test_data):
    """Test quantitative evaluation execution (using mocks)"""
    evaluation, ai_model_target, ai_model_evaluator, dataset = test_data
    
    # Mock configuration
    mock_eval.return_value = {
        '有害情報の出力制御': '{"samples": [{"input": "test", "scores": {"model_graded_qa": {"value": "C"}}}]}'
    }
    mock_register.return_value = "mockprovider"
    
    # First create evaluation result
    req = {
        "name": "結果1",
        "evaluation_id": evaluation.id,
        "target_ai_model_id": ai_model_target.id,
        "evaluator_ai_model_id": ai_model_evaluator.id,
        "quantitative_eval_state": "running",
        "quantitative_results": None,
        "qualitative_results": None
    }
    res = client.post("/evaluation_result/", json=req)
    assert res.status_code == 200
    result_id = res.json()

    quantitative_req = {
        "evaluation_id": evaluation.id,
        "target_ai_model_id": ai_model_target.id,
        "evaluator_ai_model_id": ai_model_evaluator.id
    }
    res2 = client.post(
        f"/evaluation_results/{result_id}/quantitative_result", json=quantitative_req)
    assert res2.status_code == 200
    assert isinstance(res2.json(), int)

    # Check status to verify it returns "done"
    status = client.get(f"/evaluation_results/{result_id}/status")
    assert status.status_code == 200
    assert status.json() == "done"


def test_register_qualitative_result(test_data):
    evaluation, ai_model_target, ai_model_evaluator, dataset = test_data
    # First create evaluation result
    req = {
        "name": "結果1",
        "evaluation_id": evaluation.id,
        "target_ai_model_id": ai_model_target.id,
        "evaluator_ai_model_id": ai_model_evaluator.id,
        "quantitative_eval_state": "running",
        "quantitative_results": None,
        "qualitative_results": None
    }
    res = client.post("/evaluation_result/", json=req)
    result_id = res.json()
    
    # Match evaluation_results.py QualitativeResultRequest model
    qualitative_req = {
        "evaluationId": evaluation.id,
        "results": [
            {
                "questionId": 1, 
                "answer": "implemented", 
                "text": "質問1：有害情報の出力制御は適切ですか？", 
                "perspective": "有害情報の出力制御"
            },
            {
                "questionId": 2, 
                "answer": "partially_implemented", 
                "text": "質問2：有害情報の出力制御は部分的に実装されていますか？", 
                "perspective": "有害情報の出力制御"
            },
            {
                "questionId": 3, 
                "answer": "not_implemented", 
                "text": "質問3：有害情報の出力制御は実装されていませんか？", 
                "perspective": "有害情報の出力制御"
            }
        ]
    }
    res2 = client.post(
        f"/evaluation_results/{result_id}/qualitative_result", json=qualitative_req)
    assert res2.status_code == 200
    assert res2.json() == result_id


def test_get_eval_status(test_data):
    evaluation, ai_model_target, ai_model_evaluator, dataset = test_data
    req = {
        "name": "結果1",
        "evaluation_id": evaluation.id,
        "target_ai_model_id": ai_model_target.id,
        "evaluator_ai_model_id": ai_model_evaluator.id,
        "quantitative_eval_state": "running",
        "quantitative_results": None,
        "qualitative_results": None
    }
    res = client.post("/evaluation_result/", json=req)
    result_id = res.json()
    res2 = client.get(f"/evaluation_results/{result_id}/status")
    assert res2.status_code == 200
    assert res2.json() == "running"


def test_get_all_evaluation_results(test_data):
    evaluation, ai_model_target, ai_model_evaluator, dataset = test_data
    # まず評価結果を作成
    req = {
        "name": "結果1",
        "evaluation_id": evaluation.id,
        "target_ai_model_id": ai_model_target.id,
        "evaluator_ai_model_id": ai_model_evaluator.id,
        "quantitative_eval_state": "running",
        "quantitative_results": None,
        "qualitative_results": None
    }
    res = client.post("/evaluation_result/", json=req)
    assert res.status_code == 200
    result_id = res.json()
    # GET all records
    res2 = client.get("/evaluation_results/")
    assert res2.status_code == 200
    results = res2.json()
    assert isinstance(results, list)
    assert any(r["id"] == result_id for r in results)
    # Check content match
    result = next((r for r in results if r["id"] == result_id), None)
    assert result is not None
    assert result["name"] == "結果1"


@patch('src.inspect.inspect_common.register_in_inspect_ai')
@patch('src.inspect.eval_datasets.new_eval_by_ten_perspective')
def test_get_10perspective_scores(mock_eval, mock_register, test_data):
    """Test 10 perspective score retrieval (using mocks)"""
    evaluation, ai_model_target, ai_model_evaluator, dataset = test_data
    
    # Mock configuration
    mock_eval.return_value = {
        '有害情報の出力制御': '{"samples": [{"input": "test", "scores": {"model_graded_qa": {"value": "C"}}}]}'
    }
    mock_register.return_value = "mockprovider"
    
    # First create evaluation result
    req = {
        "name": "結果1",
        "evaluation_id": evaluation.id,
        "target_ai_model_id": ai_model_target.id,
        "evaluator_ai_model_id": ai_model_evaluator.id,
        "quantitative_eval_state": "running",
        "quantitative_results": None,
        "qualitative_results": None
    }
    res = client.post("/evaluation_result/", json=req)
    assert res.status_code == 200
    result_id = res.json()

    # Execute quantitative evaluation
    quantitative_req = {
        "evaluation_id": evaluation.id,
        "target_ai_model_id": ai_model_target.id,
        "evaluator_ai_model_id": ai_model_evaluator.id
    }
    res2 = client.post(
        f"/evaluation_results/{result_id}/quantitative_result", json=quantitative_req)
    assert res2.status_code == 200

    # Register qualitative evaluation
    qualitative_req = {
        "evaluationId": evaluation.id,
        "results": [
            {"questionId": 1, "answer": "implemented",
                "text": "質問1：AIモデルの結果は信頼できますか？", "perspective": "ロバスト性"},
            {"questionId": 2, "answer": "partially_implemented",
                "text": "質問2：AIモデルの性能は満足ですか？", "perspective": "検証可能性"},
            {"questionId": 3, "answer": "not_implemented",
                "text": "質問3：AIモデルの使いやすさはどうですか？", "perspective": "検証可能性"}
        ]
    }
    res3 = client.post(
        f"/evaluation_results/{result_id}/qualitative_result", json=qualitative_req)
    assert res3.status_code == 200
    assert res3.json() == result_id

    # Call 10 perspective scores API
    res4 = client.get(f"/evaluation_results/{result_id}/10perspective_scores")
    assert res4.status_code == 200
    scores = res4.json()
    assert isinstance(scores, dict)
    # Check if all 10 perspectives are included
    expected_keys = [
        "有害情報の出力制御",
        "偽誤情報の出力・誘導の防止",
        "公平性と包摂性",
        "ハイリスク利用・目的外利用への対処",
        "プライバシー保護",
        "セキュリティ確保",
        "説明可能性",
        "ロバスト性",
        "データ品質",
        "検証可能性"
    ]
    for key in expected_keys:
        assert key in scores
        assert isinstance(scores[key], float) or isinstance(scores[key], int)


@patch('src.inspect.inspect_common.register_in_inspect_ai')
@patch('src.inspect.eval_datasets.new_eval_by_ten_perspective')
def test_get_evaluation_result_detail(mock_eval, mock_register, test_data):
    """
    Test that /evaluation_results/{eval_result_id}/detail API correctly parses quantitative_results/qualitative_results and returns details array by perspective
    """
    evaluation, ai_model_target, ai_model_evaluator, dataset = test_data
    
    # Mock configuration
    mock_eval.return_value = {
        '有害情報の出力制御': '{"samples": [{"input": "test", "scores": {"model_graded_qa": {"value": "C"}}}]}'
    }
    mock_register.return_value = "mockprovider"
    
    # Create evaluation result
    req = {
        "name": "結果1",
        "evaluation_id": evaluation.id,
        "target_ai_model_id": ai_model_target.id,
        "evaluator_ai_model_id": ai_model_evaluator.id,
        "quantitative_eval_state": "running",
        "quantitative_results": None,
        "qualitative_results": None
    }
    res = client.post("/evaluation_result/", json=req)
    assert res.status_code == 200
    result_id = res.json()

    # Execute quantitative evaluation
    quantitative_req = {
        "evaluation_id": evaluation.id,
        "target_ai_model_id": ai_model_target.id,
        "evaluator_ai_model_id": ai_model_evaluator.id
    }
    res2 = client.post(
        f"/evaluation_results/{result_id}/quantitative_result", json=quantitative_req)
    assert res2.status_code == 200

    # Register qualitative evaluation
    qualitative_req = {
        "evaluationId": evaluation.id,
        "results": [
            {"questionId": 1, "answer": "implemented",
                "text": "定性質問A", "perspective": "有害情報の出力制御"},
            {"questionId": 2, "answer": "not_implemented",
                "text": "定性質問B", "perspective": "公平性と包摂性"}
        ]
    }
    res3 = client.post(
        f"/evaluation_results/{result_id}/qualitative_result", json=qualitative_req)
    assert res3.status_code == 200
    assert res3.json() == result_id

    # Call detail API
    res4 = client.get(f"/evaluation_results/{result_id}/detail")
    assert res4.status_code == 200
    detail = res4.json()
    assert isinstance(detail, dict)
    for perspective, items in detail.items():
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, dict)
            assert "type" in item
            assert "question" in item
            assert "answer" in item
            assert "score" in item
            assert "metadata" in item
            assert item["type"] in ["quantitative", "qualitative"]


def test_comprehensive_evaluation_flow(test_data):
    """
    Test comprehensive evaluation flow
    """
    evaluation, ai_model_target, ai_model_evaluator, dataset = test_data
    
    # 1. Create evaluation result
    create_req = {
        "name": "包括的テスト結果",
        "evaluation_id": evaluation.id,
        "target_ai_model_id": ai_model_target.id,
        "evaluator_ai_model_id": ai_model_evaluator.id,
        "quantitative_eval_state": "running",
        "quantitative_results": None,
        "qualitative_results": None
    }
    create_res = client.post("/evaluation_result/", json=create_req)
    assert create_res.status_code == 200
    result_id = create_res.json()
    
    # 2. Check status (running)
    status_res = client.get(f"/evaluation_results/{result_id}/status")
    assert status_res.status_code == 200
    assert status_res.json() == "running"
    
    # 3. Register qualitative evaluation (add text field)
    qualitative_req = {
        "evaluationId": evaluation.id,
        "results": [
            {
                "questionId": 1, 
                "answer": "implemented", 
                "text": "質問1：有害情報の出力制御は適切ですか？",
                "perspective": "有害情報の出力制御"
            }
        ]
    }
    qual_res = client.post(
        f"/evaluation_results/{result_id}/qualitative_result", json=qualitative_req)
    assert qual_res.status_code == 200
    
    # 4. Check that created data is included in get all
    all_res = client.get("/evaluation_results/")
    assert all_res.status_code == 200
    results = all_res.json()
    assert any(r["id"] == result_id and r["name"] == "包括的テスト結果" for r in results)


def test_error_handling(test_data):
    """
    Test error handling
    """
    evaluation, ai_model_target, ai_model_evaluator, dataset = test_data
    
    # Status retrieval with non-existent result_id
    status_res = client.get("/evaluation_results/99999/status")
    assert status_res.status_code == 404  # Match HTTPException in evaluation_results.py
    
    # Qualitative evaluation registration with non-existent result_id (add text field)
    qualitative_req = {
        "evaluationId": evaluation.id,
        "results": [
            {
                "questionId": 1, 
                "answer": "implemented",
                "text": "テスト質問",
                "perspective": "有害情報の出力制御"
            }
        ]
    }
    qual_res = client.post("/evaluation_results/99999/qualitative_result", json=qualitative_req)
    assert qual_res.status_code == 404  # Match HTTPException in evaluation_results.py
    
    # 10 perspective score retrieval with non-existent result_id
    scores_res = client.get("/evaluation_results/99999/10perspective_scores")
    assert scores_res.status_code == 404  # Match HTTPException in evaluation_results.py
