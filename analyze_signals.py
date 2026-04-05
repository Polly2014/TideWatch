import sqlite3
from collections import defaultdict

conn = sqlite3.connect("data/signals.db")
conn.row_factory = sqlite3.Row

# === 1. Overall stats ===
total = conn.execute("SELECT COUNT(*) FROM signals").fetchone()[0]
filled_5d = conn.execute("SELECT COUNT(*) FROM signals WHERE outcome_5d IS NOT NULL").fetchone()[0]
filled_10d = conn.execute("SELECT COUNT(*) FROM signals WHERE outcome_10d IS NOT NULL").fetchone()[0]
correct_5d = conn.execute("SELECT COUNT(*) FROM signals WHERE outcome_5d='correct'").fetchone()[0]
wrong_5d = conn.execute("SELECT COUNT(*) FROM signals WHERE outcome_5d='wrong'").fetchone()[0]
correct_10d = conn.execute("SELECT COUNT(*) FROM signals WHERE outcome_10d='correct'").fetchone()[0]
wrong_10d = conn.execute("SELECT COUNT(*) FROM signals WHERE outcome_10d='wrong'").fetchone()[0]

print(f"=== Overall Stats ===")
print(f"Total signals: {total}")
print(f"5d filled: {filled_5d} (correct={correct_5d}, wrong={wrong_5d}, rate={correct_5d/filled_5d*100:.1f}%)")
print(f"10d filled: {filled_10d} (correct={correct_10d}, wrong={wrong_10d}, rate={correct_10d/filled_10d*100:.1f}%)")

# === 2. By direction ===
print(f"\n=== By Direction (5d) ===")
for dir in ["看多", "偏多", "中性观望", "偏空", "看空"]:
    rows = conn.execute("SELECT outcome_5d, pct_5d FROM signals WHERE direction=? AND outcome_5d IS NOT NULL", (dir,)).fetchall()
    if not rows:
        continue
    correct = sum(1 for r in rows if r["outcome_5d"] == "correct")
    total_d = len(rows)
    avg_pct = sum(r["pct_5d"] for r in rows) / total_d
    print(f"  {dir}: {correct}/{total_d} ({correct/total_d*100:.1f}%) avg_pct={avg_pct:+.2f}%")

# === 3. By score range ===
print(f"\n=== By Score Range (5d) ===")
ranges = [(-100, -75, "强看空"), (-75, -50, "看空"), (-50, -25, "偏空"), (-25, 0, "弱空"), (0, 25, "弱多"), (25, 50, "偏多"), (50, 75, "看多"), (75, 101, "强看多")]
for lo, hi, label in ranges:
    rows = conn.execute("SELECT outcome_5d, pct_5d, symbol, name FROM signals WHERE score>=? AND score<? AND outcome_5d IS NOT NULL", (lo, hi)).fetchall()
    if not rows:
        continue
    correct = sum(1 for r in rows if r["outcome_5d"] == "correct")
    avg_pct = sum(r["pct_5d"] for r in rows) / len(rows)
    print(f"  [{lo:+d},{hi:+d}) {label}: {correct}/{len(rows)} ({correct/len(rows)*100:.1f}%) avg={avg_pct:+.2f}%")

# === 4. By symbol (top wrong) ===
print(f"\n=== By Symbol (5d outcomes) ===")
symbols = conn.execute("SELECT DISTINCT symbol FROM signals WHERE outcome_5d IS NOT NULL").fetchall()
sym_stats = []
for s in symbols:
    sym = s[0]
    rows = conn.execute("SELECT outcome_5d, pct_5d, score, direction, conflicts FROM signals WHERE symbol=? AND outcome_5d IS NOT NULL", (sym,)).fetchall()
    correct = sum(1 for r in rows if r["outcome_5d"] == "correct")
    wrong = len(rows) - correct
    avg_pct = sum(r["pct_5d"] for r in rows) / len(rows)
    name = conn.execute("SELECT name FROM signals WHERE symbol=? LIMIT 1", (sym,)).fetchone()[0]
    sym_stats.append((sym, name, len(rows), correct, wrong, correct/len(rows)*100, avg_pct))
    
sym_stats.sort(key=lambda x: x[5])  # sort by win rate ascending
for sym, name, n, c, w, rate, avg in sym_stats:
    print(f"  {name}({sym}): {c}/{n} ({rate:.1f}%) avg={avg:+.2f}%")

# === 5. With conflicts vs without ===
print(f"\n=== Conflict Impact (5d) ===")
with_conflict = conn.execute("SELECT outcome_5d, pct_5d FROM signals WHERE conflicts IS NOT NULL AND conflicts != '' AND outcome_5d IS NOT NULL").fetchall()
without_conflict = conn.execute("SELECT outcome_5d, pct_5d FROM signals WHERE (conflicts IS NULL OR conflicts = '') AND outcome_5d IS NOT NULL").fetchall()
if with_conflict:
    c1 = sum(1 for r in with_conflict if r["outcome_5d"] == "correct")
    avg1 = sum(r["pct_5d"] for r in with_conflict) / len(with_conflict)
    print(f"  With conflict: {c1}/{len(with_conflict)} ({c1/len(with_conflict)*100:.1f}%) avg={avg1:+.2f}%")
if without_conflict:
    c2 = sum(1 for r in without_conflict if r["outcome_5d"] == "correct")
    avg2 = sum(r["pct_5d"] for r in without_conflict) / len(without_conflict)
    print(f"  Without conflict: {c2}/{len(without_conflict)} ({c2/len(without_conflict)*100:.1f}%) avg={avg2:+.2f}%")

# === 6. High score vs low score with conflicts ===
print(f"\n=== Conflict + Score Interaction (5d) ===")
for label, sql_where in [
    ("|score|>=50 + conflict", "ABS(score)>=50 AND conflicts IS NOT NULL AND conflicts != ''"),
    ("|score|>=50 no conflict", "ABS(score)>=50 AND (conflicts IS NULL OR conflicts = '')"),
    ("|score|<50 + conflict", "ABS(score)<50 AND conflicts IS NOT NULL AND conflicts != ''"),
    ("|score|<50 no conflict", "ABS(score)<50 AND (conflicts IS NULL OR conflicts = '')"),
]:
    rows = conn.execute(f"SELECT outcome_5d, pct_5d FROM signals WHERE {sql_where} AND outcome_5d IS NOT NULL").fetchall()
    if not rows:
        print(f"  {label}: no data")
        continue
    c = sum(1 for r in rows if r["outcome_5d"] == "correct")
    avg = sum(r["pct_5d"] for r in rows) / len(rows)
    print(f"  {label}: {c}/{len(rows)} ({c/len(rows)*100:.1f}%) avg={avg:+.2f}%")

# === 7. Regime impact ===
print(f"\n=== Regime Impact (5d) ===")
regimes = conn.execute("SELECT DISTINCT regime FROM signals WHERE outcome_5d IS NOT NULL").fetchall()
for reg in regimes:
    r = reg[0]
    rows = conn.execute("SELECT outcome_5d, pct_5d FROM signals WHERE regime=? AND outcome_5d IS NOT NULL", (r,)).fetchall()
    if not rows:
        continue
    c = sum(1 for row in rows if row["outcome_5d"] == "correct")
    avg = sum(row["pct_5d"] for row in rows) / len(rows)
    print(f"  {r}: {c}/{len(rows)} ({c/len(rows)*100:.1f}%) avg={avg:+.2f}%")

# === 8. Wrong signals detail ===
print(f"\n=== Wrong Signals Detail (5d) ===")
wrong_rows = conn.execute("""
    SELECT symbol, name, score, direction, price_at_signal, pct_5d, regime, conflicts, timestamp 
    FROM signals WHERE outcome_5d='wrong' ORDER BY pct_5d
""").fetchall()
for r in wrong_rows:
    conf = "Y" if r["conflicts"] else "N"
    print(f"  {r['name']}({r['symbol']}) score={r['score']:+d} {r['direction']} 5d={r['pct_5d']:+.2f}% regime={r['regime']} conflict={conf} ({r['timestamp'][:10]})")

# === 9. 10d wrong detail ===
print(f"\n=== Wrong Signals Detail (10d) ===")
wrong_10 = conn.execute("""
    SELECT symbol, name, score, direction, price_at_signal, pct_10d, regime, conflicts, timestamp 
    FROM signals WHERE outcome_10d='wrong' ORDER BY pct_10d
""").fetchall()
for r in wrong_10:
    conf = "Y" if r["conflicts"] else "N"
    print(f"  {r['name']}({r['symbol']}) score={r['score']:+d} {r['direction']} 10d={r['pct_10d']:+.2f}% regime={r['regime']} conflict={conf} ({r['timestamp'][:10]})")

conn.close()
