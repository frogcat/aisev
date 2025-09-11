import os
import json
import aiohttp
import logging
from typing import Dict, Any, Optional
from llm_client import LLMClient

# Logging settings
logger = logging.getLogger(__name__)

class CustomEndpointClient(LLMClient):
    """LLM client using custom endpoints"""
    
    def __init__(
        self,
        endpoint_url: str,
        system_prompt: Optional[str] = None,
        target_prefix: Optional[str] = None,
        use_proxy: bool = False,
        proxy_url: Optional[str] = None,
        proxy_username: Optional[str] = None,
        proxy_password: Optional[str] = None
    ):
        """
        Initialization of CustomEndpointClient
        
        Args:
            endpoint_url: URL of the Custom Endpoint
            system_prompt: System prompt
            target_prefix: Target prefix
            use_proxy: Using a proxy or not
            proxy_url: URL of the proxy
            proxy_username: User name of the proxy
            proxy_password: Password of the proxy
        """
        self.endpoint_url = endpoint_url
        self.system_prompt = system_prompt or ""
        self.target_prefix = target_prefix or ""
        
        # Proxy settings
        self.use_proxy = use_proxy
        self.proxy_url = proxy_url
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        
        # Get proxy settings from environment variables (if not set)
        if self.use_proxy and not self.proxy_url:
            self.proxy_url = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
        if self.use_proxy and not self.proxy_username:
            self.proxy_username = os.environ.get("PROXY_USERNAME")
        if self.use_proxy and not self.proxy_password:
            self.proxy_password = os.environ.get("PROXY_PASSWORD")
    
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate responses using the custom endpoint
        
        Args:
            system_prompt: System prompt (use default settings if available)
            user_prompt: User prompt
            
        Returns:
            str: Response text from LLM
        """
        # Currently activated system prompt (use an argument value if available)
        effective_system_prompt = system_prompt if system_prompt else self.system_prompt
        
        # Building the request payload
        payload = {
            "history": [{"user": user_prompt}],
            "approach": "rrr",
            "overrides": {
                "gptModel": "gpt-4o",
                "temperature": "0.7",
                "top": 10,
                "semanticRanker": True,
                "semanticCaptions": True,
                "systemPrompt": effective_system_prompt
            },
            "target_prefix": self.target_prefix
        }
        
        # Creating a ClientSession with proxy settings
        session_kwargs = {}
        if self.use_proxy and self.proxy_url:
            if self.proxy_username and self.proxy_password:
                proxy_auth = aiohttp.BasicAuth(self.proxy_username, self.proxy_password)
                session_kwargs["proxy_auth"] = proxy_auth
            session_kwargs["proxy"] = self.proxy_url
        
        try:
            logger.info(f"リクエスト送信先: {self.endpoint_url}")
            logger.debug(f"リクエスト内容: {json.dumps(payload, ensure_ascii=False)}")
            
            async with aiohttp.ClientSession(**session_kwargs) as session:
                async with session.post(
                    self.endpoint_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"エンドポイント呼び出しエラー: ステータス {response.status}, 内容: {error_text}")
                        return f"エラー: カスタムエンドポイント呼び出しに失敗しました (ステータス {response.status}): {error_text}"
                    
                    result = await response.json()
                    if "answer" in result:
                        # Unicode エスケープされた文字列を適切にデコード
                        answer = result["answer"]
                        logger.debug(f"受信したレスポンス: {answer}")
                        return answer
                    else:
                        logger.error(f"予期しないレスポンス形式: {result}")
                        return f"エラー: 予期しないレスポンス形式: {str(result)}"
        except Exception as e:
            logger.exception(f"カスタムエンドポイント呼び出し中の例外: {e}")
            return f"エラー: {str(e)}"
