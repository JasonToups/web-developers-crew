from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os


@CrewBase
class WebDevelopersCrew:
    """WebDevelopersCrew crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        self.inputs = None
        self._cached_ui_design = None  # Add cache for UI design

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
        if self._cached_ui_design:
            config["context"] = (
                f"Using this UI/UX design:\n{self._cached_ui_design}\n\n"
                + config.get("context", "")
            )

        return Task(config=config)

    def handle_development_output(self, output):
        """Helper method to handle the development task output"""
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

        # Create output directory
        output_dir = os.path.join("output", "books")
        os.makedirs(output_dir, exist_ok=True)

        # Write files
        if html:
            with open(os.path.join(output_dir, "index.html"), "w") as f:
                f.write("\n".join(html))

        if css:
            with open(os.path.join(output_dir, "index.css"), "w") as f:
                f.write("\n".join(css))

        if js:
            with open(os.path.join(output_dir, "index.js"), "w") as f:
                f.write("\n".join(js))

        return {
            "html": "\n".join(html) if html else "",
            "css": "\n".join(css) if css else "",
            "js": "\n".join(js) if js else "",
        }

    @crew
    def crew(self) -> Crew:
        """Creates the WebDevelopersCrew crew"""

        def process_inputs(inputs):
            self.inputs = inputs

        # Get the development task - modify how we find the task
        dev_task = None
        for task in self.tasks:
            if (
                isinstance(task, Task)
                and task.description
                and "frontend engineer" in task.description.lower()
            ):
                dev_task = task
                break

        if dev_task:
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
        self._cached_ui_design = design

    def get_ui_design(self):
        if not self._cached_ui_design:
            # If no cached design, run UI/UX designer task
            ui_designer = self.ui_ux_designer()
            design_task = self.design_task()
            design_task.agent = ui_designer
            self._cached_ui_design = design_task.execute_sync(ui_designer)
        return self._cached_ui_design
