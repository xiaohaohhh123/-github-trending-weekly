#!/usr/bin/env python3
"""
开源搞钱周刊 — 自主入口。
Usage:
    python main.py              # Full pipeline: scrape -> filter -> analyze -> publish
    python main.py --dry-run    # Same but don't update manifest
    python main.py --scrape-only  # Only scrape trending repos
"""
import sys
import os
import json
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(__file__))

from scraper.github_trending import fetch_trending_weekly
from engine.summarizer import analyze_all, generate_intro, generate_title
from builder.newsletter import build_newsletter
from builder.rss_feed import generate_rss
from builder.seo import generate_sitemap, generate_share_text
from promoter.platforms import promote_all

PROJECT_ROOT = os.path.dirname(__file__)
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
ISSUES_DIR = os.path.join(DOCS_DIR, "issues")
MANIFEST_PATH = os.path.join(ISSUES_DIR, "manifest.json")
RSS_PATH = os.path.join(DOCS_DIR, "rss.xml")
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "issues")


def _load_manifest() -> list[dict]:
    if not os.path.exists(MANIFEST_PATH):
        return []
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_manifest(manifest: list[dict]):
    os.makedirs(ISSUES_DIR, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    rss = generate_rss(MANIFEST_PATH)
    with open(RSS_PATH, "w", encoding="utf-8") as f:
        f.write(rss)
    print(f"[publish] RSS updated: {RSS_PATH}")


def main():
    args = set(sys.argv[1:])
    dry_run = "--dry-run" in args
    scrape_only = "--scrape-only" in args

    print("=" * 60)
    print("  开源搞钱周刊 - Open Source Money Weekly")
    print("=" * 60)

    # Step 1: Scrape
    print("\n[Step 1/5] Fetching trending repos from GitHub...")
    repos = fetch_trending_weekly()
    if not repos:
        print("[ERROR] No repos fetched.")
        sys.exit(1)

    if scrape_only:
        for i, r in enumerate(repos):
            print(f"  {i+1}. {r['stargazers_count']}* {r['full_name']} ({r['language']})")
            print(f"     {r['description'][:100]}")
        return

    # Step 2: Filter + Deep Analyze (AI selects top 3-5 money-makers)
    print("\n[Step 2/5] AI filtering & deep-analyzing for money potential...")
    repos = analyze_all(repos)

    # Step 3: Title + Intro
    print("\n[Step 3/5] Generating title and intro...")
    title = generate_title(repos)
    intro = generate_intro(repos)
    issue_number = len(_load_manifest()) + 1

    print(f"  Title: {title}")
    print(f"  Issue: #{issue_number}")

    # Step 4: Build HTML
    print("\n[Step 4/5] Building web page...")
    html = build_newsletter(repos=repos, title=title, intro=intro, issue_number=issue_number)

    os.makedirs(ISSUES_DIR, exist_ok=True)
    web_path = os.path.join(ISSUES_DIR, f"issue-{issue_number:04d}.html")
    with open(web_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[publish] Page saved: {web_path}")

    # Also archive
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, f"issue-{issue_number:04d}.html"), "w", encoding="utf-8") as f:
        f.write(html)

    # Step 5: Manifest + RSS
    print("\n[Step 5/5] Updating manifest and RSS...")
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
                "money_score": r.get("analysis", {}).get("money_score", 0),
                "revenue_estimate": r.get("analysis", {}).get("revenue_estimate", ""),
            }
            for r in repos
        ],
    })
    _save_manifest(manifest)

    # Generate sitemap
    sitemap = generate_sitemap(MANIFEST_PATH)
    with open(os.path.join(DOCS_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)

    # Generate share texts
    share_texts = generate_share_text(MANIFEST_PATH)
    share_path = os.path.join(DATA_DIR, f"share-{issue_number:04d}.md")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(share_path, "w", encoding="utf-8") as f:
        for platform, text in share_texts.items():
            f.write(f"## {platform}\n\n```\n{text}\n```\n\n")

    print("\n" + "=" * 60)
    print(f"  Done! Issue #{issue_number} published")
    print(f"  Web: https://xiaohaohhh123.github.io/-github-trending-weekly")
    print("=" * 60)

    # Step 6: Auto-promote to all configured platforms
    print("\n[Promotion] Auto-posting to social platforms...")
    promo_results = promote_all(MANIFEST_PATH)
    for platform, info in promo_results.items():
        status = "SENT" if info["posted"] else "SKIPPED (not configured)"
        print(f"  [{platform}] {status}")
        if not info["posted"]:
            # Save copyable text for manual platforms
            with open(os.path.join(DATA_DIR, f"share-{issue_number:04d}.md"), "a", encoding="utf-8") as f:
                f.write(f"\n## {platform}\n\n```\n{info['text']}\n```\n")

    print("\n  --- 手动平台推广文案已保存 ---")
    print(f"  data/issues/share-{issue_number:04d}.md")
    print()


if __name__ == "__main__":
    main()
