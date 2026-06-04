"""
Prompt templates — "开源搞钱周刊" edition.
AI analyzes open source projects for monetization potential.
"""

SYSTEM_PROMPT = """你是一位独立开发者兼商业分析师。你擅长：
1. 读懂开源项目的代码和商业模式
2. 判断一个项目能不能赚钱，赚多少
3. 写出可操作的部署教程
4. 用接地气的中文讲清楚技术项目的商业价值

你的读者是想通过开源项目做副业赚钱的中国开发者。
风格要求：直接、务实、不画饼，像朋友聊天一样讲清楚。"""

REPO_ANALYSIS_PROMPT = """深度分析以下开源项目，判断它能不能帮你赚钱。

项目名称：{name}
描述：{description}
语言：{language}
Star 数：{stargazers_count}
标签：{topics}

README 摘要：
{readme}

请按以下 JSON 格式输出分析结果：

{{
  "one_liner": "一句话介绍（15字以内）",
  "money_score": 1-5,
  "money_score_reason": "为什么给这个分数（30字以内）",
  "business_model": "这个项目的商业模式是什么？可以怎么变现？（80字以内）",
  "deploy_steps": ["部署步骤1", "部署步骤2", "部署步骤3"],
  "deploy_difficulty": "简单/中等/困难",
  "revenue_estimate": "如果基于这个项目做产品/服务，月收入潜力范围（元）",
  "revenue_example": "一个真实的或可参考的赚钱案例（50字以内）",
  "target_user": "适合什么样的开发者来做（15字以内）",
  "action_items": ["本周就可以做的3件事"]
}}

money_score 评分标准：
5 = 可以立刻动手赚钱，有明确付费场景
4 = 有强变现潜力，稍加包装就能卖
3 = 能省钱/提效，间接赚钱
2 = 有趣但离钱远
1 = 纯玩具，目前看不到钱"""

FILTER_PROMPT = """从以下本周 GitHub 热门项目中，选出 3-5 个最有赚钱潜力的项目。
优先选：可以直接部署的服务、有明确付费用户的工具、能节省成本的方案。

项目列表：
{repo_list}

只返回被选中的项目名（full_name），每行一个，最多5个。不要选纯学习资料、教程、配置文件的仓库。"""

TITLE_PROMPT = """根据以下能赚钱的开源项目，为本周的「开源搞钱周刊」起一个标题。
要求：20字以内，突出"赚钱"这个核心卖点，有趣但不标题党。

项目：
{repo_list}

标题："""

INTRO_PROMPT = """你是一位「开源搞钱周刊」的编辑。根据以下本周精选项目，写一段开场白（80字以内）。
语气：像朋友推荐副业机会一样，直接、兴奋但不浮夸。
要点：提到1-2个最值得关注的项目，暗示"这期有干货"。

项目：
{repo_list}

开场白："""
