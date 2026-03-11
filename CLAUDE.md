# CLAUDE.md — 观潮 (TideWatch)

## Project Overview

AI 投研搭档 MCP Server — 多维融合股票分析引擎。不是仪表盘，而是一个**可编程的投研引擎**。

核心理念：**不是给你看数据，而是跟你聊投资。**

## Commands

```bash
cd X-Workspace/TideWatch
poetry install              # 安装依赖
poetry run tidewatch        # 启动 MCP Server (stdio)
```

## Architecture

```
TideWatch/
├── pyproject.toml          # Poetry 配置 + 入口点
├── config.env              # 环境变量
├── src/
│   └── tidewatch/          # Python 包 (import tidewatch.xxx)
│       ├── __init__.py
│       ├── server.py       # ⭐ MCP 主入口 (FastMCP + 7 tools)
│       ├── data.py         # 数据层 (AKShare, 带缓存)
│       ├── technical.py    # 技术分析引擎
│       ├── regime.py       # 市场体制识别
│       └── narrative.py    # 叙事式分析报告生成
└── data/                   # 运行时数据 (git-ignored)
```

注意：Phase 2 计划加入 `api_server.py` (FastAPI REST API) 和 Web Dashboard，当前 Phase 1 仅 MCP Server。

## MCP Tools

| Tool | 用途 |
|------|------|
| `analyze_stock` | ⭐ 核心：个股综合分析（技术+资金+消息+体制） |
| `get_regime` | 市场体制识别（牛/熊/横盘/高波动） |
| `compare_stocks` | 多股横向对比 |
| `get_money_flow_detail` | 资金流向详细分析 |
| `get_stock_news_report` | 个股新闻消息面 |
| `get_north_flow_report` | 北向资金分析 |
| `server_status` | 服务器状态 |

## Design Principles

1. **多维交叉验证** — 技术面+资金面+消息面+市场体制，四维交叉
2. **冲突检测** — "技术面看多但主力在出货"这种矛盾才是真金
3. **体制感知** — 横盘市里看什么都是观望，牛市里回调就是机会
4. **MCP-Native** — 在 Claude/Cursor 中直接使用，UI 只是引擎的皮肤

## Roadmap

### Phase 1: ✅ MCP Engine (current)
- AKShare 数据接入
- 技术分析 + 市场体制识别
- 冲突检测

### Phase 2: 引擎增强
- [ ] 信号追踪 + 历史胜率
- [ ] 行为护栏（Anti-FOMO）
- [ ] 产业链图谱
- [ ] 叙事式分析报告（LLM 生成）

### Phase 3: Web Dashboard
- [ ] Next.js 前端
- [ ] REST API 暴露
- [ ] 实时推送
