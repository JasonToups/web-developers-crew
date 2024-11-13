#!/usr/bin/env python
import sys
import warnings

from web_developers_crew.crew import WebDevelopersCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

# List of topics to create landing pages for
TOPICS = [
    "Books",
    "Business",
    "Developer Tools",
    "Education",
    "Entertainment",
    "Finance",
    "Food & Drink",
    "Games",
    "Graphics",
    "Health",
    "Lifestyle",
    "Medical",
    "Music",
    "News",
    "Other",
    "Photo & Video",
    "Productivity",
    "Reference",
    "Shopping",
    "Social",
    "Sports",
    "Travel",
    "Utilities",
    "Weather",
]


def run():
    """
    Run the crew.
    """
    inputs = {"topic": TOPICS[0]}
    WebDevelopersCrew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {"topic": TOPICS[0]}
    try:
        WebDevelopersCrew().crew().train(
            n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        WebDevelopersCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {"topic": TOPICS[0]}
    try:
        WebDevelopersCrew().crew().test(
            n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def run_frontend_only():
    """
    Run only the frontend development task using the UI/UX design output.
    """
    inputs = {"topic": TOPICS[0]}
    crew = WebDevelopersCrew()

    # Get the frontend engineer agent
    frontend_engineer = crew.frontend_engineer()

    # Get the development task
    dev_task = crew.development_task()
    dev_task.agent = frontend_engineer
    dev_task.callback = crew.handle_development_output

    # Execute just the frontend task
    dev_task.execute_sync(frontend_engineer)


def main():
    """
    Main entry point for the CLI
    """
    if len(sys.argv) > 1 and sys.argv[1] == "frontend":
        run_frontend_only()
    else:
        run()


if __name__ == "__main__":
    main()
