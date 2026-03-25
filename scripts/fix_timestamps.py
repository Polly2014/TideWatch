#!/usr/bin/env python3
"""一次性修正：将 signals 表中的 UTC naive 时间戳转为北京时间 (+08:00)"""
import sqlite3
from datetime import datetime, timedelta, timezone

DB = "/home/azureuser/GitHub_Workspace/TideWatch-MCP-Server/data/signals.db"
BJ_TZ = timezone(timedelta(hours=8))

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# 1. 检测
rows = conn.execute("SELECT id, timestamp FROM signals ORDER BY id").fetchall()
print(f"总信号: {len(rows)}")

naive_count = 0
fixed = 0
for r in rows:
    ts = r["timestamp"]
    if "+" not in ts and "Z" not in ts:
        naive_count += 1
        # 解析为 UTC naive → 加 8 小时 → 标记 +08:00
        utc_dt = datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
        bj_dt = utc_dt.astimezone(BJ_TZ)
        new_ts = bj_dt.isoformat()
        conn.execute("UPDATE signals SET timestamp = ? WHERE id = ?", (new_ts, r["id"]))
        fixed += 1
        if fixed <= 3:
            print(f"  #{r['id']}: {ts} → {new_ts}")

print(f"naive(UTC): {naive_count}, 已修正: {fixed}")

if fixed > 0:
    conn.commit()
    print("✅ 已提交")
else:
    print("无需修正")

conn.close()
