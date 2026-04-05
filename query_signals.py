import sqlite3, json
conn = sqlite3.connect('data/signals.db')
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT symbol, name, direction, score, confidence, timestamp, outcome_5d FROM signals ORDER BY timestamp ASC LIMIT 15").fetchall()
print('=== Earliest 15 ===')
for r in rows:
    print(json.dumps(dict(r), ensure_ascii=False))
stats = conn.execute("SELECT symbol, name, COUNT(*) as cnt, ROUND(AVG(score), 1) as avg_score, MIN(timestamp) as first_seen, MAX(timestamp) as last_seen FROM signals GROUP BY symbol ORDER BY cnt DESC").fetchall()
print('\n=== Stats ===')
for s in stats:
    print(json.dumps(dict(s), ensure_ascii=False))
filled = conn.execute('SELECT COUNT(*) FROM signals WHERE outcome_5d IS NOT NULL').fetchone()[0]
print(f'\nOutcomes filled: {filled}/57')
