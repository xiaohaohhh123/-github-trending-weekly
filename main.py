#!/usr/bin/env python3
"""
AI Newsletter - GitHub Trending Weekly.
Generates a static site + RSS feed, deployable to GitHub Pages for free.

Usage:
    python main.py              # Full pipeline: scrape -> summarize -> build -> publish
    python main.py --dry-run    # Same but don't update manifest
    python main.py --scrape-only  # Only scrape trending repos
"""
import sys
import os
import json
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from scraper.github_trending import fetch_trending_weekly
from engine.summarizer import summarize_all_repos, generate_intro, generate_title
from builder.newsletter import build_newsletter, save_newsletter
from builder.rss_feed import generate_rss


PROJECT_ROOT = os.path.dirname(__file__)
WEB_DIR = os.path.join(PROJECT_ROOT, "web")
ISSUES_DIR = os.path.join(WEB_DIR, "issues")
MANIFEST_PATH = os.path.join(ISSUES_DIR, "manifest.json")
RSS_PATH = os.path.join(WEB_DIR, "rss.xml")

# Also archive to data/ for git history
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "issues")


def _load_manifest() -> list[dict]:
    """Load existing issues manifest."""
    if not os.path.exists(MANIFEST_PATH):
        return []
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_manifest(manifest: list[dict]):
    """Save manifest and regenerate RSS."""
    os.makedirs(ISSUES_DIR, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # Regenerate RSS
    rss = generate_rss(MANIFEST_PATH)
    with open(RSS_PATH, "w", encoding="utf-8") as f:
        f.write(rss)
    print(f"[publish] RSS feed updated: {RSS_PATH}")


def main():
    args = set(sys.argv[1:])
    dry_run = "--dry-run" in args
    scrape_only = "--scrape-only" in args

    print("=" * 60)
    print("  AI Newsletter - GitHub Trending Weekly")
    print("=" * 60)

    # Step 1: Scrape
    print("\n[Step 1/5] Fetching trending repos from GitHub...")
    repos = fetch_trending_weekly()
    if not repos:
        print("[ERROR] No repos fetched. Exiting.")
        sys.exit(1)

    if scrape_only:
        for i, r in enumerate(repos):
            print(f"  {i+1}. star:{r['stargazers_count']:,}  {r['full_name']}  ({r['language']})")
            print(f"     {r['description'][:100]}")
        return

    # Step 2: AI Summarize
    print("\n[Step 2/5] Generating AI summaries via DeepSeek...")
    repos = summarize_all_repos(repos)

    # Step 3: Generate title & intro
    print("\n[Step 3/5] Generating title and intro...")
    title = generate_title(repos)
    intro = generate_intro(repos)
    issue_number = len(_load_manifest()) + 1

    print(f"  Title: {title}")
    print(f"  Issue: #{issue_number}")

    # Step 4: Build HTML and save to web/ (GitHub Pages) + data/ (archive)
    print("\n[Step 4/5] Building HTML...")
    html = build_newsletter(
        repos=repos,
        title=title,
        intro=intro,
        issue_number=issue_number,
    )

    # Save to web/ for GitHub Pages
    os.makedirs(ISSUES_DIR, exist_ok=True)
    web_path = os.path.join(ISSUES_DIR, f"issue-{issue_number:04d}.html")
    with open(web_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[publish] Web page saved: {web_path}")

    # Also save to data/ for archive
    os.makedirs(DATA_DIR, exist_ok=True)
    data_path = os.path.join(DATA_DIR, f"issue-{issue_number:04d}.html")
    with open(data_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Step 5: Update manifest + RSS
    print("\n[Step 5/5] Updating manifest and RSS feed...")
    manifest = _load_manifest()
    manifest.append({
        "issue": issue_number,
        "title": title,
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "repo_count": len(repos),
        "repos": [
            {
                "full_name": r["full_name"],
                "stargazers_count": r["stargazers_count"],
                "score": r.get("summary", {}).get("score", 0),
            }
            for r in repos
        ],
    })
    _save_manifest(manifest)

    print("\n" + "=" * 60)
    print(f"  Done! Issue #{issue_number} published")
    print(f"  Web: {web_path}")
    print(f"  Site: https://xiaohaohhh123.github.io/github-trending-weekly")
    print("=" * 60)


if __name__ == "__main__":
    main()
