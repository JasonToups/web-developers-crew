from pathlib import Path
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class OutputHandler:
    """Handles parsing and writing of frontend output files"""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def parse_sections(self, output: str) -> Dict[str, list]:
        """Parse output into HTML, CSS, and JS sections"""
        sections = {"html": [], "css": [], "js": []}
        current_section = None

        for line in str(output).split("\n"):
            line_lower = line.lower().strip()

            # Detect section markers
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

            # Add content to current section
            if current_section and line.strip():
                sections[current_section].append(line)

        return sections

    def write_files(
        self,
        sections: Dict[str, list],
        template_manager=None,
        theme: Optional[str] = None,
    ) -> bool:
        """Write sections to their respective files"""
        try:
            # Handle HTML with template processing
            if sections["html"]:
                html_content = "\n".join(sections["html"])
                if template_manager and theme:
                    html_content = template_manager.process_html(
                        html_content, title=f"{theme} Homepage"
                    )
                html_path = self.output_dir / "index.html"
                html_path.write_text(html_content)
                logger.info(f"HTML written to {html_path}")

            # Write CSS
            if sections["css"]:
                css_path = self.output_dir / "style.css"
                css_content = "\n".join(sections["css"])
                css_path.write_text(css_content)
                logger.info(f"CSS written to {css_path}")

            # Write JavaScript
            if sections["js"]:
                js_path = self.output_dir / "script.js"
                js_content = "\n".join(sections["js"])
                js_path.write_text(js_content)
                logger.info(f"JavaScript written to {js_path}")

            return True

        except Exception as e:
            logger.error(f"Error writing output files: {e}")
            logger.exception("Full traceback:")
            return False
