# Kaggle Notebook Setup & Execution Guide (Cloned Repository with Pre-built Wiki)

This guide explains how to execute the ADK multi-agent assistant directly within a Kaggle Notebook when the Wiki Knowledge Base has already been pre-built offline and uploaded to your GitHub repository.

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

## Step 3: Setup Repository Workspace (Clone, Pull, and Navigate)

Run this Python cell to clone or pull your agent codebase (containing the pre-built `math-galaxy-wiki` folder) and automatically move into the folder context:

```python
import os
import subprocess

repo_dir = "/kaggle/working/github-assistant-agent"

# Idempotently Clone or Pull latest updates
if not os.path.exists(repo_dir):
    print("Cloning the agent repository...")
    subprocess.run([
        "git", "clone", 
        "https://github.com/dev-eshwar/github-assistant-agent.git", 
        repo_dir
    ])
else:
    print("Repository already exists. Pulling latest updates...")
    subprocess.run(["git", "-C", repo_dir, "pull"])

# Change directory context safely
os.chdir(repo_dir)

print("\nCurrent Working Directory successfully changed to:", os.getcwd())
print("Directory Contents:", os.listdir("."))
```

---

## Step 4: Configure `config.json`

Set up the configuration pointing to the local pre-built wiki path. Since the context is inside `github-assistant-agent`, the `.harness` folder will be created there:

```python
import json
import os

config_data = {
    "repo_path": "/kaggle/working/math-galaxy",
    "wiki_path": "/kaggle/working/github-assistant-agent/math-galaxy-wiki",
    "github_url": "dev-eshwar/math-galaxy",
    "commit_depth": 100
}

os.makedirs(".harness/transit", exist_ok=True)
with open(".harness/config.json", "w", encoding="utf-8") as f:
    json.dump(config_data, f, indent=2)
    
print("Configuration file config.json updated at:", os.path.abspath(".harness/config.json"))
```

---

## Step 5: Define Execution Cell (With Cache Clearing)

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

# Force reload of all agent modules by clearing sys.modules cache.
# This prevents Jupyter/Kaggle from using stale cached python code after you pull updates.
for name in list(sys.modules.keys()):
    if any(k in name for k in ["harness", "agent", "shared_tools", "kb_builder", "qa", "logic_reader"]):
        sys.modules.pop(name, None)

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
    
    # Inject a system instruction to tell the orchestrator to skip the KB Sync step
    system_instruction = (
        "Note: The Wiki has already been pre-built offline and is available at the wiki_path. "
        "Do not run the kb_builder_agent sync step. Proceed directly to invoking the qa_agent "
        "and performing any necessary logic analysis."
    )
    full_prompt = f"{query_str}\n\n[System Instructions]: {system_instruction}"
    
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=full_prompt)]
    )
    
    events = runner.run(
        user_id="kaggle_user",
        session_id="kaggle_session",
        new_message=content
    )
    
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                # Check for function calls first to prevent warning logs
                if getattr(part, "function_call", None) is not None:
                    continue
                if getattr(part, "text", None):
                    print(part.text, end="")
```

---

## Step 6: Ask Questions & Run Analysis

Use the following cell to run queries against the pre-built `math-galaxy` wiki:

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
