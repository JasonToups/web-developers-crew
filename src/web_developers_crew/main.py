#!/usr/bin/env python
import sys
import warnings
import os
import logging
import shutil

from web_developers_crew.crew import WebDevelopersCrew
from .utils.cache_inspector import inspect_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# List of themes for landing page generation
THEMES = [
    "Books",
    "Business",
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


def clear_cache():
    """Clear all cached outputs"""
    cache_dir = os.path.join("output")
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        logger.info("Cache cleared successfully")


def run():
    """Run the crew"""
    inputs = {
        "theme": THEMES[0],
        "topic": "",
        "page_type": "",
        "product_output": "",
        "design_output": "",
    }

    logger.info("Starting run")

    crew = WebDevelopersCrew()
    crew.inputs = inputs  # Set inputs before initializing cache
    crew.initialize_cache(inputs["theme"])

    try:
        result = crew.crew().kickoff(inputs=inputs)

        # Verify cache after run
        if crew.cache_manager:
            design_cache = crew.cache_manager.get_agent_output("ui_ux_designer")
            if design_cache:
                logger.info("UI/UX design cache verified")
            else:
                logger.warning("UI/UX design cache not found after run")

        return result
    except Exception as e:
        logger.error(f"An error occurred while running the crew: {str(e)}")
        raise


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {"topic": THEMES[0]}
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
    inputs = {"topic": THEMES[0]}
    try:
        WebDevelopersCrew().crew().test(
            n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def run_frontend():
    """Run only the frontend task using cached design"""
    inputs = {"theme": THEMES[0]}
    crew = WebDevelopersCrew()
    crew.inputs = inputs

    # Don't clear cache for frontend-only runs
    crew.initialize_cache(inputs["theme"])
    logger.info("Running frontend task with existing cache")

    try:
        cached_design = crew.cache_manager.get_agent_output("ui_ux_designer")
        if not cached_design:
            logger.error("No cached design found. Please run full crew first.")
            return 1

        result = crew.run_frontend_task(cached_design)
        return result
    except Exception as e:
        logger.error(f"Error running frontend task: {str(e)}")
        raise


def inspect():
    """Inspect the cache contents"""
    inspect_cache()


def main():
    """Main entry point for the CLI"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "frontend":
            run_frontend()
        elif sys.argv[1] == "clear-cache":
            clear_cache()
        elif sys.argv[1] == "inspect":
            inspect()
        else:
            run()
    else:
        run()


if __name__ == "__main__":
    main()
