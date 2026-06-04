"""
Newsletter builder — assembles HTML from analyzed repos.
"""
import os
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

SITE_URL = "https://xiaohaohhh123.github.io/-github-trending-weekly"


def build_newsletter(
    repos: list[dict],
    title: str = "",
    intro: str = "",
    issue_number: int = 1,
) -> str:
    """Build a complete HTML page from the analyzed repo list."""
    template = _env.get_template("weekly.html")

    today = datetime.utcnow()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    week_label = f"{monday.strftime('%Y.%m.%d')} - {sunday.strftime('%Y.%m.%d')}"

    return template.render(
        title=title or "开源搞钱周刊",
        week_label=week_label,
        issue_number=issue_number,
        intro=intro,
        repos=repos,
        site_url=SITE_URL,
        year=today.year,
    )
