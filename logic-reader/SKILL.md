---
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
