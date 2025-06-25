"""
中国A股代理模块总管理文件
整合所有中国A股相关的代理和工具
"""

from datetime import datetime
import traceback


class ChinaTradingAgents:
    """
    中国A股交易代理系统
    
    整合所有中国A股相关的代理和工具，提供完整的A股分析和交易决策系统
    """
    
    def __init__(self, config=None):
        """
        初始化中国A股交易代理系统
        
        Args:
            config (dict, optional): 配置参数
        """
        try:
            # 导入配置
            from .china_config import CHINA_CONFIG
            from .llm_providers.china_llm_provider import ChinaLLMManager
            
            self.config = config or CHINA_CONFIG
            self.llm_manager = ChinaLLMManager(self.config)
            self.llm = self.llm_manager.get_llm()
            
            # 初始化记忆系统（占位符）
            self.memory = None
            
            print("✅ 中国A股交易代理系统初始化成功")
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            traceback.print_exc()
    
    def analyze_stock(self, stock_code: str, trade_date: str = None) -> dict:
        """
        分析A股股票
        
        Args:
            stock_code (str): 股票代码
            trade_date (str, optional): 交易日期，默认为今天
            
        Returns:
            dict: 分析结果
        """
        if not trade_date:
            trade_date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            # 导入数据接口
            from .dataflows.china_interface import (
                get_china_stock_data_online,
                get_china_stock_news_online,
                get_china_fundamentals_online,
                get_china_market_sentiment_online
            )
            
            # 格式化股票代码
            formatted_code = self.format_china_stock_code(stock_code)
            
            # 获取基础数据
            print(f"📊 开始分析股票: {formatted_code}")
            
            market_report = get_china_stock_data_online(formatted_code, trade_date, trade_date)
            news_report = get_china_stock_news_online(formatted_code, trade_date)
            fundamentals_report = get_china_fundamentals_online(formatted_code, trade_date)
            sentiment_report = get_china_market_sentiment_online(formatted_code, trade_date)
            
            analysis_result = {
                "stock_code": formatted_code,
                "trade_date": trade_date,
                "market_report": market_report,
                "news_report": news_report,
                "fundamentals_report": fundamentals_report,
                "sentiment_report": sentiment_report,
            }
            
            print(f"✅ 股票分析完成: {formatted_code}")
            
            return {
                "status": "success",
                "data": analysis_result
            }
            
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "stock_code": stock_code,
                "trade_date": trade_date
            }
    
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
    
    def get_available_agents(self) -> list:
        """
        获取可用的代理列表
        
        Returns:
            list: 代理名称列表
        """
        return [
            "风险管理器", "研究管理器",
            "看涨研究员", "看跌研究员",
            "激进风险辩手", "保守风险辩手", "中性风险辩手",
            "A股交易员",
            "市场分析师", "新闻分析师", "情绪分析师", "基本面分析师"
        ]
    
    def get_system_status(self) -> dict:
        """
        获取系统状态
        
        Returns:
            dict: 系统状态信息
        """
        return {
            "system_name": "中国A股交易代理系统",
            "version": "1.0.0",
            "llm_provider": getattr(self.llm_manager, 'current_provider', 'unknown'),
            "available_agents": len(self.get_available_agents()),
            "config_env": self.config.get("ENVIRONMENT", "unknown"),
            "status": "运行中"
        }


# 便捷函数
def create_china_trading_system(config=None):
    """
    创建中国A股交易系统的便捷函数
    
    Args:
        config (dict, optional): 配置参数
        
    Returns:
        ChinaTradingAgents: 中国A股交易代理系统实例
    """
    return ChinaTradingAgents(config)


def quick_stock_analysis(stock_code: str, trade_date: str = None, config=None):
    """
    快速股票分析的便捷函数
    
    Args:
        stock_code (str): 股票代码
        trade_date (str, optional): 交易日期
        config (dict, optional): 配置参数
        
    Returns:
        dict: 分析结果
    """
    system = create_china_trading_system(config)
    return system.analyze_stock(stock_code, trade_date)


if __name__ == "__main__":
    # 测试代码
    print("🚀 中国A股交易代理系统测试启动")
    
    try:
        # 创建系统实例
        china_system = create_china_trading_system()
        
        # 显示系统状态
        status = china_system.get_system_status()
        print(f"📋 系统状态: {status}")
        
        # 显示可用代理
        agents = china_system.get_available_agents()
        print(f"🤖 可用代理: {agents}")
        
        # 测试股票分析
        print("\n🔍 测试股票分析...")
        result = china_system.analyze_stock("000001")
        print(f"📊 分析结果: {result['status']}")
        
        print("\n✅ 系统测试完成，可以开始分析A股股票！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc() 