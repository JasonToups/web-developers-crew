#!/usr/bin/env python
import sys
import warnings
import os

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
    """Run the crew"""
    inputs = {"topic": "Books"}  # Default topic
    crew = WebDevelopersCrew()
    crew.initialize_cache(inputs["topic"])

    try:
        result = crew.crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        logger.error(f"An error occurred while running the crew: {str(e)}")
        raise


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


def clear_cache():
    """Clear all cached outputs"""
    import shutil

    cache_dir = os.path.join("output")
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        print("Cache cleared successfully")


def main():
    """Main entry point for the CLI"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "frontend":
            inputs = {"topic": TOPICS[0]}
            crew = WebDevelopersCrew()
            crew.inputs = inputs
            crew.initialize_cache(inputs["topic"])
            cached_design = crew.cache_manager.get_agent_output("ui_ux_designer")
            crew.run_frontend_task(cached_design)
        elif sys.argv[1] == "clear-cache":
            clear_cache()
        else:
            run()
    else:
        run()


if __name__ == "__main__":
    main()
