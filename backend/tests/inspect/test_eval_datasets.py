import pytest
import pandas as pd
from unittest.mock import Mock, patch
from inspect_ai.dataset import Sample
from inspect_ai.scorer import exact, model_graded_qa
from inspect_ai.log import EvalLog
from src.inspect.eval_datasets import new_eval_by_ten_perspective
from src.inspect.scorer_provider import ScorerProvider

class TestNewEvalByTenPerspective:
    
    @pytest.fixture
    def scorer_provider(self):
        return ScorerProvider()
    
    @pytest.fixture
    def sample_df_requirement(self):
        return pd.DataFrame({
            'ten_perspective': ['perspective1', 'perspective1', 'perspective2', 'perspective2'],
            'text': ['text1', 'text2', 'text3', 'text4'],
            'output': ['output1', 'output2', 'output3', 'output4'],
            'requirement': ['req1', 'req2', 'req3', 'req4']  # Add this column
        })
    
    @pytest.fixture
    def sample_df_multiple_choice(self):
        return pd.DataFrame({
            'ten_perspective': ['perspective1', 'perspective1', 'perspective2'],
            'text': ['question1', 'question2', 'question3'],
            'output': ['A', 'B', 'C'],
            'choices': [['choice1', 'choice2'], ['choice1', 'choice2'], ['choice1', 'choice2', 'choice3']]
        })
    
    @pytest.fixture
    def empty_df(self):
        return pd.DataFrame({
            'ten_perspective': [],
            'text': [],
            'output': [],
            'requirement': []  # Add this column
        })
    
    @pytest.fixture
    def df_with_nan_perspectives(self):
        return pd.DataFrame({
            'ten_perspective': ['perspective1', None, 'perspective2', None],
            'text': ['text1', 'text2', 'text3', 'text4'],
            'output': ['output1', 'output2', 'output3', 'output4'],
            'requirement': ['req1', 'req2', 'req3', 'req4']  # Add this column
        })
    
    @pytest.fixture
    def single_perspective_df(self):
        return pd.DataFrame({
            'ten_perspective': ['perspective1', 'perspective1'],
            'text': ['text1', 'text2'],
            'output': ['output1', 'output2'],
            'requirement': ['req1', 'req2']  # Add this column
        })
    
    def test_requirement_eval_type(self, sample_df_requirement, scorer_provider):
        # Arrange
        scorer = scorer_provider.get_requirement_scorer()
        # Act
        result = new_eval_by_ten_perspective(
            sample_df_requirement, 
            "mockllm/model", 
            scorer, 
            "requirement_eval"
        )
        
        # Assert
        assert len(result) == 2
        assert 'perspective1' in result
        assert 'perspective2' in result
    
    def test_graded_eval_type(self, sample_df_requirement, scorer_provider):
        # Arrange
        scorer = scorer_provider.get_requirement_scorer()
        
        # Act
        result = new_eval_by_ten_perspective(
            sample_df_requirement, 
            "mockllm/model", 
            scorer, 
            "graded_eval"
        )
        
        # Assert
        assert len(result) == 2
        assert 'perspective1' in result
        assert 'perspective2' in result
    
    def test_multiple_choice_eval_type(self, sample_df_multiple_choice, scorer_provider):
        # Arrange
        scorer = scorer_provider.get_multiple_choice_scorer()
        
        # Act
        result = new_eval_by_ten_perspective(
            sample_df_multiple_choice, 
            "mockllm/model", 
            scorer, 
            "multiple_choice_eval"
        )
        
        # Assert
        assert len(result) == 2
        assert 'perspective1' in result
        assert 'perspective2' in result
    
    def test_empty_dataframe(self, empty_df, scorer_provider):
        # Arrange
        scorer = scorer_provider.get_requirement_scorer()
        
        # Act
        result = new_eval_by_ten_perspective(
            empty_df, 
            "mockllm/model", 
            scorer, 
            "requirement_eval"
        )
        
        # Assert
        assert len(result) == 0
    
    def test_nan_perspectives_filtered(self, df_with_nan_perspectives, scorer_provider):
        # Arrange
        scorer = scorer_provider.get_requirement_scorer()
        
        # Act
        result = new_eval_by_ten_perspective(
            df_with_nan_perspectives, 
            "mockllm/model", 
            scorer, 
            "requirement_eval"
        )
        
        # Assert
        assert len(result) == 2  # Only perspective1 and perspective2, NaN filtered out
        assert 'perspective1' in result
        assert 'perspective2' in result
    
    def test_single_perspective(self, single_perspective_df, scorer_provider):
        # Arrange
        scorer = scorer_provider.get_requirement_scorer()
        
        # Act
        result = new_eval_by_ten_perspective(
            single_perspective_df, 
            "mockllm/model", 
            scorer, 
            "requirement_eval"
        )
        
        # Assert
        assert len(result) == 1
        assert 'perspective1' in result
    
    def test_unknown_eval_type_uses_default(self, sample_df_requirement, scorer_provider):
        # Arrange
        scorer = scorer_provider.get_exact_match_scorer()
        
        # Act
        result = new_eval_by_ten_perspective(
            sample_df_requirement, 
            "mockllm/model", 
            scorer, 
            "unknown_eval_type"
        )
        
        # Assert
        assert len(result) == 2
    
    @patch('src.inspect.eval_datasets.eval')
    def test_model_parameter_passed_correctly(self, mock_eval, sample_df_requirement, scorer_provider):
        # Arrange
        mock_eval.return_value = [Mock()]
        target_model = "specific_test_model"
        scorer = scorer_provider.get_requirement_scorer()
        
        # Act
        new_eval_by_ten_perspective(
            sample_df_requirement, 
            target_model, 
            scorer, 
            "requirement_eval"
        )
        
        # Assert
        for call in mock_eval.call_args_list:
            assert call.kwargs['model'] == target_model
    
    @patch('src.inspect.eval_datasets.eval')
    def test_log_format_json_parameter(self, mock_eval, sample_df_requirement, scorer_provider):
        # Arrange
        mock_eval.return_value = [Mock()]
        scorer = scorer_provider.get_requirement_scorer()
        
        # Act
        new_eval_by_ten_perspective(
            sample_df_requirement, 
            "test_model", 
            scorer, 
            "requirement_eval"
        )
        
        # Assert
        for call in mock_eval.call_args_list:
            assert call.kwargs['log_format'] == "json"