# ExecMind

ExecMind is an intelligent CLI-based application designed to help you capture, research, structure, and evaluate ideas. It leverages Azure OpenAI to act as a "Deep Researcher" and strategic partner, transforming raw thoughts into structured concepts with market feasibility analysis.

## Features

- **Idea Capture**: Input ideas via text or audio (transcription supported).
- **Deep Researcher**: Automatically frames and confirms your idea, then scans the web/history for duplicates and related context.
- **Structured Output**: Saves ideas in a structured format for better organization.
- **Evaluation**: specific analysis of feasibility and market fit for your concepts.

## Prerequisites

- **OS**: Windows (WSL / Ubuntu recommended) or Linux.
- **Python**: 3.10+
- **Azure OpenAI Access**: You need an active Azure OpenAI resource with a deployed model (e.g., GPT-4o).

## Installation

1.  **Clone the repository** (if you haven't already).
2.  **Set up a virtual environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
2.  Edit `.env` and add your Azure OpenAI credentials:
    ```ini
    AZURE_OPENAI_API_KEY=your_key_here
    AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
    AZURE_OPENAI_API_VERSION=2024-02-15-preview
    AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
    ```

## Usage

Run the application using the main script from the project root:

```bash
python app/main.py
```

Follow the on-screen CLI prompts to navigate the menus.
