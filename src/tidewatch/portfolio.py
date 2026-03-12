"""
投资组合管理 — Portfolio Manager
三级股票池：持仓 > 自选 > 热门
持仓和自选存 SQLite，热门硬编码
"""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "signals.db"

# ============================================================================
# 热门股票池 — 8 赛道 ~70 只核心标的 (代码, 名称)
# ============================================================================

HOT_POOL: dict[str, list[tuple[str, str]]] = {
    "大盘权重": [
        ("601318", "中国平安"),
        ("600036", "招商银行"),
        ("601166", "兴业银行"),
        ("600030", "中信证券"),
        ("601688", "华泰证券"),
        ("600900", "长江电力"),
        ("601857", "中国石油"),
        ("600028", "中国石化"),
        ("601398", "工商银行"),
        ("000333", "美的集团"),
    ],
    "新能源": [
        ("300750", "宁德时代"),
        ("002594", "比亚迪"),
        ("300274", "阳光电源"),
        ("601012", "隆基绿能"),
        ("002459", "晶澳科技"),
        ("600438", "通威股份"),
        ("688599", "天合光能"),
        ("300763", "锦浪科技"),
        ("002129", "TCL中环"),
        ("600089", "特变电工"),
    ],
    "半导体AI": [
        ("688981", "中芯国际"),
        ("688041", "海光信息"),
        ("688256", "寒武纪"),
        ("002049", "紫光国微"),
        ("603501", "韦尔股份"),
        ("688012", "中微公司"),
        ("002371", "北方华创"),
        ("688036", "传音控股"),
        ("300782", "卓胜微"),
        ("688111", "金山办公"),
    ],
    "消费": [
        ("600519", "贵州茅台"),
        ("000858", "五粮液"),
        ("600887", "伊利股份"),
        ("603288", "海天味业"),
        ("000568", "泸州老窖"),
        ("002304", "洋河股份"),
        ("600809", "山西汾酒"),
        ("000895", "双汇发展"),
        ("603369", "今世缘"),
        ("002557", "洽洽食品"),
    ],
    "医药": [
        ("600276", "恒瑞医药"),
        ("300760", "迈瑞医疗"),
        ("000538", "云南白药"),
        ("300122", "智飞生物"),
        ("603259", "药明康德"),
        ("002007", "华兰生物"),
        ("300347", "泰格医药"),
        ("688180", "君实生物"),
    ],
    "军工": [
        ("600760", "中航沈飞"),
        ("600893", "航发动力"),
        ("002013", "中航机电"),
        ("600150", "中国船舶"),
        ("000768", "中航西飞"),
        ("600862", "中航高科"),
        ("002414", "高德红外"),
        ("688002", "睿创微纳"),
    ],
    "资源": [
        ("601899", "紫金矿业"),
        ("002466", "天齐锂业"),
        ("002460", "赣锋锂业"),
        ("600219", "南山铝业"),
        ("601600", "中国铝业"),
        ("600547", "山东黄金"),
        ("601088", "中国神华"),
        ("601225", "陕西煤业"),
    ],
    "地产基建": [
        ("600048", "保利发展"),
        ("001979", "招商蛇口"),
        ("600585", "海螺水泥"),
        ("601668", "中国建筑"),
        ("000002", "万科A"),
        ("002607", "中公教育"),
    ],
}

# 代码 → 名称 快速查找表
HOT_NAMES: dict[str, str] = {code: name for stocks in HOT_POOL.values() for code, name in stocks}


def _get_hot_symbols() -> set[str]:
    """获取热门股票池所有代码"""
    return set(HOT_NAMES.keys())


# ============================================================================
# SQLite 持仓/自选管理
# ============================================================================

def _get_conn() -> sqlite3.Connection:
    """获取数据库连接（自动建表）"""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS holdings (
            symbol TEXT PRIMARY KEY,
            name TEXT,
            cost REAL,
            shares INTEGER DEFAULT 0,
            added_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            symbol TEXT PRIMARY KEY,
            name TEXT,
            reason TEXT,
            added_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


# --- 持仓 ---

def add_holding(symbol: str, name: str = "", cost: float = 0, shares: int = 0):
    """添加或更新持仓"""
    conn = _get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO holdings (symbol, name, cost, shares, added_at) VALUES (?, ?, ?, ?, ?)",
        (symbol, name, cost, shares, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
    logger.info(f"📌 持仓更新: {symbol} {name} cost={cost} shares={shares}")


def remove_holding(symbol: str):
    """移除持仓"""
    conn = _get_conn()
    conn.execute("DELETE FROM holdings WHERE symbol = ?", (symbol,))
    conn.commit()
    conn.close()
    logger.info(f"📌 持仓移除: {symbol}")


def get_holdings() -> list[dict]:
    """获取所有持仓"""
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM holdings ORDER BY added_at").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- 自选 ---

def add_watchlist(symbol: str, name: str = "", reason: str = ""):
    """添加自选股"""
    conn = _get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO watchlist (symbol, name, reason, added_at) VALUES (?, ?, ?, ?)",
        (symbol, name, reason, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
    logger.info(f"👀 自选添加: {symbol} {name}")


def remove_watchlist(symbol: str):
    """移除自选股"""
    conn = _get_conn()
    conn.execute("DELETE FROM watchlist WHERE symbol = ?", (symbol,))
    conn.commit()
    conn.close()
    logger.info(f"👀 自选移除: {symbol}")


def get_watchlist() -> list[dict]:
    """获取所有自选股"""
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM watchlist ORDER BY added_at").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- 合并池 ---

def get_scan_pool() -> dict[str, list[str]]:
    """获取三级扫描池（去重）

    Returns:
        {"holdings": [...], "watchlist": [...], "hot": [...]}
        hot 中已排除 holdings 和 watchlist 中的重复代码
    """
    holdings = get_holdings()
    watchlist = get_watchlist()

    holding_symbols = [h["symbol"] for h in holdings]
    watchlist_symbols = [w["symbol"] for w in watchlist]

    seen = set(holding_symbols) | set(watchlist_symbols)
    hot_symbols = [s for s in sorted(_get_hot_symbols()) if s not in seen]

    return {
        "holdings": holding_symbols,
        "watchlist": watchlist_symbols,
        "hot": hot_symbols,
    }
