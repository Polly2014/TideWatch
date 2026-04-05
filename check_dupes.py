from tidewatch.tracker import _get_conn

conn = _get_conn()

# 3/17 all signals
rows = conn.execute(
    "SELECT id, symbol, name, timestamp, score, direction FROM signals "
    "WHERE timestamp LIKE '2026-03-17%' ORDER BY timestamp"
).fetchall()

for r in rows:
    ts = r["timestamp"][11:19]
    print(f"  #{r['id']} {ts} {r['symbol']} {r['name']} {r['direction']}({r['score']:+d})")
print(f"Total 3/17: {len(rows)}")

# Check for duplicates across ENTIRE table
print()
print("--- Duplicate check (same symbol+score within 5min) ---")
dupes = conn.execute("""
    SELECT s1.id, s2.id, s1.symbol, s1.name, s1.score, s1.timestamp, s2.timestamp
    FROM signals s1
    JOIN signals s2 ON s1.symbol = s2.symbol AND s1.score = s2.score AND s1.id < s2.id
    WHERE abs(julianday(s1.timestamp) - julianday(s2.timestamp)) < 0.004
    ORDER BY s1.id
""").fetchall()
for d in dupes:
    print(f"  Dupe: #{d[0]} & #{d[1]} {d[2]}({d[3]}) score={d[4]}  {d[5][:19]} vs {d[6][:19]}")
print(f"Found {len(dupes)} duplicate pairs")

# Also check within 30min (broader window)
print()
print("--- Broader check (same symbol+score within 30min) ---")
broad = conn.execute("""
    SELECT s1.id, s2.id, s1.symbol, s1.name, s1.score, s1.timestamp, s2.timestamp
    FROM signals s1
    JOIN signals s2 ON s1.symbol = s2.symbol AND s1.score = s2.score AND s1.id < s2.id
    WHERE abs(julianday(s1.timestamp) - julianday(s2.timestamp)) < 0.021
    ORDER BY s1.id
""").fetchall()
for d in broad:
    print(f"  #{d[0]} & #{d[1]} {d[2]}({d[3]}) score={d[4]}  {d[5][:19]} vs {d[6][:19]}")
print(f"Found {len(broad)} pairs")

conn.close()
