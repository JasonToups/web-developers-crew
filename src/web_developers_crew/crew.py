from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os


@CrewBase
class WebDevelopersCrew:
    """WebDevelopersCrew crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

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
        task = Task(
            config=self.tasks_config["development_task"],
        )

        # Create folder and files after development task
        def callback(output):
            topic = (
                self.crew()
                .inputs.get("topic", "landing_page")
                .replace(" ", "_")
                .lower()
            )
            folder = f"{topic}_landing_page"

            if not os.path.exists(folder):
                os.makedirs(folder)

            with open(f"{folder}/index.html", "w") as f:
                f.write(output.get("html", ""))
            with open(f"{folder}/styles.css", "w") as f:
                f.write(output.get("css", ""))
            with open(f"{folder}/script.js", "w") as f:
                f.write(output.get("js", ""))

            return output

        task.callback = callback
        return task

    @crew
    def crew(self) -> Crew:
        """Creates the WebDevelopersCrew crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
