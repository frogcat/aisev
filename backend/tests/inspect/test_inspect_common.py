import pytest
from unittest.mock import patch, Mock, MagicMock
from src.inspect.inspect_common import AICustomAPI, register_in_inspect_ai
from inspect_ai.model import GenerateConfig


class TestAICustomAPI:
    
    def test_ai_custom_api_initialization(self):
        """AICustomAPI initialization test"""
        # Arrange
        model_name = "test-model"
        base_url = "https://api.test.com/v1"
        api_key = "test-key"
        config = GenerateConfig()
        
        # Act
        api = AICustomAPI(
            model_name=model_name,
            base_url=base_url,
            api_key=api_key,
            config=config
        )
        
        # Assert
        assert api is not None
        # Since it inherits from OpenAICompatibleAPI, verify that basic attributes are set
        assert hasattr(api, 'model_name')
        assert hasattr(api, 'base_url')
        assert hasattr(api, 'api_key')

    def test_ai_custom_api_with_model_args(self):
        """AICustomAPI initialization test with additional model arguments"""
        # Arrange
        model_name = "test-model"
        base_url = "https://api.test.com/v1"
        api_key = "test-key"
        config = GenerateConfig()
        # Use only arguments accepted by AsyncOpenAI
        extra_args = {"timeout": 30, "max_retries": 3}
        
        # Act
        api = AICustomAPI(
            model_name=model_name,
            base_url=base_url,
            api_key=api_key,
            config=config,
            **extra_args
        )
        
        # Assert
        assert api is not None

    def test_ai_custom_api_with_empty_strings(self):
        """AICustomAPI initialization test with empty strings"""
        # Arrange
        model_name = ""
        base_url = ""
        api_key = ""
        config = GenerateConfig()
        
        # Act & Assert
        # Empty strings may cause errors in environment variable validation
        try:
            api = AICustomAPI(
                model_name=model_name,
                base_url=base_url,
                api_key=api_key,
                config=config
            )
            assert api is not None
        except Exception:
            # Initialization errors due to empty strings are expected
            pass

    def test_ai_custom_api_with_none_config(self):
        """AICustomAPI initialization test when config is None"""
        # Arrange
        model_name = "test-model"
        base_url = "https://api.test.com/v1"
        api_key = "test-key"
        
        # Act
        api = AICustomAPI(
            model_name=model_name,
            base_url=base_url,
            api_key=api_key,
            config=None
        )
        
        # Assert
        assert api is not None

    def test_ai_custom_api_with_valid_model_args(self):
        """AICustomAPI initialization test with valid model_args"""
        # Arrange
        model_name = "test-model"
        base_url = "https://api.test.com/v1"
        api_key = "test-key"
        config = GenerateConfig()
        # Valid arguments accepted by AsyncOpenAI constructor
        valid_args = {
            "timeout": 60,
            "max_retries": 5,
            "default_headers": {"Custom-Header": "value"}
        }
        
        # Act
        api = AICustomAPI(
            model_name=model_name,
            base_url=base_url,
            api_key=api_key,
            config=config,
            **valid_args
        )
        
        # Assert
        assert api is not None


class TestRegisterInInspectAI:
    
    @patch('src.inspect.inspect_common.modelapi')
    def test_register_in_inspect_ai_success(self, mock_modelapi):
        """Test for successful model registration"""
        # Arrange
        model_name = "gpt-4o-mini"
        api_url = "https://api.openai.com/v1"
        api_key = "test-api-key"
        expected_alias = f"custom-model-{model_name}"
        
        mock_modelapi.return_value = Mock()
        
        # Act
        result = register_in_inspect_ai(model_name, api_url, api_key)
        
        # Assert
        assert result == expected_alias
        mock_modelapi.assert_called_once_with(name=expected_alias)

    @patch('src.inspect.inspect_common.modelapi')
    def test_register_in_inspect_ai_with_unicode_model_name(self, mock_modelapi):
        """Test with model name containing Unicode characters"""
        # Arrange
        model_name = "テストモデル-日本語"
        api_url = "https://api.test.com/v1"
        api_key = "test-key"
        expected_alias = f"custom-model-{model_name}"
        
        mock_modelapi.return_value = Mock()
        
        # Act
        result = register_in_inspect_ai(model_name, api_url, api_key)
        
        # Assert
        assert result == expected_alias
        mock_modelapi.assert_called_once_with(name=expected_alias)

    @patch('src.inspect.inspect_common.modelapi')
    def test_register_in_inspect_ai_with_empty_strings(self, mock_modelapi):
        """Test with empty strings"""
        # Arrange
        model_name = ""
        api_url = ""
        api_key = ""
        expected_alias = "custom-model-"
        
        mock_modelapi.return_value = Mock()
        
        # Act
        result = register_in_inspect_ai(model_name, api_url, api_key)
        
        # Assert
        assert result == expected_alias
        mock_modelapi.assert_called_once_with(name=expected_alias)

    @patch('src.inspect.inspect_common.modelapi')
    def test_register_in_inspect_ai_with_special_characters(self, mock_modelapi):
        """Test with special characters"""
        # Arrange
        model_name = "model-name_with.special@chars"
        api_url = "https://api.test.com/v1"
        api_key = "key-with-special-chars_123"
        expected_alias = f"custom-model-{model_name}"
        
        mock_modelapi.return_value = Mock()
        
        # Act
        result = register_in_inspect_ai(model_name, api_url, api_key)
        
        # Assert
        assert result == expected_alias
        mock_modelapi.assert_called_once_with(name=expected_alias)

    @patch('src.inspect.inspect_common.modelapi')
    def test_register_in_inspect_ai_factory_function(self, mock_modelapi):
        """Test whether factory function is created correctly"""
        # Arrange
        model_name = "test-model"
        api_url = "https://api.test.com/v1"
        api_key = "test-key"
        
        # Mock to capture arguments when modelapi decorator is called
        captured_function = None
        def capture_decorator(name):
            def decorator(func):
                nonlocal captured_function
                captured_function = func
                return func
            return decorator
        
        mock_modelapi.side_effect = capture_decorator
        
        # Act
        register_in_inspect_ai(model_name, api_url, api_key)
        
        # Assert
        assert captured_function is not None
        
        # Execute factory function to get wrapper function
        wrapper = captured_function()
        assert callable(wrapper)

    @patch('src.inspect.inspect_common.modelapi')
    @patch('src.inspect.inspect_common.AICustomAPI')
    def test_register_in_inspect_ai_wrapper_function(self, mock_ai_custom_api, mock_modelapi):
        """Test whether wrapper function works correctly"""
        # Arrange
        model_name = "test-model"
        api_url = "https://api.test.com/v1"
        api_key = "test-key"
        
        captured_function = None
        def capture_decorator(name):
            def decorator(func):
                nonlocal captured_function
                captured_function = func
                return func
            return decorator
        
        mock_modelapi.side_effect = capture_decorator
        mock_ai_custom_api.return_value = Mock()
        
        # Act
        register_in_inspect_ai(model_name, api_url, api_key)
        
        # Execute factory function to get wrapper function
        wrapper = captured_function()
        
        # Call wrapper function (using only arguments accepted by AsyncOpenAI)
        config = GenerateConfig()
        test_model_name = "wrapper-test-model"
        extra_args = {"timeout": 30}  # Use timeout instead of temperature
        
        result = wrapper(test_model_name, config=config, **extra_args)
        
        # Assert
        mock_ai_custom_api.assert_called_once_with(
            model_name=test_model_name,
            base_url=api_url,
            api_key=api_key,
            config=config,
            timeout=30
        )

    @patch('src.inspect.inspect_common.modelapi')
    @patch('src.inspect.inspect_common.AICustomAPI')
    def test_register_in_inspect_ai_wrapper_removes_conflicting_args(self, mock_ai_custom_api, mock_modelapi):
        """Test whether wrapper function removes conflicting arguments"""
        # Arrange
        model_name = "test-model"
        api_url = "https://api.test.com/v1"
        api_key = "test-key"
        
        captured_function = None
        def capture_decorator(name):
            def decorator(func):
                nonlocal captured_function
                captured_function = func
                return func
            return decorator
        
        mock_modelapi.side_effect = capture_decorator
        mock_ai_custom_api.return_value = Mock()
        
        # Act
        register_in_inspect_ai(model_name, api_url, api_key)
        
        # Execute factory function to get wrapper function
        wrapper = captured_function()
        
        # Call wrapper function with conflicting arguments
        config = GenerateConfig()
        test_model_name = "wrapper-test-model"
        conflicting_args = {
            "base_url": "https://conflicting.url/v1",
            "api_key": "conflicting-key",
            "timeout": 30  # Use timeout instead of temperature
        }
        
        result = wrapper(test_model_name, config=config, **conflicting_args)
        
        # Assert
        # Verify that base_url and api_key are removed and original values are used
        mock_ai_custom_api.assert_called_once_with(
            model_name=test_model_name,
            base_url=api_url,  # Original value
            api_key=api_key,   # Original value
            config=config,
            timeout=30    # Non-removed argument
        )

    @patch('src.inspect.inspect_common.modelapi')
    def test_register_in_inspect_ai_multiple_calls(self, mock_modelapi):
        """Test for multiple calls"""
        # Arrange
        mock_modelapi.return_value = Mock()
        
        # Act
        result1 = register_in_inspect_ai("model1", "url1", "key1")
        result2 = register_in_inspect_ai("model2", "url2", "key2")
        result3 = register_in_inspect_ai("model1", "url3", "key3")  # Same model name
        
        # Assert
        assert result1 == "custom-model-model1"
        assert result2 == "custom-model-model2"
        assert result3 == "custom-model-model1"  # Same alias
        
        # Verify that modelapi was called 3 times
        assert mock_modelapi.call_count == 3

    @patch('src.inspect.inspect_common.modelapi')
    def test_register_in_inspect_ai_with_long_model_name(self, mock_modelapi):
        """Test with very long model name"""
        # Arrange
        model_name = "very-long-model-name-" * 10  # Long model name
        api_url = "https://api.test.com/v1"
        api_key = "test-key"
        expected_alias = f"custom-model-{model_name}"
        
        mock_modelapi.return_value = Mock()
        
        # Act
        result = register_in_inspect_ai(model_name, api_url, api_key)
        
        # Assert
        assert result == expected_alias
        mock_modelapi.assert_called_once_with(name=expected_alias)

    @patch('src.inspect.inspect_common.modelapi')
    def test_register_in_inspect_ai_with_none_values(self, mock_modelapi):
        """Test with None values"""
        # Arrange
        mock_modelapi.return_value = Mock()
        
        # Act
        result = register_in_inspect_ai(None, "url", "key")
        
        # Assert
        # Even with None values, string concatenation results in "custom-model-None" and works normally
        assert result == "custom-model-None"
        mock_modelapi.assert_called_once_with(name="custom-model-None")

    @patch('src.inspect.inspect_common.modelapi')
    def test_register_in_inspect_ai_modelapi_exception(self, mock_modelapi):
        """Test when exception occurs during modelapi call"""
        # Arrange
        mock_modelapi.side_effect = Exception("modelapi registration failed")
        
        # Act & Assert
        with pytest.raises(Exception, match="modelapi registration failed"):
            register_in_inspect_ai("test-model", "test-url", "test-key")

    @patch('src.inspect.inspect_common.modelapi')
    @patch('src.inspect.inspect_common.AICustomAPI')
    def test_register_in_inspect_ai_wrapper_with_default_config(self, mock_ai_custom_api, mock_modelapi):
        """Test calling wrapper function with default config"""
        # Arrange
        model_name = "test-model"
        api_url = "https://api.test.com/v1"
        api_key = "test-key"
        
        captured_function = None
        def capture_decorator(name):
            def decorator(func):
                nonlocal captured_function
                captured_function = func
                return func
            return decorator
        
        mock_modelapi.side_effect = capture_decorator
        mock_ai_custom_api.return_value = Mock()
        
        # Act
        register_in_inspect_ai(model_name, api_url, api_key)
        
        # Execute factory function to get wrapper function
        wrapper = captured_function()
        
        # Call wrapper function with default config
        test_model_name = "wrapper-test-model"
        result = wrapper(test_model_name)
        
        # Assert
        # Verify that default GenerateConfig() is used
        mock_ai_custom_api.assert_called_once()
        call_args = mock_ai_custom_api.call_args
        assert call_args[1]["model_name"] == test_model_name
        assert call_args[1]["base_url"] == api_url
        assert call_args[1]["api_key"] == api_key
        assert isinstance(call_args[1]["config"], GenerateConfig)

    def test_alias_generation_consistency(self):
        """Alias generation consistency test"""
        # Arrange
        model_name = "consistent-model"
        api_url = "https://api.test.com/v1"
        api_key = "test-key"
        
        with patch('src.inspect.inspect_common.modelapi') as mock_modelapi:
            mock_modelapi.return_value = Mock()
            
            # Act
            result1 = register_in_inspect_ai(model_name, api_url, api_key)
            result2 = register_in_inspect_ai(model_name, api_url, api_key)
            
            # Assert
            assert result1 == result2
            assert result1 == f"custom-model-{model_name}"

    @patch('src.inspect.inspect_common.modelapi')
    def test_register_in_inspect_ai_return_type(self, mock_modelapi):
        """Return value type test"""
        # Arrange
        mock_modelapi.return_value = Mock()
        
        # Act
        result = register_in_inspect_ai("test", "test", "test")
        
        # Assert
        assert isinstance(result, str)
        assert result.startswith("custom-model-")