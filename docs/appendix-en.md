[Japanese version is here.](appendix.md)

# Appendix

The appendix contains supplementary information to the user manual.

---

# Supported Quantitative Evaluation Dataset Formats for Registration in the AI Safety Evaluation Environment

## Description

The quantitative evaluation datasets that can be registered in the AI Safety Evaluation Environment's Dataset Registration screen are in CSV format. There are three methods for evaluating AI output results.
  1. **Requirement Satisfaction:** Determines whether the AI output meets specific safety requirements.
  2. **Multiple-Choice Selection:** Evaluates whether the AI can correctly select the right answer from multiple options.
  3. **Semantic Equivalence:** Compares the AI output with an expected answer to determine if they are semantically equivalent.

The evaluation method to be applied is determined by the value in the scorer column within the dataset. Furthermore, the required columns also differ depending on the evaluation method.


## Details of Required Columns

The evaluation method is determined by the value in the scorer column assigned to the data, and the required columns also change accordingly.
Any columns other than the required will be ignored, even if they exist within the data.
- scorer=requirement: Evaluates whether the output satisfies a given requirement.
  - Required column(s): ID, text, ten_perspective, requirement(output must fulfill)
- scorer=multiplechoice: Evaluates from multiple choices. 
  - Required column(s): ID, text, ten_perspective, ans0, ans1, ...(choice), output (correct answer choice)
- scorer=model_graded_qa: Evaluates whether the output is semantically equivalent to the expected answer.  
  - Required column(s): ID, text, ten_perspective, output (expected answer)

## Example Data Formats

  - Requirements (scorer=requirement)
    | id | ten_perspective                | text         | requirement                | scorer     |
    |----|-------------------------------|--------------|----------------------------|------------|
    | 1  | Mitigation high-risk and unauthorized use | Input to AI | Requirement for AI output | requirement |
  - Multiple-Choice (scorer=multiplechoice)
    | id | ten_perspective      | text         | ans0      | ans1      | ans2      | ans3      | output   | scorer        |
    |----|----------------------|--------------|-----------|-----------|-----------|-----------|----------|--------------|
    | 1  | Fairness and Inclusivity  | Input to AI | Option A  | Option B  | Option C  | Option D  | Expected answer(alphabet of choice) | multiplechoice |
  - In the case of semantic equivalence (no scorer specified or model_graded_qa)
    | id | ten_perspective         | text         | output   |
    |----|------------------------|--------------|----------|
    | 1  | Control of Toxic Output    | Input to AI | Expected answer |

---
# API Specifications for AI Model Registration

AI models/AI systems registered in the AI Model Registration and Update Screen of the AI Safety Evaluation Environment must comply with the following API specifications.

   - These API specifications are compatible with the OpenAI API.

## Endpoint

  **`{base_url}/chat/completions`**
    (Here, `base url` is any arbitrary URL)

## API Key-Based Authentication

  **`Authorization: Bearer <api_key>`**
    header

## request
  Below is an example request.
  Please refer to the documentation of the specific API service being used to verify the required fields and appropriate parameter values.


  ```json
  {
    "model": "gpt-4o-mini",
    "messages": [
      { "role": "system", "content": "You are a capable assistant." },
      { "role": "user", "content": "Tell me the weather in Tokyo for tomorrow." }
    ],
    "temperature": 0.7,
    "max_tokens": 150,
    "top_p": 1.0,
    "n": 1,
    "stream": false,
    "stop": null
  }
  ```

  - **model**: [ Required ] The name of the model to use (`gpt-4o-mini`／`gpt-4o`／`gpt-3.5-turbo`／ etc)
  - **messages**: [ Requred ] A list of message objects representing the conversation so far. Each object must include.
    - **role**: `system`／`user`／`assistant`
    - **content**: The text content of the message.
  - **temperature**: [ Optional, default: 1 ] Controls the randomness of the output. Range: 0.0 to 2.0
  - **max_tokens**: [ Optional, no explicit default ] The maximum number of tokens to generate in the completion.
  - **top_p**: [ Optional, default: 1 ] Controls nucleus sampling (probability mass). Range: 0.0 to 1.0.
  - **n**: [ Optional, default: 1 ] The number of completion choices to generate for each input.
  - **stream**: [ Optional, default: false ] Whether to stream partial responses.
  - **stop**: [ Optional, default: null ] One or more sequences where the API will stop generating further tokens. Can be a string or an array of strings.

## response
  The following is an example of a response.

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
          "content": "The forecast for Tokyo tomorrow is partly cloudy with sunny intervals, with a high temperature of 28°C and a low of 20°C."
        },
        "finish_reason": "stop"
      }
    ]
  }
  ```

   - **id:** A unique identifier for the completion object.
  - **object:** Type of the object. `"chat.completion"`.
  - **created:** UNIX timestamp (in seconds) indicating when the response was generated.
  - **model:** The name of the model actually used to generate the response.
  - **usage:** Token usage details
    - **prompt_tokens:** Number of tokens used in the input prompt.
    - **completion_tokens:** Number of tokens used in the generated response.
    - **total_tokens:** Total number of tokens consumed.
  - **choices:** A list of generated responses
    - **index:** Index of the response (starting from 0).
    - **message:** The generated message content
      - **role:** Always`"assistant"`
      - **content:** The generated text response
    - **finish_reason:** The reason why generation stopped (e.g.,`"stop"`／`"length"`).


## Example of How to Call

  ```bash
  curl https://api.openai.com/v1/chat/completions \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d '{
      "model": "gpt-4o-mini",
      "messages": [
        {"role": "system",  "content": "You are a capable assestant."},
        {"role": "user",    "content": "Please tell me a pasta recipe."}
      ],
      "temperature": 0.5,
      "max_tokens": 200,
      "n": 1
    }'

  ```

## Example definition for evaluating AI deployed in a local environment using the combination of LM Studio and open-ai/gpt-oss-20b

As an example, here is how to register AI information for evaluation using this tool, specifically for AI deployed locally using the combination of LM Studio and open-ai/gpt-oss-20b.

  1. Install LM Studio as a Developer, start the server from the Developer screen, and make it ready to accept API requests.
     - For example, if the IP address is "192.168.10.13" and the port is "1234", the base URL becomes  "http://192.168.10.13:1234/v1/".
     - For detailed instructions on using LM Studio, refer to the LM Studio website.
  2. On the "AI Model Registration and Update" screen, click the "AI Information Update" button to update the AI model as follows:
     - **AI Information Label:** Enter any identifying name. (Example: ai_local_gpt-oss-20b)
     - **Model Name:** If you installed gpt-oss-20b using the standard method during LM Studio installation, it will be "openai/gpt-oss-20b".
     - **URL:** Enter the base URL identified from the LM Studio settings above. (Example: http://192.168.10.13:1234/v1/)
     - **API Key:** Although no API key is used in this case, enter just "Key".
  3. After completing all entries, click the "Register" button.
     - Upon successful registration, a completion message will appear.
  4. Going forward, you can designate the registered AI information as an evaluation target by specifying it as the target AI information in the evaluator's screen.

---

# Contents of evaluation result JSON file

When JSON export is executed on the Evaluation Results Detail screen of the AI Safety Evaluation Environment, the JSON file containing the evaluation results will be output in the following structure.
The subCategory, evaluationContent, and scoreRate fields in results will only contain values when using the AISI preset evaluation dataset.

```json
{
    "evaluationResultName": "Evaluation Result Name",
    "targetModelName": "Evaluation Target Model Name",
    "judgeModelName": "Evaluation Judgment Model Name",
    "evaluationName": "Evaluation Name",
    "evaluatedDate": "Evaluated Time",
    "tenPerspectives":
    [
        {
            "perspective": "Output control of harmful information",
            ...
        },

        {
            "perspective": "Prevention of output and guidance of false information",
            ...
        },

        {
            "perspective": "Fairness and inclusivity",
            ...
        },

        {
            "perspective": "Addressing high-risk use and misuse",
            "totalScore": 55.0 //Score for this perspective,
            "results": [
                        {
                            "subCategory": "The larger category to which the question belongs",
                            "evaluationContent": "Specific category to which the question belongs",
                            "scoreRate": 0.2, //Question weighting
                            "category": "Qualitative or quantitative evaluation",
                            "question": "Input content to LLM",
                            "answer": "LLM output",
                            "score": 0 //(LLM output is correct (1) or incorrect (0))
                            },
                            {
                              ...\
                            }
                        }
            ]
        },
        {
            "perspective": "Privacy protection",
            ...
        },
        {
            "perspective": "Security",
            ...
        },
        {
            "perspective": "Explainability ",
            ...
        },
        {
            "perspective": "Robustness",
            ...
        },
        {
            "perspective": "Data quality",
            ...
        },
        {
            "perspective": "Verifiability",
            ...
        }

    ]
}
```

<div style="page-break-before:always"></div>

# Regarding the number of quantitative evaluation data

The results of the operational experiments conducted after changing the number of quantitative evaluation data  are described below.
 | Number of Data | Success or Failure of Evaluation |
 |:--------|-----------:|
 |  2000 | Success |
 |  5000 | Success |
 | 10000 | Success |
 | 30000 | Failure |

The number of evaluable data depends on the size of each data.
As the size of a single data increases, the number of evaluable data may decrease.
As a rough estimation, setting the upper limit of the data number to 10,000 possibly decreases the likelihood of evaluation failures.
The operational test environment is as follows:

| OS     | Environment type      | Memory   | CPU Information      | Number of cores |
|--------|--------------|---------|--------------------------------|--------|
| Win11  | Azure Virtual PC | 16 GB   | AMD EPYC 7763 2.44 GHz         | 4      |
