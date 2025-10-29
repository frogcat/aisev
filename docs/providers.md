# Model Providers

OpenAI 以外の LLM を使用するための方法をまとめます。

## Overview

<https://inspect.aisi.org.uk/providers.html> は
[inspect_ai](https://inspect.aisi.org.uk/) でさまざまな LLM を使用するためのガイドです。

このガイドに従って、使用したい LLM に応じてパッケージを導入したり、
環境変数を追加する必要があります。

パッケージの追加は `backend/requirements.txt` に、
環境変数の追加は `docker-compose.yml` の中の `services > fastapi > environment` 配下に項目を追加します。

## Example: Ollama

### 1. パッケージの追加

<https://inspect.aisi.org.uk/providers.html#ollama> によると
`openai` パッケージが必要です。
ただし、`backend/requirements.txt` にはすでに `openai` が含まれているのでこの作業は不要です。

### 2. 環境変数の追加

<https://inspect.aisi.org.uk/providers.html#ollama> によると
`OLLAMA_BASE_URL` を指定する必要があります。
指定しなかった場合は `http://localhost:11434/v1` が使用されるとのことです。

仮に Ollama が `http://ollama:4000/` で動作しているとすれば、
`docker-compose.yml` を以下のように編集します。

```yml
(前略)
  fastapi:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: fastapi
    environment:
      PYTHONPATH: /app
      DB_USER: postgres
      DB_PASSWORD: password
      DB_HOST: postgresdb
      DB_PORT: 5432
      DB_NAME: mydb
      OLLAMA_BASE_URL: http://ollama:4000/
      LOG_LEVEL: DEBUG
(後略)
```

### 3. WebUI での作業

`docker compose build` と `docker compose up` を実行した上で
[AI 情報登録・管理](http://localhost:5173/model-management?from=definer-home) を開きます。

ここで **AI 情報登録** フォームで以下のように情報を登録します。

| 項目          | 値                            | 備考                     |
| ------------- | ----------------------------- | ------------------------ |
| AI 情報ラベル | 任意文字列                    | 表示用の任意文字列を指定 |
| AI モデル名   | ollama/${ollama でのモデル名} | ※1                       |
| AI モデル名   | http://example.org/           | ※2                       |
| API キー      | default                       | ※3                       |

- ※1: <https://inspect.aisi.org.uk/providers.html> で登場する `--model ${model_name}` に使用するモデル名を指定します
- ※2: 内部的には使用されないので、適当な URL を指定します
- ※3: 内部的には使用されないので、適当な文字列を指定します

## Notice

本家の aisev では [inspec_ai の eval](https://inspect.aisi.org.uk/reference/inspect_ai.html) を実行する際に
WebUI で指定した **AIモデル名** ではなく、別の名前が渡されるという問題があります。

この fork では **Web UI で指定した AI モデル名** が使用されるように以下の変更を加えています。
このドキュメントの方法を試す場合には、本家 aisev ではなくこの fork を使用する必要があることに注意してください。

<https://github.com/frogcat/aisev/commit/ca3b4e65575486536a8defccabffa85c4cc13a03>

(以上)
