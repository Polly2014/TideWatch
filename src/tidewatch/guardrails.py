"""
行为护栏 — Guardrails
阻止你犯蠢，比告诉你买什么更值钱
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from .tracker import get_recent_signals

logger = logging.getLogger(__name__)


def check_guardrails(
    symbol: str,
    tech: dict[str, Any],
) -> list[dict[str, str]]:
    """
    检查行为护栏，返回警告列表

    Args:
        symbol: 当前分析的股票代码
        tech: 技术分析结果

    Returns:
        警告列表，每条包含 type, severity, message, advice
    """
    warnings = []

    # 规则 1: 追高检测
    w = _check_chasing(symbol, tech)
    if w:
        warnings.append(w)

    # 规则 2: 分析频次提醒
    w = _check_frequency()
    if w:
        warnings.append(w)

    # 规则 3: 连续看空还在问
    w = _check_repeated_bearish(symbol)
    if w:
        warnings.append(w)

    return warnings


def _check_chasing(symbol: str, tech: dict) -> dict | None:
    """追高检测：股票近 5 日涨幅超阈值（A股 8% / 美股 15%，美股无涨跌停波动更大）"""
    from .data import is_us_stock
    pct_5d = tech.get("price_position", {}).get("pct_5d", 0)
    threshold = 15 if is_us_stock(symbol) else 8
    if pct_5d > threshold:
        return {
            "type": "fomo_chasing",
            "severity": "high",
            "message": f"🚨 追高警告：这票近5日已涨 {pct_5d:.1f}%，你现在才来看。历史上追涨{threshold}%+的票胜率不到35%。",
            "advice": "如果真要买，等回调到5日线再介入，别在高位站岗。",
        }
    return None


def _check_frequency() -> dict | None:
    """分析频次提醒：24h内分析超过5只不同股票"""
    try:
        recent = get_recent_signals(days=1)
        symbols = list({s["symbol"] for s in recent})
        count = len(symbols)
        if count >= 8:
            return {
                "type": "over_analysis",
                "severity": "medium",
                "message": f"📊 今天已经分析了 {count} 只票（{', '.join(symbols[:5])}{'...' if len(symbols) > 5 else ''}），是不是有点焦虑？",
                "advice": "分析太多反而犹豫不决。聚焦2-3只最有把握的，其他的放一放。",
            }
        elif count >= 5:
            return {
                "type": "over_analysis",
                "severity": "low",
                "message": f"📋 今天已分析 {count} 只票，注意聚焦。",
                "advice": "不用看太多，找到最确定的机会就够了。",
            }
    except Exception as e:
        logger.warning(f"频次检测失败: {e}")
    return None


def _check_repeated_bearish(symbol: str) -> dict | None:
    """连续看空检测：同一只票最近3次都看空还在问"""
    try:
        recent = get_recent_signals(days=30, symbol=symbol)
        if len(recent) >= 3:
            last_3 = recent[:3]  # 已按时间倒序
            all_bearish = all(
                s.get("direction") in ("看空", "偏空") for s in last_3
            )
            if all_bearish:
                return {
                    "type": "bottom_fishing",
                    "severity": "high",
                    "message": f"🎣 抄底警告：你已经连续 {len(last_3)} 次分析 {symbol}，每次都是看空信号，但你还在关注。",
                    "advice": "连续看空还反复查看，是不是在等抄底？别猜底，等右侧信号（放量站上MA5）再考虑。",
                }
    except Exception as e:
        logger.warning(f"连续看空检测失败: {e}")
    return None
