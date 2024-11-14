#!/usr/bin/env python
import sys
import warnings
import os
import logging
import shutil
from pathlib import Path

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

    try:
        crew = WebDevelopersCrew()
        crew.inputs = inputs
        crew.initialize_cache(inputs["theme"])

        # Run crew with process_inputs
        result = crew.crew().kickoff()

        # Verify outputs
        if crew.cache_manager:
            for agent in ["product_manager", "ui_ux_designer"]:
                output = crew.cache_manager.get_agent_output(agent)
                if output:
                    logger.info(f"{agent} output verified in cache")
                else:
                    logger.warning(f"{agent} output not found in cache")

        return result

    except Exception as e:
        logger.error(f"An error occurred while running the crew: {str(e)}")
        logger.exception("Full traceback:")
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
    try:
        logger.info("Running frontend task with existing cache")
        crew = WebDevelopersCrew()

        # Initialize cache
        crew.initialize_cache(THEMES[0])

        # Get cached design
        cached_design = crew.cache_manager.get_agent_output("ui_ux_designer")
        if not cached_design:
            logger.error("No UI/UX design found in cache!")
            print(
                """
            Error: UI/UX design specifications not found in cache.
            Please run the full crew process first using:
                crewai run
            
            Or provide design specifications manually.
            """
            )
            return 1

        # Run frontend task with cached design
        result = crew.run_frontend_task(cached_design)

        # Verify output files were created
        output_dir = Path("output")
        expected_files = ["index.html", "style.css", "script.js"]

        for file in expected_files:
            if not (output_dir / file).exists():
                logger.warning(f"Expected output file {file} not found!")
            else:
                logger.info(f"Generated {file} successfully")

        return 0

    except Exception as e:
        logger.error(f"Error running frontend task: {e}")
        logger.exception("Full traceback:")
        return 1


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
