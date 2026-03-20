"""
叙事式分析报告生成 — Narrative Generator
把技术指标翻译成"像分析师写的短评"
核心差异化：不是仪表盘，而是跟你聊投资
"""

from typing import Any


class NarrativeGenerator:
    """把分析结果转化为叙事式短评"""

    def generate(
        self,
        stock_name: str,
        tech: dict[str, Any],
        regime: dict[str, Any],
        money: dict[str, Any],
        conflicts: list[dict],
        signal: str,
    ) -> str:
        parts = []

        price_pos = tech.get("price_position", {})
        ma_data = tech.get("ma", {})
        vol_data = tech.get("volume", {})
        mom = tech.get("momentum", {})
        boll = tech.get("volatility", {})
        trend = tech.get("trend", {})
        patterns = tech.get("patterns", [])

        price = price_pos.get("price", 0)
        pct_5d = price_pos.get("pct_5d", 0)
        pos_20d = price_pos.get("position_20d", 50)
        vol_ratio = vol_data.get("volume_ratio", 1)
        rsi = mom.get("rsi_14", 50)
        score = trend.get("score", 0)

        # ── 第一段：开场，根据形态切换口吻 ──
        has_breakout = "放量突破MA20" in patterns
        has_hammer = "长下影线(锤子)" in patterns
        has_shooting = "长上影线(射击之星)" in patterns
        is_shrinking = vol_ratio < 0.7

        if has_breakout:
            parts.append(
                f"{stock_name}今天放量突破了20日均线，这是一个值得注意的信号。"
                f"当前报{price:.2f}，近5日涨了{pct_5d:.1f}%，量比{vol_ratio:.1f}x说明资金在主动进攻。"
            )
        elif has_hammer and pos_20d < 30:
            parts.append(
                f"{stock_name}在低位走出锤子线形态，报{price:.2f}。"
                f"近5日跌了{abs(pct_5d):.1f}%后出现长下影线，说明下方有买盘承接，可能是止跌信号。"
            )
        elif has_shooting and pos_20d > 70:
            parts.append(
                f"{stock_name}高位出现射击之星，当前{price:.2f}。"
                f"上方抛压明显，冲高回落的走势说明多头力量在减弱，需要警惕。"
            )
        elif is_shrinking and abs(pct_5d) < 2:
            parts.append(
                f"{stock_name}最近几天在{price:.2f}附近磨，"
                f"{'涨' if pct_5d > 0 else '跌'}了{abs(pct_5d):.1f}%"
                f"但量能只有均量的{vol_ratio:.0%}——市场在等方向。"
            )
        elif pct_5d > 5:
            parts.append(
                f"{stock_name}近5日强势上攻，累计涨{pct_5d:.1f}%，当前{price:.2f}。"
                + (f"{'但量能跟上了' if vol_ratio > 1.2 else '不过量能并没完全跟上，持续性存疑'}。")
            )
        elif pct_5d < -5:
            parts.append(
                f"{stock_name}近5日连续走弱，累计跌{abs(pct_5d):.1f}%至{price:.2f}。"
                + (f"{'放量下跌，恐慌情绪蔓延' if vol_ratio > 1.3 else '缩量阴跌，抛压不大但也没人接'}。")
            )
        else:
            # 默认中性开场
            trend_word = "涨" if pct_5d > 0 else "跌"
            parts.append(
                f"{stock_name}当前{price:.2f}，近5日小幅{trend_word}了{abs(pct_5d):.1f}%，"
                f"处于20日区间的{pos_20d:.0f}%位置。"
            )

        # ── 第二段：多空博弈叙事 ──
        bulls = trend.get("reasons_bull", [])
        bears = trend.get("reasons_bear", [])

        if bulls and bears:
            # 有冲突时，讲"拉扯"的故事
            bull_str = "、".join(bulls[:3])
            bear_str = "、".join(bears[:3])
            parts.append(
                f"多空在博弈——利多方面有{bull_str}；"
                f"但要注意{bear_str}。"
                f"综合评分{score:+d}，{'多头占优' if score > 0 else '空头占优' if score < 0 else '势均力敌'}。"
            )
        elif bulls:
            bull_str = "、".join(bulls[:4])
            parts.append(f"技术面偏强：{bull_str}。综合评分{score:+d}。")
        elif bears:
            bear_str = "、".join(bears[:4])
            parts.append(f"技术面偏弱：{bear_str}。综合评分{score:+d}。")

        # ── 第三段：资金面 + 体制上下文 ──
        context_parts = []

        regime_name = regime.get("regime", "unknown")
        regime_desc = regime.get("description", "")
        if regime_name != "unknown":
            implications = regime.get("implications", [])
            hint = f"（{implications[0]}）" if implications else ""
            context_parts.append(f"大盘{regime_desc}{hint}")

        main_net = money.get("main_net_inflow", None)
        us_rel = money.get("_us_relative", None)
        if main_net is not None and main_net != 0:
            net_wan = abs(main_net) / 10000
            if net_wan >= 10000:
                flow_str = f"{net_wan / 10000:.2f}亿"
            else:
                flow_str = f"{net_wan:.0f}万"
            direction = "流入" if main_net > 0 else "流出"
            # 叙事化：结合资金方向和技术信号
            if main_net > 0 and score > 0:
                context_parts.append(f"主力资金净{direction}{flow_str}，与技术面共振向上")
            elif main_net < 0 and score < 0:
                context_parts.append(f"主力资金净{direction}{flow_str}，与技术面共振向下")
            elif main_net < 0 and score > 0:
                context_parts.append(f"主力资金净{direction}{flow_str}，和技术面方向矛盾")
            else:
                context_parts.append(f"主力资金净{direction}{flow_str}")
        elif us_rel:
            # 美股：用 SPY 相对强弱替代资金面
            rel = us_rel["relative"]
            spy_pct = us_rel["spy_pct_5d"]
            if abs(rel) < 1:
                context_parts.append(f"近5日与SPY走势同步（SPY {spy_pct:+.1f}%）")
            elif rel > 0:
                context_parts.append(f"近5日跑赢SPY {rel:.1f}个百分点（SPY {spy_pct:+.1f}%），相对强势")
            else:
                context_parts.append(f"近5日跑输SPY {abs(rel):.1f}个百分点（SPY {spy_pct:+.1f}%），相对弱势")

        if context_parts:
            parts.append("。".join(context_parts) + "。")

        # ── 第四段：冲突警告（如果有） ──
        if conflicts:
            high_severity = [c for c in conflicts if c.get("severity") == "high"]
            medium_severity = [c for c in conflicts if c.get("severity") == "medium"]

            if high_severity:
                parts.append("⚠️ 重要矛盾信号：" + " ".join(c["description"] for c in high_severity))
            if medium_severity:
                parts.append("注意：" + " ".join(c["description"] for c in medium_severity))

        # ── 结论：有立场的建议 ──
        conclusion_map = {
            "看多": f"综合看好，技术面和体制都支持进攻，可以择机介入，止损设在{price * 0.97:.2f}附近。",
            "偏多": f"整体偏积极，但信号还不够强，建议轻仓试探或等回调到MA5({ma_data.get('ma5', price):.2f})再介入。",
            "中性观望": f"多空僵持，方向不明。如果你已持有，拿着看；如果没有，不急着动手，等选方向。",
            "偏空": f"短期偏弱，不建议抄底。如果持有可以考虑减仓保护利润，观察{price_pos.get('low_20d', price):.2f}支撑是否有效。",
            "看空": f"技术面和资金面共振向下，建议回避或减仓。下方支撑看布林下轨{boll.get('boll_lower', price):.2f}。",
        }
        parts.append(conclusion_map.get(signal, "建议持续观察。"))

        return "\n\n".join(parts)
