# Agent-Driven Skills (Interactive Mode)

This folder contains markdown-based skill definitions (`SKILL.md`) that allow an AI coding agent to execute the knowledge graph, query, and code logic analysis workflows directly. Because it runs within the agent's active chat context, you can ask follow-up questions and interactively guide the execution.

## Directory Structure
- [harness-orchestrator/SKILL.md](harness-orchestrator/SKILL.md): Coordinator instructions for managing sessions, updating status, and chaining skills.
- [kb-builder/SKILL.md](kb-builder/SKILL.md): Incremental Git & GitHub issues documentation wiki sync logic.
- [qa/SKILL.md](qa/SKILL.md): Query parsing, document ranking, QA generation, and timeline construction rules.
- [logic-reader/SKILL.md](logic-reader/SKILL.md): Deep file trace and logic inspection instructions.

---

## How to Run This Mode (User Instructions)

To execute this assistant interactively with your AI Coding Agent, follow these steps:

### Step 1: Open your Coding Agent
Start a new chat session with your AI agent (e.g. Antigravity) inside this workspace.

### Step 2: Trigger the Harness Orchestrator Skill
Send a prompt to the agent telling it to read and follow the master coordinator skill:
```text
Please read the harness-orchestrator skill in agent_skills/harness-orchestrator/SKILL.md and use it to answer my question: "What is the history of the token leak?"
```
*(Replace the query with any question you want to ask about the repository).*

### Step 3: Agent Execution
The agent will read the instruction files and perform the following tasks sequentially:
1. Initialize configuration in [../.harness/config.json](../.harness/config.json).
2. Execute the [kb-builder/SKILL.md](kb-builder/SKILL.md) skill to sync git commits/issues and build the markdown wiki directory structure.
3. Execute the [qa/SKILL.md](qa/SKILL.md) skill to search files, score relevancy, formulate the answer, and extract code references.
4. Execute the [logic-reader/SKILL.md](logic-reader/SKILL.md) skill (if code logic analysis is needed) to view source files and trace execution paths.
5. Save step progress to JSON logs in the `../.harness/transit/` folder.
6. Present the final response in the chat window.

### Step 4: Ask Follow-Up Questions (Interactive Phase)
Since the agent maintains conversational context in the chat, you can ask follow-up questions directly. E.g.:
* *"Can you explain that specific authentication logic detail further?"*
* *"Are there any other commits related to that leak?"*
* *"Propose a code diff to fix the bug you found."*

The agent will leverage the generated wiki files and its tools to guide you through the solution.

---

## Validating Agent Outputs
To verify that the agent correctly created all expected wiki folders, index files, and transit log schemas, run:
```bash
python run_evals.py
```
*(Run this command from inside the `agent_skills/` directory, or run `python agent_skills/run_evals.py` from the project root).*
