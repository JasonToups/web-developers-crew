import os
from pathlib import Path


class TemplateManager:
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "templates"

    def read_template(self, template_name: str) -> str:
        """Read a template file"""
        template_path = self.template_dir / template_name
        with open(template_path, "r") as f:
            return f.read()

    def process_html(self, html_content: str, title: str = "Landing Page") -> str:
        """Process HTML content with the base template"""
        # Extract body content (everything between <body> tags if they exist)
        body_content = html_content
        if "<body>" in html_content and "</body>" in html_content:
            start = html_content.find("<body>") + len("<body>")
            end = html_content.find("</body>")
            body_content = html_content[start:end]

        # Get base template
        base_template = self.read_template("base.html")

        # Replace placeholders
        final_html = base_template.format(title=title, body=body_content)

        return final_html
