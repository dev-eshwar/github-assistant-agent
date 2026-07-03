import os
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
from shared_tools import (
    read_file_content,
    list_directory,
    path_exists,
)

# Load the skill content
current_dir = os.path.dirname(os.path.abspath(__file__))
skill_path = os.path.join(current_dir, "SKILL.md")
with open(skill_path, "r", encoding="utf-8") as f:
    skill_content = f.read()

# Configure retries to handle 429 rate limits
retry_config = types.HttpRetryOptions(
    initial_delay=15.0,
    attempts=6,
    backoff_multiplier=1.5
)

# Define the Logic Reader Agent
logic_reader_agent = Agent(
    name="logic_reader_agent",
    description="Performs targeted code logic reading and path analysis on specific source code files in a repository.",
    instruction=skill_content,
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    tools=[
        read_file_content,
        list_directory,
        path_exists,
    ],
)


