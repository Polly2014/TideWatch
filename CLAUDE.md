# CLAUDE.md — 观潮 (TideWatch)

## Project Overview

AI 投研搭档 MCP Server — 多维融合股票分析引擎。不是仪表盘，而是一个**可编程的投研引擎**。

核心理念：**不是给你看数据，而是跟你聊投资。**

## Commands

```bash
cd X-Workspace/TideWatch-MCP-Server
poetry install              # 安装依赖
poetry run tidewatch        # 本地模式 (stdio)
poetry run tidewatch --http --port 8889  # 远程模式 (HTTP)
```

## Architecture

```
TideWatch-MCP-Server/
├── pyproject.toml          # Poetry 配置 + 入口点
├── config.env              # 环境变量
├── setup.sh                # 一键安装脚本 (Azure VM)
├── src/
│   └── tidewatch/          # Python 包 (import tidewatch.xxx)
│       ├── __init__.py
│       ├── server.py       # ⭐ MCP 主入口 (FastMCP + stdio/HTTP 双模式, 13 工具)
│       ├── data.py         # 数据层 (baostock 日K线 + AKShare 资金/新闻)
│       ├── technical.py    # 技术分析引擎
│       ├── regime.py       # 市场体制识别
│       ├── narrative.py    # 叙事式分析报告生成
│       ├── llm.py          # LLM 叙事润色 (CopilotX + Claude Sonnet 4)
│       ├── tracker.py      # 信号追踪系统 (SQLite, 5min去重)
│       ├── guardrails.py   # 行为护栏 (Anti-FOMO, 3条规则)
│       └── portfolio.py    # 三级股票池 (持仓+自选+热饰70只)
├── config/                 # 部署配置
│   ├── nginx_tidewatch.polly.wang.conf  # Nginx 反向代理
│   └── mcp_remote.example.json         # 客户端配置示例
├── scripts/                # 部署脚本
│   ├── setup_domain.sh     # DNS + Nginx + SSL 一键配置
│   └── tidewatch.service   # systemd 服务文件
└── data/                   # 运行时数据 (git-ignored)
    └── signals.db          # 信号追踪数据库
```

注意：Phase 3 已完成 LLM 叙事润色 + 三级股票池 + 持仓自选管理。产业链图谱和雪球数据源等积累足够信号数据后再开工。Dashboard 本地维护（`static/tidewatch.html`），不走 git push。

## MCP Tools

| Tool | 用途 |
|------|------|
| `analyze_stock` | ⭐ 核心：个股综合分析（技术+资金+消息+体制），支持 `skip_llm=true` 跳过润色秒出 |
| `get_regime` | 今日潮势速读（牛/熊/横盘/高波动） |
| `compare_stocks` | 多股横向对比 |
| `get_money_flow_detail` | 资金流向详细分析 |
| `get_stock_news_report` | 个股新闻消息面 |
| `get_north_flow_report` | 北向资金分析 |
| `polish_narrative_llm` | LLM 叙事润色（配合 skip_llm 渐进加载用）|
| `review_signals` | 查看历史信号和胜率统计 |
| `update_signal_outcomes` | 回填历史信号实际走势 |
| `scan_market` | 三级股票池扫描（持仓+自选+热饰70只，串行K线+技术评分）5min缓存，asyncio.to_thread 不阻塞事件循环 |
| `manage_holdings` | 持仓管理（添加/移除/查看，带买入价和数量）|
| `manage_watchlist` | 自选股管理（添加/移除/查看，可备注关注原因）|
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
- [x] scan_market v2 — 三级股票池扫描（持仓+自选+热饰70只，并发K线+技术评分，绕过 push2 反爬）5min缓存 (2026-03-13)
- [x] manage_holdings / manage_watchlist — 持仓管理（带买入价）+ 自选股管理（SQLite）(2026-03-13)
- [ ] 产业链图谱 v1（新能源/AI/消费核心链硬编码）
- [ ] 雪球数据源（备用，实时数据更快）

### Phase 4: 触达层
- [x] Azure VM 远程部署代码准备（FastMCP HTTP 双模式 + API Key 认证 + Nginx + systemd）(2026-03-12)
- [x] Azure VM 实际部署（`tidewatch.polly.wang/mcp`，Cloudflare DNS + Let's Encrypt SSL）(2026-03-12)
- [x] Web Dashboard 主体 — `static/tidewatch.html` 本地维护 (2026-03-13):
  - 前端直接 fetch MCP JSON-RPC（`mcpCall('scan_market')` 等）
  - 持仓（浮盈/浮亏 + 买入价/数量 meta）+ 自选 + 热门三级展示
  - 顶部：市场体制 regime badge | 持仓总浮盈 | 看多/看空比
  - Skeleton + localStorage Cache (24h) + Split-Phase Init + Fade 过渡
  - Sparkline 7日趋势（无数据灰色 `---` 占位）
  - 冲突检测高亮（Apple 柔光 box-shadow + 7px 琥珀脉冲点 `::after`）
  - Hover 交互（Score legend / section tints / card 悬浮阴影）
  - 小龙虾 Review: 9.5/10 + 9/10 两轮
- [x] Web Dashboard — 个股详情面板 (2026-03-13):
  - 点击卡片 → `analyze_stock(skip_llm=true)` 秒出四维分析
  - 异步 `polish_narrative_llm` 火并忘 — LLM 完成后直接显示最终版
  - 双栏布局：左(四维卡片+冲突检测+建议仓位) / 右(🤖 AI 深度分析)
  - 休盘缓存：`isMarketOpen()` 判断，休盘期间 0ms 秒开
  - overlay fade-in (opacity+visibility 过渡)
  - 左右键切换 + Esc 关闭
- [ ] 移动端适配（tooltip → click popover，当前桌面端优先）
- [ ] 实时推送（自选股监控 + 信号变化通知）

## Deployment

### Azure VM

SSH 配置见 `ssh.config`（git-ignored），快捷连接：
```bash
ssh -F ssh.config Azure-Server
```

服务管理：
```bash
ssh -F ssh.config Azure-Server "sudo systemctl status tidewatch"   # 状态
ssh -F ssh.config Azure-Server "sudo systemctl restart tidewatch"  # 重启
ssh -F ssh.config Azure-Server "cd ~/GitHub_Workspace/TideWatch-MCP-Server && git pull && sudo systemctl restart tidewatch"  # 更新部署
```

### 本地模式 (stdio)
```bash
poetry run tidewatch            # Claude Desktop / Cursor / VS Code
```

### 远程模式 (HTTP)
```bash
# Azure VM 上运行
poetry run tidewatch --http --port 8889

# 或用 systemd
sudo cp scripts/tidewatch.service /etc/systemd/system/
sudo systemctl enable --now tidewatch
```

### 架构
```
客户端 (VS Code / Claude Desktop)
    │
    │ HTTPS + API Key (X-API-Key header)
    ▼
tidewatch.polly.wang:443 (Nginx + Let's Encrypt SSL)
    │
    │ proxy_pass (HTTP)
    ▼
127.0.0.1:8889 (FastMCP Streamable HTTP)
```

### 客户端配置
```json
{
    "TideWatch": {
        "url": "https://tidewatch.polly.wang/mcp",
        "headers": { "X-API-Key": "polly-tidewatch-xxx" }
    }
}
```

### 部署步骤
1. Cloudflare 加 A 记录: `tidewatch` → Azure VM IP
2. Azure VM 上 `git clone` + `./setup.sh`
3. 编辑 `.env` 设置 `COPILOTX_API_KEY`（`MCP_API_KEY` 由 setup.sh 自动生成）
4. `sudo ./scripts/setup_domain.sh` (配置 Nginx + SSL)
5. `sudo systemctl enable --now tidewatch`

## Known Issues

- `stock_zh_a_spot_em()` 在本地 Mac 和 Azure VM 上均无法使用 — 根因是东方财富 `push2.eastmoney.com` 对非浏览器请求做了反爬限制（SSL 握手成功但返回 Empty reply），与 DNS 和地域无关。影响范围：`scan_market`、`get_stock_realtime`、`get_stock_name`（已有 fallback）。其他 AKShare 接口（日K线 `stock_zh_a_hist`、资金流向、新闻等）正常
- MCP 工具不要加 `dict[str, Any]` 返回类型注解（FastMCP 2.x outputSchema 冲突）
- 日志必须输出到 stderr（MCP 用 stdout 通信）
- 信号记录已加 5 分钟去重窗口，同一 symbol 短时间内不重复入库
- 时间戳均使用北京时间 (UTC+8)，通过 `_now_bj()` 统一处理，Azure VM 默认 UTC
- `analyze_stock` 股票名称解析链：持仓名称 → 自选名称 → HOT_NAMES → get_stock_name()，避免 push2 失效时显示代码
- 后台预热仅在北京时间 7:00-23:59 执行，凌晨 0-7 点跳过（东方财富维护窗口断连）
- 扫描缓存持久化到 `data/scan_cache.json`，重启后自动恢复，避免冷启动 Dashboard 显示空数据
- Azure VM 并发 58 只股票拉 AKShare 会触发东方财富限流/断连，单个 analyze_stock 正常，ThreadPoolExecutor 已加 120s/10s 双层超时
- `analyze_stock` 通过 `asyncio.to_thread()` 包装，不阻塞事件循环
- `scan_market` 同样通过 `asyncio.to_thread(_scan_market_sync)` 包装 — async def 里不能做同步阻塞 I/O（73只×0.3s=22s 会卡死整个事件循环）
- 日K线数据源已迁移至 baostock（单只 0.28s，零反爬），AKShare 仅用于资金流向/新闻/龙虎榜/北向/ETF
- baostock 单连接 + `threading.Lock(acquire timeout=15s)` 保护线程安全 + 30s 自动重连
- baostock socket 三层超时保护（🦞9.0/10）：monkey-patch `connect()` 注入 10s `settimeout` → `_bs_login()` 登录后双保险 `settimeout` → 异常统一走 `_force_close_bs_socket()` 关 socket + 标记 session 失效。根治僵尸 TCP 卡死进程问题
- Dashboard 自动刷新仅在盘中 + 可见标签 + 无详情面板时触发（智能三重守卫）
