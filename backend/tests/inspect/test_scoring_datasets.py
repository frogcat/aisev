import pytest
import json
import asyncio
from unittest.mock import patch, Mock, MagicMock, AsyncMock
from src.inspect.scoring_datasets import paraphrase_and_score, get_paraphrase, read_eval_log
from inspect_ai.scorer import model_graded_qa
from inspect_ai.model import GenerateConfig


class MockModel:
    """Test model object"""
    def __init__(self, model_name="gpt-4o-mini", url="https://api.openai.com/v1", api_key="test-key"):
        self.model_name = model_name
        self.url = url
        self.api_key = api_key


class MockResponse:
    """Test response object"""
    def __init__(self, content):
        self.choices = [Mock()]
        self.choices[0].message = Mock()
        self.choices[0].message.content = content


@pytest.fixture
def sample_model():
    """Test model"""
    return MockModel()


@pytest.fixture
def mock_paraphrase_response():
    """Test paraphrase generation response"""
    return "- こんにちは世界\n- 世界へのあいさつ\n- ハロー、ワールド"


@pytest.fixture
def mock_eval_results():
    """Test evaluation results (list of JSON strings)"""
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
                "input": "世界へのあいさつ",
                "scores": {
                    "model_graded_qa": {"value": "I"}
                }
            }]
        }),
        json.dumps({
            "samples": [{
                "input": "ハロー、ワールド",
                "scores": {
                    "model_graded_qa": {"value": "C"}
                }
            }]
        })
    ]


class TestGetParaphrase:
    
    @patch('src.inspect.scoring_datasets.get_model')
    @pytest.mark.asyncio
    async def test_get_paraphrase_success(self, mock_get_model):
        """Test for successful paraphrase generation"""
        # Arrange
        mock_model = Mock()
        mock_model.generate = AsyncMock(return_value=MockResponse("- テスト言い換え1\n- テスト言い換え2"))
        mock_get_model.return_value = mock_model
        
        # Act
        result = await get_paraphrase("テスト質問", "test-model", 2)
        
        # Assert
        assert "テスト言い換え1" in result
        assert "テスト言い換え2" in result
        mock_get_model.assert_called_once()
        mock_model.generate.assert_called_once()

    @patch('src.inspect.scoring_datasets.get_model')
    @pytest.mark.asyncio
    async def test_get_paraphrase_with_unicode(self, mock_get_model):
        """Test for paraphrase generation with Unicode characters"""
        # Arrange
        mock_model = Mock()
        mock_model.generate = AsyncMock(return_value=MockResponse("- こんにちは🌍\n- 世界へ👋"))
        mock_get_model.return_value = mock_model
        
        # Act
        result = await get_paraphrase("こんにちは、世界！🌍", "test-model", 2)
        
        # Assert
        assert "こんにちは🌍" in result
        assert "世界へ👋" in result

    @patch('src.inspect.scoring_datasets.get_model')
    @pytest.mark.asyncio
    async def test_get_paraphrase_empty_response(self, mock_get_model):
        """Test for empty response"""
        # Arrange
        mock_model = Mock()
        mock_model.generate = AsyncMock(return_value=MockResponse(""))
        mock_get_model.return_value = mock_model
        
        # Act
        result = await get_paraphrase("テスト質問", "test-model", 2)
        
        # Assert
        assert result == ""

    @patch('src.inspect.scoring_datasets.get_model')
    @pytest.mark.asyncio
    async def test_get_paraphrase_model_error(self, mock_get_model):
        """Test for model error"""
        # Arrange
        mock_model = Mock()
        mock_model.generate = AsyncMock(side_effect=Exception("API Error"))
        mock_get_model.return_value = mock_model
        
        # Act & Assert
        with pytest.raises(Exception, match="API Error"):
            await get_paraphrase("テスト質問", "test-model", 2)


class TestParaphraseAndScore:
    
    @patch('src.inspect.scoring_datasets.register_in_inspect_ai')
    @patch('src.inspect.scoring_datasets.eval')
    @patch('src.inspect.scoring_datasets.eval_log_json_str')
    @patch('src.inspect.scoring_datasets.get_paraphrase')
    def test_paraphrase_and_score_success(self, mock_get_paraphrase, mock_eval_log_json_str, 
                                        mock_eval, mock_register, sample_model, mock_eval_results):
        """Test for successful paraphrase and scoring"""
        # Arrange
        mock_register.return_value = "custom-model"
        mock_get_paraphrase.return_value = "- こんにちは世界\n- 世界へのあいさつ\n- ハロー、ワールド"
        mock_eval.return_value = [Mock()]
        mock_eval_log_json_str.side_effect = mock_eval_results
        
        # Act
        result = paraphrase_and_score(
            "こんにちは、世界！",
            "Hello, World!",
            sample_model,
            model_graded_qa(),
            n_paraphrases=3
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 3
        
        # Verify that register_in_inspect_ai was called with correct arguments
        mock_register.assert_called_once_with(
            model_name=sample_model.model_name,
            api_url=sample_model.url,
            api_key=sample_model.api_key
        )
        
        # Verify that eval was called the correct number of times
        assert mock_eval.call_count == 3

    @patch('src.inspect.scoring_datasets.register_in_inspect_ai')
    @patch('src.inspect.scoring_datasets.get_paraphrase')
    def test_paraphrase_and_score_empty_paraphrases(self, mock_get_paraphrase, mock_register, sample_model):
        """Test when no paraphrases are generated"""
        # Arrange
        mock_register.return_value = "custom-model"
        # Mock to return empty result or empty string
        mock_get_paraphrase.return_value = ""
        
        # Act
        result = paraphrase_and_score(
            "テスト質問",
            "テスト回答",
            sample_model,
            model_graded_qa(),
            n_paraphrases=3
        )
        
        # Assert
        assert isinstance(result, list)
        # When no paraphrases are generated, an empty list is returned
        assert len(result) == 0

    @patch('src.inspect.scoring_datasets.register_in_inspect_ai')
    @patch('src.inspect.scoring_datasets.get_paraphrase')
    def test_paraphrase_and_score_only_empty_lines(self, mock_get_paraphrase, mock_register, sample_model):
        """Test when only empty lines are returned"""
        # Arrange
        mock_register.return_value = "custom-model"
        # Mock to return results containing only empty lines or newlines
        mock_get_paraphrase.return_value = "- \n- \n- "
        
        # Act
        result = paraphrase_and_score(
            "テスト質問",
            "テスト回答",
            sample_model,
            model_graded_qa(),
            n_paraphrases=3
        )
        
        # Assert
        assert isinstance(result, list)
        # When there are no valid paraphrases, an empty list is returned
        assert len(result) == 0

    @patch('src.inspect.scoring_datasets.register_in_inspect_ai')
    @patch('src.inspect.scoring_datasets.get_paraphrase')
    def test_paraphrase_and_score_single_empty_paraphrase(self, mock_get_paraphrase, mock_register, sample_model):
        """Test when a single empty paraphrase is returned"""
        # Arrange
        mock_register.return_value = "custom-model"
        # Mock to return a single empty paraphrase
        mock_get_paraphrase.return_value = "- "
        
        # Act
        result = paraphrase_and_score(
            "テスト質問",
            "テスト回答",
            sample_model,
            model_graded_qa(),
            n_paraphrases=3
        )
        
        # Assert
        assert isinstance(result, list)
        # When there are no valid paraphrases, an empty list is returned
        assert len(result) == 0

    @patch('src.inspect.scoring_datasets.register_in_inspect_ai')
    @patch('src.inspect.scoring_datasets.get_paraphrase')
    def test_paraphrase_and_score_mixed_empty_and_valid(self, mock_get_paraphrase, mock_register, sample_model):
        """Test when empty and valid paraphrases are mixed"""
        # Arrange
        mock_register.return_value = "custom-model"
        
        # Mock to return different results on multiple calls
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return "- \n- \n- "  # Empty paraphrases
            elif call_count == 2:
                return "- 有効な言い換え1\n- 有効な言い換え2\n- 有効な言い換え3"
            else:
                return "- 追加の言い換え"
        
        mock_get_paraphrase.side_effect = side_effect
        
        with patch('src.inspect.scoring_datasets.eval') as mock_eval, \
             patch('src.inspect.scoring_datasets.eval_log_json_str') as mock_eval_log_json_str:
            
            mock_eval.return_value = [Mock()]
            mock_eval_log_json_str.return_value = json.dumps({
                "samples": [{"input": "test", "scores": {"model_graded_qa": {"value": "C"}}}]
            })
            
            # Act
            result = paraphrase_and_score(
                "テスト質問",
                "テスト回答",
                sample_model,
                model_graded_qa(),
                n_paraphrases=3
            )
            
            # Assert
            assert isinstance(result, list)
            # When valid paraphrases are generated, results are included
            assert len(result) == 3

    @patch('src.inspect.scoring_datasets.register_in_inspect_ai')
    @patch('src.inspect.scoring_datasets.get_paraphrase')
    def test_paraphrase_and_score_max_trials(self, mock_get_paraphrase, mock_register, sample_model):
        """Test when maximum trial count is reached"""
        # Arrange
        mock_register.return_value = "custom-model"
        # Set mock data in a format that is judged as valid according to the implementation's string processing logic
        mock_get_paraphrase.return_value = "同じ言い換え- もう一つの言い換え"
        
        with patch('src.inspect.scoring_datasets.eval') as mock_eval, \
             patch('src.inspect.scoring_datasets.eval_log_json_str') as mock_eval_log_json_str:
            
            mock_eval.return_value = [Mock()]
            mock_eval_log_json_str.return_value = json.dumps({
                "samples": [{"input": "同じ言い換え", "scores": {"model_graded_qa": {"value": "C"}}}]
            })
            
            # Act
            result = paraphrase_and_score(
                "テスト質問",
                "テスト回答",
                sample_model,
                model_graded_qa(),
                n_paraphrases=10  # Increase requested count
            )
            
            # Assert
            assert isinstance(result, list)
            # Valid paraphrases are generated through the implementation's string processing
            assert len(result) >= 1

    @patch('src.inspect.scoring_datasets.register_in_inspect_ai')
    @patch('src.inspect.scoring_datasets.get_paraphrase')
    def test_paraphrase_and_score_max_trials_with_valid_paraphrase(self, mock_get_paraphrase, mock_register, sample_model):
        """Test when maximum trial count is reached (with valid paraphrases)"""
        # Arrange
        mock_register.return_value = "custom-model"
        # Set mock data in a format that is judged as valid according to the implementation's string processing logic
        mock_get_paraphrase.return_value = "有効な言い換え- 追加の言い換え"
        
        with patch('src.inspect.scoring_datasets.eval') as mock_eval, \
             patch('src.inspect.scoring_datasets.eval_log_json_str') as mock_eval_log_json_str:
            
            mock_eval.return_value = [Mock()]
            mock_eval_log_json_str.return_value = json.dumps({
                "samples": [{"input": "有効な言い換え", "scores": {"model_graded_qa": {"value": "C"}}}]
            })
            
            # Act
            result = paraphrase_and_score(
                "テスト質問",
                "テスト回答",
                sample_model,
                model_graded_qa(),
                n_paraphrases=3  # Set to smaller number
            )
            
            # Assert
            assert isinstance(result, list)
            # Valid paraphrases are generated
            assert len(result) >= 1

    @patch('src.inspect.scoring_datasets.register_in_inspect_ai')
    @patch('src.inspect.scoring_datasets.get_paraphrase')
    def test_paraphrase_and_score_insufficient_paraphrases(self, mock_get_paraphrase, mock_register, sample_model):
        """Test when fewer paraphrases than requested can be generated"""
        # Arrange
        mock_register.return_value = "custom-model"
        # Generate only 2 paraphrases according to the implementation's string processing logic
        mock_get_paraphrase.return_value = "言い換え1- 言い換え2"
        
        with patch('src.inspect.scoring_datasets.eval') as mock_eval, \
             patch('src.inspect.scoring_datasets.eval_log_json_str') as mock_eval_log_json_str:
            
            mock_eval.return_value = [Mock()]
            mock_eval_log_json_str.return_value = json.dumps({
                "samples": [{"input": "test", "scores": {"model_graded_qa": {"value": "C"}}}]
            })
            
            # Act
            result = paraphrase_and_score(
                "テスト質問",
                "テスト回答",
                sample_model,
                model_graded_qa(),
                n_paraphrases=5  # Request 5 but only 2 are generated
            )
            
            # Assert
            assert isinstance(result, list)
            # Only the generated amount is returned
            assert len(result) == 2

    @patch('src.inspect.scoring_datasets.register_in_inspect_ai')
    @patch('src.inspect.scoring_datasets.get_paraphrase')
    def test_paraphrase_and_score_gradually_successful(self, mock_get_paraphrase, mock_register, sample_model):
        """Test when paraphrases are gradually generated"""
        # Arrange
        mock_register.return_value = "custom-model"
        
        # Gradually generate paraphrases with multiple calls
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 50:  # First 50 times are empty
                return ""
            elif call_count <= 70:  # Next 20 times generate one each
                return f"言い換え{call_count - 50}- 追加言い換え{call_count - 50}"
            else:  # Remaining generate multiple
                return "追加言い換え1- 追加言い換え2- 追加言い換え3"
        
        mock_get_paraphrase.side_effect = side_effect
        
        with patch('src.inspect.scoring_datasets.eval') as mock_eval, \
             patch('src.inspect.scoring_datasets.eval_log_json_str') as mock_eval_log_json_str:
            
            mock_eval.return_value = [Mock()]
            mock_eval_log_json_str.return_value = json.dumps({
                "samples": [{"input": "test", "scores": {"model_graded_qa": {"value": "C"}}}]
            })
            
            # Act
            result = paraphrase_and_score(
                "テスト質問",
                "テスト回答",
                sample_model,
                model_graded_qa(),
                n_paraphrases=5  # Request 5
            )
            
            # Assert
            assert isinstance(result, list)
            # Eventually 5 paraphrases are generated
            assert len(result) == 5

    @patch('src.inspect.scoring_datasets.register_in_inspect_ai')
    @patch('src.inspect.scoring_datasets.get_paraphrase')
    def test_paraphrase_and_score_with_duplicates(self, mock_get_paraphrase, mock_register, sample_model):
        """Test when there are duplicate paraphrases"""
        # Arrange
        mock_register.return_value = "custom-model"
        # Generate paraphrases with duplicates (duplicates are removed by list(set()) in implementation)
        mock_get_paraphrase.return_value = "同じ言い換え- 異なる言い換え- 同じ言い換え"
        
        with patch('src.inspect.scoring_datasets.eval') as mock_eval, \
             patch('src.inspect.scoring_datasets.eval_log_json_str') as mock_eval_log_json_str:
            
            mock_eval.return_value = [Mock()]
            mock_eval_log_json_str.return_value = json.dumps({
                "samples": [{"input": "test", "scores": {"model_graded_qa": {"value": "C"}}}]
            })
            
            # Act
            result = paraphrase_and_score(
                "テスト質問",
                "テスト回答",
                sample_model,
                model_graded_qa(),
                n_paraphrases=3
            )
            
            # Assert
            assert isinstance(result, list)
            # The actual result count decreases due to duplicate removal
            assert len(result) == 2  # After duplicate removal: Same paraphrase, Different paraphrases

    @patch('src.inspect.scoring_datasets.register_in_inspect_ai')
    @patch('src.inspect.scoring_datasets.get_paraphrase')
    @patch('src.inspect.scoring_datasets.eval')
    def test_paraphrase_and_score_eval_error(self, mock_eval, mock_get_paraphrase, mock_register, sample_model):
        """Test when an error occurs during evaluation processing"""
        # Arrange
        mock_register.return_value = "custom-model"
        # Set mock data in a format that is judged as valid according to the implementation's string processing logic
        mock_get_paraphrase.return_value = "有効なテスト言い換え- もう一つの言い換え"
        mock_eval.side_effect = Exception("Evaluation Error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Evaluation Error"):
            paraphrase_and_score(
                "テスト質問",
                "テスト回答",
                sample_model,
                model_graded_qa(),
                n_paraphrases=1
            )

    @patch('src.inspect.scoring_datasets.register_in_inspect_ai')
    @patch('src.inspect.scoring_datasets.get_paraphrase')
    def test_paraphrase_and_score_eval_error_no_valid_paraphrases(self, mock_get_paraphrase, mock_register, sample_model):
        """Test when no valid paraphrases are generated and eval processing is not reached"""
        # Arrange
        mock_register.return_value = "custom-model"
        # Return only invalid paraphrases (eval is not called)
        mock_get_paraphrase.return_value = "- テスト言い換え"  # Judged as invalid in implementation
        
        # Act
        result = paraphrase_and_score(
            "テスト質問",
            "テスト回答",
            sample_model,
            model_graded_qa(),
            n_paraphrases=1
        )
        
        # Assert
        # Since no valid paraphrases are generated, an empty list is returned
        assert isinstance(result, list)
        assert len(result) == 0

    @patch('src.inspect.scoring_datasets.register_in_inspect_ai')
    @patch('src.inspect.scoring_datasets.eval')
    @patch('src.inspect.scoring_datasets.eval_log_json_str')
    @patch('src.inspect.scoring_datasets.get_paraphrase')
    def test_full_workflow(self, mock_get_paraphrase, mock_eval_log_json_str, 
                          mock_eval, mock_register, sample_model):
        """Complete workflow integration test"""
        # Arrange
        mock_register.return_value = "custom-model"
        mock_get_paraphrase.return_value = "- テスト言い換え1\n- テスト言い換え2"
        mock_eval.return_value = [Mock()]
        mock_eval_log_json_str.side_effect = [
            json.dumps({
                "samples": [{
                    "input": "テスト言い換え1",
                    "scores": {"model_graded_qa": {"value": "C"}}
                }]
            }),
            json.dumps({
                "samples": [{
                    "input": "テスト言い換え2",
                    "scores": {"model_graded_qa": {"value": "I"}}
                }]
            })
        ]
        
        # Act
        paraphrase_results = paraphrase_and_score(
            "テスト質問",
            "テスト回答",
            sample_model,
            model_graded_qa(),
            n_paraphrases=2
        )
        
        final_results = read_eval_log(paraphrase_results)
        
        # Assert
        assert len(final_results["results"]) == 2
        assert final_results["total_correct"] == 1
        assert final_results["results"][0]["paraphrase"] == "テスト言い換え1"
        assert final_results["results"][0]["is_correct"] == "C"
        assert final_results["results"][1]["paraphrase"] == "テスト言い換え2"
        assert final_results["results"][1]["is_correct"] == "I"

    @patch('src.inspect.scoring_datasets.register_in_inspect_ai')
    @patch('src.inspect.scoring_datasets.get_paraphrase')
    def test_error_handling_in_workflow(self, mock_get_paraphrase, mock_register, sample_model):
        """Test for error handling during workflow"""
        # Arrange
        mock_register.return_value = "custom-model"
        mock_get_paraphrase.side_effect = Exception("Paraphrase generation failed")
        
        # Act & Assert
        with pytest.raises(Exception, match="Paraphrase generation failed"):
            paraphrase_and_score(
                "テスト質問",
                "テスト回答",
                sample_model,
                model_graded_qa(),
                n_paraphrases=1
            )


class TestReadEvalLog:
    
    def test_read_eval_log_success(self, mock_eval_results):
        """Test for successful log reading"""
        # Act
        result = read_eval_log(mock_eval_results)
        
        # Assert
        assert isinstance(result, dict)
        assert "results" in result
        assert "total_correct" in result
        
        assert len(result["results"]) == 3
        assert result["total_correct"] == 2  # Two “C ”s
        
        # Verify the structure of each result
        for paraphrase_result in result["results"]:
            assert "paraphrase" in paraphrase_result
            assert "is_correct" in paraphrase_result
        
        # Verify specific results
        assert result["results"][0]["paraphrase"] == "こんにちは世界"
        assert result["results"][0]["is_correct"] == "C"
        assert result["results"][1]["paraphrase"] == "世界へのあいさつ"
        assert result["results"][1]["is_correct"] == "I"
        assert result["results"][2]["paraphrase"] == "ハロー、ワールド"
        assert result["results"][2]["is_correct"] == "C"

    def test_read_eval_log_empty_list(self):
        """Test for empty list"""
        # Act
        result = read_eval_log([])
        
        # Assert
        assert result["results"] == []
        assert result["total_correct"] == 0

    def test_read_eval_log_all_correct(self):
        """Test for all correct cases"""
        # Arrange
        mock_results = [
            json.dumps({
                "samples": [{
                    "input": "正解1",
                    "scores": {"model_graded_qa": {"value": "C"}}
                }]
            }),
            json.dumps({
                "samples": [{
                    "input": "正解2",
                    "scores": {"model_graded_qa": {"value": "C"}}
                }]
            })
        ]
        
        # Act
        result = read_eval_log(mock_results)
        
        # Assert
        assert len(result["results"]) == 2
        assert result["total_correct"] == 2
        for paraphrase_result in result["results"]:
            assert paraphrase_result["is_correct"] == "C"

    def test_read_eval_log_all_incorrect(self):
        """Test for all incorrect cases"""
        # Arrange
        mock_results = [
            json.dumps({
                "samples": [{
                    "input": "不正解1",
                    "scores": {"model_graded_qa": {"value": "I"}}
                }]
            }),
            json.dumps({
                "samples": [{
                    "input": "不正解2",
                    "scores": {"model_graded_qa": {"value": "I"}}
                }]
            })
        ]
        
        # Act
        result = read_eval_log(mock_results)
        
        # Assert
        assert len(result["results"]) == 2
        assert result["total_correct"] == 0
        for paraphrase_result in result["results"]:
            assert paraphrase_result["is_correct"] == "I"

    def test_read_eval_log_invalid_json(self):
        """Test for invalid JSON"""
        # Arrange
        invalid_json_results = ["invalid json", "not json either"]
        
        # Act & Assert
        with pytest.raises(json.JSONDecodeError):
            read_eval_log(invalid_json_results)

    def test_read_eval_log_missing_fields(self):
        """Test when required fields are missing"""
        # Arrange
        incomplete_results = [
            json.dumps({
                "samples": [{
                    # input is missing
                    "scores": {"model_graded_qa": {"value": "C"}}
                }]
            })
        ]
        
        # Act & Assert
        with pytest.raises(KeyError):
            read_eval_log(incomplete_results)

    def test_read_eval_log_missing_scores(self):
        """Test when scores are missing"""
        # Arrange
        incomplete_results = [
            json.dumps({
                "samples": [{
                    "input": "テスト",
                    "scores": {
                        # model_graded_qa is missing
                    }
                }]
            })
        ]
        
        # Act & Assert
        with pytest.raises(KeyError):
            read_eval_log(incomplete_results)

    def test_read_eval_log_with_unicode(self):
        """Test for results containing Unicode characters"""
        # Arrange
        unicode_results = [
            json.dumps({
                "samples": [{
                    "input": "こんにちは世界🌍",
                    "scores": {"model_graded_qa": {"value": "C"}}
                }]
            }),
            json.dumps({
                "samples": [{
                    "input": "世界へ👋",
                    "scores": {"model_graded_qa": {"value": "I"}}
                }]
            })
        ]
        
        # Act
        result = read_eval_log(unicode_results)
        
        # Assert
        assert len(result["results"]) == 2
        assert result["total_correct"] == 1
        assert result["results"][0]["paraphrase"] == "こんにちは世界🌍"
        assert result["results"][1]["paraphrase"] == "世界へ👋"

    def test_read_eval_log_multiple_samples_per_result(self):
        """Test when one result contains multiple samples"""
        # Arrange
        multi_sample_results = [
            json.dumps({
                "samples": [
                    {
                        "input": "第1サンプル",
                        "scores": {"model_graded_qa": {"value": "C"}}
                    },
                    {
                        "input": "第2サンプル",  # Normally only one, but when there are multiple
                        "scores": {"model_graded_qa": {"value": "I"}}
                    }
                ]
            })
        ]
        
        # Act
        result = read_eval_log(multi_sample_results)
        
        # Assert
        # Current implementation uses only the first sample
        assert len(result["results"]) == 1
        assert result["results"][0]["paraphrase"] == "第1サンプル"
        assert result["results"][0]["is_correct"] == "C"
        assert result["total_correct"] == 1


class TestIntegration:
    
    @patch('src.inspect.scoring_datasets.register_in_inspect_ai')
    @patch('src.inspect.scoring_datasets.eval')
    @patch('src.inspect.scoring_datasets.eval_log_json_str')
    @patch('src.inspect.scoring_datasets.get_paraphrase')
    def test_full_workflow(self, mock_get_paraphrase, mock_eval_log_json_str, 
                          mock_eval, mock_register, sample_model):
        """Complete workflow integration test"""
        # Arrange
        mock_register.return_value = "custom-model"
        mock_get_paraphrase.return_value = "- テスト言い換え1\n- テスト言い換え2"
        mock_eval.return_value = [Mock()]
        mock_eval_log_json_str.side_effect = [
            json.dumps({
                "samples": [{
                    "input": "テスト言い換え1",
                    "scores": {"model_graded_qa": {"value": "C"}}
                }]
            }),
            json.dumps({
                "samples": [{
                    "input": "テスト言い換え2",
                    "scores": {"model_graded_qa": {"value": "I"}}
                }]
            })
        ]
        
        # Act
        paraphrase_results = paraphrase_and_score(
            "テスト質問",
            "テスト回答",
            sample_model,
            model_graded_qa(),
            n_paraphrases=2
        )
        
        final_results = read_eval_log(paraphrase_results)
        
        # Assert
        assert len(final_results["results"]) == 2
        assert final_results["total_correct"] == 1
        assert final_results["results"][0]["paraphrase"] == "テスト言い換え1"
        assert final_results["results"][0]["is_correct"] == "C"
        assert final_results["results"][1]["paraphrase"] == "テスト言い換え2"
        assert final_results["results"][1]["is_correct"] == "I"

    @patch('src.inspect.scoring_datasets.register_in_inspect_ai')
    @patch('src.inspect.scoring_datasets.get_paraphrase')
    def test_error_handling_in_workflow(self, mock_get_paraphrase, mock_register, sample_model):
        """Test for error handling during workflow"""
        # Arrange
        mock_register.return_value = "custom-model"
        mock_get_paraphrase.side_effect = Exception("Paraphrase generation failed")
        
        # Act & Assert
        with pytest.raises(Exception, match="Paraphrase generation failed"):
            paraphrase_and_score(
                "テスト質問",
                "テスト回答",
                sample_model,
                model_graded_qa(),
                n_paraphrases=1
            )