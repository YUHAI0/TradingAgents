"""
中国A股数据接口
整合tushare、akshare等国内数据源，提供与原系统兼容的接口
"""

from typing import Annotated, Dict
from datetime import datetime, timedelta
from .china_stock_utils import (
    get_china_stock_data,
    get_china_stock_technical_indicators,
    get_china_stock_news,
    get_china_market_sentiment,
    get_china_stock_fundamentals
)

# 全局配置变量
_china_config: Dict = {}

def set_china_config(config: Dict):
    """设置中国A股数据接口的配置"""
    global _china_config
    _china_config = config

def get_china_config() -> Dict:
    """获取中国A股数据接口的配置"""
    return _china_config or {}

# 主要在线数据接口
def get_china_stock_data_online(
    ts_code: Annotated[str, "股票代码，如 '000001.SZ' 或 '600000.SH'"],
    start_date: Annotated[str, "开始日期，格式：YYYY-MM-DD"],
    end_date: Annotated[str, "结束日期，格式：YYYY-MM-DD"]
) -> str:
    """获取中国A股在线数据"""
    return get_china_stock_data(ts_code, start_date, end_date)

def get_china_stockstats_indicators_report_online(
    ts_code: Annotated[str, "股票代码"],
    curr_date: Annotated[str, "当前交易日期，格式：YYYY-MM-DD"]
) -> str:
    """获取中国A股技术指标报告"""
    result = f"## {ts_code} 技术指标分析报告\n\n"
    
    # 主要技术指标
    indicators = ['sma', 'rsi']
    for indicator in indicators:
        indicator_report = get_china_stock_technical_indicators(ts_code, indicator, curr_date, 20)
        result += indicator_report + "\n\n"
    
    return result

def get_china_stock_news_online(
    ts_code: Annotated[str, "股票代码"],
    curr_date: Annotated[str, "当前日期"]
) -> str:
    """获取中国A股相关新闻"""
    return get_china_stock_news(ts_code, curr_date)

def get_china_fundamentals_online(
    ts_code: Annotated[str, "股票代码"],
    curr_date: Annotated[str, "当前日期"]
) -> str:
    """获取中国A股基本面数据"""
    return get_china_stock_fundamentals(ts_code, curr_date)

def get_china_market_sentiment_online(
    curr_date: Annotated[str, "当前日期"]
) -> str:
    """获取中国A股市场情绪数据"""
    return get_china_market_sentiment(curr_date) 