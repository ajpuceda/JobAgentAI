# 🤖 Local AI Job Agent: Direct Employer Matcher

A privacy-first, ultra-fast Python agent that automates job description extraction and performs localized resume-to-job compatibility analysis. Running entirely on your local machine using **Playwright** and **Ollama**, this tool bypasses heavy anti-bot restrictions by fetching cleaner data directly from corporate career sites.

## 🚀 Key Features

*   **Anti-Bot Bypass:** Connects to an existing Chrome debugging session to read authentic employer job posts smoothly.
*   **Privacy-First Architecture:** Processes both your CV (PDF) and the target job description completely offline using local models.
*   **Dual-Stage Evaluation:** 
    *   **Phase 1:** Runs a quick match score (1 to 10) and extracts key role requirements under 15 seconds.
    *   **Phase 2 (Conditional):** If the match score is ≥ 8/10, it triggers an advanced generation step to compose a tailored motivation letter.
*   **Automated Organization:** Auto-creates folder structures named by date (`DDMMYYYY`) and exports the data using AI-generated short slug keywords.
*   **Performance Tracking:** Features a built-in precise hardware execution timer to measure CPU performance per run.

## 🛠️ Tech Stack & Requirements

*   **Language:** Python 3.10+
*   **Browser Automation:** Playwright (Sync API)
*   **AI Engine:** Ollama (Running `llama3.2` text model locally)
*   **PDF Processing:** pypdf

## 📦 Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com
    cd YOUR_REPOSITORY_NAME
    ```

2.  **Install Python Dependencies:**
    ```bash
    pip install pypdf ollama playwright pyautogui Pillow
    playwright install
    ```

3.  **Prepare local AI models:** Ensure Ollama is installed and running, then pull the lightweight text model:
    ```bash
    ollama pull llama3.2
    ```

## 🖥️ How to Use

1.  **Launch Chrome in Remote Debugging Mode:**
    Close all Chrome instances and launch a dedicated terminal window using the following command to allow Playwright connections:
    ```cmd
    start chrome --remote-debugging-port=9222 --user-data-dir="C:\chrome_agente"
    ```

2.  **Navigate to the Job Post:** In the newly opened Chrome window, go directly to the target employer's official job description page (e.g., Docplanner Careers). Keep this tab active.

3.  **Prepare your CV:** Place your resume in the project root directory and name it exactly `mi_cv.pdf`.

4.  **Run the Agent:** Execute the Python script forcing immediate console output:
    ```bash
    python -u agente.py
    ```

## 📊 Sample Output Structure

When a highly compatible role is processed (≥ 8/10), the agent outputs the report on the console and structures the workspace as follows:

```text
📂 [Current_Date_DDMMYYYY]/
 ├── 📄 engineering_manager_product_ofert.txt
 └── 📄 engineering_manager_product_motivation_letter.txt
```

---
*Developed as a local automation experiment to evaluate lightweight LLM deployment on consumer laptop CPUs.*
