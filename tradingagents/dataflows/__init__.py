from .finnhub_utils import get_data_in_range
from .googlenews_utils import getNewsData
from .reddit_utils import fetch_top_from_category
from .stockstats_utils import StockstatsUtils

# 可选导入 YFinanceUtils
try:
    from .yfin_utils import YFinanceUtils
except ImportError:
    YFinanceUtils = None
    print("⚠️ yfinance 未安装，Yahoo Finance功能不可用")

# 尝试导入中国接口，如果失败则使用原始接口
try:
    from .china_interface import (
        # China-specific functions
        get_china_stock_data_online,
        get_china_stockstats_indicators_report_online,
        get_china_stock_news_online,
        get_china_fundamentals_online,
        get_china_market_sentiment_online,
    )
    print("✅ 成功导入中国A股数据接口")
    CHINA_INTERFACE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 中国接口导入失败: {e}")
    CHINA_INTERFACE_AVAILABLE = False

# 导入原始接口（可选，如果依赖可用）
try:
    from .interface import (
        # News and sentiment functions
        get_finnhub_news,
        get_finnhub_company_insider_sentiment,
        get_finnhub_company_insider_transactions,
        get_google_news,
        get_reddit_global_news,
        get_reddit_company_news,
        # Financial statements functions
        get_simfin_balance_sheet,
        get_simfin_cashflow,
        get_simfin_income_statements,
        # Technical analysis functions
        get_stock_stats_indicators_window,
        get_stockstats_indicator,
        # Market data functions
        get_YFin_data_window,
        get_YFin_data,
    )
    ORIGINAL_INTERFACE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 原始接口导入失败（部分依赖缺失）: {e}")
    ORIGINAL_INTERFACE_AVAILABLE = False
    # 定义空函数避免导入错误
    def get_finnhub_news(*args, **kwargs): return "原始数据源不可用"
    def get_finnhub_company_insider_sentiment(*args, **kwargs): return "原始数据源不可用"
    def get_finnhub_company_insider_transactions(*args, **kwargs): return "原始数据源不可用"
    def get_google_news(*args, **kwargs): return "原始数据源不可用"
    def get_reddit_global_news(*args, **kwargs): return "原始数据源不可用"
    def get_reddit_company_news(*args, **kwargs): return "原始数据源不可用"
    def get_simfin_balance_sheet(*args, **kwargs): return "原始数据源不可用"
    def get_simfin_cashflow(*args, **kwargs): return "原始数据源不可用"
    def get_simfin_income_statements(*args, **kwargs): return "原始数据源不可用"
    def get_stock_stats_indicators_window(*args, **kwargs): return "原始数据源不可用"
    def get_stockstats_indicator(*args, **kwargs): return "原始数据源不可用"
    def get_YFin_data_window(*args, **kwargs): return "原始数据源不可用"
    def get_YFin_data(*args, **kwargs): return "原始数据源不可用"

__all__ = [
    # News and sentiment functions
    "get_finnhub_news",
    "get_finnhub_company_insider_sentiment",
    "get_finnhub_company_insider_transactions",
    "get_google_news",
    "get_reddit_global_news",
    "get_reddit_company_news",
    # Financial statements functions
    "get_simfin_balance_sheet",
    "get_simfin_cashflow",
    "get_simfin_income_statements",
    # Technical analysis functions
    "get_stock_stats_indicators_window",
    "get_stockstats_indicator",
    # Market data functions
    "get_YFin_data_window",
    "get_YFin_data",
]
