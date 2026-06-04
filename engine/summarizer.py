"""
AI analysis engine — "开源搞钱周刊" edition.
Two-stage pipeline:
  1. Filter: select top 3-5 repos with monetization potential
  2. Analyze: deep-dive into business model, deploy guide, revenue estimate
"""
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from .templates import (
    SYSTEM_PROMPT,
    REPO_ANALYSIS_PROMPT,
    FILTER_PROMPT,
    TITLE_PROMPT,
    INTRO_PROMPT,
)

load_dotenv()

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY not set in .env")
        _client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    return _client


def _chat(prompt: str, system: str = SYSTEM_PROMPT, max_tokens: int = 800) -> str:
    """Send a chat request to DeepSeek."""
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


def _parse_json(raw: str) -> dict:
    """Robust JSON parsing from LLM output."""
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    return json.loads(raw.strip())


def filter_money_repos(repos: list[dict], top_n: int = 5) -> list[dict]:
    """
    Stage 1: Filter repos to only those with monetization potential.
    Uses AI to select the top N most promising projects.
    """
    if len(repos) <= top_n:
        return repos

    repo_list = "\n".join(
        f"- {r['full_name']}: {r['description'][:80]} (⭐{r['stargazers_count']})"
        for r in repos
    )
    prompt = FILTER_PROMPT.format(repo_list=repo_list)

    try:
        raw = _chat(prompt, max_tokens=300)
        selected = [
            line.strip().lstrip("- ").strip()
            for line in raw.strip().split("\n")
            if line.strip()
        ]
        # Match selected names back to repos
        filtered = []
        for name in selected:
            for r in repos:
                if r["full_name"] == name:
                    filtered.append(r)
                    break
        if len(filtered) >= 3:
            print(f"[engine] AI filtered: {len(repos)} -> {len(filtered)} repos")
            return filtered[:top_n]
    except Exception as e:
        print(f"[engine] Filter failed, using all repos: {e}")

    return repos[:top_n]


def analyze_repo(repo: dict) -> dict:
    """
    Stage 2: Deep analysis of a single repo.
    Returns dict with: money_score, business_model, deploy_steps,
    deploy_difficulty, revenue_estimate, revenue_example, action_items
    """
    readme = repo.get("readme", "")[:1500]
    prompt = REPO_ANALYSIS_PROMPT.format(
        name=repo["full_name"],
        description=repo["description"],
        language=repo["language"],
        stargazers_count=repo["stargazers_count"],
        topics=", ".join(repo.get("topics", [])),
        readme=readme,
    )

    try:
        raw = _chat(prompt, max_tokens=800)
        return _parse_json(raw)
    except Exception as e:
        print(f"[engine] Analysis failed for {repo['full_name']}: {e}")
        return {
            "one_liner": repo["description"][:50] or "暂无简介",
            "money_score": 3,
            "money_score_reason": "信息不足，建议自行评估",
            "business_model": "详见项目主页",
            "deploy_steps": ["git clone 项目", "按 README 部署"],
            "deploy_difficulty": "中等",
            "revenue_estimate": "不确定",
            "revenue_example": "暂无参考案例",
            "target_user": "有动手能力的开发者",
            "action_items": ["阅读 README", "本地跑通项目", "研究目标用户"],
        }


def generate_title(repos: list[dict]) -> str:
    """Generate a catchy title."""
    repo_list = "\n".join(f"- {r['full_name']}" for r in repos[:5])
    prompt = TITLE_PROMPT.format(repo_list=repo_list)
    result = _chat(prompt, system="你是标题高手。", max_tokens=50)
    return result.strip().strip('"').strip("《》")


def generate_intro(repos: list[dict]) -> str:
    """Generate an engaging intro."""
    repo_list = "\n".join(
        f"- {r['full_name']}: {r.get('analysis', {}).get('one_liner', r['description'][:60])}"
        for r in repos
    )
    prompt = INTRO_PROMPT.format(repo_list=repo_list)
    return _chat(prompt, max_tokens=200)


def analyze_all(repos: list[dict]) -> list[dict]:
    """
    Full pipeline:
    1. Filter to top 5 monetizable repos
    2. Deep-analyze each one
    Returns repos with 'analysis' key.
    """
    # Stage 1: Filter
    print(f"[engine] Filtering {len(repos)} repos for money-making potential...")
    selected = filter_money_repos(repos)

    # Stage 2: Deep analyze
    print(f"[engine] Deep-analyzing {len(selected)} repos via DeepSeek...")
    for i, repo in enumerate(selected):
        print(f"[engine]   ({i + 1}/{len(selected)}) {repo['full_name']}...")
        repo["analysis"] = analyze_repo(repo)

    print("[engine] Done!")
    return selected
