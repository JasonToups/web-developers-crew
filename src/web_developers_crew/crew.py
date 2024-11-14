from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os
import logging
from .utils.cache_manager import CacheManager
from .utils.template_manager import TemplateManager

logger = logging.getLogger(__name__)


@CrewBase
class WebDevelopersCrew:
    """WebDevelopersCrew crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        self.inputs = None
        self.cache_manager = None
        self.template_manager = TemplateManager()
        self.logger = logging.getLogger(__name__)
        self.topic = None

    def initialize_cache(self, topic: str):
        self.cache_manager = CacheManager(topic)

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
        return Task(
            config=self.tasks_config["product_requirements_task"],
        )

    @task
    def design_task(self) -> Task:
        return Task(
            config=self.tasks_config["design_task"],
        )

    @task
    def development_task(self) -> Task:
        """Development task that creates the landing page"""
        config = self.tasks_config["development_task"]

        # Modify task to include UI design in context
        if self.cache_manager:
            cached_design = self.cache_manager.get_agent_output("ui_ux_designer")
            if cached_design:
                config["context"] = (
                    f"Using this UI/UX design:\n{cached_design}\n\n"
                    + config.get("context", "")
                )

        return Task(config=config)

    def handle_development_output(self, output):
        """Helper method to handle the development task output"""
        self.logger.info("Processing development output...")
        try:
            if self.inputs is None:
                raise ValueError("Inputs not initialized")

            # Sanitize theme and topic for directory names
            theme = self.inputs["theme"].lower()
            topic = self.inputs["topic"].lower()

            # Replace spaces and special chars with underscores
            topic_dir = "".join(
                c if c.isalnum() or c == "_" else "_" for c in topic.replace(" ", "_")
            )

            # Create output directory structure
            output_dir = os.path.join("output", theme, topic_dir)
            os.makedirs(output_dir, exist_ok=True)

            logger.info(f"Creating output in directory: {output_dir}")

            # Extract HTML, CSS, JS sections
            sections = {"html": [], "css": [], "js": []}

            current_section = None
            for line in str(output).split("\n"):
                line_lower = line.lower().strip()

                if "html:" in line_lower or "```html" in line_lower:
                    current_section = "html"
                    continue
                elif "css:" in line_lower or "```css" in line_lower:
                    current_section = "css"
                    continue
                elif "js:" in line_lower or "```javascript" in line_lower:
                    current_section = "js"
                    continue
                elif "```" in line:
                    current_section = None
                    continue

                if current_section and line.strip():
                    sections[current_section].append(line)

            # Write files
            if sections["html"]:
                processed_html = self.template_manager.process_html(
                    "\n".join(sections["html"]),
                    title=f"{self.inputs['topic']} - {self.inputs['theme']} Landing Page",
                )
                with open(os.path.join(output_dir, "index.html"), "w") as f:
                    f.write(processed_html)

            if sections["css"]:
                with open(os.path.join(output_dir, "styles.css"), "w") as f:
                    f.write("\n".join(sections["css"]))

            if sections["js"]:
                with open(os.path.join(output_dir, "main.js"), "w") as f:
                    f.write("\n".join(sections["js"]))

            return {
                "html": "\n".join(sections["html"]) if sections["html"] else "",
                "css": "\n".join(sections["css"]) if sections["css"] else "",
                "js": "\n".join(sections["js"]) if sections["js"] else "",
                "theme": theme,
                "topic": topic,
                "output_dir": output_dir,
            }

        except Exception as e:
            logger.error(f"Error in handle_development_output: {str(e)}")
            raise

    @crew
    def crew(self) -> Crew:
        def process_inputs(inputs):
            try:
                # Step 1: Product Manager Task
                product_task = self.product_requirements_task()
                product_output = product_task.execute_sync(self.product_manager())

                # Extract topic and page type
                output_lines = product_output.split("\n")
                for line in output_lines:
                    line = line.strip()
                    if line.startswith("TOPIC:"):
                        inputs["topic"] = line.replace("TOPIC:", "").strip().strip('"')
                    elif line.startswith("PAGE_TYPE:"):
                        inputs["page_type"] = (
                            line.replace("PAGE_TYPE:", "").split("(")[0].strip()
                        )

                logger.info(f"Generated topic: {inputs['topic']}")
                logger.info(f"Page type: {inputs['page_type']}")

                # Cache product manager output
                if self.cache_manager:
                    self.cache_manager.cache_agent_output(
                        "product_manager", str(product_output)
                    )

                # Step 2: Design Task
                design_task = self.design_task()
                design_task.description = f"""
                As a UI/UX Designer for a {inputs['theme']} landing page:

                Based on the Product Manager's requirements:
                Topic: {inputs['topic']}
                Page Type: {inputs['page_type']}

                Full Requirements:
                {product_output}

                Create an innovative design that reflects both the theme and specific requirements
                while maintaining a cohesive user experience.

                1. Layout Innovation
                   - Design a layout that best suits the {inputs['page_type']} format
                   - Create a distinctive hero section that highlights "{inputs['topic']}"
                   - Implement section arrangements that support the content flow
                   - Design transitions that enhance the user journey
                """
                design_output = design_task.execute_sync(self.ui_ux_designer())

                # Cache design output
                if self.cache_manager:
                    self.cache_manager.cache_agent_output(
                        "ui_ux_designer", str(design_output)
                    )

                # Step 3: Development Task
                dev_task = self.development_task()
                dev_task.description = f"""
                As a Frontend Engineer for a {inputs['theme']} landing page:

                Project Details:
                Topic: {inputs['topic']}
                Page Type: {inputs['page_type']}

                Design Specifications:
                {design_output}

                Implement this design using Bootstrap, ensuring responsive behavior and optimal performance.
                """
                return dev_task.execute_sync(self.frontend_engineer())

            except Exception as e:
                logger.error(f"Error in process_inputs: {str(e)}")
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
