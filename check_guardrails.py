import sqlite3
from datetime import datetime, timedelta, timezone

conn = sqlite3.connect("data/signals.db")
conn.row_factory = sqlite3.Row
bj = timezone(timedelta(hours=8))

symbols = [r[0] for r in conn.execute("SELECT DISTINCT symbol FROM signals").fetchall()]
print("=== Rule 3: Repeated Bearish ===")
for sym in symbols:
    rows = conn.execute("SELECT direction, score, timestamp FROM signals WHERE symbol=? ORDER BY timestamp DESC LIMIT 3", (sym,)).fetchall()
    if len(rows) >= 3:
        all_bear = all(r["direction"] in ("看空", "偏空") for r in rows)
        if all_bear:
            name = conn.execute("SELECT name FROM signals WHERE symbol=? ORDER BY timestamp DESC LIMIT 1", (sym,)).fetchone()["name"]
            dirs = [str(r["direction"]) + "(" + str(r["score"]) + ")" for r in rows]
            print("  " + name + "(" + sym + "): " + " -> ".join(dirs))

print()
print("=== Rule 4: Conflict + Low Score ===")
rows = conn.execute("SELECT symbol, name, score, conflicts, timestamp FROM signals WHERE conflicts IS NOT NULL AND conflicts != '' ORDER BY timestamp DESC LIMIT 50").fetchall()
seen = set()
for r in rows:
    key = r["symbol"]
    if key in seen:
        continue
    if abs(r["score"]) < 50 and r["conflicts"]:
        seen.add(key)
        print("  " + r["name"] + "(" + r["symbol"] + "): score=" + str(r["score"]) + " | " + r["conflicts"][:80])

print()
cutoff = (datetime.now(bj) - timedelta(hours=24)).isoformat()
recent = conn.execute("SELECT DISTINCT symbol FROM signals WHERE timestamp > ?", (cutoff,)).fetchall()
syms = [r[0] for r in recent]
print("=== Rule 2: Frequency (24h) ===")
print("  Count:", len(syms), "symbols:", syms)
print("  Triggered:", len(syms) >= 5)

conn.close()
