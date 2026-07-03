#!/usr/bin/env python3
import os
import sys
import json
import re

def check_file_exists(path):
    if not os.path.exists(path):
        print(f"[FAIL] Missing expected file: {path}")
        return False
    print(f"[PASS] File exists: {path}")
    return True

def run_evals():
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate agent skills outputs.")
    parser.add_argument("--setup-mock", action="store_true", help="Set up a mock directory structure to run the evaluations on.")
    args = parser.parse_args()

    print("=== STARTING AGENT SKILLS EVALUATION ===")
    
    # 1. Resolve paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(base_dir)
    harness_dir = os.path.join(project_dir, ".harness")
    transit_dir = os.path.join(harness_dir, "transit")
    config_file = os.path.join(harness_dir, "config.json")
    
    if args.setup_mock:
        print("Setting up mock environment for evaluation...")
        os.makedirs(harness_dir, exist_ok=True)
        os.makedirs(transit_dir, exist_ok=True)
        
        # Setup mock config
        mock_wiki = os.path.join(project_dir, "test_env", "wiki")
        mock_repo = os.path.join(project_dir, "test_env", "repo")
        os.makedirs(mock_wiki, exist_ok=True)
        os.makedirs(mock_repo, exist_ok=True)
        
        config_data = {
            "repo_path": mock_repo,
            "wiki_path": mock_wiki,
            "github_url": "test-owner/test-repo",
            "commit_depth": 10
        }
        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=2)
            
        # Setup mock transit files
        with open(os.path.join(transit_dir, "01_init.json"), "w") as f:
            json.dump({"query": "What is the token leak?", "timestamp": "2026-07-02T11:59:20Z", "config": config_data}, f, indent=2)
        with open(os.path.join(transit_dir, "02_kb_status.json"), "w") as f:
            json.dump({"status": "success", "timestamp": "2026-07-02T11:59:21Z"}, f, indent=2)
        with open(os.path.join(transit_dir, "03_qa_result.json"), "w") as f:
            json.dump({"status": "found", "stdout": "Leak resolved in auth.py.", "code_references": ["auth.py"], "timestamp": "2026-07-02T11:59:22Z"}, f, indent=2)
        with open(os.path.join(transit_dir, "04_logic_analysis.json"), "w") as f:
            json.dump({"run": True, "files_analyzed": ["auth.py"], "stdout": "Analysis result.", "timestamp": "2026-07-02T11:59:23Z"}, f, indent=2)
        with open(os.path.join(transit_dir, "05_final_response.json"), "w") as f:
            json.dump({"final_output": "Leak resolved in auth.py.", "timestamp": "2026-07-02T11:59:24Z"}, f, indent=2)
        # Setup mock Wiki directory structure
        categories = ["architecture", "features", "history", "bugs", "security"]
        for cat in categories:
            cat_dir = os.path.join(mock_wiki, cat)
            os.makedirs(cat_dir, exist_ok=True)
            with open(os.path.join(cat_dir, "index.md"), "w") as f:
                f.write(f"# {cat.capitalize()} Index\n- [Sample item](sample.md)\n")
                
        # Setup mock component documents under architecture
        arch_dir = os.path.join(mock_wiki, "architecture")
        with open(os.path.join(arch_dir, "overview.md"), "w") as f:
            f.write("# Architecture Overview\nLogical components in the codebase.\n- [Auth Component](component_auth.md)\n")
        with open(os.path.join(arch_dir, "component_auth.md"), "w") as f:
            f.write("# Auth Component\n- `auth.py`\n\nHandles authentication logic.\n")
                
        # Setup mock global index README.md
        with open(os.path.join(mock_wiki, "README.md"), "w") as f:
            f.write("# Knowledge Base Index\n" + "\n".join([f"- [{c.capitalize()}]({c}/index.md)" for c in categories]))
            
        # Setup mock metadata
        with open(os.path.join(mock_wiki, ".metadata.json"), "w") as f:
            json.dump({"last_sync_timestamp": "2026-07-02T11:59:25Z", "last_sync_commit": "e4ea97c4bb022bb36bdb5a97ff4f9bda432d1666"}, f, indent=2)
            
        print("Mock environment setup complete.\n")

    # Read config to find wiki path
    if not os.path.exists(config_file):
        print(f"[ERROR] Config file not found at {config_file}. Please run the orchestrator or initialize the configuration first.")
        sys.exit(1)
        
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"[FAIL] Failed to parse config file: {e}")
        sys.exit(1)
        
    wiki_path = config.get("wiki_path")
    if not wiki_path:
        print("[FAIL] 'wiki_path' is missing from config.json")
        sys.exit(1)
        
    print(f"Using Wiki Path: {wiki_path}")
    print(f"Using Transit Path: {transit_dir}")
    
    all_passed = True
    
    # --- 1. Evaluate Orchestrator & Transit Files ---
    print("\n--- Evaluating Harness Transit States ---")
    transit_files = [
        "01_init.json",
        "02_kb_status.json",
        "03_qa_result.json",
        "04_logic_analysis.json",
        "05_final_response.json"
    ]
    
    for tf in transit_files:
        path = os.path.join(transit_dir, tf)
        if not check_file_exists(path):
            all_passed = False
            continue
            
        # Validate JSON format & schemas
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"[PASS] Valid JSON syntax in: {tf}")
            
            # Specific schema checks
            if tf == "01_init.json":
                if "query" not in data or "config" not in data:
                    print("[FAIL] 01_init.json is missing 'query' or 'config' keys")
                    all_passed = False
            elif tf == "02_kb_status.json":
                if "status" not in data:
                    print("[FAIL] 02_kb_status.json is missing 'status' key")
                    all_passed = False
            elif tf == "03_qa_result.json":
                if "status" not in data or "stdout" not in data or "code_references" not in data:
                    print("[FAIL] 03_qa_result.json is missing required keys ('status', 'stdout', 'code_references')")
                    all_passed = False
                # Strict missing response check
                if data.get("status") == "not_found":
                    expected_msg = "This information is not present in the current knowledge base."
                    if expected_msg not in data.get("stdout", ""):
                        print(f"[FAIL] 03_qa_result.json has 'not_found' status but output does not contain strict missing message: '{expected_msg}'")
                        all_passed = False
            elif tf == "04_logic_analysis.json":
                if "run" not in data:
                    print("[FAIL] 04_logic_analysis.json is missing 'run' key")
                    all_passed = False
            elif tf == "05_final_response.json":
                if "final_output" not in data:
                    print("[FAIL] 05_final_response.json is missing 'final_output' key")
                    all_passed = False
                    
        except Exception as e:
            print(f"[FAIL] Error parsing JSON file {tf}: {e}")
            all_passed = False

    # --- 2. Evaluate Wiki Structure & Formatting ---
    print("\n--- Evaluating Wiki Structure ---")
    categories = ["architecture", "features", "history", "bugs", "security"]
    
    # Check category directories
    for cat in categories:
        cat_dir = os.path.join(wiki_path, cat)
        if not os.path.isdir(cat_dir):
            print(f"[FAIL] Missing category directory: {cat_dir}")
            all_passed = False
            continue
        print(f"[PASS] Category directory exists: {cat}")
        
        # Check index file in each category
        index_file = os.path.join(cat_dir, "index.md")
        if not check_file_exists(index_file):
            all_passed = False
        else:
            # Check for relative link consistency (avoiding absolute paths in index)
            with open(index_file, "r", encoding="utf-8") as f:
                index_content = f.read()
                if "file:///" in index_content or "C:\\" in index_content or "/Users/" in index_content:
                    print(f"[FAIL] Category index {cat}/index.md contains absolute paths. Only relative paths are allowed.")
                    all_passed = False
                else:
                    print(f"[PASS] Category index {cat}/index.md uses clean relative links.")
    # Check codebase component mapping documents
    arch_dir = os.path.join(wiki_path, "architecture")
    if os.path.isdir(arch_dir):
        overview_file = os.path.join(arch_dir, "overview.md")
        if not check_file_exists(overview_file):
            all_passed = False
        else:
            print("[PASS] overview.md exists in architecture/")
            
        # Check that there is at least one component page
        component_files = [f for f in os.listdir(arch_dir) if f.startswith("component_") and f.endswith(".md")]
        if not component_files:
            print("[FAIL] Missing component mapping documentation (component_*.md) in architecture/")
            all_passed = False
        else:
            print(f"[PASS] Found {len(component_files)} codebase component documentation files (e.g. {component_files[0]})")
            
    # Check global README.md
    global_readme = os.path.join(wiki_path, "README.md")
    if not check_file_exists(global_readme):
        all_passed = False
    else:
        with open(global_readme, "r", encoding="utf-8") as f:
            readme_content = f.read()
            # Must mention categories
            for cat in categories:
                if cat not in readme_content.lower():
                    print(f"[FAIL] README.md index is missing mention of category: {cat}")
                    all_passed = False
                    
    # Check .metadata.json
    metadata_file = os.path.join(wiki_path, ".metadata.json")
    if not check_file_exists(metadata_file):
        all_passed = False
    else:
        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
            if "last_sync_timestamp" not in meta or "last_sync_commit" not in meta:
                print("[FAIL] .metadata.json is missing required sync fields")
                all_passed = False
            else:
                print("[PASS] .metadata.json structure is valid")
        except Exception as e:
            print(f"[FAIL] Failed to parse .metadata.json: {e}")
            all_passed = False

    print("\n========================================")
    if all_passed:
        print("RESULT: ALL EVALUATION CHECKS PASSED!")
        sys.exit(0)
    else:
        print("RESULT: SOME EVALUATION CHECKS FAILED. Please review output above.")
        sys.exit(1)

if __name__ == "__main__":
    run_evals()
