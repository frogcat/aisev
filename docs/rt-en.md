[Japanese version is here.](rt.md)

# Automated Red Teaming Manual

This manual explains the overview and usage procedure of the Automated Red Teaming feature.


# Overview

Automated Red Teaming is a feature designed to support red teaming as described in the "Guide to Red Teaming Methodology on AI Safety". Red teaming is an activity conducted at various phases of AI system development and operation, involving diverse stakeholders such as experts in relevant domains and AI safety and security. The current Automated Red Teaming feature does not automate the entire red teaming process. Instead, it aims to facilitate red teaming more easily than before by automating the parts traditionally performed by humans leveraging their specialized expertise.
The Automated Red Teaming feature evaluates the safety state of an AI system by inputting documents related to the system under evaluation (such as PDFs of operational manuals or specifications) and using adversarial prompts
automatically generated from these input documents. Specifically, the evaluation proceeds in the following
sequence:

1. Extraction of requirements the AI system must adhere to
   - The Automated Red Teaming feature extracts candidate AI safety requirements that the AI system should
adhere to, based on the input documents and the content of the "Guide to Evaluation Perspectives on AI Safety".
2. Generation of adversarial prompts violating extracted requirements
   - If an AI system exhibits behavior that violates the requirements it should adhere to, it can be interpreted as having a safety issue.
   - The Automated Red Teaming feature generates adversarial prompts designed to induce the AI system to
produce outputs that violate these requirements.
3. Evaluating the safety of the AI system using the generated adversarial prompts
   - Input the generated adversarial prompts into the target AI system and collect the AI system's outputs.
   - Compare the collected outputs against the requirements to determine compliance.
   - If outputs exist that do not meet the requirements, it can be interpreted that there is some vulnerability
associated with the corresponding adversarial prompt.


# Setting Up Automated Red Teaming

Automated red teaming is included in the AI Safety Evaluation Environment, but its use as an accompanying tool is optional, requiring additional setup work.


## Setup Procedure

To use the Automated Red Teaming feature, after setting up the AI Safety Evaluation Environment, the following setup steps must be completed beforehand.

1. Open a terminal and navigate to the `llm-evaluation-system` folder within your evaluation environment directory using the 'cd' command.
   ```
   cd llm-evaluation-system/
   ```

2. Create a Docker container for the Evaluation Environment Integration service by executing the following command on the terminal.
   ```
   docker compose build
   ```

3. Start the created Docker container for the Evaluation Environment Integration service by executing the following command on the terminal. It will start with the container name`manager-backend`. If the `manager-backend` container is not running, You cannot transition to the automatic red teaming screen from the evaluation environment.
   ```
   docker compose up
   ```

4. On the evaluation environment home screen, click the **Automated Red Teaming Tool** button. 

5. The initial screen for the Automated Red Teaming will be displayed. The first time You access it, screen transitions may take time. If the initial screen for the Automated Red Teaming does not display, please reload the page.



# Operating Procedures

If You need to return to a previous screen during the procedure, please use the step navigation. Closing your browser during evaluation will not save your data. To save evaluation results, click the Export button on the evaluation results
screen and download them in HTML or CSV format.
1. **① LLM Settings** screen: On the initial screen of the Automated Red Teaming Tool, click **Open LLM Settings Modal**.
2. On the "LLM Settings" screen, enter the required items for each of the following: "Requirement Generation AI", "Adversarial Prompt Generation AI", "Response Evaluation AI" and "Target AI."
   - "Target AI" refers to the AI model/system being evaluated. The others are AI models used as tools during the Automated Red Teaming process.
   - While various AI models can be used for "Requirement Generation AI", "Adversarial Prompt Generation AI", and "Response Evaluation AI", AISI has developed the Automated Red Teaming Tool based on OpenAI's GPT-4o model as the standard. If evaluation issues arise when using other AI models, please consider utilizing gpt-4o.




3. Please click the **Save** button.
4. **② Document Upload** screen: Upload files as needed.
   - The documents entered here should be specifications, rules, or constraints that the AI model/AI system under evaluation must follow, such as the AI model/AI system's specification documents or related operational manuals.
   - You can upload any PDF file. However, if You upload a PDF file that is difficult to extract text from, such as one containing many images, the subsequent step of generating requirements may not produce valid requirements.
— If a document with a large amount of text is input, the text will be summarized and shortened before
generating requirements. However, this may result in a significant gap between user expectations and the generated requirements. If there are sections You wish to prioritize for automated red teaming, consider creating an excerpted PDF version before inputting it.
5. Click the **Proceed to the Next Step** button.
6. **③ Requirement Generation** screen: Please configure the following.
   - **Purpose of Target AI:** Describe the purpose of the target AI here. For example: "This LLM will be used as a customer support chatbot to provide product information and answer general questions." If You uploaded a document on the previous screen and wish to use it, You can omit entering the purpose.
   - **Number of Requirements to Generate:** Set any number. Default is 10, minimum 1, maximum 100.
   - If You have not uploaded a file, uncheck the "Use Uploaded Document" option.
7. Click the **Generate Requirements** button.
8. Once requirements are generated, click the **Proceed to the Next Step** button.
9. **④ Generate Adversarial Prompts** screen: Set the "Number of Prompts to Generate Per Requirement" to any
desired number. However, setting it to 3 or higher often results in responses being rejected. The default is 3,
minimum 1, maximum 10.
10. Click the **Generate Adversarial Prompt** button.
11. Once the generated prompt is displayed, please click the  **Proceed to the Next Step** button.
12. **⑤ Execute Evaluation** screen: Click the **Execute Evaluation** button.
13. A fter evaluation is complete, click the **Display Evaluation Results** button.
14. On the "Evaluation Results" screen, please confirm the evaluation results.

