"""
Sample of creating a custom model.
Here is an example of implementing a custom model using multiple approaches.
"""

from inspect_ai import Task, task, eval
from inspect_ai.dataset import Sample, example_dataset
from inspect_ai.solver import generate, system_message, multiple_choice
from inspect_ai.scorer import exact, model_graded_qa, choice, Scorer
from inspect_ai.log import read_eval_log, EvalLog
from inspect_ai.log._file import eval_log_json_str, eval_log_json
from inspect_ai.model import ModelAPI, GenerateConfig, modelapi, ModelOutput, get_model
from inspect_ai.model._providers.openai_compatible import OpenAICompatibleAPI
from inspect_ai.model._chat_message import ChatMessage, ChatMessageSystem, ChatMessageUser, ChatMessageAssistant
from inspect_ai.tool import ToolInfo, ToolChoice
from json import loads
from dotenv import load_dotenv
import pytest
import os
from typing import Any, List
import asyncio


load_dotenv()


class MyCustomAPI(OpenAICompatibleAPI):
    def __init__(
        self,
        model_name: str,
        base_url: str | None = None,
        api_key: str | None = None,
        config: GenerateConfig = GenerateConfig(),
        **model_args: Any,
    ) -> None:
        super().__init__(
            model_name=model_name,
            base_url=base_url or "https://api.openai.com/v1",
            api_key=api_key,
            config=config,
            service="OpenAI",
            service_base_url="https://api.openai.com/v1",
            **model_args,
        )

@modelapi(name="mycustom")
def mycustom() -> MyCustomAPI:
    return MyCustomAPI

def sample_task():
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


@pytest.mark.skip("slow")
def test_custom_model_sample():
    os.environ["MYCUSTOMSERVICE_API_KEY"] = os.getenv("OPENAI_API_KEY")
    model = get_model("mycustom/gpt-4o-mini")
    logs = eval(sample_task(),model=model)
