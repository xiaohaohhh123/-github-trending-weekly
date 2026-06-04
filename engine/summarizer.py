"""
AI summarization engine using DeepSeek API (OpenAI-compatible).
"""
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from .templates import (
    SYSTEM_PROMPT,
    REPO_SUMMARY_PROMPT,
    NEWSLETTER_INTRO_PROMPT,
    NEWSLETTER_TITLE_PROMPT,
)

load_dotenv()

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY not set in .env")
        _client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )
    return _client


def _chat(prompt: str, system: str = SYSTEM_PROMPT, max_tokens: int = 800) -> str:
    """Send a chat request to DeepSeek, return the response text."""
    client = _get_client()
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return resp.choices[0].message.content


def summarize_repo(repo: dict) -> dict:
    """
    Generate a Chinese summary for a single GitHub repo.
    Returns a dict with keys: one_liner, features, why_matters, audience, score
    """
    readme = repo.get("readme", "")
    if len(readme) > 2000:
        readme = readme[:2000]  # keep it reasonable

    prompt = REPO_SUMMARY_PROMPT.format(
        name=repo["full_name"],
        description=repo["description"],
        language=repo["language"],
        stargazers_count=repo["stargazers_count"],
        topics=", ".join(repo.get("topics", [])),
        readme=readme[:1500],
    )

    try:
        raw = _chat(prompt, max_tokens=600)
        # Try to parse JSON from the response
        raw = raw.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        return json.loads(raw.strip())
    except Exception as e:
        print(f"[engine] Failed to summarize {repo['full_name']}: {e}")
        return {
            "one_liner": repo["description"][:50] or "暂无简介",
            "features": ["详见项目主页"],
            "why_matters": "本周新晋热门项目",
            "audience": "开发者",
            "score": 3,
        }


def generate_intro(repos: list[dict]) -> str:
    """Generate an engaging intro paragraph for the newsletter."""
    repo_list = "\n".join(
        f"- {r['full_name']}: {r.get('summary', {}).get('one_liner', r['description'][:60])}"
        for r in repos[:10]
    )
    prompt = NEWSLETTER_INTRO_PROMPT.format(repo_list=repo_list)
    return _chat(prompt, max_tokens=200)


def generate_title(repos: list[dict]) -> str:
    """Generate a catchy title for the newsletter."""
    repo_list = "\n".join(
        f"- {r['full_name']}"
        for r in repos[:5]
    )
    prompt = NEWSLETTER_TITLE_PROMPT.format(repo_list=repo_list)
    result = _chat(prompt, system="你是一位标题创作专家。", max_tokens=50)
    return result.strip().strip('"').strip("《》")


def summarize_all_repos(repos: list[dict]) -> list[dict]:
    """
    Summarize all repos in the list. Modifies the list in-place
    by adding a 'summary' key to each repo dict.
    Returns the modified list.
    """
    print(f"[engine] Summarizing {len(repos)} repos via DeepSeek API...")
    for i, repo in enumerate(repos):
        print(f"[engine]   ({i + 1}/{len(repos)}) {repo['full_name']}...")
        repo["summary"] = summarize_repo(repo)
    print("[engine] Done!")
    return repos
