import pytest
import json
from unittest.mock import patch, Mock, MagicMock
from src.manager.scoring_dataset_manager import ScoringDatasetManager
from src.db.define_tables import AIModel
from datetime import date


class MockRequest:
    """Mock request object for testing"""
    def __init__(self, question: str, expected_answer: str, model_id: int):
        self.question = question
        self.expected_answer = expected_answer
        self.model_id = model_id


@pytest.fixture
def sample_ai_model(session):
    """AI model for testing"""
    ai_model = AIModel(
        name="テストモデル",
        model_name="gpt-4o-mini",
        url="http://test-model",
        api_key="test-key",
        api_request_format={},
        type="target"
    )
    session.add(ai_model)
    session.commit()
    return ai_model


@pytest.fixture
def sample_request():
    """Request data for testing"""
    return MockRequest(
        question="こんにちは、世界！",
        expected_answer="Hello, World!",
        model_id=1
    )


@pytest.fixture
def mock_eval_results():
    """Evaluation results for testing (JSON string list)"""
    return [
        json.dumps({
            "samples": [{
                "input": "こんにちは世界",
                "scores": {
                    "model_graded_qa": {"value": "C"}
                }
            }]
        }),
        json.dumps({
            "samples": [{
                "input": "世界こんにちは",
                "scores": {
                    "model_graded_qa": {"value": "I"}
                }
            }]
        }),
        json.dumps({
            "samples": [{
                "input": "ハロー世界",
                "scores": {
                    "model_graded_qa": {"value": "C"}
                }
            }]
        })
    ]


class TestScoringDatasetManager:
    
    @patch('src.inspect.scoring_datasets.paraphrase_and_score')  # Fixed to correct path
    def test_scoring_results_success(self, mock_paraphrase, session, sample_ai_model, sample_request, mock_eval_results):
        """Test for successful scoring process"""
        # Arrange
        mock_paraphrase.return_value = mock_eval_results
        
        # Act
        result = ScoringDatasetManager.scoring_results(session, sample_request, sample_ai_model.id)
        
        # Assert
        assert isinstance(result, dict)
        assert "results" in result
        assert "total_correct" in result
        
        # Verify result details
        assert len(result["results"]) == 3
        assert result["total_correct"] == 2  # "C"が2個
        
        # Check structure of each result
        for paraphrase_result in result["results"]:
            assert "paraphrase" in paraphrase_result
            assert "is_correct" in paraphrase_result
        
        # Check specific results
        assert result["results"][0]["paraphrase"] == "こんにちは世界"
        assert result["results"][0]["is_correct"] == "C"
        assert result["results"][1]["paraphrase"] == "世界こんにちは"
        assert result["results"][1]["is_correct"] == "I"
        assert result["results"][2]["paraphrase"] == "ハロー世界"
        assert result["results"][2]["is_correct"] == "C"
        
        # Verify that paraphrase_and_score was called with correct arguments
        mock_paraphrase.assert_called_once()
        call_args = mock_paraphrase.call_args
        assert call_args[0][0] == sample_request.question
        assert call_args[0][1] == sample_request.expected_answer
        assert call_args[0][2] == sample_ai_model  # modelオブジェクト

    def test_scoring_results_model_not_found(self, session, sample_request):
        """Error test for non-existent model ID"""
        # Arrange
        non_existent_model_id = 99999
        
        # Act & Assert
        with pytest.raises(ValueError, match="AIModel not found"):
            ScoringDatasetManager.scoring_results(session, sample_request, non_existent_model_id)

    @patch('src.inspect.scoring_datasets.paraphrase_and_score')  # Fixed to correct path
    def test_scoring_results_empty_results(self, mock_paraphrase, session, sample_ai_model, sample_request):
        """Test for empty evaluation results"""
        # Arrange
        mock_paraphrase.return_value = []
        
        # Act
        result = ScoringDatasetManager.scoring_results(session, sample_request, sample_ai_model.id)
        
        # Assert
        assert result["results"] == []
        assert result["total_correct"] == 0

    @patch('src.inspect.scoring_datasets.paraphrase_and_score')  # Fixed to correct path
    def test_scoring_results_all_incorrect(self, mock_paraphrase, session, sample_ai_model, sample_request):
        """Test for all incorrect answers"""
        # Arrange
        mock_eval_results = [
            json.dumps({
                "samples": [{
                    "input": "テスト1",
                    "scores": {
                        "model_graded_qa": {"value": "I"}
                    }
                }]
            }),
            json.dumps({
                "samples": [{
                    "input": "テスト2",
                    "scores": {
                        "model_graded_qa": {"value": "I"}
                    }
                }]
            })
        ]
        mock_paraphrase.return_value = mock_eval_results
        
        # Act
        result = ScoringDatasetManager.scoring_results(session, sample_request, sample_ai_model.id)
        
        # Assert
        assert len(result["results"]) == 2
        assert result["total_correct"] == 0
        for paraphrase_result in result["results"]:
            assert paraphrase_result["is_correct"] == "I"

    @patch('src.inspect.scoring_datasets.paraphrase_and_score')  # Fixed to correct path
    def test_scoring_results_all_correct(self, mock_paraphrase, session, sample_ai_model, sample_request):
        """Test for all correct answers"""
        # Arrange
        mock_eval_results = [
            json.dumps({
                "samples": [{
                    "input": "正解1",
                    "scores": {
                        "model_graded_qa": {"value": "C"}
                    }
                }]
            }),
            json.dumps({
                "samples": [{
                    "input": "正解2",
                    "scores": {
                        "model_graded_qa": {"value": "C"}
                    }
                }]
            })
        ]
        mock_paraphrase.return_value = mock_eval_results
        
        # Act
        result = ScoringDatasetManager.scoring_results(session, sample_request, sample_ai_model.id)
        
        # Assert
        assert len(result["results"]) == 2
        assert result["total_correct"] == 2
        for paraphrase_result in result["results"]:
            assert paraphrase_result["is_correct"] == "C"

    @patch('src.inspect.scoring_datasets.paraphrase_and_score')  # Fixed to correct path
    def test_scoring_results_invalid_json(self, mock_paraphrase, session, sample_ai_model, sample_request):
        """Test for invalid JSON format results"""
        # Arrange
        mock_paraphrase.return_value = ["invalid json", "not json either"]
        
        # Act & Assert
        with pytest.raises(json.JSONDecodeError):
            ScoringDatasetManager.scoring_results(session, sample_request, sample_ai_model.id)

    @patch('src.inspect.scoring_datasets.paraphrase_and_score')  # Fixed to correct path
    def test_scoring_results_malformed_result_structure(self, mock_paraphrase, session, sample_ai_model, sample_request):
        """Test for malformed result structure"""
        # Arrange
        mock_eval_results = [
            json.dumps({
                "samples": [{
                    # input is missing
                    "scores": {
                        "model_graded_qa": {"value": "C"}
                    }
                }]
            })
        ]
        mock_paraphrase.return_value = mock_eval_results
        
        # Act & Assert
        with pytest.raises(KeyError):
            ScoringDatasetManager.scoring_results(session, sample_request, sample_ai_model.id)

    @patch('src.inspect.scoring_datasets.paraphrase_and_score')  # Fixed to correct path
    def test_scoring_results_missing_score(self, mock_paraphrase, session, sample_ai_model, sample_request):
        """Test for results with missing score"""
        # Arrange
        mock_eval_results = [
            json.dumps({
                "samples": [{
                    "input": "テスト",
                    "scores": {
                        # model_graded_qa is missing
                    }
                }]
            })
        ]
        mock_paraphrase.return_value = mock_eval_results
        
        # Act & Assert
        with pytest.raises(KeyError):
            ScoringDatasetManager.scoring_results(session, sample_request, sample_ai_model.id)

    @patch('src.inspect.scoring_datasets.paraphrase_and_score')  # Fixed to correct path
    def test_scoring_results_with_unicode_characters(self, mock_paraphrase, session, sample_ai_model):
        """Test for questions with Unicode characters"""
        # Arrange
        unicode_request = MockRequest(
            question="こんにちは、世界！🌍",
            expected_answer="Hello, World! 🌎",
            model_id=sample_ai_model.id
        )
        mock_eval_results = [
            json.dumps({
                "samples": [{
                    "input": "こんにちは世界🌍",
                    "scores": {
                        "model_graded_qa": {"value": "C"}
                    }
                }]
            })
        ]
        mock_paraphrase.return_value = mock_eval_results
        
        # Act
        result = ScoringDatasetManager.scoring_results(session, unicode_request, sample_ai_model.id)
        
        # Assert
        assert result["results"][0]["paraphrase"] == "こんにちは世界🌍"
        assert result["total_correct"] == 1

    @patch('src.inspect.scoring_datasets.paraphrase_and_score')  # Fixed to correct path
    def test_scoring_results_with_empty_question(self, mock_paraphrase, session, sample_ai_model):
        """Test for empty question"""
        # Arrange
        empty_request = MockRequest(
            question="",
            expected_answer="何かの回答",
            model_id=sample_ai_model.id
        )
        mock_paraphrase.return_value = []
        
        # Act
        result = ScoringDatasetManager.scoring_results(session, empty_request, sample_ai_model.id)
        
        # Assert
        assert result["results"] == []
        assert result["total_correct"] == 0

    @patch('src.inspect.scoring_datasets.paraphrase_and_score')  # Fixed to correct path
    def test_scoring_results_with_long_text(self, mock_paraphrase, session, sample_ai_model):
        """Test for long text"""
        # Arrange
        long_question = "これは非常に長い質問文です。" * 100
        long_answer = "これは非常に長い回答文です。" * 100
        long_request = MockRequest(
            question=long_question,
            expected_answer=long_answer,
            model_id=sample_ai_model.id
        )
        mock_eval_results = [
            json.dumps({
                "samples": [{
                    "input": "長い質問の言い換え",
                    "scores": {
                        "model_graded_qa": {"value": "I"}
                    }
                }]
            })
        ]
        mock_paraphrase.return_value = mock_eval_results
        
        # Act
        result = ScoringDatasetManager.scoring_results(session, long_request, sample_ai_model.id)
        
        # Assert
        assert len(result["results"]) == 1
        assert result["total_correct"] == 0

    @patch('src.inspect.scoring_datasets.paraphrase_and_score')  # Fixed to correct path
    def test_scoring_results_paraphrase_and_score_called_with_correct_params(self, mock_paraphrase, session, sample_ai_model, sample_request):
        """Test that paraphrase_and_score is called with correct parameters"""
        # Arrange
        mock_paraphrase.return_value = []
        
        # Act
        ScoringDatasetManager.scoring_results(session, sample_request, sample_ai_model.id)
        
        # Assert
        mock_paraphrase.assert_called_once()
        call_args = mock_paraphrase.call_args
        
        # Verify order and content of arguments
        assert call_args[0][0] == sample_request.question  # question
        assert call_args[0][1] == sample_request.expected_answer  # expected_answer
        assert call_args[0][2] == sample_ai_model  # model object
        
        # Verify keyword arguments
        # May need adjustment based on paraphrase_and_score implementation
        assert len(call_args[0]) >= 4  # scorer引数も含まれる
        assert call_args[1].get('n_paraphrases', 10) == 10  # デフォルト値

    @patch('src.inspect.scoring_datasets.paraphrase_and_score')  # Fixed to correct path
    def test_scoring_results_handles_paraphrase_exception(self, mock_paraphrase, session, sample_ai_model, sample_request):
        """Test for when paraphrase_and_score throws an exception"""
        # Arrange
        mock_paraphrase.side_effect = Exception("API error")
        
        # Act & Assert
        with pytest.raises(Exception, match="API error"):
            ScoringDatasetManager.scoring_results(session, sample_request, sample_ai_model.id)

    def test_scoring_results_with_different_model_types(self, session, sample_request):
        """Test for different model types"""
        # Arrange
        eval_model = AIModel(
            name="評価モデル",
            model_name="gpt-4o",
            url="http://eval-model",
            api_key="eval-key",
            api_request_format={},
            type="eval"  # eval instead of target
        )
        session.add(eval_model)
        session.commit()
        
        # Act & Assert
        # This test behavior may vary depending on implementation
        # Current implementation doesn't seem to check model type
        with patch('src.inspect.scoring_datasets.paraphrase_and_score') as mock_paraphrase:  # Fixed to correct path
            mock_paraphrase.return_value = []
            result = ScoringDatasetManager.scoring_results(session, sample_request, eval_model.id)
            assert result["results"] == []
            assert result["total_correct"] == 0

    @patch('src.inspect.scoring_datasets.paraphrase_and_score')  # Fixed to correct path
    def test_scoring_results_multiple_samples_per_result(self, mock_paraphrase, session, sample_ai_model, sample_request):
        """Test for edge case where one result contains multiple samples"""
        # Arrange
        mock_eval_results = [
            json.dumps({
                "samples": [
                    {
                        "input": "第1サンプル",
                        "scores": {
                            "model_graded_qa": {"value": "C"}
                        }
                    },
                    {
                        "input": "第2サンプル",  # Usually only one, but in case of multiple
                        "scores": {
                            "model_graded_qa": {"value": "I"}
                        }
                    }
                ]
            })
        ]
        mock_paraphrase.return_value = mock_eval_results
        
        # Act
        result = ScoringDatasetManager.scoring_results(session, sample_request, sample_ai_model.id)
        
        # Assert
        # Current implementation uses only the first sample
        assert len(result["results"]) == 1
        assert result["results"][0]["paraphrase"] == "第1サンプル"
        assert result["results"][0]["is_correct"] == "C"
        assert result["total_correct"] == 1