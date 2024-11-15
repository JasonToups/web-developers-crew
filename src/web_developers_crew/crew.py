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
        try:
            # Initialize inputs if not already set
            if self.inputs is None:
                self.inputs = {"theme": "Books"}  # Default theme

            # Initialize cache if needed
            if not self.cache_manager:
                logger.info("Initializing cache manager...")
                self.initialize_cache(self.inputs.get("theme", "Books"))

            # Verify cache contents
            if not cached_design:
                logger.info("No design provided, checking cache...")
                cached_design = self.cache_manager.get_agent_output("ui_ux_designer")

                if not cached_design:
                    logger.error("No UI/UX design found in cache!")
                    raise ValueError(
                        "Cannot proceed: UI/UX design specifications not found in cache. "
                        "Please run the full crew process first or provide design specifications."
                    )

            logger.info(
                "Found UI/UX design specifications, proceeding with frontend task"
            )

            # Create and configure frontend task
            frontend_engineer = self.frontend_engineer()
            dev_task = self.development_task()

            # Set context with verified design
            dev_task.context = f"""
            IMPLEMENT THESE EXACT DESIGN SPECIFICATIONS:
            
            {cached_design}
            
            {dev_task.context}
            """

            dev_task.agent = frontend_engineer
            dev_task.callback = self.handle_development_output

            # Execute task
            return dev_task.execute_sync(frontend_engineer)

        except Exception as e:
            logger.error(f"Error in run_frontend_task: {str(e)}")
            logger.exception("Full traceback:")
            raise

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
        theme = self.inputs.get("theme", "Books")

        # Update task description with theme
        task_description = task_config["description"].replace("{theme}", theme)

        return Task(
            description=task_description,
            expected_output=task_config["expected_output"],
            agent=self.product_manager(),
        )

    @task
    def design_task(self) -> Task:
        """Create the design task with cached product requirements"""
        task_config = self.tasks_config["design_task"]
        theme = self.inputs.get("theme", "Books")

        # Get product requirements from cache
        product_requirements = self.cache_manager.get_agent_output("product_manager")
        if not product_requirements:
            logger.error("Product requirements missing from cache")
            raise ValueError(
                f"Cannot start Design: {theme} Product requirements not found in cache"
            )

        # Log the requirements we're actually using
        logger.info(
            f"Using product requirements from cache: {product_requirements[:100]}..."
        )

        # Update task description with theme and cached requirements
        task_description = task_config["description"].replace("{theme}", theme)
        task_description = f"""
        {task_description}
        
        USE THESE EXACT PRODUCT REQUIREMENTS FOR {theme.upper()}:
        {product_requirements}
        """

        return Task(
            description=task_description,
            expected_output=task_config["expected_output"],
            agent=self.ui_ux_designer(),
        )

    @task
    def development_task(self) -> Task:
        """Create the development task with cached design specs"""
        task_config = self.tasks_config["development_task"]
        theme = self.inputs.get("theme", "Books")

        # Get design specs from cache
        design_specs = self.cache_manager.get_agent_output("ui_ux_designer")
        if not design_specs:
            raise ValueError(
                f"Cannot start Development: {theme} Design specifications not found in cache"
            )

        # Update task description with theme and cached specs
        task_description = task_config["description"].replace("{theme}", theme)
        task_description = f"""
        {task_description}
        
        IMPLEMENT THESE EXACT DESIGN SPECIFICATIONS FOR {theme.upper()}:
        {design_specs}
        """

        return Task(
            description=task_description,
            expected_output=task_config["expected_output"],
            agent=self.frontend_engineer(),
        )

    def handle_development_output(self, output):
        """Handle the frontend development output"""
        try:
            # Create output directory
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)

            # Initialize section collectors
            sections = {"html": [], "css": [], "js": []}
            current_section = None

            # Parse output into sections
            for line in str(output).split("\n"):
                line_lower = line.lower().strip()

                # Check for section markers
                if "```html" in line_lower:
                    current_section = "html"
                    continue
                elif "```css" in line_lower:
                    current_section = "css"
                    continue
                elif "```javascript" in line_lower or "```js" in line_lower:
                    current_section = "js"
                    continue
                elif "```" in line:
                    current_section = None
                    continue

                # Add content to current section if we're in one
                if current_section and line.strip():
                    sections[current_section].append(line)

            # Process HTML through template
            if sections["html"]:
                html_content = "\n".join(sections["html"])
                # Get theme from cache or inputs
                theme = self.inputs.get("theme", "Books")
                # Process through template
                processed_html = self.template_manager.process_html(
                    html_content, title=f"{theme} Landing Page"
                )
                html_path = output_dir / "index.html"
                html_path.write_text(processed_html)
                logger.info(f"HTML written to {html_path}")

            # Write other files
            if sections["css"]:
                css_path = output_dir / "style.css"
                css_content = "\n".join(sections["css"])
                css_path.write_text(css_content)
                logger.info(f"CSS written to {css_path}")

            if sections["js"]:
                js_path = output_dir / "script.js"
                js_content = "\n".join(sections["js"])
                js_path.write_text(js_content)
                logger.info(f"JavaScript written to {js_path}")

            return True

        except Exception as e:
            logger.error(f"Error handling development output: {e}")
            logger.exception("Full traceback:")
            return False

    @crew
    def crew(self) -> Crew:
        def process_inputs(inputs):
            try:
                logger.info("Process inputs started...")

                # Clear cache at the start of a new run
                self.clear_cache()

                # Initialize cache
                if not self.cache_manager:
                    theme = inputs.get("theme", "Books")
                    self.initialize_cache(theme)
                    self.inputs = inputs

                # Step 1: Product Manager Task
                logger.info("Starting Product Manager task...")
                product_task = self.product_requirements_task()
                product_output = product_task.execute_sync(self.product_manager())

                # Cache product output with verification and error handling
                if not self.cache_manager.cache_agent_output(
                    "product_manager", str(product_output)
                ):
                    logger.error("Failed to cache Product Manager output")
                    raise ValueError("Failed to cache Product Manager output")
                logger.info("Product Manager output cached and verified")

                # Step 2: Design Task (reads from cache)
                logger.info("Starting UI/UX Designer task...")
                try:
                    design_task = (
                        self.design_task()
                    )  # Will raise error if cache missing
                    design_output = design_task.execute_sync(self.ui_ux_designer())

                    # Cache design output with verification
                    if not self.cache_manager.cache_agent_output(
                        "ui_ux_designer", str(design_output)
                    ):
                        raise ValueError("Failed to cache UI/UX Designer output")
                    logger.info("UI/UX Designer output cached and verified")
                except ValueError as e:
                    logger.error(f"Design task failed: {e}")
                    raise

                # Step 3: Frontend Task (reads from cache)
                logger.info("Starting Frontend Engineer task...")
                try:
                    dev_task = (
                        self.development_task()
                    )  # Will raise error if cache missing
                    dev_output = dev_task.execute_sync(self.frontend_engineer())

                    # Handle development output
                    if not self.handle_development_output(dev_output):
                        raise ValueError("Failed to handle development output")
                    logger.info("Frontend output processed successfully")
                except ValueError as e:
                    logger.error(f"Development task failed: {e}")
                    raise

                return dev_output

            except Exception as e:
                logger.error(f"Error in process_inputs: {str(e)}")
                logger.exception("Full traceback:")
                raise

        # Create tasks with callbacks
        product_task = self.product_requirements_task()
        product_task.callback = lambda output: self.cache_manager.cache_agent_output(
            "product_manager", str(output)
        )

        design_task = self.design_task()
        design_task.callback = lambda output: self.cache_manager.cache_agent_output(
            "ui_ux_designer", str(output)
        )

        dev_task = self.development_task()
        dev_task.callback = self.handle_development_output

        return Crew(
            agents=[
                self.product_manager(),
                self.ui_ux_designer(),
                self.frontend_engineer(),
            ],
            tasks=[product_task, design_task, dev_task],  # Use tasks with callbacks
            process=Process.sequential,
            process_inputs=process_inputs,  # This will now be called after each task
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

    def clear_cache(self):
        """Clear the cache before starting a new run"""
        if self.cache_manager:
            self.cache_manager.clear()
            logger.info("Cache cleared successfully")

    def run_product_requirements(self):
        """Run only the product requirements task and update cache"""
        try:
            if not self.cache_manager:
                self.initialize_cache(self.inputs.get("theme", "Books"))

            # Clear existing cache
            self.clear_cache()

            # Run product manager task
            product_task = self.product_requirements_task()
            product_output = product_task.execute_sync(self.product_manager())

            # Cache the output
            if not self.cache_manager.cache_agent_output(
                "product_manager", str(product_output)
            ):
                raise ValueError("Failed to cache Product Manager output")

            return product_output

        except Exception as e:
            logger.error(f"Error in run_product_requirements: {str(e)}")
            raise
