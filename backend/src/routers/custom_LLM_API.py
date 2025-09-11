"""
OpenAI-compatible API implementation (processing with pure JSON without using pydantic)
"""

import time
import uuid
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Header, Depends, Request
from fastapi.responses import JSONResponse
from src.utils.logger import logger

router = APIRouter(
    prefix="/v1",
    tags=["OpenAI Compatible API"]
)

# API key authentication configuration
API_KEY = "test-api-key"  # Read from environment variables in actual environment

def verify_api_key(authorization: Optional[str] = Header(None)):
    """Perform API key authentication"""
    logger.info("verify_api_key: APIキー認証を開始します。")
    if not authorization:
        logger.error("verify_api_key: API key required.")
        raise HTTPException(status_code=401, detail="API key required")
    
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization
    
    if token != API_KEY:
        logger.error("verify_api_key: Invalid API key.")
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    logger.info("verify_api_key: APIキー認証に成功しました。")
    return token

def validate_chat_completion_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate chat completion request"""
    logger.info("validate_chat_completion_request: リクエスト検証を開始します。")
    # Check required fields
    if "model" not in data:
        logger.error("validate_chat_completion_request: model is required.")
        raise HTTPException(status_code=400, detail="model is required")
    
    if "messages" not in data or not isinstance(data["messages"], list):
        logger.error("validate_chat_completion_request: messages is required and must be a list.")
        raise HTTPException(status_code=400, detail="messages is required and must be a list")
    
    # Message validation
    for i, message in enumerate(data["messages"]):
        if not isinstance(message, dict):
            logger.error(f"validate_chat_completion_request: Message {i} must be an object.")
            raise HTTPException(status_code=400, detail=f"Message {i} must be an object")
        
        if "role" not in message:
            logger.error(f"validate_chat_completion_request: Message {i} must have a role.")
            raise HTTPException(status_code=400, detail=f"Message {i} must have a role")
        
        if "content" not in message:
            logger.error(f"validate_chat_completion_request: Message {i} must have content.")
            raise HTTPException(status_code=400, detail=f"Message {i} must have content")
        
        if message["role"] not in ["system", "user", "assistant"]:
            logger.error(f"validate_chat_completion_request: Message {i} role must be system, user, or assistant.")
            raise HTTPException(status_code=400, detail=f"Message {i} role must be system, user, or assistant")
    
    # Set default values
    validated_data = {
        "model": data["model"],
        "messages": data["messages"],
        "temperature": data.get("temperature", 0.7),
        "max_tokens": data.get("max_tokens"),
        "top_p": data.get("top_p", 1.0),
        "n": data.get("n", 1),
        "stream": data.get("stream", False),
        "stop": data.get("stop")
    }
    logger.info("validate_chat_completion_request: リクエスト検証が完了しました。")
    return validated_data

@router.post("/chat/completions")
async def chat_completions(
    request: Request,
    api_key: str = Depends(verify_api_key)
) -> JSONResponse:
    """
    OpenAI-compatible chat completion endpoint
    """
    logger.info("chat_completions: チャット補完リクエストの処理を開始します。")
    # Get request body
    try:
        request_data = await request.json()
    except Exception:
        logger.error("chat_completions: Invalid JSON.")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Validate request
    try:
        validated_data = validate_chat_completion_request(request_data)
    except HTTPException as e:
        logger.error(f"chat_completions: リクエスト検証エラー: {e.detail}")
        raise

    # Generate mock response
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:29]}"
    created = int(time.time())
    
    # Get last message
    messages = validated_data["messages"]
    last_message = messages[-1] if messages else None
    
    # Generate mock response content
    mock_content = f"This is a mock response to: {last_message['content'] if last_message else 'No message'}"
    
    # Calculate prompt token count (simple calculation)
    prompt_tokens = sum(len(msg["content"].split()) for msg in messages)
    completion_tokens = len(mock_content.split())
    total_tokens = prompt_tokens + completion_tokens
    
    # Create response
    response_data = {
        "id": completion_id,
        "object": "chat.completion",
        "created": created,
        "model": validated_data["model"],
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": mock_content
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }
    }
    logger.info("chat_completions: チャット補完レスポンスの生成が完了しました。")
    return JSONResponse(content=response_data)

@router.get("/models")
async def list_models(api_key: str = Depends(verify_api_key)) -> JSONResponse:
    """
    Return a list of available models
    """
    logger.info("list_models: モデル一覧取得リクエストの処理を開始します。")
    response_data = {
        "object": "list",
        "data": [
            {
                "id": "gpt-4o-mini",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "openai"
            },
            {
                "id": "gpt-4o",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "openai"
            },
            {
                "id": "gpt-3.5-turbo",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "openai"
            }
        ]
    }
    logger.info("list_models: モデル一覧レスポンスの生成が完了しました。")
    return JSONResponse(content=response_data)

@router.get("/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint
    """
    logger.info("health_check: ヘルスチェックリクエストの処理を開始します。")
    return JSONResponse(content={"status": "healthy"})
