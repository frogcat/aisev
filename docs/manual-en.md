[Japanese version is here.](manual.md)

# User Manual Overview

This document provides step-by-step instructions for using the AI Safety Evaluation Environment. Below are the usage instructions for cases where the AISI Preset Evaluation Dataset, a standard evaluation dataset, is used as an example.

# Procedures for AI Safety Evaluation Using the AISI Preset Evaluation Dataset

This document explains the procedure for AI safety evaluation using the AISI Preset Evaluation Dataset (prototype version).

## AI Safety Evaluation Environment Setup

Please set up the AI Safety Evaluation Environment on the corresponding operating environment using the following as a reference.

### Runtime Environment

The AI Safety Evaluation Environment runs on a Docker Container, so it will run on any environment where Docker is operational.
The following are the confirmed operating environments. While it may run on other environments, AISI cannot guarantee its operation.

   - **OS:** Windows 11, MacOS(Sequoia)
   - **Python:** Python 3.12.7
   - **Docker Environment/Compatible Environment:** Rancher Desktop 1.19.3

### Preparing the runtime environment

Refer to the official websites for Python and Docker to set up the operating environment. Note that Rancher Desktop should be downloaded from the following URL for the corresponding OS and installed with all default settings.
- [https://rancherdesktop.io/](https://rancherdesktop.io/)

Before setting up the AI Safety Evaluation Environment, Rancher Desktop should be launched.

### Downloading the AI Safety Evaluation Environment

Open the terminal (for Windows, PowerShell) and execute the following command to download the AI Safety Evaluation Environment.

   ```
    git clone https://github.com/Japan-AISI/aisev.git
   ```
   - If the git command is unavailable, you can also download the entire source code as a zip file. Click “Code” in the upper-right corner of the file list on the GitHub repository's main page, then download the ZIP file from “Download ZIP”.

<div style="page-break-before:always"></div>

### Evaluation procedure using the AISI preset evaluation dataset

1. [Only for re-setup] If any of the following containers are running, stop them and delete all containers
    - postgresdb container
    - frontend container
    - fastapi container
    - init-db container
    - manager-backend container (* May exist if the Automated Red Teaming was used prior to the re-setup)
    - llm-evaluation-system-automated-rt-app-1 container (* May exist if the Automated Red Teaming was used prior to the re-setup)
    - llm-eval-(number) container (e.g., llm-eval-18001) (* May exist if the Automated Red Teaming was used prior to the re-setup)

2. [First time only] Please extract the downloaded AI Safety Evaluation Environment source code package to any folder of your choice.

3. Move to the folder where you extracted the source code in the terminal, then run the following command to create the container.

   ```
   docker compose build
   ```
   After completion, please execute the following command to start the created container.
   ```
   docker compose up
   ```
    - The folder where you execute the docker compose command is the directory containing frontend, backend, llm-evaluation-system, docker-compose.yml, etc.
    - After completing the initial setup, subsequent runs should start from this step 3 `docker compose up`.
    - Due to network issues or other problems, `docker compose build` or `docker compose up` may fail even if there are no issues with the source code and procedure. If it fails, please retry after a few minutes.
    - If `docker compose up` executes correctly and outputs `fastapi | INFO: Application startup complete.` in the terminal, the AI Safety Evaluation Environment is running. After startup, logs from the evaluation environment will appear in the terminal window where the command was executed. Note that closing the terminal window or pressing Ctrl-C will stop the AI Safety Evaluation Environment.

4. Open your browser and go to [http://localhost:5173](http://localhost:5173). The AI Safety Evaluation Environment home screen will appear.
    - From this point onward, all evaluation-related operations will be performed in the browser. While terminal operations will no longer be necessary, we recommend keeping the terminal open to periodically check the displayed information, as relevant details will be updated throughout the evaluation process

5. [First time only] Click the **Initialize DB** button. This initializes the database used internally by the AI Safety Evaluation Environment and loads the AISI preset evaluation dataset.
    - **If you are already using the AI Safety Evaluation Environment and do not need to initialize the database, please do not click the **Initialize DB** button. If pressed, all data generated from previous usage will be permanently deleted.**

6. [First time only] Move from the **Initial Screen for Evaluation Definers Screen** to the **Evaluation Definition Management Screen**, enter an arbitrary evaluation content definition name (e.g., aisi_preset), check **Use AISI Preset** for all 10 criteria, and click the **Register Evaluation Definition** button and return to the **Initial Screen for Evaluation Definers** screen.

7. [First time only] Move from the **Initial Screen for Evaluation Definers Screen** to the **AI Model Registration and Update Screen**, enter an arbitrary AI Information Label (e.g., my_ai_info_1), enter the AI Model Name (e.g., gpt-5-mini), URL (e.g., https://api.openai.com/v1/), API key (e.g., sk-********************), then click the **Register** button. If using two or more AI information, register each one separately. After registering all AI information, return to the Home screen.

8. On the home screen, clicking the **Initial Screen for Evaluators Screen** button will navigate you to the **Initial Screen for Evaluators** screen. From there, select the AI information to be evaluated, the AI information for evaluation judgment, and the evaluation content definition (registered by specifying an AISI preset), enter an arbitrary evaluation identification label (e.g., eval_001), and click the **Execute Evaluation** button to transition to the **Evaluation Execution Screen**.

9. Evaluation Execution Screen: Please conduct both quantitative and qualitative evaluations as follows. After completing both evaluations, the **Display Evaluation Results** button will appear at the bottom of the screen. Please click it.
    - **Quantitative Evaluation:** Since this runs in the background, please wait until the screen display changes from **Running** to **Completed**. Even while waiting, you can enter responses for the next qualitative evaluation.
    - **Qualitative Evaluation:** For each verification item displayed on the screen, select one of the four options: **No Problem** / **Partially Problematic** / **Problematic** / **Not Applicable**. Since **Not Applicable** is set as the default value, verification items that are not relevant to the AI system under evaluation should remain unchanged. After answering all items, click the **Register Qualitative Results** button.
    - Clicking the **Display Evaluation Results** button will take you to the Evaluation Results Summary screen.

10. Evaluation Results Summary Screen: Review the summary of evaluation results using radar charts and other visualizations. To view detailed results, click the **Go to Detail Screen** button to proceed to the **Evaluation Results Detail (By Perspective)**.

11. Evaluation Results Detail (By Perspective) Screen: A table displaying evaluation results by perspective is shown. If you need to output the file, click the **Create Report** button to navigate to the **Evaluation Result Report** screen. To save as a JSON file, click the **Export as JSON** button.

12. Evaluation Result Report Screen: The report content, consisting of a radar chart and detailed results, is displayed. If you need to output the file, click the **Export PDF** button to output the report as a PDF file.


<div style="page-break-before: always"></div>

# Screen-by-Screen Guide to the AI Safety Evaluation Tool

This section provides an overview of each screen in the AI Safety Evaluation Tool and offers detailed instructions on how to use them.

---

## Function Selection(Home Screen)

**【Figure: Function Selection(Home Screen)】**  
![Function Selection](images-en/Home-1.png)

- **Function Description:**  
  This screen functions as a selection interface, directing users to either the "Initial Screen for Evaluation Definers" or the "Initial Screen for Evaluators", based on tool user’s assigned roles. Additionally, a navigation button is available for launching the separate "Automated Red Teaming Tool". For detailed information on the Automated Red Teaming Tool, refer to [Automated Red Teaming Manual](rt-en.md). At the top of the screen, a list of screen transitions labeled "Home," a button to switch languages, and the title of this service are displayed.<br>
(*) Clicking the "Initrialize DB" button will initialize all saved databases. Please be careful not to click this button unintentionally.


- **Main Operation Steps:**
  1. **Select a Function Based on User Roles:** Click either the "Initial Screen for Evaluation Definers" or the "Initial Screen for Evaluators", button, depending on user’s assigned role.
  2. **Screen Transition:** The system navigates to the corresponding initial screen based on the selected role.
  3. **Launch the Automated Red Teaming Tool:** Click the "Automated Red Teaming Tool" button to move to the Automated Red Teaming Tool screen. If the screen transition fails, an alert will be displayed. For more information, refer to [Automated Red Teaming Manual](rt-en.md).
  4. **Language Switching:** Use the "Japanese/English" toggle button located at the top of the screen to switch the display language.

---

## Initial Screen for Evaluation Definers

**【Figure: Initial Screen for Evaluation Definers】**
![Initial Screen for Evaluators](images-en/Initial_Screen_for_Evaluators-3.png)

- **Function Description:**  
  This screen serves as the main interface for evaluation definers, providing access to a range of settings and management functions necessary for conducting AI safety evaluations.

- **Main Operation Steps:**
  1. Click the button corresponding to the desired function to navigate to the appropriate management screen:
     - **Dataset Registration Screen:** Opens the screen for registering and managing datasets used in quantitative evaluations
     - **Qualitative Evaluation Question Creation Screen:** Opens the screen for creating and managing questions used in qualitative evaluations.
     - **AI Model Registration and Update Screen:** Opens the screen for registering and managing AI model information.
     - **Evaluation Definition Management Screen:** Opens the screen for defining and managing evaluation content and structures.
  2. Various settings, registration, and editing operations are performed on the management screen corresponding to the selected button.

---

## Dataset Registration Screen

**【Figure: Dataset Registration Screen】**
![Dataset Registration](images-en/Dataset_Registration-4.png)

- **Function Description:**  
  This screen is used to register and manage datasets for use in quantitative evaluations. Supported file formats include CSV and Parquet. For the columns required for the data to be registered, refer to [Appendix](appendix-en.md). Please use UTF-8 character encoding.

- **Main Operation Steps:**

  1. **Enter Dataset Name:** Enter any name in the "Dataset Name" field. Since the entered dataset name will appear in later processes, it is recommended to use a descriptive name that clearly identifies the dataset. 
  2. **Upload File:** Select the file to be registered at the "Upload CSV file" field. Although it states "CSV files" in the field, Parquet format datasets can also be uploaded as mentioned above. However, please note that multiple files cannot be registered at once. <br>(*) If your browser's language setting is Japanese, "ファイルを選択" will be displayed. In this case, it will not be changed to English with this tool.
  3. **Input Perspective Information:** If the evaluation perspective information is not included in the columns of the input data, you can enter the evaluation perspective information in this field. Check "Input Perspective Information" to display a list of perspective, allowing you to select your desired evaluation perspective. For details on the format of the input data columns, please refer to [Appendix](appendix-en.md).

![Aspect_Information](images-en/Aspect_Information-5.png)
  4. **Click the Register Button:** Check all entered information, then click the "Register" button to complete the dataset registration.


---

## Qualitative Evaluation Question Creation Screen

**【Figure: Question List Screen】**
![Question List](images-en/Question_List-6.png)
**【Figure: Question_Creation Screen】**
![Question_Creation](images-en/Question_Creation-7.png)

- **Function Description:**  
  The Qualitative Evaluation Question Creation Screen consists of two primary components:

  - **Question List:** 	Allows users to view, select, and delete existing qualitative evaluation questions.
  - **Question Creation:** Enables users to create and register new qualitative evaluation questions.

- **Main Operation Steps: Question List:**

  1. **Review Existing Questions:** Browse the list of previously created qualitative evaluation questions displayed on the screen.
  2. **Navigate the List:** If more than six items exist, use the "Next" and "Previous" buttons to scroll through additional pages. 
  3. **Delete a Question (Optional):** To delete a qualitative evaluation question, select the qualitative evaluation question set name and click the "Delete" button.

- **Main Operation Steps: Question Creation**
  1. **Enter the Question Name:** Input a name for the qualitative evaluation item set in the "Question Name" field.
  2. **Select an Evaluation Perspective:** Choose the appropriate evaluation perspective from the dropdown menu. 
  3. **Add Question Content:** Enter the question in the"Question Content" field. To add multiple questions, click the "+Add" button for each additional question.
  4. **Register the Qualitative Evaluation Question:** Check the qualitative evaluation questions you entered and click the "Create" button. A message indicating that creation is complete will be displayed.

---

## AI Model Registration and Update Screen

**【Figure: AI Information List Screen】**
![AI Information List](images-en/AI_Information_List-9.png)
**【Figure: AI Information Registration Screen（New Entry）】**
![AI Information Registration Screen（New Entry）](images-en/AI_Information_New_Entry-10.png)
**【Figure: AI Information Updated Screen (Update)】**
![AI Information Updated Screen (Update)](images-en/AI_Information_Update-11.png)

- **Function Description:**  
  The AI Model Registration and Update Screen consists of two primary components.

  - **AI Information List:** Allows users to examine, select, and delete registered AI models.
  - **AI Information Registration / Update:** Enables users to register new AI models or edit and update existing ones.

- **Main Operation Steps: AI Information List**

  1. **Review Registered AI Models:** Examine the list of AI models currently registered in the system. For security reasons, only the first five characters of the API key are displayed; the remaining characters are masked with asterisks (*).
  2. **Navigate the List:** If more than six models are registered, use the "Next" and "Previous"  buttons to browse through additional entries. 
  3. **Delete or Update a Model:** If needed, select a model from the list to perform a delete or update operation.	

- **Main Operation Steps: AI Information Registration / Update**
  1. **Select the Operation Mode:** To register a new AI model, click the "AI Information Registration" button and to update an AI model, click the "AI Information Updated" button to display the respective screen.
  2. **Register a New AI Model:** When registering a new AI model, fill in the following fields.
     - **AI Information Label:** Enter the display name to be used within this service. Duplicate labels that match already registered names are not allowed.
     - **Model Name:** Enter the name of the AI model to be registered. If using a public LLM, use its official name.
     - **URL:** Enter the URL. For example, with OpenAI APIs, input up to :<br>
        - `https://api.openai.com/v1/`
     - **API Key:** Enter the appropriate API key in the API Key field. 
  3. **Updating an Existing AI Model:** When updating, follow next steps.
     - **Update the Target AI Information Label:** Choose the name of the AI model to be updated from the dropdown list. Once selected, the corresponding fields will be auto filled. Modify any necessary information before proceeding.
  4. **Complete the Operation:** After confirming all inputs, click either the "Register" or "Update" button as appropriate.
     - If the operation is successful, a confirmation message will appear.

---

## Evaluation Definition Management Screen
**【Figure: Evaluation Definition List Screen】**
![Evaluation Definition List](images-en/Evaluation_Definition_List-14.png)
**【Figure: Evaluation Definition Creation Screen】**
![Evaluation Definition Creation](images-en/Evaluation_Definition_Registration-15.png)
**【Figure: Evaluation Definition Creation Detail Screen】**
![Evaluation Definition Creation Detail](images-en/Evaluation_Definition_Registration-15-2.png)

- **Function Description:**  
  The Evaluation Definition Management screen consists of two main interfaces.

  - **Evaluation Definition List Screen:** Allows users to examine, select, and delete existing evaluation definitions.
  - **Evaluation Definition Creation Screen:** Enables users to create new evaluation definitions or edit and update existing ones.

- **Main Operation Steps: Evaluation Definition List**

  1. **Review Registered Evaluation Definitions:** Examine the list of registered evaluation definition names displayed on the screen.
  2. **Navigate the List:** If more than six definitions are present, use the "Next" and "Previous" buttons to scroll through additional entries.
  3. **Delete an Evaluation Definition (Optional):** To delete a definition, select a definition from the list and click the "Delete Definition" button. 
  4. Once the evaluation definition is registered, the registered content cannot be confirmed.


- **Main Operation Steps: Evaluation Definition Registration**
  1. In the Evaluation Definition Name field, enter a name for the new evaluation definition. 
  2. Open the dropdown menu for each evaluation perspectives to be defined and enter the following items.
     - **Use AISI Preset:** In case of using the AISI preset for evaluation, check the "Use AISI Preset" check box. When using an AISI preset, the Quantitative or Qualitative Evaluation cannot be used.
     - **Quantitative Evaluation:** To enable quantitative evaluation, check the "Quantitative Evaluation" check box and select one or more datasets. Multiple datasets can be selected by holding the Shift or Ctrl key while clicking.
     - 	**Qualitative Evaluation:** To enable qualitative evaluation, check the "Qualitative Evaluation" check box and select one or more datasets. Multiple datasets can be selected by holding the Shift or Ctrl key while clicking. 
     - 	**Quantitative / Qualitative Ratio:** If both evaluation types are enabled, assign weights using the "Quantitative Evaluation Ratio" and "Qualitative Evaluation Ratio" fields. Entering one weight will automatically adjust the other proportionally to ensure a total of 100%.
  3. After configuring all necessary settings for each evaluation aspect, click the "Register Evaluation Definition" button. If registration is successful, a confirmation message will appear.
---

## Initial Screen for Evaluators

**【Figure: Initial Screen for Evaluators】**
![Initial Screen for Evaluators](images-en/Initial_Screen_for_Assessors-18.png)

- **Function Description:**  
  This screen serves as the main interface for evaluators, providing access to essential functions such as configuring evaluation settings, executing evaluation tasks, and reviewing results.
- **Main Operation Steps:**
  1. On the Initial Screen for Evaluators Screen, set the following parameters.
     - **AI Information of Target AI:** From the dropdown menu, select the AI information to be evaluated for the AI Safety Evaluation. Typically, the evaluation targets are AI models/AI systems used in business operations, and corresponding AI information should be selected. It is also possible to evaluate commonly used AI models such as OpenAI's gpt-5 or gpt-5-mini.
     - **AI Information of judge AI:** From the dropdown menu, select the AI information to be used for evaluation in the AI Safety Evaluation. For evaluation purposes, it is desirable to use AI models that are commonly employed and provide a reasonably high level of performance, such as OpenAI's gpt-5 or gpt-5-mini. Select the AI information corresponding to these models.
     - **Evaluation Definition:** Choose an evaluation definition from the dropdown list. Definitions available here are those configured on the "Evaluation Definition Creation"  screen. 
     - **Evaluation Name:** Enter a label to identify the evaluation. This label will appear when viewing results, so it is recommended to use a descriptive name that clearly reflects the evaluation content.
  2. After configuring all parameters, click the "Execute Evaluation" button to start the evaluation. The system will automatically transition to the Evaluation Execution Screen.
  3. If you click the "AI Model Registration and  Update Screen" button while configuring settings, you will be redirected to the AI Information Registration Screen, where you can register or update AI models.
  4. To review results from previous evaluations, click the "View Evaluation Results" button. This will take you to the Evaluation Results Summary Screen, where past results can be viewed and analyzed.


---

## Evaluation Execution Screen

**【Figure: Evaluation Execution Screen】**  
![Evaluation Execution Screen](images-en/Evaluation_Execution-19.png)

- **Function Description:**  
  This screen is displayed after the evaluator initiates the evaluation process. It allows the evaluator to monitor the progress of quantitative evaluations and to manually input results for qualitative evaluations.
- **Main Operation Steps:**
  1. The progress of quantitative evaluations is displayed as "Running" while the evaluation is being conducted, and as "Completed" once the evaluation is complete.
  2. The qualitative evaluation items defined in the selected evaluation configuration will be displayed. For each item, select the most appropriate response based on the item’s content.
  3. After selecting responses for all items, click the "Register Qualitative Results" button to submit the qualitative evaluation results.
  4. Once both the quantitative evaluation is completed and the qualitative results have been registered, the "Display Evaluation Results" button will become visible at the bottom of the screen.
  5. Click the "Display Evaluation Results" button to navigate to the Evaluation Results Summary Screen, where you can review the evaluation outcomes.

---

## Evaluation Results Summary Screen

**【Figure: Evaluation Results Summary – Radar Chart】**
![Radar Chart](images-en/Radar_Chart-21.png)
**【Figure: Evaluation Results Summary – "Go to Detail Screen" Button】**
![Go to Detail](images-en/Go_to_Detail-22.png)
**【Figure: Evaluation Results Summary – Evaluation Result List Screen】**
![Result List](images-en/Evaluation_Result-23.png)

- **Function Description:**  
  　This screen displays the results of both quantitative and qualitative evaluations. It consists of three main sections.
  - **Top Section:** A radar chart visualizes the evaluation results across the ten evaluation perspectives defined in the Guide to Evaluation Perspectives on AI Safety. 
  - **Middle Section:** This section shows the detailed content of the current evaluation, including quantitative scores and qualitative judgments.
  - **Bottom Section:** A table displays the results of previous evaluations for reference and comparison.

- **Main Operation Steps: Radar Chart Display**

  1. **Select Evaluation Results**
     - Select the evaluation results to be viewed from the evaluation results list. Up to three results can be displayed at a time.
  2. **Display the Radar Chart**
     - Once an evaluation result is selected from the list, a radar chart will appear at the top of the screen, visualizing the selected data.
  3. **Compare Results**
     - If multiple evaluation results are selected, their radar chart plots will be overlaid, allowing for visual comparison of the results across different evaluation perspectives.

- **Main Operation Steps: Displaying Evaluation Content**
  1. **Select Evaluation Results**
     - Select the evaluation results to be viewed from the evaluation results list. Up to three results can be displayed at a time.
  2. **Display Evaluation Content**
     - The content of the selected evaluation(s) will be displayed in the middle section of the screen. If multiple results are selected, each result will appear under a separate button, labeled with its Evaluation Identifier Label.
  3. **Review Evaluation Content**
     - Click a button to view the evaluation content associated with that specific identifier. This allows for quick navigation between multiple evaluation records.
- **Main Operation Steps: Viewing Detailed Evaluation Results**
  1. **Select an Evaluation Result from the list**
     - From the Evaluation Results List, choose the result you want to review.
  2. **Click the"Go to Detail Screen"Button**
     - In the middle section of the screen, click the "Go to Detail Screen" button associated with the selected evaluation result.
  3. **Navigate to the Detailed Evaluation Results Screen**
     - Clicking the button will take you to the "Evaluation Results Detail (By Perspective)" screen, where you can review the evaluation data in greater depth for each perspective.


---

## Evaluation Results Detail (By Perspective) Screen

**【Figure: Evaluation Results Detail (By Perspective) Screen】**
![Evaluation Results Detail (By Perspective) Screen](images-en/Result_Detail-24.png)

- **Function Description:**  
  This screen displays detailed evaluation results for each of the ten evaluation perspectives defined in the Guide to Evaluation Perspectives on AI Safety.
Each category represents a specific perspective used to assess the AI system’s performance.
- **Main Operation Steps:**
  1. For each of the ten evaluation perspectives, click the dropdown menu to expand and view detailed evaluation results, including the following items:
     - **Sub Category:** Displayed only when an AISI preset is used in the evaluation definition. Shows the evaluation category defined in the AISI preset. 
     - **Evaluation Content:** Displayed only when an AISI preset is used. For each evaluation perspective, this indicates what content is being evaluated. When the classification is quantitative evaluation, the displayed evaluation content is compared with the responses from the target AI model/AI system to evaluate validity, and the resulting evaluation outcome becomes the score. When the classification is qualitative evaluation, the content equivalent to the evaluation perspective is displayed.
     - **Category:** Indicates whether the evaluation item is part of quantitative or qualitative evaluation.
     - **Question:** If the classification is quantitative evaluation, the evaluation content used as input to the AI model/AI system being evaluated is displayed. If the classification is qualitative evaluation, the evaluation items answered on the evaluation execution screen are displayed.
     - **Answer:** Displays the responses for each evaluation perspective. For quantitative evaluations, displays the responses from the evaluated AI model/AI system. For qualitative evaluations, displays the responses entered on the Evaluation Execution Screen.
     - **Score:** Displays the score assigned to each response based on the evaluation perspectives. Please note that the scores displayed in this scoring section are base scores. Therefore, the total score across evaluation perspectives and the radar chart displayed on the evaluation summary screen may not necessarily match.
  2. To generate a report, click the "Create Report" button located at the top of the screen. This will navigate you to the Evaluation Result Report Screen.
  3. Click the "Export as JSON" button located at the top of the screen to download the evaluation results JSON file. For details on the contents of the downloadable JSON file, refer to [Appendix](appendix-en.md)

---

## Evaluation Result Report Screen

**【Figure: Evaluation Result Report Screen (Top Section)】**
![Result Report](images-en/Result_Report-25.png)

**【Figure: Evaluation Result Report Screen (Bottom Section , Partial View)】**
![Result Report Partial](images-en/Result_Report_Partial-26.png)

**【Figure: PDF Export Screen】**
![PDF Export](images-en/PDF_Export-27.png)

- **Function Description:**  
  This screen displays a sample preview of the evaluation report, showing how it will appear when exported as a PDF.
- **Main Operation Steps:**
  1. **Review Report Content:**
     - Examine the radar chart and evaluation details to ensure that the content is accurate and complete.
  2. **Export as PDF:**
     - Click the "Export PDF" button to generate the evaluation report in PDF format.
     - PDF output uses the browser's print function, so output may take longer as the number of pages increases. If there is a large amount of evaluation data and the number of pages required for PDF output increases, please consider using the lighter JSON format instead of PDF output.


<div style="page-break-before:always"></div>

# AI Safety Evaluation Tool: Usage Procedures

This section outlines the operational flow based on the user's role, describing the Evaluation Definer's Flow and the Evaluator's Flow.

---

## Evaluation Definer Transition Flow

The following sequence outlines the typical steps an Evaluation Definer follows when using the AI Safety Evaluation Tool.


1. **Navigate to the Evaluation Definers Screen**
   - From the "Function Selection(Home Screen)", proceed to the "Initial Screen for Evaluation Definers" screen.
2. **Register Quantitative Evaluation Datasets**
   - Click the "Dataset Registration Screen" button to upload the required datasets.
3. **Create Qualitative Evaluation Items**
   - Use the "Qualitative Evaluation Question Creation Screen" button to define evaluation question for each evaluation perspective.
4. **Register AI Models**
   - Click the "AI Model Registration and Update Screen" button to register the AI models that will be evaluated.
5. **Define AI Safety Evaluation Content**
   - Click "Evaluation Definition Management Screen" button to configure the evaluation perspectives and methods, and to create the evaluation definition.
6. **Initiate an Evaluation**
   - To conduct the evaluation, return to the "Function Selection (Home Screen)" and proceed to the "Initial Screen for Evaluators".
   - For a step-by-step procedure on running evaluations, refer to the Evaluator Transition Flow section.

---

## Evaluator Transition Flow

The following sequence outlines the typical steps an evaluator follows when using the AI Safety Evaluation Tool.

1. **Navigate to the Evaluator Screen**
   - From the "Function Selection(Home Screen)", proceed to the "Initial Screen for Evaluators".
2. **Configure Evaluation Settings**
   - On the "Initial Screen for Evaluators", set the evaluation parameters and initiate the evaluation process.
3. **Register Evaluation Results**
   - On the "Evaluation Execution Screen", after completing the quantitative evaluation, select and register the results of the qualitative evaluation.
4. **Review Evaluation Results**
   - Click the "View Evaluation Results" button to view the evaluation results on the "Evaluation Results Summary Screen."
   - If necessary, compare the results with past evaluations.
5. **Examine Detailed Evaluation Results**
   - Click the "Go to Detail Screen" button on the "Evaluation Results Summary Screen" to access the "Evaluation Results (By Perspective) Screen".
6. **Generate Evaluation Report**
   - On the "Evaluation Results (By Perspective) Screen", click the "Create Report" button to create a structured evaluation report.
7. **Export Evaluation Result as JSON**
   - On the "Evaluation Results (By Perspective) Screen", click the "Export as JSON" button to export the evaluation results in JSON format.
8. **Export Evaluation Report as PDF**
   - On the "Evaluation Result Report Screen", click the "Export PDF" button to download the report in PDF format.


