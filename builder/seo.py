"""
Sitemap + SEO metadata generator. Powers auto-indexing by Google/Baidu.
"""
import os
import json
from datetime import datetime

SITE_URL = "https://xiaohaohhh123.github.io/-github-trending-weekly"


def generate_sitemap(manifest_path: str) -> str:
    """Generate sitemap.xml from issue manifest."""
    urls = [
        f"  <url><loc>{SITE_URL}/</loc><priority>1.0</priority><changefreq>weekly</changefreq></url>",
    ]

    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            issues = json.load(f)
        for issue in issues:
            loc = f"{SITE_URL}/issues/issue-{issue['issue']:04d}.html"
            urls.append(
                f"  <url><loc>{loc}</loc><priority>0.8</priority><changefreq>never</changefreq></url>"
            )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""


def generate_share_text(manifest_path: str) -> dict:
    """Generate pre-written share texts for various platforms."""
    if not os.path.exists(manifest_path):
        return {"v2ex": "暂无内容", "wechat": "暂无内容", "twitter": "暂无内容"}

    with open(manifest_path, "r", encoding="utf-8") as f:
        issues = json.load(f)

    if not issues:
        return {"v2ex": "暂无内容", "wechat": "暂无内容", "twitter": "暂无内容"}

    latest = max(issues, key=lambda i: i["issue"])
    title = latest["title"]
    repos = latest.get("repos", [])
    issue_num = latest["issue"]

    # Pick top 3 money-makers
    top_repos = sorted(repos, key=lambda r: r.get("money_score", 0), reverse=True)[:3]
    repo_list = "\n".join(
        f"- {r['full_name']}：{r.get('revenue_estimate', '')}"
        for r in top_repos
    )

    return {
        "v2ex": f"""标题：[开源搞钱周刊 #{issue_num}] {title}

{repo_list}

每期从 GitHub Trending 中 AI 筛选出能赚钱的开源项目，拆解商业模式 + 部署教程 + 收入预估。

👉 在线阅读：{SITE_URL}
👉 RSS 订阅：{SITE_URL}/rss.xml""",

        "juejin": f"""# 开源搞钱周刊 #{issue_num}：{title}

> AI 从本周 GitHub 热门项目中筛选出最有赚钱潜力的 5 个，手把手教你部署变现。

{repo_list}

每期附带商业模式拆解 + 部署指南 + 收入潜力评估。

🔗 全文：{SITE_URL}/issues/issue-{issue_num:04d}.html""",

        "twitter": f"""开源搞钱周刊 #{issue_num}：{title}

本周最赚钱的开源项目：
{chr(10).join(f'{i+1}. {r["full_name"]} — {r.get("revenue_estimate", "?")}' for i, r in enumerate(top_repos))}

全文：{SITE_URL}/issues/issue-{issue_num:04d}.html""",
    }
