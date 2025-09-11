import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from src.main import app
from src.db.define_tables import AIModel
from src.manager.scoring_dataset_manager import ScoringDatasetManager

client = TestClient(app)

class TestScoringDatasetRouter:
    
    @pytest.fixture
    def sample_request_data(self):
        """Test request data"""
        return {
            "question": "こんにちは、世界！",
            "expected_answer": "Hello, World!",
            "model_id": 1
        }
    
    @pytest.fixture
    def sample_ai_model(self, session):
        """Test AI model"""
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

    @patch.object(ScoringDatasetManager, 'scoring_results')
    def test_scoring_dataset_success(self, mock_scoring_results, sample_request_data):
        """Test normal scoring process"""
        # Arrange
        expected_response = {
            "results": [
                {"paraphrase": "こんにちは世界", "is_correct": True},
                {"paraphrase": "世界こんにちは", "is_correct": False},
                {"paraphrase": "ハロー世界", "is_correct": True}
            ],
            "total_correct": 2
        }
        mock_scoring_results.return_value = expected_response
        
        # Act
        response = client.post("/scoring-dataset", json=sample_request_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json() == expected_response
        
        # Verify that manager was called with correct arguments
        mock_scoring_results.assert_called_once()
        call_args = mock_scoring_results.call_args
        assert call_args[0][1].question == sample_request_data["question"]
        assert call_args[0][1].expected_answer == sample_request_data["expected_answer"]
        assert call_args[0][1].model_id == sample_request_data["model_id"]
        assert call_args[0][2] == sample_request_data["model_id"]

    @patch.object(ScoringDatasetManager, 'scoring_results')
    def test_scoring_dataset_with_empty_question(self, mock_scoring_results):
        """Test scoring process with empty question"""
        # Arrange
        request_data = {
            "question": "",
            "expected_answer": "Hello, World!",
            "model_id": 1
        }
        mock_scoring_results.return_value = {
            "results": [],
            "total_correct": 0
        }
        
        # Act
        response = client.post("/scoring-dataset", json=request_data)
        
        # Assert
        assert response.status_code == 200
        mock_scoring_results.assert_called_once()

    @patch.object(ScoringDatasetManager, 'scoring_results')
    def test_scoring_dataset_with_empty_expected_answer(self, mock_scoring_results):
        """Test scoring process with empty expected answer"""
        # Arrange
        request_data = {
            "question": "こんにちは、世界！",
            "expected_answer": "",
            "model_id": 1
        }
        mock_scoring_results.return_value = {
            "results": [],
            "total_correct": 0
        }
        
        # Act
        response = client.post("/scoring-dataset", json=request_data)
        
        # Assert
        assert response.status_code == 200
        mock_scoring_results.assert_called_once()

    @patch.object(ScoringDatasetManager, 'scoring_results')
    def test_scoring_dataset_manager_exception(self, mock_scoring_results):
        """Test when exception occurs in manager"""
        # Arrange
        request_data = {
            "question": "こんにちは、世界！",
            "expected_answer": "Hello, World!",
            "model_id": 999  # Non-existent model_id
        }
        mock_scoring_results.side_effect = ValueError("Model not found")
        
        # Act & Assert
        with pytest.raises(ValueError):
            response = client.post("/scoring-dataset", json=request_data)

    def test_scoring_dataset_invalid_request_format(self):
        """Test invalid request format"""
        # Arrange
        invalid_data = {
            "question": "こんにちは、世界！",
            # expected_answer is missing
            "model_id": 1
        }
        
        # Act
        response = client.post("/scoring-dataset", json=invalid_data)
        
        # Assert
        assert response.status_code == 422  # Validation Error

    def test_scoring_dataset_invalid_model_id_type(self):
        """Test invalid model_id type"""
        # Arrange
        invalid_data = {
            "question": "こんにちは、世界！",
            "expected_answer": "Hello, World!",
            "model_id": "invalid_id"  # String is invalid
        }
        
        # Act
        response = client.post("/scoring-dataset", json=invalid_data)
        
        # Assert
        assert response.status_code == 422  # Validation Error

    def test_scoring_dataset_missing_fields(self):
        """Test when required fields are missing"""
        # Arrange
        incomplete_data = {
            "question": "こんにちは、世界！"
            # expected_answer and model_id are missing
        }
        
        # Act
        response = client.post("/scoring-dataset", json=incomplete_data)
        
        # Assert
        assert response.status_code == 422  # Validation Error

    @patch.object(ScoringDatasetManager, 'scoring_results')
    def test_scoring_dataset_with_unicode_characters(self, mock_scoring_results):
        """Test scoring process with Unicode characters in question"""
        # Arrange
        request_data = {
            "question": "こんにちは、世界！🌍",
            "expected_answer": "Hello, World! 🌎",
            "model_id": 1
        }
        expected_response = {
            "results": [
                {"paraphrase": "こんにちは世界🌍", "is_correct": True}
            ],
            "total_correct": 1
        }
        mock_scoring_results.return_value = expected_response
        
        # Act
        response = client.post("/scoring-dataset", json=request_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json() == expected_response

    @patch.object(ScoringDatasetManager, 'scoring_results')
    def test_scoring_dataset_with_long_text(self, mock_scoring_results):
        """Test scoring process with long text"""
        # Arrange
        long_question = "これは非常に長い質問文です。" * 100
        long_answer = "これは非常に長い回答文です。" * 100
        request_data = {
            "question": long_question,
            "expected_answer": long_answer,
            "model_id": 1
        }
        expected_response = {
            "results": [
                {"paraphrase": "長い質問の言い換え", "is_correct": False}
            ],
            "total_correct": 0
        }
        mock_scoring_results.return_value = expected_response
        
        # Act
        response = client.post("/scoring-dataset", json=request_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json() == expected_response

    @patch.object(ScoringDatasetManager, 'scoring_results')
    def test_scoring_dataset_with_special_characters(self, mock_scoring_results):
        """Test scoring process with special characters in question"""
        # Arrange
        request_data = {
            "question": "質問: 2+2=? & 3*3=?",
            "expected_answer": "答え: 4 & 9",
            "model_id": 1
        }
        expected_response = {
            "results": [
                {"paraphrase": "2足す2は？かつ3掛ける3は？", "is_correct": True}
            ],
            "total_correct": 1
        }
        mock_scoring_results.return_value = expected_response
        
        # Act
        response = client.post("/scoring-dataset", json=request_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json() == expected_response

    def test_scoring_dataset_content_type_validation(self):
        """Test Content-Type validation"""
        # Arrange
        request_data = {
            "question": "こんにちは、世界！",
            "expected_answer": "Hello, World!",
            "model_id": 1
        }
        
        # Act - Send as string instead of JSON
        response = client.post(
            "/scoring-dataset",
            data=json.dumps(request_data),
            headers={"Content-Type": "text/plain"}
        )
        
        # Assert
        assert response.status_code == 422  # Validation Error

    @patch.object(ScoringDatasetManager, 'scoring_results')
    def test_scoring_dataset_zero_model_id(self, mock_scoring_results):
        """Test when model_id is 0"""
        # Arrange
        request_data = {
            "question": "こんにちは、世界！",
            "expected_answer": "Hello, World!",
            "model_id": 0
        }
        expected_response = {
            "results": [],
            "total_correct": 0
        }
        mock_scoring_results.return_value = expected_response
        
        # Act
        response = client.post("/scoring-dataset", json=request_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json() == expected_response

    @patch.object(ScoringDatasetManager, 'scoring_results')
    def test_scoring_dataset_negative_model_id(self, mock_scoring_results):
        """Test with negative model_id"""
        # Arrange
        request_data = {
            "question": "こんにちは、世界！",
            "expected_answer": "Hello, World!",
            "model_id": -1
        }
        expected_response = {
            "results": [],
            "total_correct": 0
        }
        mock_scoring_results.return_value = expected_response
        
        # Act
        response = client.post("/scoring-dataset", json=request_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json() == expected_response

    @patch.object(ScoringDatasetManager, 'scoring_results')
    def test_scoring_dataset_large_model_id(self, mock_scoring_results):
        """Test with very large model_id"""
        # Arrange
        request_data = {
            "question": "こんにちは、世界！",
            "expected_answer": "Hello, World!",
            "model_id": 999999999
        }
        mock_scoring_results.side_effect = ValueError("Model not found")
        
        # Act & Assert
        with pytest.raises(ValueError):
            response = client.post("/scoring-dataset", json=request_data)

    @patch.object(ScoringDatasetManager, 'scoring_results')
    def test_scoring_dataset_empty_results(self, mock_scoring_results):
        """Test when empty results are returned"""
        # Arrange
        request_data = {
            "question": "こんにちは、世界！",
            "expected_answer": "Hello, World!",
            "model_id": 1
        }
        expected_response = {
            "results": [],
            "total_correct": 0
        }
        mock_scoring_results.return_value = expected_response
        
        # Act
        response = client.post("/scoring-dataset", json=request_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json() == expected_response
        assert response.json()["results"] == []
        assert response.json()["total_correct"] == 0