import sqlite3, sys
sys.path.insert(0, "src")
from tidewatch.data import MarketData

md = MarketData()

# Test get_stock_daily for 002111
df = md.get_stock_daily("002111", days=15)
print(f"DataFrame shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
if not df.empty:
    print(f"date dtype: {df['date'].dtype}")
    print(f"First 3 rows:")
    print(df[['date','close']].head(3))
    print(f"Last 3 rows:")
    print(df[['date','close']].tail(3))
    
    # Simulate backfill logic
    from datetime import datetime, date
    signal_dt = date(2026, 3, 12)
    print(f"\nSignal date: {signal_dt}")
    
    # Check what df['date'].dt.date gives
    try:
        future = df[df["date"].dt.date > signal_dt]
        print(f"Future rows after {signal_dt}: {len(future)}")
        if len(future) >= 5:
            print(f"5d close: {float(future.iloc[4]['close'])}")
    except Exception as e:
        print(f"ERROR with .dt.date: {e}")
        # Try alternative
        print(f"date column sample: {df['date'].iloc[0]} type={type(df['date'].iloc[0])}")
else:
    print("DataFrame is EMPTY!")
