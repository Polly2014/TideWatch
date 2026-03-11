"""Quick end-to-end test for TideWatch"""

from tidewatch.data import MarketData
from tidewatch.technical import TechnicalAnalyzer
from tidewatch.regime import RegimeDetector

md = MarketData()
ta = TechnicalAnalyzer()
rd = RegimeDetector()

# 测试获取 002111 威海广泰的数据
print("📊 获取 002111 日K线...")
df = md.get_stock_daily("002111", days=120)
print(f"  获取到 {len(df)} 条数据")
if not df.empty:
    print(f"  最新: {df.iloc[-1]['date']} 收盘 {df.iloc[-1]['close']}")

    # 技术分析
    print("\n🔬 技术分析...")
    tech = ta.analyze(df)
    print(f"  趋势评分: {tech['trend']['score']}")
    print(f"  信号: {tech['trend']['signal']} ({tech['trend']['strength']})")
    print(f"  RSI: {tech['momentum']['rsi_14']}")
    print(f"  MACD交叉: {tech['momentum']['macd_cross']}")
    print(f"  形态: {tech['patterns']}")
    print(f"  均线多头: {tech['ma']['bullish_aligned']}")
    print(f"  量比: {tech['volume']['volume_ratio']}")
    print(f"  20日位置: {tech['price_position']['position_20d']}%")

# 市场体制
print("\n🌊 市场体制识别...")
idx = md.get_index_daily("000001", days=120)
if not idx.empty:
    regime = rd.detect(idx)
    print(f"  体制: {regime['emoji']} {regime['description']}")
    for imp in regime.get("implications", []):
        print(f"    - {imp}")
else:
    print("  指数数据获取失败")

print("\n✅ 全链路测试通过!")
