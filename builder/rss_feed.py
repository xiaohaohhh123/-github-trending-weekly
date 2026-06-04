"""RSS feed generator."""
import os
import json
from datetime import datetime


def _escape(text: str) -> str:
    """Escape text for XML."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def generate_rss(manifest_path: str, site_url: str = "https://xiaohaohhh123.github.io/github-trending-weekly") -> str:
    """
    Generate RSS 2.0 XML from the issues manifest.
    """
    if not os.path.exists(manifest_path):
        return '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>GitHub Trending Weekly</title><description>No issues yet</description></channel></rss>'

    with open(manifest_path, "r", encoding="utf-8") as f:
        issues = json.load(f)

    items = []
    for issue in sorted(issues, key=lambda i: i["issue"], reverse=True):
        pub_date = issue.get("date", "")
        try:
            dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
            pub_date = dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
        except Exception:
            pass

        link = f"{site_url}/issues/issue-{issue['issue']:04d}.html"
        repo_names = ", ".join(r["full_name"] for r in issue.get("repos", [])[:5])

        items.append(f"""    <item>
      <title>{_escape(issue['title'])}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <description>本周收录 {issue.get('repo_count', 0)} 个热门项目：{_escape(repo_names)}</description>
      <pubDate>{pub_date}</pubDate>
    </item>""")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>GitHub Trending Weekly</title>
    <link>{site_url}</link>
    <description>每周一自动抓取 GitHub 热门项目，DeepSeek AI 生成中文点评</description>
    <language>zh-CN</language>
    <lastBuildDate>{datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>"""
