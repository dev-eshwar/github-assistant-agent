import os
import json
import importlib.util
from datetime import datetime
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from shared_tools import (
    read_file_content,
    write_file_content,
    list_directory,
    path_exists,
    make_directory,
)

# Helper to dynamically import modules from hyphenated directories
def import_agent_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Resolve paths to sub-agents
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Import sub-agents
kb_builder_module = import_agent_from_path(
    "kb_builder_agent_instance",
    os.path.join(parent_dir, "kb-builder", "agent.py")
)
kb_builder_agent_obj = kb_builder_module.kb_builder_agent

qa_module = import_agent_from_path(
    "qa_agent_instance",
    os.path.join(parent_dir, "qa", "agent.py")
)
qa_agent_obj = qa_module.qa_agent

logic_reader_module = import_agent_from_path(
    "logic_reader_agent_instance",
    os.path.join(parent_dir, "logic-reader", "agent.py")
)
logic_reader_agent_obj = logic_reader_module.logic_reader_agent


# Define Orchestrator Tools
def initialize_session(query: str) -> str:
    """Initializes the coordination session. Reads or creates the config,
    clears previous transit files, and writes the 01_init.json event.
    
    Args:
        query: The user's query/question.
    """
    try:
        harness_dir = os.path.join(parent_dir, ".harness")
        transit_dir = os.path.join(harness_dir, "transit")
        config_path = os.path.join(harness_dir, "config.json")
        
        # Verify directory structure
        os.makedirs(transit_dir, exist_ok=True)
        
        # Read or create config.json
        config_data = {}
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        else:
            config_data = {
                "repo_path": "./repo",
                "wiki_path": "./wiki",
                "github_url": "",
                "commit_depth": 100
            }
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
                
        # Clear old transit files
        for f in os.listdir(transit_dir):
            if f.endswith(".json"):
                try:
                    os.remove(os.path.join(transit_dir, f))
                except Exception:
                    pass
                    
        # Create 01_init.json
        init_event = {
            "query": query,
            "timestamp": datetime.now().isoformat() + "Z",
            "config": config_data
        }
        with open(os.path.join(transit_dir, "01_init.json"), "w", encoding="utf-8") as f:
            json.dump(init_event, f, indent=2)
            
        return f"Session successfully initialized. Configuration: {json.dumps(config_data)}"
    except Exception as e:
        return f"Error initializing session: {e}"

def write_kb_status(status: str) -> str:
    """Writes the status/result of the KB synchronization step to 02_kb_status.json.
    
    Args:
        status: The synchronization status (e.g. 'success').
    """
    try:
        transit_dir = os.path.join(parent_dir, ".harness", "transit")
        kb_status_event = {
            "status": status,
            "timestamp": datetime.now().isoformat() + "Z"
        }
        with open(os.path.join(transit_dir, "02_kb_status.json"), "w", encoding="utf-8") as f:
            json.dump(kb_status_event, f, indent=2)
        return "Successfully wrote 02_kb_status.json"
    except Exception as e:
        return f"Error writing KB status: {e}"

def write_qa_result(status: str, qa_output_text: str, code_references: list[str]) -> str:
    """Writes the results of the Wiki QA step to 03_qa_result.json.
    
    Args:
        status: Whether the answer was found or not ('found' or 'not_found').
        qa_output_text: The synthesized text answer from the QA agent.
        code_references: List of code file references found in the wiki.
    """
    try:
        transit_dir = os.path.join(parent_dir, ".harness", "transit")
        qa_event = {
            "status": status,
            "stdout": qa_output_text,
            "code_references": code_references,
            "timestamp": datetime.now().isoformat() + "Z"
        }
        with open(os.path.join(transit_dir, "03_qa_result.json"), "w", encoding="utf-8") as f:
            json.dump(qa_event, f, indent=2)
        return "Successfully wrote 03_qa_result.json"
    except Exception as e:
        return f"Error writing QA result: {e}"

def write_logic_analysis_report(run: bool, files_analyzed: list[str], stdout: str, reason: str = "") -> str:
    """Writes the results of the Logic Analysis step to 04_logic_analysis.json.
    
    Args:
        run: True if logic analysis was executed, False if skipped.
        files_analyzed: List of files analyzed during this step.
        stdout: The generated markdown analysis report.
        reason: The reason for skipping analysis if run is False.
    """
    try:
        transit_dir = os.path.join(parent_dir, ".harness", "transit")
        logic_event = {
            "run": run,
            "files_analyzed": files_analyzed,
            "stdout": stdout,
            "timestamp": datetime.now().isoformat() + "Z"
        }
        if not run:
            logic_event["reason"] = reason
            
        with open(os.path.join(transit_dir, "04_logic_analysis.json"), "w", encoding="utf-8") as f:
            json.dump(logic_event, f, indent=2)
        return "Successfully wrote 04_logic_analysis.json"
    except Exception as e:
        return f"Error writing logic analysis: {e}"

def write_final_response(final_output: str) -> str:
    """Assembles and saves the final response string to 05_final_response.json.
    
    Args:
        final_output: The final compiled response to present to the user.
    """
    try:
        transit_dir = os.path.join(parent_dir, ".harness", "transit")
        final_event = {
            "final_output": final_output,
            "timestamp": datetime.now().isoformat() + "Z"
        }
        with open(os.path.join(transit_dir, "05_final_response.json"), "w", encoding="utf-8") as f:
            json.dump(final_event, f, indent=2)
        return "Successfully wrote 05_final_response.json"
    except Exception as e:
        return f"Error writing final response: {e}"

def read_session_config() -> str:
    """Reads and returns the config.json data as a JSON string."""
    try:
        config_path = os.path.join(parent_dir, ".harness", "config.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.dumps(json.load(f))
        return "Config file not found"
    except Exception as e:
        return f"Error reading config: {e}"

def update_session_config(repo_path: str, wiki_path: str, github_url: str, commit_depth: int) -> str:
    """Updates the config.json file with new configuration parameters.
    
    Args:
        repo_path: Path to the local git clone.
        wiki_path: Path to the output Wiki folder.
        github_url: The GitHub repo URL or owner/repo.
        commit_depth: Max commits to sync.
    """
    try:
        config_path = os.path.join(parent_dir, ".harness", "config.json")
        config_data = {
            "repo_path": repo_path,
            "wiki_path": wiki_path,
            "github_url": github_url,
            "commit_depth": commit_depth
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
        return f"Config updated: {json.dumps(config_data)}"
    except Exception as e:
        return f"Error updating config: {e}"

async def kb_builder_agent(query: str) -> str:
    """Executes the KB Builder sub-agent to parse commits/issues and build the Wiki database.
    
    Args:
        query: Operational query details for the KB builder.
    """
    try:
        # Resolve config path
        harness_dir = os.path.join(parent_dir, ".harness")
        config_path = os.path.join(harness_dir, "config.json")
        config_data = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except Exception:
                pass
        
        # Structure the prompt for the sub-agent
        sub_agent_prompt = f"config: {json.dumps(config_data)}\nquery: {query}"
        
        runner = Runner(
            app_name="kb-builder-subapp",
            agent=kb_builder_agent_obj,
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
            artifact_service=InMemoryArtifactService(),
            auto_create_session=True,
        )
        content = types.Content(role="user", parts=[types.Part.from_text(text=sub_agent_prompt)])
        output = ""
        async for event in runner.run_async(user_id="sub_user", session_id="sub_session", new_message=content):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if getattr(part, "function_call", None) is not None:
                        continue
                    if getattr(part, "text", None):
                        output += part.text
        return output if output else "KB sync completed successfully."
    except Exception as e:
        return f"Error running KB Builder: {e}"

async def qa_agent(query: str) -> str:
    """Executes the Wiki QA sub-agent to answer a query using strictly the local Wiki markdown files.
    
    Args:
        query: The question to answer.
    """
    try:
        # Resolve config path and extract wiki_path
        harness_dir = os.path.join(parent_dir, ".harness")
        config_path = os.path.join(harness_dir, "config.json")
        wiki_path = "./wiki"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                    wiki_path = config_data.get("wiki_path", wiki_path)
            except Exception:
                pass
        
        # Structure the prompt for the sub-agent
        sub_agent_prompt = f"wiki_path: {wiki_path}\nquery: {query}"
        
        runner = Runner(
            app_name="qa-subapp",
            agent=qa_agent_obj,
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
            artifact_service=InMemoryArtifactService(),
            auto_create_session=True,
        )
        content = types.Content(role="user", parts=[types.Part.from_text(text=sub_agent_prompt)])
        output = ""
        async for event in runner.run_async(user_id="sub_user", session_id="sub_session", new_message=content):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if getattr(part, "function_call", None) is not None:
                        continue
                    if getattr(part, "text", None):
                        output += part.text
        return output if output else "No response from QA agent."
    except Exception as e:
        return f"Error running QA Agent: {e}"

async def logic_reader_agent(query: str) -> str:
    """Executes the Logic Reader sub-agent to perform deep code inspection and trace execution flows.
    
    Args:
        query: Operational query details including file paths and logic analysis request.
    """
    try:
        # Resolve config path and extract repo_path
        harness_dir = os.path.join(parent_dir, ".harness")
        config_path = os.path.join(harness_dir, "config.json")
        repo_path = "./repo"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                    repo_path = config_data.get("repo_path", repo_path)
            except Exception:
                pass
        
        # Extract files to analyze from the QA result
        transit_dir = os.path.join(harness_dir, "transit")
        qa_result_path = os.path.join(transit_dir, "03_qa_result.json")
        files_to_analyze = []
        if os.path.exists(qa_result_path):
            try:
                with open(qa_result_path, "r", encoding="utf-8") as f:
                    qa_data = json.load(f)
                    files_to_analyze = qa_data.get("code_references", [])
            except Exception:
                pass

        # Structure the prompt for the sub-agent
        sub_agent_prompt = f"repo_path: {repo_path}\n"
        if files_to_analyze:
            sub_agent_prompt += f"files: {json.dumps(files_to_analyze)}\n"
        sub_agent_prompt += f"query: {query}"
        
        runner = Runner(
            app_name="logic-reader-subapp",
            agent=logic_reader_agent_obj,
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
            artifact_service=InMemoryArtifactService(),
            auto_create_session=True,
        )
        content = types.Content(role="user", parts=[types.Part.from_text(text=sub_agent_prompt)])
        output = ""
        async for event in runner.run_async(user_id="sub_user", session_id="sub_session", new_message=content):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if getattr(part, "function_call", None) is not None:
                        continue
                    if getattr(part, "text", None):
                        output += part.text
        return output if output else "No response from Logic Reader."
    except Exception as e:
        return f"Error running Logic Reader: {e}"


# Load the skill content
skill_path = os.path.join(current_dir, "SKILL.md")
with open(skill_path, "r", encoding="utf-8") as f:
    skill_content = f.read()

# Configure retries to handle 429 rate limits
retry_config = types.HttpRetryOptions(
    initial_delay=15.0,
    attempts=6
)

# Define the Harness Orchestrator Agent
harness_orchestrator_agent = Agent(
    name="harness_orchestrator_agent",
    description="Orchestrates the multi-agent workflow for analyzing a repository, building/updating a knowledge base, answering questions, and performing code logic reviews.",
    instruction=skill_content,
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    tools=[
        initialize_session,
        write_kb_status,
        write_qa_result,
        write_logic_analysis_report,
        write_final_response,
        read_session_config,
        update_session_config,
        read_file_content,
        write_file_content,
        list_directory,
        path_exists,
        make_directory,
        kb_builder_agent,
        qa_agent,
        logic_reader_agent,
    ],
)
