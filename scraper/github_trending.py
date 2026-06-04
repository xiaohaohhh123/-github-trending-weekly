"""
GitHub Trending scraper — fetches trending repositories with their README content.
Uses GitHub's search API (no auth needed for public data, rate limit 10 req/min).
"""
import requests
import time
import re
from datetime import datetime


GITHUB_API = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github.v3+json"}


def _clean_html(raw: str) -> str:
    """Strip HTML tags from description text."""
    return re.sub(r"<[^>]+>", "", raw)


def fetch_trending_repos(language: str = "", per_page: int = 10) -> list[dict]:
    """
    Fetch trending repos by stars created in the last 7 days.
    Returns list of dicts with keys:
      full_name, description, html_url, language, stargazers_count,
      forks_count, topics, created_at, readme
    """
    date_threshold = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    # go back 7 days
    from datetime import timedelta
    date_since = (date_threshold - timedelta(days=7)).isoformat() + "Z"

    query = f"created:>={date_since}"
    if language:
        query += f"+language:{language}"

    url = (
        f"{GITHUB_API}/search/repositories"
        f"?q={query}&sort=stars&order=desc&per_page={per_page}"
    )
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code == 403:
        # Rate limited — wait and retry once
        time.sleep(10)
        resp = requests.get(url, headers=HEADERS, timeout=30)

    if resp.status_code != 200:
        print(f"[ERROR] GitHub search API returned {resp.status_code}: {resp.text[:200]}")
        return []

    data = resp.json()
    repos = []
    for item in data.get("items", []):
        readme = _fetch_readme(item["full_name"])
        repos.append({
            "full_name": item["full_name"],
            "description": _clean_html(item.get("description") or ""),
            "html_url": item["html_url"],
            "language": item.get("language") or "Unknown",
            "stargazers_count": item["stargazers_count"],
            "forks_count": item["forks_count"],
            "topics": item.get("topics", []),
            "created_at": item["created_at"],
            "readme": readme,
        })
        time.sleep(0.5)  # be polite to GitHub's API

    return repos


def _fetch_readme(full_name: str) -> str:
    """Fetch README content for a repo, truncated to ~3000 chars for AI processing."""
    url = f"{GITHUB_API}/repos/{full_name}/readme"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return ""

    import base64
    try:
        content = base64.b64decode(resp.json()["content"]).decode("utf-8", errors="replace")
    except Exception:
        return ""

    # Truncate to save tokens — first 3000 chars is usually enough for context
    return content[:3000]


def fetch_trending_weekly() -> list[dict]:
    """
    Fetch this week's trending repos across all languages.
    This is the primary entry point for the weekly newsletter.
    """
    print("[scraper] Fetching trending repos from GitHub...")
    repos = fetch_trending_repos(per_page=10)
    print(f"[scraper] Got {len(repos)} repos")
    return repos


if __name__ == "__main__":
    repos = fetch_trending_weekly()
    for r in repos:
        print(f"  ⭐ {r['stargazers_count']:,} — {r['full_name']} ({r['language']})")
        print(f"     {r['description'][:100]}")
        print(f"     README: {len(r['readme'])} chars")
        print()
