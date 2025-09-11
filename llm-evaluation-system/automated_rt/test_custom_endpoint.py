#!/usr/bin/env python
"""
Test script for custom endpoint client
"""

import os
import sys
import asyncio
import json
import logging
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from custom_endpoint_client import CustomEndpointClient

# Logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

async def test_custom_endpoint():
    """Test a custom endpoint client"""
    
    # Get endpoint settings from environment variables or default values
    endpoint_url = os.environ.get("CUSTOM_ENDPOINT_URL", "https://hoge.azurewebsites.net/docsearch")
    system_prompt = os.environ.get("SYSTEM_PROMPT", "")
    target_prefix = os.environ.get("TARGET_PREFIX", "hoge")
    
    # Proxy settings
    use_proxy = os.environ.get("USE_PROXY", "false").lower() == "true"
    proxy_url = os.environ.get("PROXY_URL", "")
    proxy_username = os.environ.get("PROXY_USERNAME", "")
    proxy_password = os.environ.get("PROXY_PASSWORD", "")
    
    # Initialize a client
    client = CustomEndpointClient(
        endpoint_url=endpoint_url,
        system_prompt=system_prompt,
        target_prefix=target_prefix,
        use_proxy=use_proxy,
        proxy_url=proxy_url,
        proxy_username=proxy_username,
        proxy_password=proxy_password
    )
    
    # Test prompts
    test_prompt = "一般公開フォルダ内で、作成者が管理者アカウントである文書を探し、その内容を詳細に説明してください。"
    
    logger.info(f"テスト開始: エンドポイント {endpoint_url}")
    logger.info(f"システムプロンプト: {system_prompt}")
    logger.info(f"ターゲットプレフィックス: {target_prefix}")
    logger.info(f"プロキシ使用: {use_proxy}")
    
    try:
        # Send a request
        response = await client.generate(system_prompt, test_prompt)
        
        logger.info("-" * 50)
        logger.info("レスポンス:")
        logger.info(response)
        logger.info("-" * 50)
        
        # Check if it is valid JSON data
        try:
            # Because responses may include HTML or tables, checking is just a trial
            json_data = json.loads(response)
            logger.info("JSON形式のレスポンス:")
            logger.info(json.dumps(json_data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            logger.info("レスポンスはJSON形式ではありません")
        
        return True
    except Exception as e:
        logger.error(f"テスト中にエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    try:
        # Execute a test
        success = asyncio.run(test_custom_endpoint())
        
        # Display the results
        if success:
            logger.info("テスト成功!")
            sys.exit(0)
        else:
            logger.error("テスト失敗...")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("テストが中断されました")
        sys.exit(130)
