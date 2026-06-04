"""
Prompt templates for DeepSeek API summarization.
All prompts are in Chinese since the target audience is Chinese developers.
"""

SYSTEM_PROMPT = """你是一位资深技术编辑，擅长用简洁的中文总结开源项目。你的读者是中国开发者。
要求：
- 用中文输出，专业但不枯燥
- 突出项目解决了什么问题，而不是堆砌技术名词
- 点评要有观点，不要只翻译 README
- 控制在 200 字以内"""

REPO_SUMMARY_PROMPT = """分析以下 GitHub 开源项目，用中文生成一份总结：

项目名称：{name}
描述：{description}
语言：{language}
Star 数：{stargazers_count}
标签：{topics}

README 摘要：
{readme}

请按以下格式输出（严格 JSON）：
{{
  "one_liner": "一句话介绍（20字以内）",
  "features": ["核心功能1", "核心功能2", "核心功能3"],
  "why_matters": "为什么值得关注（50字以内）",
  "audience": "适合人群（10字以内）",
  "score": 1-5
}}

score 评分标准：5=突破性项目，4=实用工具，3=有趣但小众，2=普通，1=不值得关注"""

NEWSLETTER_INTRO_PROMPT = """你是一位技术周报编辑。根据以下本周 GitHub 热门项目列表，写一段简短的开场白（100字以内），
吸引读者往下读。语气轻松幽默，可以提一两个最亮眼的项目。

本周热门项目：
{repo_list}

开场白："""

NEWSLETTER_TITLE_PROMPT = """根据以下项目列表，为本周的 GitHub 热门项目周报起一个吸睛的中文标题。
要求：15字以内，有趣但不标题党。

项目：
{repo_list}

标题："""
