"""Test analyze_stock with narrative output"""
import asyncio
from tidewatch.server import analyze_stock


async def main():
    print("🌊 观潮 — 测试完整分析 (002111 威海广泰)\n")
    result = await analyze_stock("002111", include_news=False, include_money_flow=True)

    if "error" in result:
        print(f"❌ {result['error']}")
        return

    # Signal
    sig = result["signal"]
    print(f"📊 信号: {sig['direction']} (评分 {sig['adjusted_score']}, 置信度 {sig['confidence']}%)")
    print(f"   原始评分 {sig['raw_score']} + 体制调整 {sig['regime_adjustment']:+d} = {sig['adjusted_score']}")

    # Regime
    regime = result["regime"]
    print(f"\n🌊 大盘体制: {regime['emoji']} {regime['description']}")

    # Conflicts
    conflicts = result["conflicts"]
    if conflicts:
        print(f"\n⚠️ 冲突检测 ({len(conflicts)} 个):")
        for c in conflicts:
            print(f"   {c['description']}")
    else:
        print("\n✅ 无冲突信号")

    # Narrative!
    narrative = result.get("narrative", "")
    print(f"\n📝 叙事式分析:\n{'─' * 50}")
    print(narrative)
    print(f"{'─' * 50}")

    # Advice
    advice = result["advice"]
    print(f"\n💡 建议仓位上限: {advice['position_max']}")
    print(f"   {advice['stop_loss_hint']}")


asyncio.run(main())
