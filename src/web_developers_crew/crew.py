from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os
import logging
from .utils.cache_manager import CacheManager
from .utils.template_manager import TemplateManager
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


@CrewBase
class WebDevelopersCrew:
    """WebDevelopersCrew crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        # Load config files
        config_dir = Path(__file__).parent / "config"

        with open(config_dir / "tasks.yaml", "r") as f:
            self.tasks_config = yaml.safe_load(f)

        with open(config_dir / "agents.yaml", "r") as f:
            self.agents_config = yaml.safe_load(f)

        self.inputs = None
        self.cache_manager = None
        self.template_manager = TemplateManager()
        self.logger = logging.getLogger(__name__)
        self.topic = None

    def initialize_cache(self, topic: str):
        """Initialize cache with topic"""
        if not self.inputs:
            logger.warning("Inputs not set before cache initialization")
            self.inputs = {"theme": topic}

        self.cache_manager = CacheManager(topic)
        logger.info(f"Cache initialized for topic: {topic}")

    def run_frontend_task(self, cached_design: str = None):
        """Run the frontend development task"""
        # Initialize inputs if not already set
        if self.inputs is None:
            self.inputs = {"theme": "Books"}  # Default theme

        frontend_engineer = self.frontend_engineer()
        dev_task = self.development_task()

        # If we have cached design, include it in the task context
        if cached_design:
            dev_task.context = (
                f"Using this UI/UX design:\n{cached_design}\n\n" + dev_task.context
            )

        dev_task.agent = frontend_engineer
        dev_task.callback = self.handle_development_output
        return dev_task.execute_sync(frontend_engineer)

    @agent
    def product_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["product_manager"],
            verbose=True,
        )

    @agent
    def ui_ux_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["ui_ux_designer"],
            verbose=True,
        )

    @agent
    def frontend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config["frontend_engineer"],
            verbose=True,
        )

    @task
    def product_requirements_task(self) -> Task:
        """Create the product requirements task"""
        task_config = self.tasks_config["product_requirements_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.product_manager(),
        )

    @task
    def design_task(self) -> Task:
        """Create the design task"""
        task_config = self.tasks_config["design_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.ui_ux_designer(),
        )

    @task
    def development_task(self) -> Task:
        """Create the development task"""
        task_config = self.tasks_config["development_task"]
        return Task(
            description=task_config["description"],
            expected_output=task_config["expected_output"],
            agent=self.frontend_engineer(),
        )

    def handle_development_output(self, output):
        """Helper method to handle the development task output"""
        # Add debug logging at start
        logger.debug(
            f"Starting handle_development_output with output: {output[:100]}..."
        )
        self.logger.info("Processing development output...")

        try:
            if self.inputs is None:
                self.logger.error("Inputs not initialized")
                raise ValueError("Inputs not initialized")

            # Sanitize theme and topic for directory names
            theme = self.inputs["theme"].lower()
            topic = self.inputs["topic"].lower()

            # Add debug logging for inputs
            self.logger.debug(f"Using theme: {theme}, topic: {topic}")

            # Replace spaces and special chars with underscores
            topic_dir = "".join(
                c if c.isalnum() or c == "_" else "_" for c in topic.replace(" ", "_")
            )

            # Create output directory structure
            output_dir = os.path.join("output", theme, topic_dir)
            os.makedirs(output_dir, exist_ok=True)

            self.logger.info(f"Creating output in directory: {output_dir}")

            # Extract HTML, CSS, JS sections
            sections = {"html": [], "css": [], "js": []}
            current_section = None

            # Add debug logging for output parsing
            self.logger.debug("Starting to parse output sections")

            for line in str(output).split("\n"):
                line_lower = line.lower().strip()

                if "html:" in line_lower or "```html" in line_lower:
                    current_section = "html"
                    self.logger.debug("Found HTML section")
                    continue
                elif "css:" in line_lower or "```css" in line_lower:
                    current_section = "css"
                    self.logger.debug("Found CSS section")
                    continue
                elif "js:" in line_lower or "```javascript" in line_lower:
                    current_section = "js"
                    self.logger.debug("Found JS section")
                    continue
                elif "```" in line:
                    current_section = None
                    continue

                if current_section and line.strip():
                    sections[current_section].append(line)

            # Write files with logging
            if sections["html"]:
                self.logger.info("Writing HTML file...")
                processed_html = self.template_manager.process_html(
                    "\n".join(sections["html"]),
                    title=f"{self.inputs['topic']} - {self.inputs['theme']} Landing Page",
                )
                with open(os.path.join(output_dir, "index.html"), "w") as f:
                    f.write(processed_html)
                self.logger.info("HTML file written successfully")

            if sections["css"]:
                self.logger.info("Writing CSS file...")
                with open(os.path.join(output_dir, "styles.css"), "w") as f:
                    f.write("\n".join(sections["css"]))
                self.logger.info("CSS file written successfully")

            if sections["js"]:
                self.logger.info("Writing JS file...")
                with open(os.path.join(output_dir, "main.js"), "w") as f:
                    f.write("\n".join(sections["js"]))
                self.logger.info("JS file written successfully")

            self.logger.info("Development output processing completed successfully")
            return {
                "html": "\n".join(sections["html"]) if sections["html"] else "",
                "css": "\n".join(sections["css"]) if sections["css"] else "",
                "js": "\n".join(sections["js"]) if sections["js"] else "",
                "theme": theme,
                "topic": topic,
                "output_dir": output_dir,
            }

        except Exception as e:
            self.logger.error(f"Error in handle_development_output: {str(e)}")
            self.logger.exception("Full traceback:")
            raise

    @crew
    def crew(self) -> Crew:
        def process_inputs(inputs):
            try:
                # Initialize cache if needed
                if not self.cache_manager:
                    self.initialize_cache(inputs.get("theme", "Books"))

                # Step 1: Product Manager Task
                logger.info("Starting Product Manager task...")
                product_task = self.product_requirements_task()
                product_output = product_task.execute_sync(self.product_manager())

                # Force save to cache
                self.cache_manager.cache_agent_output(
                    "product_manager", str(product_output)
                )
                logger.info("Product Manager output saved to cache")

                # Step 2: Design Task - READ FROM CACHE
                logger.info("Starting UI/UX Designer task...")
                design_task = self.design_task()

                # Get requirements from cache
                product_requirements = self.cache_manager.get_agent_output(
                    "product_manager"
                )
                if not product_requirements:
                    raise ValueError(
                        "Cannot proceed: Product requirements not found in cache"
                    )

                # Set context from cache
                design_task.context = (
                    f"Use these Product Manager requirements:\n{product_requirements}"
                )

                # Execute design task
                design_output = design_task.execute_sync(self.ui_ux_designer())

                # Save design to cache
                self.cache_manager.cache_agent_output(
                    "ui_ux_designer", str(design_output)
                )
                logger.info("UI/UX Designer output saved to cache")

                # Step 3: Frontend Task - READ FROM CACHE
                logger.info("Starting Frontend Engineer task...")
                dev_task = self.development_task()

                # Get design from cache
                design_specs = self.cache_manager.get_agent_output("ui_ux_designer")
                if not design_specs:
                    raise ValueError(
                        "Cannot proceed: Design specifications not found in cache"
                    )

                # Set context from cache
                dev_task.context = (
                    f"Implement these design specifications:\n{design_specs}"
                )

                # Execute development task
                return dev_task.execute_sync(self.frontend_engineer())

            except Exception as e:
                logger.error(f"Error in process_inputs: {str(e)}")
                logger.exception("Full traceback:")
                raise

        return Crew(
            agents=[
                self.product_manager(),
                self.ui_ux_designer(),
                self.frontend_engineer(),
            ],
            tasks=[
                self.product_requirements_task(),
                self.design_task(),
                self.development_task(),
            ],
            process=Process.sequential,
            process_inputs=process_inputs,
            verbose=True,
        )

    # Add method to get/set UI design
    def set_ui_design(self, design):
        if self.cache_manager:
            self.cache_manager.cache_agent_output("ui_ux_designer", design)

    def get_ui_design(self):
        if not self.cache_manager:
            # If no cached design, run UI/UX designer task
            ui_designer = self.ui_ux_designer()
            design_task = self.design_task()
            design_task.agent = ui_designer
            design_task.callback = self.handle_development_output
            self.cache_manager.cache_agent_output(
                "ui_ux_designer", design_task.execute_sync(ui_designer)
            )
        return self.cache_manager.get_agent_output("ui_ux_designer")

    def handle_design_output(self, output):
        """Cache UI/UX design output"""
        if self.cache_manager:
            self.cache_manager.cache_agent_output("ui_ux_designer", str(output))
        return output
