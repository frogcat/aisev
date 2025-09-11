[Japanese version is here.](rt.md)

# Automated Red Teaming Manual

This manual explains the overview and usage procedure of the Automated Red Teaming feature.


# Overview

Automated Red Teaming is a feature designed to support red teaming as described in the "Guide to Red Teaming Methodology on AI Safety". Red teaming is an activity conducted during various phases of AI system development and operation, involving diverse stakeholders such as experts in the AI system under evaluation or the tasks it handles, as well as specialists in AI safety and security.The current automated red teaming feature does not automate the entire red teaming process. Instead, it is designed to automate certain parts, making red teaming easier to conduct than before.
The automated red teaming function evaluates the safety state of an AI system by inputting documents related to the system under evaluation (such as PDFs of operational manuals or specifications) and using adversarial prompts
automatically generated from these input documents. Specifically, the evaluation proceeds in the following
sequence:

1. Extraction of requirements the AI system must adhere to
   - The automated red teaming function extracts candidate AI safety requirements that the AI system should
adhere to, based on the input documents and the content of the "Guide to Evaluation Perspectives on AI Safety".
2. Generation of adversarial prompts violating extracted requirements
   - If an AI system exhibits behavior that violates the requirements it should adhere to, it can be interpreted as having a safety issue.
   - The automated red teaming function generates adversarial prompts designed to induce the AI system to
produce outputs that violate these requirements.
3. Evaluating the safety of the AI system using the generated adversarial prompts
   - Input the generated adversarial prompts into the target AI system and collect the AI system's outputs.
   - Compare the collected outputs against the requirements to determine compliance.
   - If outputs exist that do not meet the requirements, it can be interpreted that there is some vulnerability
associated with the corresponding adversarial prompt.


# Setting Up Automated Red Teaming

Automated red teaming is included in the AI Safety Evaluation Environment, but it is a highly independent tool and its use is optional, requiring additional setup work.

## Setup Procedure

To use the automated red teaming feature, the following setup steps must be completed beforehand.

1. Open a terminal and navigate to the `llm-evaluation-system` folder within your evaluation environment directory.
   ```
   cd llm-evaluation-system/
   ```

2. Create a Docker container for the Evaluation Environment Integration service.
   ```
   docker compose build
   ```

3. Start the created Docker container for the Evaluation Environment Integration service. It will start with the container name`manager-backend`. If the `manager-backend` container is not running, you cannot transition to the automatic red teaming screen from the evaluation environment.
   ```
   docker compose up
   ```

4. On the evaluation environment home screen, press the **Automated Red Teaming Tool** button. The first time you
access it, screen transitions may take time. If the page does not display, please reload the page.


5. The initial screen for Automated Red Teaming will be displayed.


# Operation Manual



