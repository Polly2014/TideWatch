"""
市场体制识别 — Market Regime Detection
识别大盘当前处于牛市/熊市/横盘/高波动状态
同一技术形态在不同体制下含义完全不同
"""

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class RegimeDetector:
    """市场体制识别器"""

    def detect(self, index_df: pd.DataFrame) -> dict[str, Any]:
        """
        基于指数日K线判断市场体制

        Args:
            index_df: 指数日K线 (close, volume, date)

        Returns:
            dict: regime, description, implications
        """
        if index_df.empty or len(index_df) < 60:
            return {"regime": "unknown", "description": "数据不足"}

        close = index_df["close"]

        # 1. 趋势判断: 使用 60日均线斜率 + 价格位置
        ma20 = close.rolling(20).mean()
        ma60 = close.rolling(60).mean()

        ma60_slope = (ma60.iloc[-1] - ma60.iloc[-10]) / ma60.iloc[-10] * 100
        price_vs_ma60 = (close.iloc[-1] / ma60.iloc[-1] - 1) * 100

        # 2. 波动率
        returns = close.pct_change()
        vol_20d = returns.tail(20).std() * np.sqrt(252) * 100
        vol_60d = returns.tail(60).std() * np.sqrt(252) * 100

        # 3. 趋势强度: 20日内涨跌幅
        pct_20d = (close.iloc[-1] / close.iloc[-21] - 1) * 100

        # 4. 市场宽度近似: 最近20日阳线占比
        bull_days = sum(1 for i in range(-20, 0) if close.iloc[i] > close.iloc[i-1])
        bull_ratio = bull_days / 20

        # 体制判断逻辑
        regime = self._classify(ma60_slope, price_vs_ma60, vol_20d, pct_20d, bull_ratio)

        return {
            "regime": regime["name"],
            "emoji": regime["emoji"],
            "description": regime["description"],
            "implications": regime["implications"],
            "metrics": {
                "ma60_slope": round(ma60_slope, 2),
                "price_vs_ma60": round(price_vs_ma60, 2),
                "volatility_20d": round(vol_20d, 1),
                "pct_20d": round(pct_20d, 2),
                "bull_day_ratio": round(bull_ratio, 2),
            },
        }

    def _classify(
        self,
        ma60_slope: float,
        price_vs_ma60: float,
        vol_20d: float,
        pct_20d: float,
        bull_ratio: float,
    ) -> dict:
        """体制分类"""

        # 高波动优先检测
        if vol_20d > 35:
            return {
                "name": "high_volatility",
                "emoji": "🌊",
                "description": "高波动 — 市场剧烈震荡，方向不明",
                "implications": [
                    "缩小仓位，控制风险",
                    "只做高确定性机会",
                    "技术指标失真概率大",
                    "止损设宽一些，不要被洗出去",
                ],
            }

        # 牛市: 均线上行 + 价格在MA60上方 + 近期上涨
        if ma60_slope > 0.3 and price_vs_ma60 > 2 and pct_20d > 0:
            return {
                "name": "bull",
                "emoji": "🐂",
                "description": "牛市 — 趋势向上，均线多头排列",
                "implications": [
                    "回调是买入机会",
                    "信号偏进攻，可右侧追强",
                    "持仓可适当加重",
                    "注意涨多了的获利回吐",
                ],
            }

        # 熊市: 均线下行 + 价格在MA60下方 + 近期下跌
        if ma60_slope < -0.3 and price_vs_ma60 < -2 and pct_20d < 0:
            return {
                "name": "bear",
                "emoji": "🐻",
                "description": "熊市 — 趋势向下，反弹可能是陷阱",
                "implications": [
                    "反弹不要追，可能是诱多",
                    "信号偏防守，控制仓位",
                    "只做超跌反弹的确定性机会",
                    "现金为王，等待右侧信号",
                ],
            }

        # 横盘: 波动率低 + 均线走平 + 涨跌幅小
        if abs(ma60_slope) < 0.3 and abs(pct_20d) < 3:
            return {
                "name": "sideways",
                "emoji": "🦀",
                "description": "横盘震荡 — 无明确方向，区间波动",
                "implications": [
                    "高抛低吸策略为主",
                    "不要追涨杀跌",
                    "支撑位买、压力位卖",
                    "等待方向选择后再加注",
                ],
            }

        # 默认: 震荡偏强/偏弱
        if pct_20d > 0:
            return {
                "name": "mild_bull",
                "emoji": "📈",
                "description": "震荡偏强 — 温和上行，方向尚未确立",
                "implications": [
                    "可轻仓参与强势个股",
                    "不宜重仓",
                    "关注能否突破确立趋势",
                ],
            }
        else:
            return {
                "name": "mild_bear",
                "emoji": "📉",
                "description": "震荡偏弱 — 温和下行，需谨慎",
                "implications": [
                    "整体防守为主",
                    "减仓观望",
                    "关注能否止跌企稳",
                ],
            }

    def get_regime_adjustment(self, regime: str) -> dict:
        """
        根据体制给出信号调整建议

        Returns:
            dict: signal_bias (偏移), position_advice (仓位建议), risk_multiplier
        """
        adjustments = {
            "bull": {"signal_bias": 10, "position_max": 0.8, "stop_loss_multiplier": 1.2},
            "mild_bull": {"signal_bias": 5, "position_max": 0.6, "stop_loss_multiplier": 1.0},
            "sideways": {"signal_bias": 0, "position_max": 0.4, "stop_loss_multiplier": 0.8},
            "mild_bear": {"signal_bias": -5, "position_max": 0.3, "stop_loss_multiplier": 0.8},
            "bear": {"signal_bias": -15, "position_max": 0.2, "stop_loss_multiplier": 0.7},
            "high_volatility": {"signal_bias": 0, "position_max": 0.2, "stop_loss_multiplier": 1.5},
        }
        return adjustments.get(regime, {"signal_bias": 0, "position_max": 0.5, "stop_loss_multiplier": 1.0})
