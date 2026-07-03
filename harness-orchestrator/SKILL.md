---
name: harness-orchestrator
description: Orchestrates the multi-agent workflow for analyzing a repository, building/updating a knowledge base, answering questions, and performing code logic reviews.
---

# Harness Orchestrator Skill

This skill coordinates the workflow between sub-agents executing the `kb-builder`, `qa`, and `logic-reader` skills. It enables you (the agent) to run the steps manually or delegate tasks to specialized sub-agents.

---

## Sub-Agent Definitions & Roles

When orchestrating, you should define and invoke the following specialized sub-agents:

1. **`kb-builder-agent`**:
   - **Role:** `KB Builder Sub-Agent`
   - **Responsibility:** Executes the `kb-builder` skill. Parses local Git history, scans codebase structure, catalogs logical architectural elements, queries GitHub Issues/PRs, and regenerates category indices.
2. **`qa-agent`**:
   - **Role:** `Wiki QA Sub-Agent`
   - **Responsibility:** Executes the `qa` skill. Restricts searches strictly to Wiki markdown directories, ranks articles by query keywords, and formats summaries and code references.
3. **`logic-reader-agent`**:
   - **Role:** `Logic Analyzer Sub-Agent`
   - **Responsibility:** Executes the `logic-reader` skill. Inspects source code files, traces execution control flows, analyzes variable values, and diagnoses logic bugs.

---

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

---

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
1. Invoke the **`kb-builder-agent`** passing the config and `kb-builder/SKILL.md` instructions.
2. If the builder agent skips sync because no files have changed (based on last modified time comparison), log this status.
3. After completion, write a status summary to `02_kb_status.json`:
   ```json
   {
     "status": "success",
     "timestamp": "ISO_TIMESTAMP"
   }
   ```

### Step 3: Run Wiki-Based QA
1. Invoke the **`qa-agent`** passing the query and `qa/SKILL.md` instructions.
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
   - Re-invoke the **`kb-builder-agent`** with instructions to force-bypass modifications checks and pull a deeper git history/GitHub Issues sync.
   - Once the re-sync completes, re-invoke the **`qa-agent`** on the updated Wiki.
   - Update `03_qa_result.json` with the new QA outcome.
3. If still not found or `commit_depth` is already maximum, proceed to Step 5.

### Step 4: Logic Analysis (Conditional)
1. Analyze the query for keywords indicating logic/code analysis (e.g., `analyze`, `bug`, `why`, `code`, `logic`, `fix`, `read`, `error`).
2. If `03_qa_result.json` contains `code_references` and the query implies logic analysis:
   - Invoke the **`logic-reader-agent`** with `logic-reader/SKILL.md` for those referenced files.
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

---

## Interactive Follow-Up Questions Loop

When the user asks a follow-up question after receiving the final response:
1. **Context Check:** Assess if the follow-up question refers to information/code files already present in the current Wiki or generated QA/Logic reports.
2. **Looping Logic:**
   - **DO NOT** clear `.harness/transit/` or re-initialize the session.
   - **DO NOT** re-run the `kb-builder-agent` (skip Step 2) unless the user explicitly requests to sync/update new code changes or fresh commits.
   - Directly run **Step 3 (Wiki-Based QA)** and/or **Step 4 (Logic Analysis)** using the new follow-up query against the existing Wiki and code files.
   - Update the relevant `03_qa_result.json` and `04_logic_analysis.json` files and compile the new answer.
3. Keep the session active for further follow-up loops.
