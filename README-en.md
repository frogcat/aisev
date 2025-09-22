[Japanese version is here.](README.md)

![Japan-AISI](images/aisi_logo.png)

# Introduction

The AI Safety Evaluation Environment is an evaluation tool and evaluation dataset designed to support AI safety evaluation based on the "Guide to Evaluation Perspectives on AI Safety" provided by Japan AI Safety Institute (hereinafter referred to as "AISI"). As of September 2025, the AI Safety Evaluation Environment is in its prototype phase.
   - This tool is provided to assist in evaluation work. Results obtained using specific datasets (e.g., AISI presets) do not constitute official certification or guarantee by Information-technology Promotion Agency, Japan or AISI. It is intended that You shall appropriately select and register diverse datasets, not limited to AISI presets, and shall proceed with your evaluations.

# Disclaimer

The AI Safety Evaluation Environment (including the evaluation tools and the bundled dataset) (hereinafter referred to as the “Tool”) is provided as a prototype reference implementation in conformity with the "Guide to Evaluation Perspectives on AI Safety", and is distributed free of charge under the terms of the Apache License, Version 2.0 (http://www.apache.org/licenses/). AISI supplies the Tool on an “AS IS” basis and makes no warranties, express or implied, with respect to quality, functionality, performance, security level, permissions or any other matter whatsoever.<br>
AISI shall not be liable to You for damages, including any direct, indirect, special, incidental, or consequential damages of any character arising from this License or from the use of or inability to use the Work, and any other use (including but not limited to damages for loss of goodwill and any and all other commercial damages or losses, work stoppage, damage to or loss of data, computer failure or malfunction, infringement of third-party rights), regardless of contract, tort, or any other legal ground.<br>
Furthermore, AISI may suspend publication of the Tool at any time without prior notice if deemed reasonably necessary, and bug reports may be submitted through the repository’s issue tracking function; however, no warranty is made as to whether such reports will be addressed or the timing thereof. Depending on the content or circumstances, the issue may be closed without action, or the acceptance of such reports may be suspended at any time.



# Overview

The AI Safety Evaluation Environment is an evaluation tool and dataset designed to support AI safety evaluation based on the "Guide to Evaluation Perspectives on AI Safety". Utilizing this environment facilitates the implementation of AI safety evaluation for AI systems. The "Guide to Evaluation Perspectives on AI Safety" defines 10 evaluation perspectives and recommends AI safety evaluation from various viewpoints. To address evaluations from a broad range of perspectives, this evaluation tool combines quantitative evaluation—which statistically evaluates the content of inputs and outputs to the AI system—with qualitative evaluation—which asks evaluators about the current state of the AI system—to provide a comprehensive evaluation.

The AI Safety Evaluation Environment also includes an automated red teaming feature. Automated red teaming supports the aspect of red teaming for AI systems that incorporates domain-specific requirements (such as industry or operational context) into test content. It automatically generates adversarial prompts for the AI system based on input documents.

The AI Safety Evaluation Environment is a tool installed on personal computers or similar devices. It requires Docker or a Docker-compatible runtime environment. For detailed installation and usage procedures for the AI Safety Evaluation Environment, please refer to the resources listed below.

## Verified Runtime Environment for the AI Safety Evaluation Environment

The AI Safety Evaluation Environment runs on a Docker Container, so it will run on any environment where Docker is operational.
The following are the confirmed operating environments. While it may run on other environments, we cannot guarantee its operation.

   - **OS:** Windows 11, MacOS(Sequoia)
   - **Python:** Python 3.12.7
   - **Docker Environment/Compatible Environment:** Rancher Desktop 1.19.3

# Detailed usage procedures

   - [User Manual](docs/manual-en.md)
   - [Automated Red Teaming Manual](docs/rt-en.md)
   - [Appendix](docs/appendix-en.md)

