---
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

## Tool Call Constraints
- The only valid tools you can call are: `run_shell_command`, `read_file_content`, `write_file_content`, `list_directory`, `path_exists`, `make_directory`, `http_get_request`.
- Do NOT call any other tools.
- To provide the final summary of what was synced, do NOT call any tool. Simply return the summary as a direct text message.
