import sqlite3
conn = sqlite3.connect("data/signals.db")

# Find signals where 20d == 10d (bad data)
rows = conn.execute("""
    SELECT id, symbol, price_10d, price_20d FROM signals 
    WHERE price_20d IS NOT NULL AND price_10d IS NOT NULL 
    AND ABS(price_20d - price_10d) < 0.001
""").fetchall()

print(f"Found {len(rows)} signals with 20d == 10d:")
for r in rows:
    print(f"  #{r[0]} {r[1]}: 10d={r[2]}, 20d={r[3]}")

if rows:
    ids = [r[0] for r in rows]
    conn.execute(f"""
        UPDATE signals SET price_20d = NULL, pct_20d = NULL, outcome_20d = NULL 
        WHERE id IN ({','.join('?' * len(ids))})
    """, ids)
    conn.commit()
    print(f"Cleared 20d data for {len(rows)} signals")

    # Verify
    check = conn.execute("SELECT COUNT(*) FROM signals WHERE price_20d IS NOT NULL").fetchone()[0]
    print(f"Remaining signals with 20d: {check}")

conn.close()
