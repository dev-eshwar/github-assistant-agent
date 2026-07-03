# Kaggle Notebook Setup & Execution Guide (Cloned Repository)

This guide explains how to execute the ADK multi-agent assistant directly within a Kaggle Notebook by cloning the agent codebase from GitHub.

---

## Step 1: Initialize the Environment & Install ADK

In a new Python notebook cell on Kaggle, install the Google Agent Development Kit (ADK):

```python
# Install the Google Agent Development Kit (ADK)
!pip install google-adk
```

---

## Step 2: Authentication & API Key Setup

ADK agents utilize the Google GenAI SDK under the hood to invoke models like `gemini-2.5-flash`. The SDK automatically authenticates by checking the `GEMINI_API_KEY` environment variable.

To configure this in a Kaggle Notebook safely without hardcoding your key:
1. Click **Add-ons** in the top menu bar of your Kaggle Notebook.
2. Select **Secrets**.
3. Add a new secret:
   - **Label:** `GEMINI_API_KEY`
   - **Value:** *[Your Google AI Studio API Key]*
4. Toggle on the checkmark to enable sharing this secret with the notebook.

---

## Step 3: Clone the Repositories

In a new cell, clone the agent codebase and the target repository (`math-galaxy`) to analyze:

```python
# 1. Clone the agent codebase into the working directory
!git clone https://github.com/dev-eshwar/github-assistant-agent.git /kaggle/working/github-assistant-agent

# 2. Clone the target repository to analyze
!git clone https://github.com/dev-eshwar/math-galaxy.git /kaggle/working/math-galaxy
```

---

## Step 4: Move Directory Context to Cloned Repo

Instead of copying files, run this Python cell to change the working directory context into the cloned repository so that all python imports find `shared_tools.py` and sub-agents correctly:

```python
import os

# Change current working directory to the cloned repo
os.chdir("/kaggle/working/github-assistant-agent")

print("Current Working Directory changed to:", os.getcwd())
print("Directory Contents:", os.listdir("."))
```

---

## Step 5: Configure `config.json`

Set up the configuration pointing to the target directories. Since the context is inside `github-assistant-agent`, the `.harness` folder will be created there:

```python
import json
import os

config_data = {
    "repo_path": "/kaggle/working/math-galaxy",
    "wiki_path": "/kaggle/working/math-galaxy-wiki",
    "github_url": "dev-eshwar/math-galaxy",
    "commit_depth": 100
}

os.makedirs(".harness/transit", exist_ok=True)
with open(".harness/config.json", "w", encoding="utf-8") as f:
    json.dump(config_data, f, indent=2)
    
print("Configuration file config.json updated at:", os.path.abspath(".harness/config.json"))
```

---

## Step 6: Define Execution Cell

Define the main runner block to load the orchestrator agent and run queries:

```python
import os
import sys
import importlib.util
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types
from kaggle_secrets import UserSecretsClient

# Load Gemini API key from Kaggle Secrets environment
user_secrets = UserSecretsClient()
os.environ["GEMINI_API_KEY"] = user_secrets.get_secret("GEMINI_API_KEY")

# Define target agent path
agent_path = "/kaggle/working/github-assistant-agent/harness-orchestrator/agent.py"

# Double check that the file exists to prevent FileNotFoundError
if not os.path.exists(agent_path):
    raise FileNotFoundError(f"Could not find agent.py at: {agent_path}. Current working directory contents: {os.listdir('.')}")

# Helper to dynamically import the orchestrator agent
def import_agent_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import the orchestrator agent dynamically due to hyphenated directory name
harness_module = import_agent_from_path(
    "harness_orchestrator_agent",
    agent_path
)
harness_orchestrator_agent = harness_module.harness_orchestrator_agent

def execute_agent_query(query_str: str):
    runner = Runner(
        app_name="harness-orchestrator-app",
        agent=harness_orchestrator_agent,
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
        artifact_service=InMemoryArtifactService(),
        auto_create_session=True,
    )
    
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=query_str)]
    )
    
    events = runner.run(
        user_id="kaggle_user",
        session_id="kaggle_session",
        new_message=content
    )
    
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if getattr(part, "text", None):
                    print(part.text, end="")
```

---

## Step 7: Ask Questions & Run Analysis

Use the following cell to run queries against the `math-galaxy` repository:

### Query 1: How are the math problems generated?
Run this block and wait for the response:

```python
execute_agent_query("How are the math problems generated? Does this architecture have a database of questions?")
```

### Query 2: Follow-up on Word Problems
Once the response is returned, ask the follow-up question by running:

```python
execute_agent_query("Does math-galaxy generate any word problem questions?")
```
