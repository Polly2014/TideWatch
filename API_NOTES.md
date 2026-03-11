# 雪球 API 验证结果（已测试通过 2026-03-11）

## 认证方式
- Cookie 名：`xqat`（不是 xq_a_token！）
- 需要带的 Headers：
  ```
  Cookie: xqat=<token>;cookiesu=<id>;u=<uid>;xq_is_login=1;device_id=<did>
  User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
  Referer: https://xueqiu.com/S/<SYMBOL>
  ```

## 已验证 API

### 1. 实时行情
```
GET https://stock.xueqiu.com/v5/stock/quote.json?symbol=SZ002111&extend=detail
```
- 只需 `xq_a_token` cookie 即可（用 cookie name `xq_a_token` 也行）
- 返回：current, high, low, open, last_close, volume, amount, percent, chg, pe, pb, market_capital 等

### 2. K线数据
```
GET https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol=SZ002111&begin=<timestamp_ms>&period=day&type=before&count=-20&indicator=kline
```
- **必须用完整 cookie**（xqat + cookiesu + u + xq_is_login + device_id）
- **必须带 Referer header**
- 返回字段名是 `item`（不是 items！）
- column: ["timestamp", "volume", "open", "high", "low", "close", "chg", "percent", "turnoverrate", "amount", "volume_post", "amount_post"]
- period 可选: day, week, month, quarter, year, 60m, 120m, etc.
- type=before + count=-N = 从 begin 往前取 N 根K线
- begin 用毫秒时间戳

### 3. 其他待验证
- 财务数据: `https://stock.xueqiu.com/v5/stock/finance/`
- 持仓: 需要进一步探索
