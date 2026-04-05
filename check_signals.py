import sqlite3
conn = sqlite3.connect("data/signals.db")
rows = conn.execute("SELECT id, symbol, timestamp, price_10d, price_20d FROM signals WHERE price_20d IS NOT NULL").fetchall()
print("Signals with 20d:", len(rows))
for r in rows:
    same = " SAME" if abs(r[3]-r[4]) < 0.001 else ""
    print(f"  #{r[0]} {r[1]} {r[2][:16]} 10d={r[3]} 20d={r[4]}{same}")
conn.close()
