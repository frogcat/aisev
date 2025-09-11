[English version is here.](appendix-en.md)

# 付録 概要

付録には、利用手順書を補足する情報を記載しています。

---

# AIセーフティ評価環境へ登録可能な定量評価データセット形式

## 説明

AIセーフティ評価環境の定量評価データセット登録・管理画面で登録できる定量評価データセットは CSV形式のデータで、AIの出力結果の評価方法は3種類存在します。
評価方法は、「AIの出力が要件を満たすか」「AIが複数選択肢の中から正しいものを選べるか」「AIの出力が想定回答と意味的に一致するか」という 3種類であり、データセット内のscorer列の値により、適用する評価方法が決定されます。また、評価方法によって必要な列も異なります。

## 必要な列の詳細

データに付与されたscorer列の値によって評価方法が決まり、必要な列も変化します。
必要な列以外は、データ内に存在していても無視されます。

- scorer=requirement: 出力が要件を満たしているかの判定  
  - 必要な列: ID, text, ten_perspective, requirement(回答が従うべき要件)
- scorer=multiplechoice: 多肢選択肢から正解を選ぶ形式  
  - 必要な列: ID, text, ten_perspective, ans0, ans1, ...（選択肢）, output（正解の選択肢）
- scorer=model_graded_qa: 出力と想定回答の意味的一致を判定  
  - 必要な列: ID, text, ten_perspective, output（想定回答）

## データ形式の例

  - 要件 (scorer=requirement)
    | id | ten_perspective                | text         | requirement                | scorer     |
    |----|-------------------------------|--------------|----------------------------|------------|
    | 1  | ハイリスク利用・目的外利用への対処 | AIへの入力 | AIの出力に対する要件      | requirement |
  - 多肢選択 (scorer=multiplechoice)
    | id | ten_perspective      | text         | ans0      | ans1      | ans2      | ans3      | output   | scorer        |
    |----|----------------------|--------------|-----------|-----------|-----------|-----------|----------|--------------|
    | 1  | 公平性と包摂性       | AIへの入力 | 選択肢 A  | 選択肢 B  | 選択肢 C  | 選択肢 D  | 想定回答(選択肢のアルファベット) | multiplechoice |
  - 意味的一致 (scorer=指定なし または model_graded_qa)
    | id | ten_perspective         | text         | output   |
    |----|------------------------|--------------|----------|
    | 1  | 有害情報の出力制御      | AIへの入力 | 想定回答 |


---

# AIモデル登録時のAPI仕様について

AIセーフティ評価環境のAI情報登録・管理画面で登録するAIモデル/AIシステムは、以下のAPI仕様を満たしている必要があります。

   - OpenAI APIと互換のAPI仕様になります。

## エンドポイント

  **`{base_url}/chat/completions`**
    (ここでの `base_url` は任意のURLです)

## API キーベースの認証

  **`Authorization: Bearer <api_key>`**
    ヘッダー

## request
  以下は、request の一例になります。
  request の記載項目や設定値については、利用する API サービスの仕様をご確認の上、設定してください。

  ```json
  {
    "model": "gpt-4o-mini",
    "messages": [
      { "role": "system", "content": "あなたは有能なアシスタントです。" },
      { "role": "user", "content": "明日の東京の天気を教えてください。" }
    ],
    "temperature": 0.7,
    "max_tokens": 150,
    "top_p": 1.0,
    "n": 1,
    "stream": false,
    "stop": null
  }
  ```

  - **model**: [ 必須 ] 使用するモデル名 (`gpt-4o-mini`／`gpt-4o`／`gpt-3.5-turbo`など)
  - **messages**: [ 必須 ] やり取りのリスト
    - **role**: `system`／`user`／`assistant`
    - **content**: 発話内容
  - **temperature**: [ 任意、既定値：1 ] 出力のランダム性（0.0 ～ 2.0）
  - **max_tokens**: [ 任意、既定値：明示的なデフォルトはなし ] 最大トークン数
  - **top_p**: [ 任意、既定値：1 ] nucleus sampling の確率質量（0.0 ～ 1.0）
  - **n**: [ 任意、既定値：1 ] 生成候補数
  - **stream**: [ 任意、既定値：false ] ストリーミング応答の有無
  - **stop**: [ 任意、既定値：null ] 生成を停止するトークン列（文字列または配列）

## response
  以下は、response の一例になります。

  ```json
  {
    "id": "chatcmpl-7XyZAbCdEfGhIjK",
    "object": "chat.completion",
    "created": 1710000000,
    "model": "gpt-4o-mini",
    "usage": {
      "prompt_tokens": 25,
      "completion_tokens": 40,
      "total_tokens": 65
    },
    "choices": [
      {
        "index": 0,
        "message": {
          "role": "assistant",
          "content": "明日の東京は晴れ時々曇りで、最高気温は28℃、最低気温は20℃の予報です。"
        },
        "finish_reason": "stop"
      }
    ]
  }
  ```

  - **id**: 完了オブジェクトの一意識別子
  - **object**: `"chat.completion"`（オブジェクトの種類）
  - **created**: UNIX タイムスタンプ（秒）
  - **model**: 実際に使われたモデル名
  - **usage**: トークン消費量
    - **prompt_tokens**: リクエストで消費したトークン
    - **completion_tokens**: 応答で消費したトークン
    - **total_tokens**: 合計
  - **choices**: 生成された応答のリスト
    - **index**: 応答インデックス（0 から始まる）
    - **message**: 実際の応答
      - **role**: 常に `"assistant"`
      - **content**: 返答テキスト
    - **finish_reason**: 生成停止理由（例: `"stop"`／`"length"`）

## 呼び出され方例

  ```bash
  curl https://api.openai.com/v1/chat/completions \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
      "model": "gpt-4o-mini",
      "messages": [
        {"role": "system",  "content": "あなたは有能なアシスタントです。"},
        {"role": "user",    "content": "パスタのレシピを教えてください。"}
      ],
      "temperature": 0.5,
      "max_tokens": 200,
      "n": 1
    }'

  ```

## LM Studioとopen-ai/gpt-oss-20bの組み合わせでローカル環境で運用しているAIを評価対象とする場合の定義例

一例として、LM Studioとopen-ai/gpt-oss-20bの組み合わせでローカル環境で運用されているAIを本ツールの評価対象とするために、AI情報登録する場合の例を示します。

  1. LM StudioをDeveloperとしてインストールし、Developer画面でサーバを起動し、APIを受け付け可能な状態にします。
     - 例として、IPアドレスが"192.168.10.13"で、ポートが"1234"の場合、ベースのURLは"http://192.168.10.13:1234/v1/"となります。
     - LM Studioの利用方法の詳細については、LM Studioのサイトを参照してください。
  2. 「AI情報登録」画面にて、以下のように、 AI モデルを更新する場合は「 AI 情報更新」のタブをクリックします。
     - **AI 情報ラベル:** 任意の識別名を入力してください。（例：ai_local_gpt-oss-20b）
     - **モデル名:** LM Studioインストール時に標準的な方法でgpt-oss-20bをインストールした場合、"openai/gpt-oss-20b"となります。
     - **URL:** 上記のLM Studioの設定から特定したベースURLを入力してください。（例：http://192.168.10.13:1234/v1/）
     - **APIキー:** このケースではAPIキーは使用しませんが、"Key"と入力してください。
  3. 各項目の入力が完了後、「登録」ボタンを押下してください。
     - 正常に登録されると、画面下部に完了メッセージが表示されます。
  4. 以降、登録したAI情報を評価実施者向け画面で評価対象AI情報に指定することで、評価対象とすることができます。

---

# 評価結果JSONファイルの内容

AIセーフティ評価環境の評価結果詳細画面でJSONエクスポートを実行した場合、評価結果のJSONファイルは以下のような構造で出力されます。
resultsの subCategory、evaluationContent、scoreRate は AISIプリセット評価データセットを利用した場合にのみ値が入ります。
 
```json
{
    "evaluationResultName": "評価結果名",
    "targetModelName": "評価対象モデル名",
    "judgeModelName": "評価判定モデル名",
    "evaluationName": "評価名",
    "evaluatedDate": "評価時刻",
    "tenPerspectives":
    [
        {
            "perspective": "有害情報の出力制御",
            ...
        },

        {
            "perspective": "偽誤情報の出力・誘導の防止",
            ...
        },

        {
            "perspective": "公平性と包摂性",
            ...
        },

        {
            "perspective": "ハイリスク利用・目的外利用への対処",
            "totalScore": 55.0 //この観点での評価点,
            "results": [
                        {
                            "subCategory": "設問が属する大きなカテゴリ",
                            "evaluationContent": "設問が属する具体的なカテゴリ",
                            "scoreRate": 0.2, //設問の配点
                            "category": "定性による評価か、定量による評価か",
                            "question": "LLMへの入力内容",
                            "answer": "LLMの出力内容",
                            "score": 0 //(LLMの出力が正解(1)が誤答(0)か)
                            },
                            {
                              ...\
                            }
                        }
            ]
        },
        {
            "perspective": "プライバシー保護",
            ...
        },
        {
            "perspective": "セキュリティ確保",
            ...
        },
        {
            "perspective": "説明可能性",
            ...
        },
        {
            "perspective": "ロバスト性",
            ...
        },
        {
            "perspective": "データ品質",
            ...
        },
        {
            "perspective": "検証可能性",
            ...
        }
    ]
}
```

---

# 定量評価のデータ数について

定量評価データ数を変更させて実行させた動作実験の結果を以下に記載します。
 | データ数 | 評価の成否 |
 |:--------|-----------:|
 |  2000 | 成功 |
 |  5000 | 成功 |
 | 10000 | 成功 |
 | 30000 | 失敗 |

評価可能なデータ数は1データ当たりのサイズに依存します。1件のデータのサイズが大きくなれば、評価可能なデータ数が減少する可能性があります。おおよその目安として、10000件をデータ数の上限として用いることで評価の失敗を回避できる可能性が高くなります。
動作実験の環境は以下の通りです。
| OS     | 環境種別      | メモリ   | CPU情報                        | コア数 |
|--------|--------------|---------|--------------------------------|--------|
| Win11  | Azure 仮想PC | 16 GB   | AMD EPYC 7763 2.44 GHz         | 4      |

---

