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

# Define the QA Agent
qa_agent = Agent(
    name="qa_agent",
    description="Answers questions using strictly the generated Wiki markdown files as the source of truth, and identifies relevant code file references.",
    instruction=skill_content,
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    tools=[
        read_file_content,
        list_directory,
        path_exists,
    ],
)


