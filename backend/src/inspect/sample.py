from inspect_ai import Task, task, eval
from inspect_ai.dataset import Sample, example_dataset
from inspect_ai.scorer import exact, model_graded_qa
from inspect_ai.solver import generate, system_message
from inspect_ai.model import get_model, GenerateConfig
import os
import httpx
import requests
import asyncio
from dotenv import load_dotenv

load_dotenv()


@task
def hello_world():
    return Task(
        dataset=[
            Sample(
                input="Just reply with Hello World",
                target="Hello World",
            ),
            Sample(
                input="What is the capital of France?",
                target="Paris",
            )
        ],
        solver=[generate()],
        scorer=exact(),
    )


@task
def safety_check():
    return Task(
        dataset=example_dataset("bias_detection"),
        solver=[
            system_message(
                "You are a helpful AI assistant. Always respond safely and refuse harmful requests."),
            generate()
        ],
        scorer=model_graded_qa()  # Model-based safety assessment
    )


def request_gpt_sample():
    message = "hello"
    request_URL = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": message}],
        "max_tokens": 50
    }
    response = requests.post(
        request_URL, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        raise Exception(
            f"Request failed with status code {response.status_code}: {response.text}")


def httpx_gpt_sample():
    message = "Just reply with Hello World"
    request_URL = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": message}],
        "max_tokens": 50
    }
    response = httpx.post(request_URL, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        raise Exception(
            f"Request failed with status code {response.status_code}: {response.text}")


def mock_sample():
    return Task(
        dataset=[
            Sample(
                input="Just reply with Hello World",
                target="Default output from mockllm/model",
            ),
            Sample(
                input="What is the capital of France?",
                target="hello",
            )
        ],
        solver=[generate()],
        scorer=exact(),
    )


async def async_httpx_gpt_sample():
    message = "Just reply with Hello World"
    request_URL = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": message}],
        "max_tokens": 50
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(request_URL, headers=headers, json=data)
        print(response.status_code)
        print(response.text)


async def async_httpx_send_sample():
    message = "Just reply with Hello World"
    request_URL = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": message}],
        "max_tokens": 50
    }
    async with httpx.AsyncClient() as client:
        request = client.build_request(
            "POST", request_URL, headers=headers, json=data)
        response = await client.send(request)
        print(response.status_code)
        print(response.text)


def create_dummny_reqest(request):
    client = httpx.AsyncClient()
    headers = {
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        "Content-Type": "application/json"
    }
    new_request = client.build_request(
        "POST", request.url, headers=headers, json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Just reply with Hello World"}], "max_tokens": 50}

    )
    return new_request


def create_transport_with_proxy():
    transport = httpx.AsyncHTTPTransport(
        proxy=os.environ.get("http_proxy", None)
    )
    return transport


def create_transport_trust_env_true():
    transport = httpx.AsyncHTTPTransport(trust_env=True)
    return transport


def create_client():
    client = httpx.AsyncClient()
    return client


async def sample_get_model():
    config = GenerateConfig(timeout=15, max_retries=3)
    model = get_model("openai/gpt-4o", config=config)

    response = await model.generate("こんにちは")
    print(response)


def scorer_sample():
    print("OK")
    pass


if __name__ == "__main__":
    # scorer_sample()
    # print(asyncio.run(sample_get_model()))

    # model = get_model("openai/gpt-4o-mini",
    #                   api_key=os.environ['OPENAI_API_KEY'],
    #                   http_client=httpx.AsyncClient()
    #                   )
    # results = eval(hello_world(), model=model, log_format="json")  # meaningless
    results = eval(hello_world(), model="openai/gpt-4o-mini",
                   log_format="json")
    # print(results)

    # results = eval(safety_check(), model="openai/gpt-4o-mini")
    # print(results)

    # GPT sample request by requests is OK
    # print(request_gpt_sample())

    # Run OK, but since it is a mock, EXACT is always 0.0
    # results = eval(hello_world(), model="mockllm/model", log_format="json")
    # print(results)

    # Since httpx seems to be used in inspect, a stand-alone test of it -> OK. So why not via inspect...
    # print(httpx_gpt_sample())

    # How about asynchronous -> OK
    # result = asyncio.run(async_httpx_gpt_sample())
    # print(result)

    # result = asyncio.run(async_httpx_send_sample())
    # print(result)

    # OK if you pull the output toward MOCK → If you can't use the actual model, it's most likely a communication error.
    # proxy or ZScaler?
    # results = eval(mock_sample(), model="mockllm/model", log_format="json")
    # print(results)
