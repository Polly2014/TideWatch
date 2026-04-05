"""
LLM 叙事润色 — 通过 CopilotX API 将模板叙事润色为自然的分析师语气
失败时 fallback 到模板叙事，零影响
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# 延迟初始化（避免启动时就报错）
_client = None


def _get_client():
    """延迟初始化 OpenAI 客户端"""
    global _client
    if _client is not None:
        return _client

    api_key = os.getenv("COPILOTX_API_KEY", "")
    api_base = os.getenv("COPILOTX_API_BASE", "https://api.polly.wang/v1")

    if not api_key:
        logger.info("未配置 COPILOTX_API_KEY，LLM 润色禁用")
        return None

    try:
        from openai import OpenAI
        _client = OpenAI(api_key=api_key, base_url=api_base, default_headers={"X-Client-Id": "tidewatch"})
        logger.info(f"LLM 客户端已初始化: {api_base}")
        return _client
    except Exception as e:
        logger.warning(f"LLM 客户端初始化失败: {e}")
        return None


def polish_narrative(
    template_narrative: str,
    stock_name: str,
    score: int,
    model: str = "",
    portfolio_context: str = "",
    is_us: bool = False,
    news: list = None,
    lhb: list = None,
    data_summary: str = "",
) -> str:
    """
    用 LLM 润色模板叙事

    Args:
        template_narrative: 模板生成的叙事文本
        stock_name: 股票名称
        score: 综合评分
        model: LLM 模型（默认从环境变量读取）
        portfolio_context: 用户持仓上下文
        is_us: 是否为美股
        news: 新闻列表
        lhb: 龙虎榜数据

    Returns:
        润色后的叙事文本（失败时返回原文）
    """
    client = _get_client()
    if client is None:
        return template_narrative

    model = model or os.getenv("COPILOTX_MODEL", "claude-sonnet-4")

    portfolio_section = ""
    if portfolio_context:
        portfolio_section = f"""
用户持仓情况：{portfolio_context}
请结合用户的持仓状况给出个性化建议（如：持仓成本、浮盈浮亏幅度、是否应该止盈/止损/加仓/减仓/观望）。
"""

    if is_us:
        market_role = "美股分析师"
        market_rules = "- 美股支持碎股交易，无最小交易单位限制"
    else:
        market_role = "A股分析师"
        market_rules = '- A股交易规则：最小交易单位1手=100股，不能买卖零股。如果用户只持1手，不要建议"减半仓"'

    # 新闻摘要（如有）
    news_section = ""
    if news:
        headlines = [f"- {n.get('title', '')}" for n in news[:5] if n.get('title')]
        if headlines:
            news_section = f"\n近期新闻：\n" + "\n".join(headlines) + "\n请结合新闻判断消息面对技术走势的影响，如有重大利好/利空务必提及。\n"

    # 龙虎榜（如有）
    lhb_section = ""
    if lhb:
        lhb_lines = []
        for item in lhb[:3]:
            net = item.get('net', 0)
            net_str = f"净{'买' if net > 0 else '卖'}{abs(net)/10000:.0f}万"
            lhb_lines.append(f"- {item.get('date', '')} {item.get('reason', '')} {net_str}")
        if lhb_lines:
            lhb_section = f"\n龙虎榜（近期上榜）：\n" + "\n".join(lhb_lines) + "\n龙虎榜反映机构/游资动向，请结合技术面判断主力意图。\n"

    # 结构化数据摘要（如有）
    data_section = ""
    if data_summary:
        data_section = f"""
结构化数据：
{data_summary}
请基于以上数据做独立判断，不要只改写模板叙事的措辞。如果数据之间有矛盾（如技术面看空但估值便宜），请明确指出。
"""

    prompt = f"""你是一位经验丰富的{market_role}，正在和朋友聊投资。
请基于以下数据和分析，输出一段自然的、有"聊天感"的投资短评。

要求：
- 基于结构化数据做独立交叉验证，不要只改写模板叙事
- 语气像在微信群里给朋友分享观点，不要太正式
- 如果数据之间有矛盾（技术vs基本面、资金vs价格），要重点分析
- 如果有冲突信号或护栏警告，必须突出强调
- 如果有用户持仓信息，结合持仓成本和浮盈做出具体操作建议
{market_rules}
- 控制在 300 字以内
- 不要加任何标题或格式标记，纯文本即可

股票：{stock_name}
综合评分：{score:+d}
{data_section}{portfolio_section}{news_section}{lhb_section}
模板分析（供参考，不要照搬）：
{template_narrative}"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
        )
        polished = response.choices[0].message.content.strip()
        if polished:
            logger.info(f"✨ LLM 叙事润色完成: {stock_name}")
            return polished
    except Exception as e:
        logger.warning(f"LLM 润色失败，使用模板叙事: {e}")

    return template_narrative
