# TideWatch（观潮）— AI 投研搭档

## 项目愿景

不是仪表盘，是**可编程的 AI 投研搭档**。核心是 MCP Server，Web Dashboard 是引擎的一个皮肤。

## Phase 1 目标（本次交付）

搭建 MCP Server 骨架 + 核心分析引擎，能在 Claude/Cursor 中通过 MCP 协议调用。

### 技术栈

- **Python 3.11+**
- **FastMCP** — MCP Server 框架
- **FastAPI** — REST API（与 MCP 共享同一引擎）
- **数据源**：雪球 API（A股行情/基本面）+ 备用 AKShare
- **分析**：pandas / numpy / ta-lib（技术指标）
- **包管理**：uv（如果可用）或 pip

### 项目结构

```
TideWatch/
├── SPEC.md                  # 本文件
├── README.md                # 项目说明
├── pyproject.toml           # 项目配置
├── .env.example             # 环境变量模板
├── src/
│   └── tidewatch/
│       ├── __init__.py
│       ├── mcp_server.py    # MCP Server 入口
│       ├── api_server.py    # FastAPI REST 入口
│       ├── core/
│       │   ├── __init__.py
│       │   ├── engine.py        # 分析引擎主逻辑（被 MCP 和 API 共用）
│       │   ├── regime.py        # 市场体制识别（牛/熊/横盘/高波动）
│       │   ├── technical.py     # 技术面分析（K线/量价/均线/形态）
│       │   ├── fundamental.py   # 基本面分析（财报/估值）
│       │   ├── sentiment.py     # 消息面/情绪分析
│       │   └── risk.py          # 风控 + 行为护栏
│       ├── data/
│       │   ├── __init__.py
│       │   ├── provider.py      # 数据源抽象层
│       │   ├── xueqiu.py        # 雪球数据源实现
│       │   └── akshare.py       # AKShare 备用数据源
│       ├── models/
│       │   ├── __init__.py
│       │   └── schemas.py       # Pydantic 数据模型
│       └── utils/
│           ├── __init__.py
│           └── helpers.py       # 工具函数
└── tests/
    └── test_basic.py
```

### MCP 工具定义（Phase 1 核心）

```python
@mcp.tool()
async def analyze_stock(
    symbol: str,           # 股票代码，如 "002111.SZ" 或 "BTCUSDT"
    depth: str = "quick"   # "quick"(30s) / "deep"(含基本面+消息面)
) -> AnalysisResult:
    """对单只股票进行多维分析，返回结构化报告 + 叙事式短评"""

@mcp.tool()
async def get_market_regime() -> MarketRegime:
    """识别当前大盘体制：牛市/熊市/横盘/高波动"""

@mcp.tool()
async def scan_market(
    criteria: str = "异动",  # "异动" / "突破" / "超跌反弹" / 自定义
    limit: int = 10
) -> list[ScanResult]:
    """扫描市场，按条件筛选标的"""

@mcp.tool()
async def get_quote(symbol: str) -> Quote:
    """获取实时行情快照"""
```

### 数据模型核心

```python
class AnalysisResult(BaseModel):
    symbol: str
    name: str
    signal: Literal["强烈买入", "买入", "观望", "卖出", "强烈卖出"]
    confidence: float  # 0-100
    regime: str  # 当前市场体制
    narrative: str  # 叙事式分析短评（像分析师写的）
    technical: TechnicalAnalysis
    risk_warnings: list[str]
    action_items: ActionItems  # 优先关注/风险红线/下一步

class MarketRegime(BaseModel):
    regime: Literal["bull", "bear", "sideways", "volatile"]
    confidence: float
    description: str
    implications: list[str]  # 对交易策略的含义
```

### 雪球数据接入

- 雪球需要 cookie 认证（从浏览器获取 xq_a_token）
- 核心 API：
  - 行情：`https://stock.xueqiu.com/v5/stock/quote.json?symbol=SZ002111`
  - K线：`https://stock.xueqiu.com/v5/stock/chart/kline.json`
  - 财务：`https://stock.xueqiu.com/v5/stock/finance/`
- 用 httpx 异步请求，带 cookie 和 User-Agent

### 分析引擎逻辑

1. **技术面**（technical.py）
   - 均线系统：MA5/10/20/60
   - 量价关系：量比、OBV、VWAP
   - K线形态：锤子线、吞没、十字星等
   - 动量指标：RSI、MACD、KDJ

2. **市场体制**（regime.py）
   - 基于上证指数 + 创业板指
   - 均线排列 + 波动率 + 涨跌比 + 成交量趋势
   - 输出：牛/熊/横盘/高波动 + 置信度

3. **风控**（risk.py）
   - 连板风险、追高检测
   - 仓位建议（基于波动率）
   - 止损位计算

4. **叙事生成**
   - 把结构化数据转成自然语言短评
   - 风格：像老手分析师跟朋友聊天，不是八股文
   - 先写模板，后续接 LLM 生成

### 环境变量

```
XUEQIU_TOKEN=xxx        # 雪球 xq_a_token cookie
TIDEWATCH_LLM_API=xxx   # 可选，LLM API for 叙事生成
```

## Phase 2 规划（后续）

- 信号追踪 + 历史胜率
- 行为护栏（Anti-FOMO / Anti-Revenge）
- 产业链图谱
- Web Dashboard (Next.js)
- 回测引擎

## 设计原则

1. **MCP-First**：所有功能先通过 MCP 工具暴露，Web API 是二等公民
2. **数据源可插拔**：通过 provider 抽象层，方便切换/增加数据源
3. **分析模块独立**：每个分析维度是独立模块，引擎负责编排
4. **叙事 > 数据**：最终输出是人话，不是指标表格
5. **先跑通再优化**：Phase 1 不追求完美，追求能用
