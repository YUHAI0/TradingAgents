"""
中国A股代理工具集成模块
提供中国A股市场专用的工具和实用函数
"""

from typing import Annotated
from langchain_core.messages import BaseMessage, HumanMessage, RemoveMessage
from langchain_core.tools import tool
from datetime import date, timedelta, datetime
import pandas as pd
import os
from dateutil.relativedelta import relativedelta

# 导入中国A股数据接口
import tradingagents.dataflows.china_interface as china_interface
from tradingagents.china_config import CHINA_DEFAULT_CONFIG


def create_china_msg_delete():
    """
    创建中国A股消息删除函数
    
    Returns:
        function: 消息删除函数
    """
    def delete_messages(state):
        """清除消息并添加占位符以保持兼容性"""
        messages = state["messages"]
        
        # 移除所有消息
        removal_operations = [RemoveMessage(id=m.id) for m in messages]
        
        # 添加最小占位符消息
        placeholder = HumanMessage(content="继续分析")
        
        return {"messages": removal_operations + [placeholder]}
    
    return delete_messages


class ChinaToolkit:
    """
    中国A股工具包
    
    提供专门针对中国A股市场的数据获取和分析工具
    """
    
    _config = CHINA_DEFAULT_CONFIG.copy()

    @classmethod
    def update_config(cls, config):
        """更新类级别的配置"""
        cls._config.update(config)

    @property
    def config(self):
        """访问配置"""
        return self._config

    def __init__(self, config=None):
        if config:
            self.update_config(config)

    @staticmethod
    @tool
    def get_china_stock_data(
        symbol: Annotated[str, "股票代码，如 000001.SZ"],
        start_date: Annotated[str, "开始日期，格式: yyyy-mm-dd"],
        end_date: Annotated[str, "结束日期，格式: yyyy-mm-dd"],
    ) -> str:
        """
        获取中国A股股票价格数据
        
        Args:
            symbol (str): 股票代码，如 000001.SZ, 600000.SH
            start_date (str): 开始日期，格式: yyyy-mm-dd
            end_date (str): 结束日期，格式: yyyy-mm-dd
            
        Returns:
            str: 格式化的股票价格数据
        """
        result_data = china_interface.get_china_stock_data_online(
            symbol, start_date, end_date
        )
        return result_data

    @staticmethod
    @tool
    def get_china_technical_indicators(
        symbol: Annotated[str, "股票代码，如 000001.SZ"],
        indicator: Annotated[str, "技术指标名称，如 MACD, KDJ, RSI"],
        curr_date: Annotated[str, "当前交易日期，格式: yyyy-mm-dd"],
        look_back_days: Annotated[int, "回看天数"] = 30,
    ) -> str:
        """
        获取中国A股技术指标分析报告
        
        Args:
            symbol (str): 股票代码，如 000001.SZ
            indicator (str): 技术指标名称
            curr_date (str): 当前交易日期，格式: yyyy-mm-dd
            look_back_days (int): 回看天数，默认30天
            
        Returns:
            str: 格式化的技术指标分析报告
        """
        result_indicators = china_interface.get_china_stockstats_indicators_report_online(
            symbol, curr_date
        )
        return result_indicators

    @staticmethod
    @tool
    def get_china_stock_news(
        symbol: Annotated[str, "股票代码，如 000001.SZ"],
        curr_date: Annotated[str, "当前日期，格式: yyyy-mm-dd"],
        days_back: Annotated[int, "回看天数"] = 7,
    ) -> str:
        """
        获取中国A股相关新闻
        
        Args:
            symbol (str): 股票代码，如 000001.SZ
            curr_date (str): 当前日期，格式: yyyy-mm-dd
            days_back (int): 回看天数，默认7天
            
        Returns:
            str: 格式化的新闻报告
        """
        news_result = china_interface.get_china_stock_news_online(
            symbol, curr_date
        )
        return news_result

    @staticmethod
    @tool
    def get_china_fundamentals(
        symbol: Annotated[str, "股票代码，如 000001.SZ"],
        curr_date: Annotated[str, "当前日期，格式: yyyy-mm-dd"],
    ) -> str:
        """
        获取中国A股基本面数据
        
        Args:
            symbol (str): 股票代码，如 000001.SZ
            curr_date (str): 当前日期，格式: yyyy-mm-dd
            
        Returns:
            str: 格式化的基本面分析报告
        """
        fundamentals_result = china_interface.get_china_fundamentals_online(
            symbol, curr_date
        )
        return fundamentals_result

    @staticmethod
    @tool
    def get_china_market_sentiment(
        symbol: Annotated[str, "股票代码，如 000001.SZ"],
        curr_date: Annotated[str, "当前日期，格式: yyyy-mm-dd"],
    ) -> str:
        """
        获取中国A股市场情绪分析
        
        Args:
            symbol (str): 股票代码，如 000001.SZ
            curr_date (str): 当前日期，格式: yyyy-mm-dd
            
        Returns:
            str: 格式化的市场情绪分析报告
        """
        sentiment_result = china_interface.get_china_market_sentiment_online(
            curr_date
        )
        return sentiment_result

    @staticmethod
    @tool
    def get_china_policy_news(
        industry: Annotated[str, "行业名称，如 新能源、半导体、医药"],
        curr_date: Annotated[str, "当前日期，格式: yyyy-mm-dd"],
        days_back: Annotated[int, "回看天数"] = 7,
    ) -> str:
        """
        获取中国政策相关新闻
        
        Args:
            industry (str): 行业名称
            curr_date (str): 当前日期，格式: yyyy-mm-dd
            days_back (int): 回看天数，默认7天
            
        Returns:
            str: 格式化的政策新闻报告
        """
        # 这里应该调用政策新闻接口，暂时使用通用新闻接口
        policy_news = china_interface.get_china_stock_news_online(
            industry, curr_date
        )
        return f"【政策新闻】{policy_news}"

    @staticmethod
    @tool
    def get_northbound_funds_flow(
        symbol: Annotated[str, "股票代码，如 000001.SZ"],
        curr_date: Annotated[str, "当前日期，格式: yyyy-mm-dd"],
        days_back: Annotated[int, "回看天数"] = 10,
    ) -> str:
        """
        获取北向资金流向数据
        
        Args:
            symbol (str): 股票代码，如 000001.SZ
            curr_date (str): 当前日期，格式: yyyy-mm-dd
            days_back (int): 回看天数，默认10天
            
        Returns:
            str: 格式化的北向资金流向报告
        """
        # 这里应该调用北向资金接口，暂时返回模拟数据
        return f"【北向资金流向】{symbol} 在过去{days_back}天的北向资金流向分析"

    @staticmethod
    @tool
    def get_concept_analysis(
        concept: Annotated[str, "概念名称，如 新能源、元宇宙、军工"],
        curr_date: Annotated[str, "当前日期，格式: yyyy-mm-dd"],
    ) -> str:
        """
        获取概念板块分析
        
        Args:
            concept (str): 概念名称
            curr_date (str): 当前日期，格式: yyyy-mm-dd
            
        Returns:
            str: 格式化的概念分析报告
        """
        # 这里应该调用概念分析接口，暂时返回模拟数据
        return f"【概念分析】{concept} 概念板块在 {curr_date} 的分析报告"

    @staticmethod
    def format_china_stock_code(code: str) -> str:
        """
        格式化中国A股股票代码
        
        Args:
            code (str): 股票代码
            
        Returns:
            str: 格式化后的股票代码
        """
        # 去除空格和特殊字符
        code = code.strip().upper()
        
        # 如果已经包含交易所后缀，直接返回
        if '.' in code:
            return code
            
        # 根据代码添加交易所后缀
        if code.startswith('00') or code.startswith('30'):
            return f"{code}.SZ"  # 深交所
        elif code.startswith('60') or code.startswith('68'):
            return f"{code}.SH"  # 上交所
        else:
            return code  # 其他情况直接返回

    @staticmethod
    def get_trading_calendar(date_str: str) -> dict:
        """
        获取A股交易日历信息
        
        Args:
            date_str (str): 日期字符串，格式: yyyy-mm-dd
            
        Returns:
            dict: 交易日历信息
        """
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            # 简单的交易日判断（排除周末）
            is_trading_day = target_date.weekday() < 5
            
            return {
                "date": date_str,
                "is_trading_day": is_trading_day,
                "weekday": target_date.weekday(),
                "weekday_name": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][target_date.weekday()]
            }
        except:
            return {"date": date_str, "is_trading_day": False, "error": "日期格式错误"}

    @staticmethod
    def calculate_limit_prices(current_price: float, stock_type: str = "主板") -> dict:
        """
        计算涨跌停价格
        
        Args:
            current_price (float): 当前价格
            stock_type (str): 股票类型（主板/科创板/创业板/ST）
            
        Returns:
            dict: 涨跌停价格信息
        """
        # 根据股票类型确定涨跌停幅度
        if stock_type == "ST":
            limit_pct = 0.05  # 5%
        elif stock_type in ["科创板", "创业板"]:
            limit_pct = 0.20  # 20%
        else:
            limit_pct = 0.10  # 10%
        
        limit_up_price = current_price * (1 + limit_pct)
        limit_down_price = current_price * (1 - limit_pct)
        
        return {
            "current_price": current_price,
            "limit_up_price": round(limit_up_price, 2),
            "limit_down_price": round(limit_down_price, 2),
            "limit_pct": limit_pct * 100,
            "stock_type": stock_type
        } 