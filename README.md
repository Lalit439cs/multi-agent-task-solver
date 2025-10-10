# Multi-Agent Task Solver

This project is a multi-agent task-solving system built with FastAPI and LangGraph. It can take a high-level user request, break it down into subtasks, and orchestrate multiple specialized AI agents to execute them in parallel. The system supports both GPT-4 and Gemini models, integrates real-time web search, and provides a simple UI for interaction.

## Features

-   **FastAPI Backend**: Asynchronous, high-performance API for managing tasks.
-   **LangGraph Orchestration**: Robust and stateful agent orchestration using LangGraph for complex workflows.
-   **Multi-Agent System**: Specialized agents (Researcher, Summarizer, Data Analyst, Code Executor) that work together to solve problems.
-   **Dual LLM Support**: Seamlessly switch between or combine GPT-4 and Gemini models.
-   **Asynchronous Execution**: Agents and tools run asynchronously for improved performance.
-   **Real Web Search**: Integrated with DuckDuckGo search for real-time information gathering.
-   **Code Execution**: A sandboxed Python code executor for data analysis and other tasks.
-   **Simple UI**: A clean web interface for submitting tasks and viewing results in real-time.
-   **Dockerized**: Comes with `Dockerfile` and `docker-compose.yml` for easy setup and deployment.

## Architecture

The system is designed with a modular architecture, centered around a FastAPI application that communicates with a LangGraph-powered orchestrator. The orchestrator manages the state of the task and coordinates the execution of various agents and tools.

*   **UI (HTML/JS)**: The user interacts with the system through a simple web page.
*   **FastAPI App (`main.py`)**: Receives user requests, manages task state, and serves the UI.
*   **Orchestrator (`orchestrator.py`)**: The core of the system, built with LangGraph. It plans the task, dispatches subtasks to agents, and aggregates the results.
*   **Agents**: LLM-powered workers with specialized roles.
*   **Tools (`tools.py`)**: Functions that agents can use to interact with the outside world (e.g., web search, code execution).
*   **Configuration (`config.py`)**: Manages API keys and other settings.

## Getting Started

### Prerequisites

-   Docker
-   An OpenAI API key (for GPT-4) OR a Google AI Studio API key (for Gemini) - at least one is required

### Setup and Installation

1.  **Clone the Repository**:

    ```bash
    git clone <repository_url>
    cd multi-agent-task-solver
    ```

2.  **Create Environment File**:

    Create a `.env` file in the root of the project with your API keys and configuration:

    ```bash
    # Create .env file
    cat > .env << EOF
    # API Keys (Required - at least one)
    OPENAI_API_KEY=your_openai_api_key_here
    GOOGLE_API_KEY=your_google_api_key_here

    # Model Configuration
    OPENAI_MODEL=gpt-4o
    GEMINI_MODEL=gemini-2.5-pro
    GEMINI_PROJECT_ID = <id>

    # Search Configuration
    SEARCH_ENABLED=true

    # Agent Configuration
    MAX_CONCURRENT_AGENTS=3
    AGENT_TIMEOUT=60

    # File I/O Configuration
    TEMP_DIR=./temp
    EOF
    ```

3.  **Add Your API Keys**:

    Edit the `.env` file and replace the placeholder values with your actual API keys. You need at least one:
    - Get OpenAI API key from: https://platform.openai.com/api-keys
    - Get Google AI Studio key from: https://makersuite.google.com/app/apikey

4.  **Test API Connectivity** (Recommended):

    Before running the main application, verify that your API keys are working correctly:

    ```bash
    python3 test_llm_api.py
    ```

    This script will:
    - Check if your `.env` file exists
    - Test connectivity to OpenAI API (if key provided)
    - Test connectivity to Google Gemini API (if key provided)
    - Provide a summary showing which APIs are working

    **Note**: For Gemini, you may need to enable the Generative Language API in your Google Cloud Console if it's your first time using it. The test script will provide the activation URL if needed.

### Running the Application

#### Using Docker (Recommended)

1.  **Build the Docker Image**:

    ```bash
    docker build -t multi-agent-task-solver .
    ```

2.  **Run the Container**:

    ```bash
    docker run -p 8000:8000 --env-file .env -v $(pwd)/temp:/app/temp multi-agent-task-solver
    ```

    The API will be available at `http://localhost:8000`.

3.  **Access the UI**:

    Open your web browser and navigate to `http://localhost:8000`.

### How to Use

1.  **Open the UI**: Go to `http://localhost:8000` in your browser.
2.  **Enter a Request**: Type a complex request into the text area. For example:
    *   "Summarize the latest news on AI advancements and provide key statistics on market growth."
    *   "Find the current stock price of NVIDIA (NVDA ) and explain the recent trends in its stock performance."
3.  **Select Models**: Choose whether to use GPT-4, Gemini, or both.
4.  **Submit Task**: Click the "Submit Task" button.
5.  **View Progress**: The UI will show the task status, a running log of the agent's progress, and the final result once completed.

### Running Tests

A test client script is included to demonstrate how to interact with the API programmatically.

1.  **Ensure the server is running** (see "Running the Application" section above).
2.  **Run the test client**:

    ```bash
    python3 test_client.py
    ```

    This script will send several test requests to the API and print the status and results to the console.

## Project Structure

```
multi-agent-task-solver/
├── .gitignore
├── .env                # Your API keys and configuration (create this)
├── Dockerfile
├── README.md
├── config.py
├── main.py
├── orchestrator.py
├── requirements.txt
├── static/
│   └── index.html
├── temp/
│   └── .gitkeep
├── test_client.py      # Test script for API endpoints
├── test_llm_api.py     # Test script for LLM API connectivity
└── tools.py
```


## Key Components Explained

-   **`main.py`**: The entry point of the FastAPI application. It defines the API endpoints, manages background tasks, and serves the static UI.
-   **`orchestrator.py`**: Contains the `MultiAgentOrchestrator` class, which is built using LangGraph. It defines the nodes (planner, agent executor, aggregator) and edges of the agent workflow.
-   **`tools.py`**: Implements the tools available to the agents, such as `WebSearchTool`, `PythonCodeExecutor`, and `FileIOTool`.
-   **`config.py`**: A centralized configuration management class that loads settings from environment variables (via `.env` file).
-   **`static/index.html`**: A single-page UI with JavaScript to interact with the backend API, submit tasks, and poll for status updates.
-   **`test_llm_api.py`**: A diagnostic script to verify API connectivity with OpenAI and Google Gemini before running the main application.
-   **`test_client.py`**: A test script to interact with the running FastAPI server and demonstrate API usage.
-   **`Dockerfile`**: Defines the containerized environment for running the application with all necessary dependencies.

## Trade-offs Made Due to the 24h Constraint

Given the time limitation, certain design decisions and trade-offs were necessary to deliver a functional multi-agent system:

-   **Local Hosting**: The system is designed to run locally rather than deploying to cloud platforms (AWS, GCP, Azure), which would require additional infrastructure setup and configuration.
-   **Avoided Local LLM Models**: Instead of setting up and hosting local LLM models (e.g., Ollama, LLaMA), the system relies on cloud-based APIs (OpenAI GPT-4 and Google Gemini) for faster development and more reliable performance.
-   **Limited Corner Case Testing**: While core functionality is thoroughly tested, comprehensive edge case testing and error handling for all possible scenarios was not fully implemented.
-   **Code Refactoring**: Some code duplication and opportunities for abstraction exist. Given more time, the codebase could be further modularized and optimized for maintainability.
-   **Bonus Points Not Addressed**: Additional points mentioned in shared documents were diificult to prioritized within the 24-hour window.
-   **Simple UI interaction interface**

These trade-offs allowed for rapid iteration and delivery of a working proof-of-concept while maintaining code quality and core functionality. Also, Friday was also a normal working day at current company.

## Avoiding Hallucination and Repetition

To ensure reliable and accurate LLM responses, several strategies were implemented:

-   **Structured Response Format**: Agents are instructed to return responses in specific JSON formats, reducing ambiguity and making outputs more predictable and parseable.
-   **Clearly Specified Instructions**: Each agent receives detailed system prompts with explicit role definitions and task instructions, minimizing confusion and off-topic responses.
-   **Low Temperature Setting**: LLM temperature is set to 0.3 or lower (configurable) to reduce randomness and hallucination, encouraging more focused and deterministic outputs.
-   **Multiple Safe API Calls**: The system includes retry logic and error handling for LLM API calls, ensuring robustness against transient failures and rate limiting.
-   **Strong LLM Models**: By using top performing model variants of GPT-4 and Gemini, the system benefits from advanced reasoning capabilities and reduced hallucination rates compared to smaller models.
-   **Validation and Verification Steps**: The orchestrator includes validation logic to check subtask outputs and ensure they meet expected formats. The aggregator acts as a final reviewer, synthesizing and cross-checking results before presenting the final answer to the user.
