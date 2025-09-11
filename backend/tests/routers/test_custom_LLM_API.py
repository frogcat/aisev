"""
Test script for OpenAI-compatible API
"""

from fastapi.testclient import TestClient
from src.main import app
from inspect_ai import Task, eval
from inspect_ai.dataset import Sample
from inspect_ai.solver import generate
from inspect_ai.scorer import exact
from inspect_ai.model import ModelAPI, GenerateConfig, modelapi, get_model
from inspect_ai.model._providers.openai_compatible import OpenAICompatibleAPI
from typing import Any
import os
from dotenv import load_dotenv
import pytest
from src.inspect.inspect_common import register_in_inspect_ai

load_dotenv()


client = TestClient(app)


# @pytest.fixture
# def custom_test_api():
#     """Fixture for CustomTestAPI"""
#     class CustomTestAPI(OpenAICompatibleAPI):
#         def __init__(
#             self,
#             model_name: str,
#             base_url: str | None = None,
#             api_key: str | None = None,
#             config: GenerateConfig = GenerateConfig(),
#             **model_args: Any,
#         ) -> None:
#             super().__init__(
#                 model_name=model_name,
#                 base_url=base_url or "http://localhost:8000/v1",
#                 api_key=api_key or "test-api-key",
#                 config=config,
#                 service="CustomTest",
#                 service_base_url="http://localhost:8000/v1",
#                 **model_args,
#             )

#     @modelapi(name="customtest")
#     def customtest() -> CustomTestAPI:
#         return CustomTestAPI
    
#     return CustomTestAPI


@pytest.fixture
def sample_task():
    """Fixture for sample_task"""
    def _sample_task():
        return Task(
            dataset=[
                Sample(
                    input="Just reply with Hello World",
                    target="Hello World",
                ),
            ],
            solver=[generate()],
            scorer=exact(),
        )
    return _sample_task


def test_localhost_access():
    """Test for simple HTTP access to localhost"""
    # NOTE: health_check OK
    # response = client.get("http://localhost:8000/v1/health")
    headers = {"Authorization": "Bearer test-api-key"}
    # NOTE: list_models OK
    # response = client.get("http://localhost:8000/v1/models", headers=headers)
    # NOTE: chat_completion OK
    response = client.post("/v1/chat/completions", headers=headers, json={
        "model": "mock-model",
        "messages": [
            {"role": "user", "content": "Hello, how are you?"}
        ],
        "temperature": 0.7
        })
    assert response.status_code == 200
    data = response.json()
    print(f"Response from localhost: {data}")


# Test for using API with inspect_ai
# @pytest.mark.skip("社内proxyにひっかかる")
@pytest.mark.asyncio
async def test_use_api_in_inspect_ai(sample_task):
    """Test for using API with inspect_ai"""


    # Register custom model in inspect_ai
    api_url = "http://localhost:8000/v1"
    alias = register_in_inspect_ai(
        model_name="mock-model",
        api_url=api_url,
        api_key="test-api-key"
    )

    
    # Try generate
    # If api_url is local, temporarily save and disable http_proxy
    if api_url.startswith("http://localhost") or api_url.startswith("http://127.0.0.1"):
        original_http_proxy = os.environ.get("http_proxy")
        os.environ["http_proxy"] = ""
    else:
        original_http_proxy = None
    try:
        print(f"outer proxy: {os.environ.get('http_proxy')}")
        os.environ["CUSTOMTEST_API_KEY"] = "test-api-key"
        model = get_model(f"{alias}/mock-model")
        # Test with inspect_ai using custom API
        response = await model.generate("hello")
    finally:
        # Restore original http_proxy
        if original_http_proxy is not None:
            os.environ["http_proxy"] = original_http_proxy
    print(f"Generated response: {response}")


def test_eval_with_inspect_ai(sample_task):
    """Test for using API with inspect_ai eval"""
    api_url = "http://localhost:8000/v1"
    alias = register_in_inspect_ai(
        model_name="mock-model",
        api_url=api_url,
        api_key="test-api-key"
    )

    if api_url.startswith("http://localhost") or api_url.startswith("http://127.0.0.1"):
        original_http_proxy = os.environ.get("http_proxy")
        os.environ["http_proxy"] = ""
    else:
        original_http_proxy = None
    try:
        os.environ["CUSTOMTEST_API_KEY"] = "test-api-key"
        model = get_model(f"{alias}/mock-model")
        # Test using eval
        logs = eval(sample_task(), mode=model, display="none")
        assert logs is not None
    finally:
        if original_http_proxy is not None:
            os.environ["http_proxy"] = original_http_proxy


# Test for API itself

def test_health_check():
    """Test for health check"""
    response = client.get("/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_models():
    """Test for model list"""
    headers = {"Authorization": "Bearer test-api-key"}
    response = client.get("/v1/models", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "object" in data
    assert "data" in data
    assert data["object"] == "list"
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0
    model = data["data"][0]
    assert "id" in model
    assert "object" in model
    assert "created" in model
    assert "owned_by" in model


def test_chat_completion():
    """Test for chat completion"""
    headers = {
        "Authorization": "Bearer test-api-key",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mock-model",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    response = client.post("/v1/chat/completions", headers=headers, json=data)
    assert response.status_code == 200
    response_data = response.json()
    
    # Validate response structure
    assert "id" in response_data
    assert "object" in response_data
    assert "created" in response_data
    assert "model" in response_data
    assert "choices" in response_data
    assert "usage" in response_data
    
    assert response_data["object"] == "chat.completion"
    assert response_data["model"] == "mock-model"
    assert len(response_data["choices"]) == 1
    
    choice = response_data["choices"][0]
    assert "index" in choice
    assert "message" in choice
    assert "finish_reason" in choice
    
    message = choice["message"]
    assert "role" in message
    assert "content" in message
    assert message["role"] == "assistant"
    assert message["content"] is not None
    
    usage = response_data["usage"]
    assert "prompt_tokens" in usage
    assert "completion_tokens" in usage
    assert "total_tokens" in usage

@pytest.mark.skip("一旦保留")
def test_chat_completion_with_tools():
    """Test for chat completion with tool usage"""
    headers = {
        "Authorization": "Bearer test-api-key",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mock-model",
        "messages": [
            {"role": "user", "content": "What's the weather like?"}
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current weather",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string", "description": "The city and state"}
                        },
                        "required": ["location"]
                    }
                }
            }
        ],
        "tool_choice": "auto"
    }
    
    response = client.post("/v1/chat/completions", headers=headers, json=data)
    assert response.status_code == 200
    response_data = response.json()
    
    # Validate response structure
    assert "id" in response_data
    assert "object" in response_data
    assert "created" in response_data
    assert "model" in response_data
    assert "choices" in response_data
    assert "usage" in response_data
    
    choice = response_data["choices"][0]
    assert choice["finish_reason"] == "tool_calls"
    
    message = choice["message"]
    assert "role" in message
    assert "tool_calls" in message
    assert message["role"] == "assistant"
    assert message["tool_calls"] is not None
    assert len(message["tool_calls"]) > 0
    
    tool_call = message["tool_calls"][0]
    assert "id" in tool_call
    assert "type" in tool_call
    assert "function" in tool_call
    assert tool_call["type"] == "function"
    
    function = tool_call["function"]
    assert "name" in function
    assert "arguments" in function


def test_unauthorized_access():
    """Test for access without authentication"""
    response = client.get("/v1/models")
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "API key required"


def test_invalid_api_key():
    """Test for invalid API key"""
    headers = {"Authorization": "Bearer invalid-key"}
    response = client.get("/v1/models", headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Invalid API key"
