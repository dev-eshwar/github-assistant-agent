---
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
