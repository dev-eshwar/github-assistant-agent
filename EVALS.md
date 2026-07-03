# Agent Skills Evaluation Guide & Scenarios

This document defines the evaluation criteria, manual test cases, and automated validation rules for the markdown-based agent skills.

---

## 1. KB Builder Skill Evaluation (`kb-builder`)
**Goal:** Verify the agent correctly parses git history, categorizes information, outputs valid markdown files, and maintains index files.

### Scenario A: Clean Initialization
* **Input:** A test repository with 3 commits (one containing `"feat:"`, one containing `"fix:"` referencing issue `#10`, one containing `"security:"`).
* **Expected Output:**
  - Directory structure created with `architecture/`, `features/`, `history/`, `bugs/`, `security/`.
  - Inside `architecture/`, an `overview.md` file exists detailing the logical components.
  - Inside `architecture/`, `component_<name>.md` files exist for each parsed codebase segment, listing the relevant file paths and responsibilities.
  - `.metadata.json` created containing `last_sync_commit` and `last_sync_timestamp`.
  - Inside `features/`, `commit_<hash>.md` file exists.
  - Inside `bugs/`, `commit_<hash>.md` exists, containing a relative link `[Issue #10](../bugs/issue_10.md)` and a `## Affected Architectural Components` section linking back to the architecture component markdown documentation.
  - Inside `bugs/index.md`, a relative link to the commit file is listed.
  - `README.md` at root lists all 5 categories with correct item counts.

### Validation Checklist:
- [ ] No empty markdown files created.
- [ ] Relative links use `../category/file.md` format rather than absolute filesystem paths.
- [ ] Component documentation pages (`component_<name>.md`) contain file listings and logical scope.
- [ ] Commit and issue files include links pointing to the affected architectural components.
- [ ] `.metadata.json` updated with the latest commit hash.

---

## 2. Wiki-Based QA Skill Evaluation (`qa`)
**Goal:** Verify the agent restricts its source of truth to the Wiki files and formats answers correctly.

### Scenario B: Answer Found in Wiki
* **Input:** Query: "What is the token leak history?" with a wiki containing a matching security commit file.
* **Expected Output:**
  - 2-3 direct bullet points summarizing the leak history.
  - A `## Code References` section listing `auth.py`.
  - A history timeline table listing the dates, commit hashes, and description of the leak and resolution.

### Scenario C: Answer Missing (Strict Rule)
* **Input:** Query: "How to compile C++ code on windows?"
* **Expected Output:**
  - Exactly: `This information is not present in the current knowledge base.` (No extra commentary or markdown formatting).

---

## 3. Code Logic Reader Skill Evaluation (`logic-reader`)
**Goal:** Verify targeted code reading and path analysis.

### Scenario D: Logic Trace
* **Input:** Target file `auth.py`, Query: "Analyze how tokens are generated."
* **Expected Output:**
  - Detailed explanation of `generate_token` function.
  - Highlights use of `hashlib.sha256` hashing.
  - Clear recommendations on logic safety.

---

## 4. Orchestrator Skill Evaluation (`harness-orchestrator`)
**Goal:** Verify step-by-step state transition via transit files.

### Expected Output Sequence:
- `01_init.json`: Initial configuration and query.
- `02_kb_status.json`: Contains sync status.
- `03_qa_result.json`: Contains QA result + code references.
- `04_logic_analysis.json`: Contains logic analysis results or skipped state.
- `05_final_response.json`: Compiled final response string.
