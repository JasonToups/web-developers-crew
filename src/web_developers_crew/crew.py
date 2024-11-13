from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os
from .utils.cache_manager import CacheManager
from .utils.template_manager import TemplateManager
import logging

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

    def initialize_cache(self, topic: str):
        self.cache_manager = CacheManager(topic)

    def run_frontend_task(self, cached_design: str = None):
        """Run the frontend development task"""
        # Initialize inputs if not already set
        if self.inputs is None:
            self.inputs = {"topic": "Books"}  # Default topic

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
        try:
            # Ensure inputs are initialized
            if self.inputs is None:
                self.inputs = {"topic": "Books"}

            html = []
            css = []
            js = []

            # Convert TaskOutput to string and split
            output_text = str(output)
            sections = output_text.split("\n")

            current_section = None

            # Look for both markdown-style and plain text markers
            for line in sections:
                line_lower = line.lower().strip()

                # Check for section markers
                if "html:" in line_lower or "```html" in line_lower:
                    current_section = "html"
                    continue
                elif "css:" in line_lower or "```css" in line_lower:
                    current_section = "css"
                    continue
                elif (
                    "js:" in line_lower
                    or "javascript:" in line_lower
                    or "```js" in line_lower
                    or "```javascript" in line_lower
                ):
                    current_section = "js"
                    continue
                elif "```" in line:
                    current_section = None
                    continue

                # Only append non-empty lines while in a section
                if current_section and line.strip():
                    if current_section == "html":
                        html.append(line)
                    elif current_section == "css":
                        css.append(line)
                    elif current_section == "js":
                        js.append(line)

            # Process HTML with template and safe title access
            if html:
                title = f"{self.inputs.get('topic', 'Default')} Landing Page"
                processed_html = self.template_manager.process_html(
                    "\n".join(html), title=title
                )
            else:
                processed_html = ""

            # Create output directory
            output_dir = os.path.join("output", "books")
            os.makedirs(output_dir, exist_ok=True)

            # Write files
            if processed_html:  # Use processed HTML instead of raw HTML
                with open(os.path.join(output_dir, "index.html"), "w") as f:
                    f.write(processed_html)

            if css:
                with open(os.path.join(output_dir, "index.css"), "w") as f:
                    f.write("\n".join(css))

            if js:
                with open(os.path.join(output_dir, "index.js"), "w") as f:
                    f.write("\n".join(js))

            if self.cache_manager:
                self.cache_manager.cache_agent_output("frontend_engineer", str(output))

            return {
                "html": "\n".join(html) if html else "",
                "css": "\n".join(css) if css else "",
                "js": "\n".join(js) if js else "",
            }

        except Exception as e:
            logger.error(f"Error in handle_development_output: {str(e)}")
            raise

    @crew
    def crew(self) -> Crew:
        """Creates the WebDevelopersCrew crew"""
        # Initialize default inputs if not set
        if self.inputs is None:
            self.inputs = {"topic": "Books"}  # Default topic

        def process_inputs(inputs):
            # Merge with existing inputs or use new ones
            self.inputs = inputs if inputs else self.inputs

        # Get the development task
        dev_task = self.development_task()
        dev_task.callback = self.handle_development_output

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
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
