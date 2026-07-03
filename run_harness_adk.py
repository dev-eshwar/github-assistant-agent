#!/usr/bin/env environment python3
import os
import sys
import argparse
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types

import importlib.util

def import_agent_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import the orchestrator agent dynamically due to hyphenated directory name
current_dir = os.path.dirname(os.path.abspath(__file__))
harness_module = import_agent_from_path(
    "harness_orchestrator_agent",
    os.path.join(current_dir, "harness-orchestrator", "agent.py")
)
harness_orchestrator_agent = harness_module.harness_orchestrator_agent

def main():
    parser = argparse.ArgumentParser(description="Run the ADK Harness Orchestrator Agent.")
    parser.add_argument("query", nargs="?", help="The user query/question to analyze")
    args = parser.parse_args()

    query = args.query
    if not query:
        print("No query provided. Please enter your query:")
        query = input("> ").strip()
        if not query:
            print("Empty query. Exiting.")
            sys.exit(0)

    print(f"=== Running ADK Multi-Agent Harness Orchestrator ===")
    print(f"Query: '{query}'\n")

    # Instantiate the runner with the main orchestrator agent
    runner = Runner(
        app_name="harness-orchestrator-app",
        agent=harness_orchestrator_agent,
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
        artifact_service=InMemoryArtifactService(),
        auto_create_session=True,
    )

    # Wrap the query into GenAI Content types
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=query)]
    )

    # Run the agent using the runner
    events_generator = runner.run(
        user_id="user_123",
        session_id="session_123",
        new_message=content
    )

    # Iterate over events and print output
    final_output = ""
    for event in events_generator:
        # Check if the event has content parts
        if event.content and event.content.parts:
            for part in event.content.parts:
                # Print agent thoughts
                if getattr(part, "thought", None):
                    sys.stdout.write(f"[Thought] {part.text}\n")
                    sys.stdout.flush()
                # Print agent text response
                elif getattr(part, "text", None):
                    sys.stdout.write(part.text)
                    sys.stdout.flush()
                    final_output += part.text

    print("\n\n=== Run Complete ===")

if __name__ == "__main__":
    main()
