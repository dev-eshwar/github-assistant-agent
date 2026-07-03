# Kaggle Notebook Setup & Execution Guide

This guide explains how to install and execute the ADK multi-agent repository assistant directly within a Kaggle Notebook. It will analyze the `math-galaxy` repository and build a Wiki Knowledge Base for it.

---

## Step 1: Initialize the Environment

Create a new Python notebook on Kaggle and run the following command in a cell to install the required libraries:

```python
# Install the Google Agent Development Kit (ADK)
!pip install google-adk
```

---

## Step 1.5: Authentication & API Key Setup

ADK agents utilize the Google GenAI SDK under the hood to invoke models like `gemini-2.5-flash`. The SDK automatically authenticates by checking the `GEMINI_API_KEY` environment variable.

To configure this in a Kaggle Notebook safely without hardcoding your key:
1. Click **Add-ons** in the top menu bar of your Kaggle Notebook.
2. Select **Secrets**.
3. Add a new secret:
   - **Label:** `GEMINI_API_KEY`
   - **Value:** *[Your Google AI Studio API Key]*
4. Toggle on the checkmark to enable sharing this secret with the notebook.

---

## Step 2: Clone the Target Repository

Clone the `math-galaxy` repository (the target codebase to analyze) into the Kaggle environment:

```python
# Clone the repository
!git clone https://github.com/dev-eshwar/math-galaxy.git
```

---

## Step 3: Setup Project Directory Structure

Run this cell to create the agent directory structures and the `.harness` configuration directory:

```python
import os

# Create directories for each agent's skill
os.makedirs("harness-orchestrator", exist_ok=True)
os.makedirs("kb-builder", exist_ok=True)
os.makedirs("logic-reader", exist_ok=True)
os.makedirs("qa", exist_ok=True)

# Create harness config directory
os.makedirs(".harness/transit", exist_ok=True)
print("Directory structure created successfully.")
```

---

## Step 4: Write Configuration (`config.json`)

Set up the configuration pointing to the local git clone and output Wiki path:

```python
import json

config_data = {
    "repo_path": "/kaggle/working/math-galaxy",
    "wiki_path": "/kaggle/working/math-galaxy-wiki",
    "github_url": "dev-eshwar/math-galaxy",
    "commit_depth": 100
}

with open(".harness/config.json", "w", encoding="utf-8") as f:
    json.dump(config_data, f, indent=2)
    
print("Configuration file config.json created.")
```

---

## Step 5: Write the Skills (`SKILL.md` files)

Create the skill definition files for the agents using Python write commands:

```python
# Write kb-builder SKILL.md
kb_skill = r"""---
name: kb-builder
description: Build or incrementally update a local markdown-based Wiki/Knowledge Base using Git history and GitHub REST APIs.
---

# Knowledge Base Builder Skill

This skill allows you to build and incrementally update a local markdown-based Wiki/Knowledge Base from a target Git repository and GitHub issues.

## Inputs & Prerequisites

1. Read the target config from [config.json](../../.harness/config.json) (or receive parameters: `repo_path`, `wiki_path`, `github_url`, `commit_depth`).
2. Ensure you have the `GITHUB_PAT` environment variable set if you plan to fetch GitHub issues/PRs.

## Execution Workflow

### Step 1: Initialize Directory Structure
1. In the `wiki_path`, create the following subdirectories:
   - `architecture/`
   - `features/`
   - `history/`
   - `bugs/`
   - `security/`
2. Check for the existence of `.metadata.json` in `wiki_path` to retrieve:
   - `last_sync_commit` (string, hash of the last synced commit)
   - `last_sync_timestamp` (string, ISO timestamp of the last sync)

### Step 1.2: Check Modification Timing (Skip Update Logic)
1. **Compare Git Commits:** Run `git -C <repo_path> rev-parse HEAD` to fetch the latest local commit hash.
2. Compare the latest commit hash with `last_sync_commit` from `.metadata.json`.
3. **Check for Changes:** If the latest commit hash matches `last_sync_commit`, check if there are any new updates needed (such as GitHub issues updates). If the local repository state matches the last synced state and no API updates are pending:
   - Print: `"Wiki is up-to-date. Skipping generation."`
   - **Bypass and skip** all subsequent steps (Step 1.5 through Step 6).
   - Terminate the KB builder execution early as a success.

### Step 1.5: Analyze Codebase Architecture & Map Components
1. **Scan Source Code:** List and inspect the files and directories inside `repo_path`.
2. **Identify Components/Features:** Group the files and directories into distinct, high-level logical domains or architectural elements based on the codebase structure (e.g., in an e-commerce app, group code into components like `cart`, `payment`, `catalog`, `auth`, `routing`).
3. **Generate Component Documentation:** For each identified architectural component, create a documentation file at `wiki_path/architecture/component_<name>.md`.
   - **Title:** Component name (e.g., `# Cart Component`).
   - **Files list:** Bullet points listing the source file paths belonging to this component (relative to `repo_path`).
   - **Responsibility:** A concise description explaining what this component does, its key functions/classes, and how it interacts with other components.
4. **Create Architecture Overview:** Create or update `wiki_path/architecture/overview.md` summarizing the overall system architecture, linking to the individual component files.

### Step 2: Fetch Git Commits
1. Run `git log` on the `repo_path` to find new commits since `last_sync_commit` up to `commit_depth`.
   - Command: `git -C <repo_path> log <last_sync_commit>..HEAD --pretty=format:"%H%n%an%n%ae%n%cI%n%s%n%b%n___KB_COMMIT_END_TOKEN___"`
   - If `last_sync_commit` is not set or not found in the repository history, fetch the last `commit_depth` commits: `git -C <repo_path> log --max-count=<commit_depth> --pretty=format:"..."`
2. For each commit, retrieve the list of modified files and their modification status:
   - Command: `git -C <repo_path> show --name-status --pretty=format: <commit_hash>`

### Step 3: Fetch GitHub Issues & PRs (Optional)
1. Parse the owner and repository name from `github_url` (e.g. `owner/repo`).
2. If `GITHUB_PAT` is configured, execute a GET request to:
   `https://api.github.com/repos/<owner>/<repo>/issues?state=all&per_page=100&since=<last_sync_timestamp>`
3. Retrieve JSON response containing issues and PRs updated since the last sync.

### Step 4: Classification
For each commit and issue, classify it into one of the categories:
- **security**: Title or body contains keywords like `security`, `vuln`, `cve`, `leak`, `auth`, `exploit`, `token`, `password`, `xss`, `csrf`, `cors` or associated labels.
- **architecture**: Title or body contains keywords like `arch`, `architecture`, `design`, `refactor`, `structure`, `module`, `framework`, `database schema` or associated labels.
- **bugs**: Title or body contains keywords like `fix`, `bug`, `issue`, `resolve`, `defect`, `error`, `crash`, `fail`, `broken`, `regression` or associated labels.
- **features**: Title or body contains keywords like `feat`, `feature`, `add`, `new`, `implement`, `enhancement`, `improvement` or associated labels.
- **history**: Default category if no other categories match.

### Step 5: Generate Markdown Documentation Files
1. **Commit Files**: Write to `wiki_path/<category>/commit_<hash>.md`:
   - Include header fields: Hash, Author, Date, Category.
   - Include the commit message and body.
   - Include a **Modified Files** list.
   - **Link to Components:** Map the modified files to the components identified in Step 1.5. Create a section `## Affected Architectural Components` linking to the respective `component_<name>.md` files (e.g. `[Cart Component](../architecture/component_cart.md)`).
   - Search for issue numbers (e.g. `#12`) in the commit message. If found, link them: `[Issue #12](../<issue_category>/issue_12.md)`.
2. **Issue Files**: Write to `wiki_path/<category>/issue_<number>.md`:
   - Include header fields: State, Author, Created/Updated/Closed dates, Type (Issue vs PR), Labels, URL.
   - Include the issue description.
   - **Link to Components:** Deduce which architectural components this issue/PR impacts (by analyzing titles, descriptions, or linked commits). Include links to the corresponding `component_<name>.md` files.
   - Include a **Related Commits** list linked to the relevant commit files: `[Commit abc1234](../<commit_category>/commit_abc1234.md)`.

### Step 6: Generate Category and Global Indices
1. **Category Indices**: For each of the 5 categories, compile a list of all markdown documents in that folder.
   - Read their Titles and Dates.
   - Sort them by Date (descending).
   - Write/overwrite `wiki_path/<category>/index.md` listing the articles as relative links.
2. **Global Index**: Write/overwrite `wiki_path/README.md` listing the categories, item counts, and sync timestamps.

### Step 7: Save Metadata
1. Write/overwrite `wiki_path/.metadata.json` with the current timestamp and the latest commit hash (the first commit in the newly fetched commits, or the previous hash if no new commits).
"""

# Write qa SKILL.md
qa_skill = r"""---
name: qa
description: Answer questions using strictly the generated Wiki markdown files as the source of truth, and identify relevant code file references.
---

# Wiki-Based QA Skill

This skill searches the compiled Wiki/Knowledge Base directory to answer a user's question, extracts relevant code references, and optionally traces the timeline of feature development or bug fixes.

## Inputs

1. `query`: The user question or request.
2. `wiki_path`: Path to the local Wiki directory.

## Execution Workflow

### Step 1: Scan and Rank Wiki Articles
1. Find all `.md` files under the `wiki_path` (excluding `index.md` and `README.md`).
2. Parse each document to read its contents, title, and headers.
3. Clean the user `query` to remove common stopwords (e.g. `the`, `is`, `a`, `and`, `to`) and extract keywords.
4. If the query contains references to issues (e.g. `#12`, `12`) or commit hashes (e.g. `abc1234`), extract those explicitly.
5. Score each wiki document:
   - Match by specific issue filename or commit filename (+1000 points).
   - Match by query keywords in the article title (+15 points per keyword).
   - Match by query keywords in the filename (+10 points per keyword).
   - Count keyword occurrences in the body content (+1 point per occurrence).
6. Rank files by score and select the top matching documents (e.g., top 3-5 documents).

### Step 2: Formulate Answer (Wiki Constraint)
1. **Rule of Truth**: Rely *only* on the facts and information contained in the selected matching Wiki documents. Do not assume or project details not present in the files.
2. If no documents score above 0 or if the query cannot be answered using the documents, respond with exactly:
   `This information is not present in the current knowledge base.`

### Step 3: Format the Response
If the answer is found in the Wiki, structure the response precisely with the following sections:

1. **Direct Answer**:
   - Limit the explanation to 2-3 direct, concise points.
2. **Code References**:
   - Identify any code file paths mentioned in the documents (e.g., `src/auth.py`).
   - Format them as a bulleted list titled `## Code References`, using format:
     `- \`path/to/file.py\``
3. **History/Timeline (Conditional)**:
   - If the query requests a history, timeline, or series of events, extract all dates, commits, and actions.
   - Construct a markdown table:
     | Date/Timestamp | Action/Commit | Author | Source Document |
     | --- | --- | --- | --- |
     | `2026-07-01` | Commit message / Issue title | @user | `commit_abc123.md` |
"""

# Write logic-reader SKILL.md
logic_skill = r"""---
name: logic-reader
description: Perform targeted code logic reading and path analysis on specific source code files in a repository.
---

# Code Logic Reader Skill

This skill performs deep code inspection and logical execution analysis on specified files in the local Git repository to identify bug reasons, trace function paths, or detail variable states.

## Inputs

1. `files`: A list of file paths (relative to `repo_path`) to read and analyze.
2. `query`: The user question focusing on logic analysis.
3. `repo_path`: Path to the local repository directory.

## Execution Workflow

### Step 1: Read Targeted Files
1. Locate the absolute path of each file specified in the list by prefixing it with the `repo_path`.
2. Verify the files exist.
3. Read the content of the target files (or specific sections of the files, using a code viewer or terminal reads).

### Step 2: Perform Execution Path and Logic Analysis
1. Analyze the function definitions, imports, conditionals, and variables relevant to the user query.
2. Trace how data flows through the file, paying close attention to:
   - Exception handling and error-prone zones.
   - Authentication, validation, and authorization checkpoints.
   - Variable mutation and configuration constants.
3. Identify logical bugs, security gaps, or structural flaws.

### Step 3: Write Analysis Report
Format the analysis report as a markdown summary containing:
1. **Targeted Code Logic Analysis**:
   - Briefly state which files and functions were inspected.
2. **Key Findings**:
   - List detailed, technical points about how the logic operates.
   - Describe any flaws, safety risks, or functional anomalies found.
3. **Execution Trace/Pseudocode** (Optional):
   - Provide a simplified code snippet or step-by-step logic path to clarify the execution flows.
4. **Resolution Recommendations**:
   - Provide concrete code diffs or instructions on how to correct any identified logical issues.
"""

# Write harness-orchestrator SKILL.md
orch_skill = r"""---
name: harness-orchestrator
description: Orchestrates the multi-agent workflow for analyzing a repository, building/updating a knowledge base, answering questions, and performing code logic reviews.
---

# Harness Orchestrator Skill

This skill coordinates the workflow between sub-agents executing the `kb-builder`, `qa`, and `logic-reader` skills. It enables you (the agent) to run the steps manually or delegate tasks to specialized sub-agents.

## Sub-Agent Definitions & Roles

When orchestrating, you should define and invoke the following specialized sub-agents:

1. **`kb_builder_agent`**:
   - **Role:** `KB Builder Sub-Agent`
   - **Responsibility:** Executes the `kb-builder` skill. Parses local Git history, scans codebase structure, catalogs logical architectural elements, queries GitHub Issues/PRs, and regenerates category indices.
2. **`qa_agent`**:
   - **Role:** `Wiki QA Sub-Agent`
   - **Responsibility:** Executes the `qa` skill. Restricts searches strictly to Wiki markdown directories, ranks articles by query keywords, and formats summaries and code references.
3. **`logic_reader_agent`**:
   - **Role:** `Logic Analyzer Sub-Agent`
   - **Responsibility:** Executes the `logic-reader` skill. Inspects source code files, traces execution control flows, analyzes variable values, and diagnoses logic bugs.

## Context Passing

When launching/invoking a sub-agent, you must pass the exact operational context in the prompt message:
```json
{
  "config": {
    "repo_path": "./repo",
    "wiki_path": "./wiki",
    "github_url": "owner/repo",
    "commit_depth": 100
  },
  "query": "The active user query",
  "transit_dir": ".harness/transit",
  "instruction_file": "relative/path/to/skill/SKILL.md"
}
```
Ensure all sub-agents read from and write to the `.harness/transit/` folder to pass state updates.

## Step-by-Step Orchestration Workflow

### Step 1: Initialize Session
1. Read the target config from [config.json](../../.harness/config.json).
2. If the configuration doesn't exist, create it with the following structure:
   - `repo_path`: Path to the local git clone.
   - `wiki_path`: Path to the output Wiki folder.
   - `github_url`: The GitHub repo URL or `owner/repo`.
   - `commit_depth`: Max commits to sync (default: 100).
3. Create/verify the directory structure: `.harness/transit/`.
4. Clear any old `.json` files inside `.harness/transit/` (for fresh runs only; skip when looping follow-up questions).
5. Create `01_init.json` with the current user query, timestamp, and resolved configuration.

### Step 2: Build/Update Knowledge Base (KB)
1. Invoke the **`kb_builder_agent`** passing the config and `kb-builder/SKILL.md` instructions.
2. If the builder agent skips sync because no files have changed (based on last modified time comparison), log this status.
3. After completion, write a status summary to `02_kb_status.json`:
   ```json
   {
     "status": "success",
     "timestamp": "ISO_TIMESTAMP"
   }
   ```

### Step 3: Run Wiki-Based QA
1. Invoke the **`qa_agent`** passing the query and `qa/SKILL.md` instructions.
2. Inspect the output from the QA agent.
3. Write the results to `03_qa_result.json`:
   ```json
   {
     "status": "found" or "not_found",
     "stdout": "QA_OUTPUT_TEXT",
     "code_references": ["list/of/files.py"],
     "timestamp": "ISO_TIMESTAMP"
   }
   ```

### Step 3.5: Missing Info KB Re-sync Logic (Dynamic Fallback)
If the QA agent reports `status: "not_found"`:
1. Inspect the current `commit_depth` in your configuration.
2. If `commit_depth` is small (e.g., `< 500`):
   - Temporarily double the `commit_depth` (e.g. increase from 100 to 500).
   - Re-invoke the **`kb_builder_agent`** with instructions to force-bypass modifications checks and pull a deeper git history/GitHub Issues sync.
   - Once the re-sync completes, re-invoke the **`qa_agent`** on the updated Wiki.
   - Update `03_qa_result.json` with the new QA outcome.
3. If still not found or `commit_depth` is already maximum, proceed to Step 5.

### Step 4: Logic Analysis (Conditional)
1. Analyze the query for keywords indicating logic/code analysis (e.g., `analyze`, `bug`, `why`, `code`, `logic`, `fix`, `read`, `error`).
2. If `03_qa_result.json` contains `code_references` and the query implies logic analysis:
   - Invoke the **`logic_reader_agent`** with `logic-reader/SKILL.md` for those referenced files.
   - Write the logic analysis output to `04_logic_analysis.json`.
3. If not required, write a skipped state to `04_logic_analysis.json`:
   ```json
   {
     "run": false,
     "reason": "No code references found or query does not imply logical analysis",
     "timestamp": "ISO_TIMESTAMP"
   }
   ```

### Step 5: Assemble Final Response
1. Formulate the final response:
   - If QA returned `"not_found"`, output: `"This information is not present in the current knowledge base."`
   - Otherwise, output the QA summary and append the Logic Analysis report (if run).
2. Save the final output to `05_final_response.json`.
3. Present the final response to the user.

## Interactive Follow-Up Questions Loop

When the user asks a follow-up question after receiving the final response:
1. **Context Check:** Assess if the follow-up question refers to information/code files already present in the current Wiki or generated QA/Logic reports.
2. **Looping Logic:**
   - **DO NOT** clear `.harness/transit/` or re-initialize the session.
   - **DO NOT** re-run the `kb_builder_agent` (skip Step 2) unless the user explicitly requests to sync/update new code changes or fresh commits.
   - Directly run **Step 3 (Wiki-Based QA)** and/or **Step 4 (Logic Analysis)** using the new follow-up query against the existing Wiki and code files.
   - Update the relevant `03_qa_result.json` and `04_logic_analysis.json` files and compile the new answer.
3. Keep the session active for further follow-up loops.
"""

with open("kb-builder/SKILL.md", "w", encoding="utf-8") as f:
    f.write(kb_skill)
with open("qa/SKILL.md", "w", encoding="utf-8") as f:
    f.write(qa_skill)
with open("logic-reader/SKILL.md", "w", encoding="utf-8") as f:
    f.write(logic_skill)
with open("harness-orchestrator/SKILL.md", "w", encoding="utf-8") as f:
    f.write(orch_skill)

print("Skills files written successfully.")
```

---

## Step 6: Write Python Agent Implementations

Write the python code definitions for the agents.

### 6.1 Shared Tools (`shared_tools.py`)
```python
%%writefile shared_tools.py
import subprocess
import os
import urllib.request
import urllib.error
import json

def run_shell_command(command: str) -> str:
    try:
        res = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        output = res.stdout
        if res.stderr: output += "\n" + res.stderr
        return output
    except Exception as e: return f"Error: {e}"

def read_file_content(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f: return f.read()
    except Exception as e: return f"Error: {e}"

def write_file_content(path: str, content: str) -> str:
    try:
        abs_path = os.path.abspath(path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f: f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e: return f"Error: {e}"

def list_directory(path: str) -> str:
    try:
        if not os.path.exists(path): return f"Directory {path} does not exist"
        return json.dumps(os.listdir(path))
    except Exception as e: return f"Error: {e}"

def path_exists(path: str) -> bool:
    return os.path.exists(path)

def make_directory(path: str) -> str:
    try:
        os.makedirs(path, exist_ok=True)
        return f"Created {path}"
    except Exception as e: return f"Error: {e}"

def http_get_request(url: str, headers_json: str = "{}") -> str:
    try:
        headers = json.loads(headers_json)
        req = urllib.request.Request(url)
        for k, v in headers.items(): req.add_header(k, v)
        with urllib.request.urlopen(req) as response: return response.read().decode("utf-8")
    except Exception as e: return f"Error: {e}"
```

### 6.2 KB Builder Agent (`kb-builder/agent.py`)
```python
%%writefile kb-builder/agent.py
import os
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
from shared_tools import run_shell_command, read_file_content, write_file_content, list_directory, path_exists, make_directory, http_get_request

current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, "SKILL.md"), "r", encoding="utf-8") as f:
    skill_content = f.read()

retry_config = types.HttpRetryOptions(initial_delay=15.0, attempts=6, backoff_multiplier=1.5)

kb_builder_agent = Agent(
    name="kb_builder_agent",
    description="Builds or incrementally updates a local markdown-based Wiki/Knowledge Base from a target Git repository and GitHub issues.",
    instruction=skill_content,
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    tools=[run_shell_command, read_file_content, write_file_content, list_directory, path_exists, make_directory, http_get_request]
)
```

### 6.3 QA Agent (`qa/agent.py`)
```python
%%writefile qa/agent.py
import os
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
from shared_tools import read_file_content, list_directory, path_exists

current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, "SKILL.md"), "r", encoding="utf-8") as f:
    skill_content = f.read()

retry_config = types.HttpRetryOptions(initial_delay=15.0, attempts=6, backoff_multiplier=1.5)

qa_agent = Agent(
    name="qa_agent",
    description="Answers questions using strictly the generated Wiki markdown files as the source of truth, and identifies relevant code file references.",
    instruction=skill_content,
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    tools=[read_file_content, list_directory, path_exists]
)
```

### 6.4 Logic Reader Agent (`logic-reader/agent.py`)
```python
%%writefile logic-reader/agent.py
import os
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
from shared_tools import read_file_content, list_directory, path_exists

current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, "SKILL.md"), "r", encoding="utf-8") as f:
    skill_content = f.read()

retry_config = types.HttpRetryOptions(initial_delay=15.0, attempts=6, backoff_multiplier=1.5)

logic_reader_agent = Agent(
    name="logic_reader_agent",
    description="Performs targeted code logic reading and path analysis on specific source code files in a repository.",
    instruction=skill_content,
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    tools=[read_file_content, list_directory, path_exists]
)
```

### 6.5 Harness Orchestrator Agent (`harness-orchestrator/agent.py`)
```python
%%writefile harness-orchestrator/agent.py
import os
import json
import importlib.util
from datetime import datetime
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
from shared_tools import read_file_content, write_file_content, list_directory, path_exists, make_directory

def import_agent_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

kb_builder_agent = import_agent_from_path("kb_builder_agent", os.path.join(parent_dir, "kb-builder", "agent.py")).kb_builder_agent
qa_agent = import_agent_from_path("qa_agent", os.path.join(parent_dir, "qa", "agent.py")).qa_agent
logic_reader_agent = import_agent_from_path("logic_reader_agent", os.path.join(parent_dir, "logic-reader", "agent.py")).logic_reader_agent

def initialize_session(query: str) -> str:
    try:
        transit_dir = os.path.join(parent_dir, ".harness", "transit")
        os.makedirs(transit_dir, exist_ok=True)
        config_path = os.path.join(parent_dir, ".harness", "config.json")
        with open(config_path, "r", encoding="utf-8") as f: config_data = json.load(f)
        for f in os.listdir(transit_dir):
            if f.endswith(".json"): os.remove(os.path.join(transit_dir, f))
        init_event = {"query": query, "timestamp": datetime.now().isoformat() + "Z", "config": config_data}
        with open(os.path.join(transit_dir, "01_init.json"), "w", encoding="utf-8") as f: json.dump(init_event, f, indent=2)
        return f"Session initialized: {json.dumps(config_data)}"
    except Exception as e: return f"Error: {e}"

def write_kb_status(status: str) -> str:
    try:
        transit_dir = os.path.join(parent_dir, ".harness", "transit")
        with open(os.path.join(transit_dir, "02_kb_status.json"), "w", encoding="utf-8") as f:
            json.dump({"status": status, "timestamp": datetime.now().isoformat() + "Z"}, f, indent=2)
        return "Success"
    except Exception as e: return f"Error: {e}"

def write_qa_result(status: str, qa_output_text: str, code_references: list[str]) -> str:
    try:
        transit_dir = os.path.join(parent_dir, ".harness", "transit")
        with open(os.path.join(transit_dir, "03_qa_result.json"), "w", encoding="utf-8") as f:
            json.dump({"status": status, "stdout": qa_output_text, "code_references": code_references, "timestamp": datetime.now().isoformat() + "Z"}, f, indent=2)
        return "Success"
    except Exception as e: return f"Error: {e}"

def write_logic_analysis_report(run: bool, files_analyzed: list[str], stdout: str, reason: str = "") -> str:
    try:
        transit_dir = os.path.join(parent_dir, ".harness", "transit")
        data = {"run": run, "files_analyzed": files_analyzed, "stdout": stdout, "timestamp": datetime.now().isoformat() + "Z"}
        if not run: data["reason"] = reason
        with open(os.path.join(transit_dir, "04_logic_analysis.json"), "w", encoding="utf-8") as f: json.dump(data, f, indent=2)
        return "Success"
    except Exception as e: return f"Error: {e}"

def write_final_response(final_output: str) -> str:
    try:
        transit_dir = os.path.join(parent_dir, ".harness", "transit")
        with open(os.path.join(transit_dir, "05_final_response.json"), "w", encoding="utf-8") as f:
            json.dump({"final_output": final_output, "timestamp": datetime.now().isoformat() + "Z"}, f, indent=2)
        return "Success"
    except Exception as e: return f"Error: {e}"

def read_session_config() -> str:
    try:
        with open(os.path.join(parent_dir, ".harness", "config.json"), "r", encoding="utf-8") as f: return json.dumps(json.load(f))
    except Exception as e: return f"Error: {e}"

def update_session_config(repo_path: str, wiki_path: str, github_url: str, commit_depth: int) -> str:
    try:
        data = {"repo_path": repo_path, "wiki_path": wiki_path, "github_url": github_url, "commit_depth": commit_depth}
        with open(os.path.join(parent_dir, ".harness", "config.json"), "w", encoding="utf-8") as f: json.dump(data, f, indent=2)
        return "Success"
    except Exception as e: return f"Error: {e}"

with open(os.path.join(current_dir, "SKILL.md"), "r", encoding="utf-8") as f: skill_content = f.read()

retry_config = types.HttpRetryOptions(initial_delay=15.0, attempts=6, backoff_multiplier=1.5)

harness_orchestrator_agent = Agent(
    name="harness_orchestrator_agent",
    description="Orchestrates the multi-agent workflow for analyzing a repository.",
    instruction=skill_content,
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    tools=[initialize_session, write_kb_status, write_qa_result, write_logic_analysis_report, write_final_response, read_session_config, update_session_config, read_file_content, write_file_content, list_directory, path_exists, make_directory],
    sub_agents=[kb_builder_agent, qa_agent, logic_reader_agent]
)
```

---

## Step 7: Execution cell

Define the main runner block and set your API keys:

```python
import os
import sys
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types
from kaggle_secrets import UserSecretsClient

import importlib.util

# Load Gemini API key from Kaggle Secrets environment
user_secrets = UserSecretsClient()
os.environ["GEMINI_API_KEY"] = user_secrets.get_secret("GEMINI_API_KEY")

def import_agent_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import the orchestrator agent dynamically due to hyphenated directory name
harness_module = import_agent_from_path(
    "harness_orchestrator_agent",
    "/kaggle/working/harness-orchestrator/agent.py"
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

## Step 8: Ask Questions (Interactive Phase)

Use the following cell to run queries against the `math-galaxy` repository:

### Query 1: How are the math problems generated?
Run this block and wait for the response:

```python
execute_agent_query("How are the math problems generated? Does this architecture have a database of questions?")
```

**Expected Response Details:**
The agent will sync the repository using `kb-builder`, search the topics files, and report:
* The math problems are generated dynamically (programmatically) on the fly using JavaScript functions (e.g. `generateQuestion(difficulty)` in each topic file) and a randomizer helper.
* The architecture **does not** have a database of questions (the progression and answers are saved to `progress.json`, but the questions themselves are made on-the-fly without any external database requirements).

---

### Query 2: Follow-up on Word Problems
Once the response is returned, ask the follow-up question by running:

```python
execute_agent_query("Does math-galaxy generate any word problem questions?")
```

**Expected Response Details:**
The agent will inspect the files in the `data/topics` directory and confirm that:
* The questions are currently purely numerical equations (coordinate grid representations, place value checks, decimal subtraction/addition, operations fractions calculations).
* There are **no word problems** (story or text-based questions) generated inside the topic JS files.
