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
        return Task(config=self.tasks_config["development_task"])

    def handle_development_output(self, output):
        """Helper method to handle the development task output"""
        topic = (
            self.inputs.get("topic", "landing_page") if self.inputs else "landing_page"
        )
        output_dir = os.path.join("output", topic.lower().replace(" ", "_"))
        os.makedirs(output_dir, exist_ok=True)

        sections = output.split("\n")
        current_section = None
        html = []
        css = []
        js = []

        for line in sections:
            if "HTML:" in line:
                current_section = "html"
            elif "CSS:" in line:
                current_section = "css"
            elif "JS:" in line:
                current_section = "js"
            elif current_section == "html":
                html.append(line)
            elif current_section == "css":
                css.append(line)
            elif current_section == "js":
                js.append(line)

        with open(os.path.join(output_dir, "index.html"), "w") as f:
            f.write("\n".join(html))
        with open(os.path.join(output_dir, "styles.css"), "w") as f:
            f.write("\n".join(css))
        with open(os.path.join(output_dir, "script.js"), "w") as f:
            f.write("\n".join(js))

        return output

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
