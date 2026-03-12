# CLAUDE.md — 观潮 (TideWatch)

## Project Overview

AI 投研搭档 MCP Server — 多维融合股票分析引擎。不是仪表盘，而是一个**可编程的投研引擎**。

核心理念：**不是给你看数据，而是跟你聊投资。**

## Commands

```bash
cd X-Workspace/TideWatch-MCP-Server
poetry install              # 安装依赖
poetry run tidewatch        # 启动 MCP Server (stdio)
```

## Architecture

```
TideWatch-MCP-Server/
├── pyproject.toml          # Poetry 配置 + 入口点
├── config.env              # 环境变量
├── src/
│   └── tidewatch/          # Python 包 (import tidewatch.xxx)
│       ├── __init__.py
│       ├── server.py       # ⭐ MCP 主入口 (FastMCP + 10 tools)
│       ├── data.py         # 数据层 (AKShare, 带缓存)
│       ├── technical.py    # 技术分析引擎
│       ├── regime.py       # 市场体制识别
│       ├── narrative.py    # 叙事式分析报告生成
│       ├── llm.py          # LLM 叙事润色 (CopilotX + Claude Sonnet 4)
│       ├── tracker.py      # 信号追踪系统 (SQLite, 5min去重)
│       └── guardrails.py   # 行为护栏 (Anti-FOMO, 3条规则)
└── data/                   # 运行时数据 (git-ignored)
    └── signals.db          # 信号追踪数据库
```

注意：Phase 3 已完成 LLM 叙事润色。产业链图谝和雪球数据源等积累足够信号数据后再开工。

## MCP Tools

| Tool | 用途 |
|------|------|
| `analyze_stock` | ⭐ 核心：个股综合分析（技术+资金+消息+体制） |
| `get_regime` | 市场体制识别（牛/熊/横盘/高波动） |
| `compare_stocks` | 多股横向对比 |
| `get_money_flow_detail` | 资金流向详细分析 |
| `get_stock_news_report` | 个股新闻消息面 |
| `get_north_flow_report` | 北向资金分析 |
| `review_signals` | 查看历史信号和胜率统计 |
| `update_signal_outcomes` | 回填历史信号实际走势 |
| `scan_market` | 全市场扫描强弱股 Top/Bottom N（盘中效果最佳） |
| `server_status` | 服务器状态 |

## Design Principles

1. **多维交叉验证** — 技术面+资金面+消息面+市场体制，四维交叉
2. **冲突检测** — "技术面看多但主力在出货"这种矛盾才是真金
3. **体制感知** — 横盘市里看什么都是观望，牛市里回调就是机会
4. **MCP-Native** — 在 Claude/Cursor 中直接使用，UI 只是引擎的皮肤

## Roadmap

### Phase 1: ✅ MCP Engine (2026-03-11)
- [x] AKShare 数据接入（日K线 + 资金流向 + 新闻 + 北向资金 + 龙虎榜）
- [x] 技术分析（8维评分：MA/RSI/MACD/KDJ/BOLL/ATR/OBV/形态识别）
- [x] 市场体制识别（6种：牛/熊/横盘/高波动/震荡偏强/震荡偏弱）
- [x] 冲突检测（5种矛盾信号：技术vs资金、个股vs大盘、量价背离等）
- [x] 叙事式分析报告（形态驱动开场 + 多空博弈 + 有立场结论）
- [x] 代理兼容（NO_PROXY + 失败冷却60s + 日K线fallback）

### Phase 2: ✅ 引擎增强 (2026-03-12)
- [x] 信号追踪系统（SQLite，每次分析自动记录，5/10/20日胜率回填）
- [x] 行为护栏 v1（追高检测 / 分析频次提醒 / 连续看空检测）
- [x] scan_market 工具（全市场扫描 Top/Bottom N 强弱股）

### Phase 3: 深度进化
- [x] LLM 叙事润色（CopilotX API + Claude Sonnet 4，失败 fallback 模板叙事）(2026-03-12)
- [ ] 产业链图谝 v1（新能源/AI/消费核心链硬编码）
- [ ] 雪球数据源（备用，实时数据更快）

### Phase 4: 触达层
- [ ] Azure VM 远程部署（FastMCP HTTP + Nginx + SSL → `tidewatch.polly.wang/mcp`，参考 Stylist-MCP-Server）
- [ ] Web Dashboard（Next.js 前端 + REST API）
- [ ] 实时推送（自选股监控 + 信号变化通知）

## Known Issues

- `stock_zh_a_spot_em()` 在本地 Mac 上无法使用 — 根因是 DNS 解析问题：`push2.eastmoney.com` 通过 `push2ipv6.trafficmanager.cn` 做区域路由，Google DNS (8.8.8.8) 解析到的节点 (43.144.251.121) 返回 Empty reply。国内 DNS (114.114.114.114) 解析到不同 IP (47.112.165.11) 但同样无响应。**部署到 Azure VM 后自动解决**。影响范围：`scan_market`、`get_stock_realtime`、`get_stock_name`（已有 fallback）
- MCP 工具不要加 `dict[str, Any]` 返回类型注解（FastMCP 2.x outputSchema 冲突）
- 日志必须输出到 stderr（MCP 用 stdout 通信）
- 信号记录已加 5 分钟去重窗口，同一 symbol 短时间内不重复入库
