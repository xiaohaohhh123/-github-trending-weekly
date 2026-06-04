"""
Newsletter builder — assembles the HTML email from scraped data and AI summaries.
"""
import os
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def build_newsletter(
    repos: list[dict],
    title: str = "",
    intro: str = "",
    issue_number: int = 1,
    unsubscribe_url: str = "",
) -> str:
    """
    Build a complete HTML email from the repo list.
    Returns the HTML string.
    """
    template = _env.get_template("weekly.html")

    # Calculate week label
    today = datetime.utcnow()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    week_label = f"{monday.strftime('%Y.%m.%d')} - {sunday.strftime('%Y.%m.%d')}"

    return template.render(
        title=title or "GitHub 热门项目周报",
        week_label=week_label,
        issue_number=issue_number,
        intro=intro,
        repos=repos,
        unsubscribe_url=unsubscribe_url or "https://example.com/unsubscribe",
        year=today.year,
    )


def save_newsletter(html: str, issue_number: int):
    """Save the HTML to the issues archive."""
    archive_dir = os.path.join(
        os.path.dirname(__file__), "..", "data", "issues"
    )
    os.makedirs(archive_dir, exist_ok=True)
    filepath = os.path.join(archive_dir, f"issue-{issue_number:04d}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[builder] Saved to {filepath}")
    return filepath
