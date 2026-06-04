"""
Multi-platform auto-promotion engine.
Posts to Twitter/X, Telegram, Discord, and generates copy for manual platforms.
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

SITE_URL = "https://xiaohaohhh123.github.io/-github-trending-weekly"


# ─── Content Generation ───────────────────────────────────────────

def build_promotion_texts(manifest_path: str) -> dict:
    """Generate optimized post content for every platform."""
    if not os.path.exists(manifest_path):
        return {}

    with open(manifest_path, "r", encoding="utf-8") as f:
        issues = json.load(f)
    if not issues:
        return {}

    latest = max(issues, key=lambda i: i["issue"])
    title = latest["title"]
    repos = latest.get("repos", [])
    issue_num = latest["issue"]
    issue_url = f"{SITE_URL}/issues/issue-{issue_num:04d}.html"

    # Sort by money score, pick top 3
    top3 = sorted(repos, key=lambda r: r.get("money_score", 0), reverse=True)[:3]

    twitter_text = _build_twitter_text(title, top3, issue_num, issue_url)
    telegram_text = _build_telegram_text(title, repos, issue_num, issue_url)
    weibo_text = _build_weibo_text(title, top3, issue_num, issue_url)
    bilibili_text = _build_bilibili_text(title, repos, issue_num, issue_url)
    xiaohongshu_text = _build_xiaohongshu_text(title, top3, issue_num, issue_url)
    discord_text = _build_discord_text(title, top3, issue_num, issue_url)

    return {
        "twitter": twitter_text,
        "telegram": telegram_text,
        "discord": discord_text,
        "weibo": weibo_text,
        "bilibili": bilibili_text,
        "xiaohongshu": xiaohongshu_text,
    }


def _build_twitter_text(title: str, top3: list, issue_num: int, url: str) -> str:
    lines = [f"开源搞钱周刊 #{issue_num}", f"{title}", ""]
    for i, r in enumerate(top3):
        name = r["full_name"].split("/")[-1]
        rev = r.get("revenue_estimate", "?")
        lines.append(f"{i+1}. {name} — {rev}")
    lines.extend(["", f"全文: {url}", "#开源项目 #副业 #搞钱"])
    return "\n".join(lines)


def _build_telegram_text(title: str, repos: list, issue_num: int, url: str) -> str:
    top5 = sorted(repos, key=lambda r: r.get("money_score", 0), reverse=True)
    lines = [f"<b>💰 开源搞钱周刊 #{issue_num}</b>", f"<b>{title}</b>", ""]
    for i, r in enumerate(top5):
        name = r["full_name"]
        score = r.get("money_score", "?")
        rev = r.get("revenue_estimate", "?")
        stars = "⭐" * score if isinstance(score, int) else "⭐"
        lines.append(f"{stars} <a href='https://github.com/{name}'>{name}</a>")
        lines.append(f"   赚钱力 {score}/5 · {rev}")
    lines.extend(["", f"<a href='{url}'>📖 阅读全文</a> | <a href='{SITE_URL}/rss.xml'>📡 RSS</a>"])
    return "\n".join(lines)


def _build_weibo_text(title: str, top3: list, issue_num: int, url: str) -> str:
    lines = [f"#开源搞钱周刊# 第{issue_num}期：{title}", ""]
    for i, r in enumerate(top3):
        name = r["full_name"].split("/")[-1]
        rev = r.get("revenue_estimate", "?")
        lines.append(f"{i+1}. {name} — {rev}")
    lines.extend(["", f"全文: {url}", "#开源项目 #副业"])
    return "\n".join(lines)


def _build_bilibili_text(title: str, repos: list, issue_num: int, url: str) -> str:
    top5 = sorted(repos, key=lambda r: r.get("money_score", 0), reverse=True)
    lines = [f"【开源搞钱周刊 第{issue_num}期】{title}", ""]
    for i, r in enumerate(top5):
        name = r["full_name"]
        rev = r.get("revenue_estimate", "?")
        lines.append(f"{i+1}. {name} （{rev}）")
    lines.extend(["", f"每期 AI 精选 GitHub 热门项目，拆解商业模式+部署教程", f"更多: {url}"])
    return "\n".join(lines)


def _build_xiaohongshu_text(title: str, top3: list, issue_num: int, url: str) -> str:
    lines = [
        f"这周 GitHub 上最能赚钱的 {len(top3)} 个项目 💰",
        "",
        f"📌 {title}",
    ]
    for i, r in enumerate(top3):
        name = r["full_name"].split("/")[-1]
        rev = r.get("revenue_estimate", "?")
        lines.append(f"{i+1}️⃣ {name}")
        lines.append(f"   💰 {rev}")
    lines.extend([
        "",
        "🏷️ AI 自动分析商业模式 + 部署教程",
        "🏷️ 每期附带收入潜力评估",
        "🏷️ 独立开发者搞副业必备",
        "",
        f"🔗 全文戳: {url}",
        "",
        "#开源项目 #副业 #程序员搞钱 #GitHub",
    ])
    return "\n".join(lines)


def _build_discord_text(title: str, top3: list, issue_num: int, url: str) -> str:
    lines = [f"**💰 开源搞钱周刊 #{issue_num}**", f"**{title}**", ""]
    for i, r in enumerate(top3):
        name = r["full_name"]
        rev = r.get("revenue_estimate", "?")
        lines.append(f"**{i+1}.** [{name}](https://github.com/{name}) — *{rev}*")
    lines.extend(["", f":link: 全文: {url}"])
    return "\n".join(lines)


# ─── Platform Posters ─────────────────────────────────────────────

def post_to_twitter(text: str) -> bool:
    """Post to Twitter/X using API v2."""
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret = os.getenv("TWITTER_ACCESS_SECRET")

    if not all([api_key, api_secret, access_token, access_secret]):
        print("[twitter] Twitter keys not configured. Skipping.")
        return False

    try:
        # OAuth 1.0a for posting tweets
        from requests_oauthlib import OAuth1

        oauth = OAuth1(api_key, api_secret, access_token, access_secret)
        resp = requests.post(
            "https://api.twitter.com/2/tweets",
            json={"text": text[:280]},
            auth=oauth,
            timeout=15,
        )
        if resp.status_code in (200, 201):
            tweet_id = resp.json().get("data", {}).get("id", "?")
            print(f"[twitter] Posted! tweet_id={tweet_id}")
            return True
        else:
            print(f"[twitter] Failed: {resp.status_code} {resp.text[:200]}")
            return False
    except ImportError:
        print("[twitter] requests_oauthlib not installed. Run: pip install requests-oauthlib")
        return False
    except Exception as e:
        print(f"[twitter] Error: {e}")
        return False


def post_to_telegram(text: str) -> bool:
    """Post to a Telegram channel via Bot API."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    channel_id = os.getenv("TELEGRAM_CHANNEL_ID")

    if not bot_token or not channel_id:
        print("[telegram] Bot token or channel ID not configured. Skipping.")
        return False

    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={
                "chat_id": channel_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            },
            timeout=15,
        )
        if resp.status_code == 200:
            print(f"[telegram] Posted to channel!")
            return True
        else:
            print(f"[telegram] Failed: {resp.status_code} {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"[telegram] Error: {e}")
        return False


def post_to_discord(text: str) -> bool:
    """Post to a Discord channel via webhook."""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        print("[discord] Webhook URL not configured. Skipping.")
        return False

    try:
        resp = requests.post(
            webhook_url,
            json={"content": text[:2000]},
            timeout=15,
        )
        if resp.status_code in (200, 204):
            print(f"[discord] Posted!")
            return True
        else:
            print(f"[discord] Failed: {resp.status_code} {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"[discord] Error: {e}")
        return False


def promote_all(manifest_path: str) -> dict:
    """
    Generate content for ALL platforms and auto-post to those configured.
    Returns a dict of platform -> (text, posted_bool)
    """
    texts = build_promotion_texts(manifest_path)
    results = {}

    for platform, text in texts.items():
        posted = False
        if platform == "twitter":
            posted = post_to_twitter(text)
        elif platform == "telegram":
            posted = post_to_telegram(text)
        elif platform == "discord":
            posted = post_to_discord(text)
        else:
            # Manual platforms — save text for copy-paste
            pass
        results[platform] = {"text": text, "posted": posted}

    return results
