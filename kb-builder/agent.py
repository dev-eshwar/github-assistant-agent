import os
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
from shared_tools import (
    run_shell_command,
    read_file_content,
    write_file_content,
    list_directory,
    path_exists,
    make_directory,
    http_get_request,
)

# Load the skill content
current_dir = os.path.dirname(os.path.abspath(__file__))
skill_path = os.path.join(current_dir, "SKILL.md")
with open(skill_path, "r", encoding="utf-8") as f:
    skill_content = f.read()

# Configure retries to handle 429 rate limits
retry_config = types.HttpRetryOptions(
    initial_delay=15.0,
    attempts=6
)

# Define the KB Builder Agent
kb_builder_agent = Agent(
    name="kb_builder_agent",
    description="Builds or incrementally updates a local markdown-based Wiki/Knowledge Base from a target Git repository and GitHub issues.",
    instruction=skill_content,
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    tools=[
        run_shell_command,
        read_file_content,
        write_file_content,
        list_directory,
        path_exists,
        make_directory,
        http_get_request,
    ],
)


