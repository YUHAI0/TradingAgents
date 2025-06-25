"""
中国A股代理模块总初始化文件
整合所有中国A股相关的代理和工具
"""

# 导入管理器
from .managers.china_risk_manager import create_china_risk_manager
from .managers.china_research_manager import create_china_research_manager

# 导入研究员
from .researchers.china_bull_researcher import create_china_bull_researcher
from .researchers.china_bear_researcher import create_china_bear_researcher

# 导入风险管理辩手
from .risk_mgmt.china_aggressive_debator import create_china_aggressive_debator
from .risk_mgmt.china_conservative_debator import create_china_conservative_debator
from .risk_mgmt.china_neutral_debator import create_china_neutral_debator

# 导入交易员
from .trader.china_trader import create_china_trader

# 导入分析师
from .analysts.china_market_analyst import (
    create_china_market_analyst,
    create_china_news_analyst,
    create_china_sentiment_analyst,
    create_china_fundamentals_analyst
)

# 导入工具和状态管理
from .utils.china_agent_utils import ChinaToolkit, create_china_msg_delete
from .utils.china_agent_states import (
    ChinaAgentState,
    ChinaInvestDebateState,
    ChinaRiskDebateState,
    ChinaMarketMetrics,
    ChinaPolicyImpact,
    ChinaConceptAnalysis
)

# 导入数据流接口
from ..dataflows.china_interface import (
    get_china_stock_data_online,
    get_china_stockstats_indicators_report_online,
    get_china_stock_news_online,
    get_china_fundamentals_online,
    get_china_market_sentiment_online
)

# 导入配置
from ..china_config import CHINA_DEFAULT_CONFIG
from ..llm_providers.china_llm_provider import ChinaLLMManager


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
        self.config = config or CHINA_DEFAULT_CONFIG
        self.llm_manager = ChinaLLMManager(self.config)
        self.llm = self.llm_manager.get_llm()
        
        # 初始化工具包
        self.toolkit = ChinaToolkit(config)
        
        # 初始化记忆系统（这里需要实现）
        self.memory = None  # TODO: 实现记忆系统
        
        # 初始化各个代理
        self._init_agents()
    
    def _init_agents(self):
        """初始化所有代理"""
        
        # 管理器
        self.risk_manager = create_china_risk_manager(self.llm, self.memory)
        self.research_manager = create_china_research_manager(self.llm, self.memory)
        
        # 研究员
        self.bull_researcher = create_china_bull_researcher(self.llm, self.memory)
        self.bear_researcher = create_china_bear_researcher(self.llm, self.memory)
        
        # 风险管理辩手
        self.aggressive_debator = create_china_aggressive_debator(self.llm)
        self.conservative_debator = create_china_conservative_debator(self.llm)
        self.neutral_debator = create_china_neutral_debator(self.llm)
        
        # 交易员
        self.trader = create_china_trader(self.llm, self.memory)
        
        # 分析师
        self.market_analyst = create_china_market_analyst(self.llm)
        self.news_analyst = create_china_news_analyst(self.llm)
        self.sentiment_analyst = create_china_sentiment_analyst(self.llm)
        self.fundamentals_analyst = create_china_fundamentals_analyst(self.llm)
    
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
            from datetime import datetime
            trade_date = datetime.now().strftime("%Y-%m-%d")
        
        # 格式化股票代码
        formatted_code = ChinaToolkit.format_china_stock_code(stock_code)
        
        # 构建初始状态
        initial_state = {
            "company_of_interest": formatted_code,
            "trade_date": trade_date,
            "messages": [],
        }
        
        try:
            # 1. 获取基础数据报告
            market_report = get_china_stock_data_online(formatted_code, trade_date, trade_date)
            news_report = get_china_stock_news_online(formatted_code, trade_date)
            fundamentals_report = get_china_fundamentals_online(formatted_code, trade_date)
            sentiment_report = get_china_market_sentiment_online(formatted_code, trade_date)
            
            # 更新状态
            initial_state.update({
                "market_report": market_report,
                "news_report": news_report,
                "fundamentals_report": fundamentals_report,
                "sentiment_report": sentiment_report,
            })
            
            return {
                "status": "success",
                "stock_code": formatted_code,
                "trade_date": trade_date,
                "analysis": initial_state
            }
            
        except Exception as e:
            return {
                "status": "error",
                "stock_code": formatted_code,
                "trade_date": trade_date,
                "error": str(e)
            }
    
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
            "llm_provider": self.llm_manager.current_provider,
            "available_agents": len(self.get_available_agents()),
            "config": self.config.get("ENVIRONMENT", "unknown"),
            "status": "运行中"
        }


# 导出主要类和函数
__all__ = [
    # 主系统类
    "ChinaTradingAgents",
    
    # 管理器
    "create_china_risk_manager",
    "create_china_research_manager",
    
    # 研究员
    "create_china_bull_researcher",
    "create_china_bear_researcher",
    
    # 风险管理辩手
    "create_china_aggressive_debator",
    "create_china_conservative_debator", 
    "create_china_neutral_debator",
    
    # 交易员
    "create_china_trader",
    
    # 分析师
    "create_china_market_analyst",
    "create_china_news_analyst",
    "create_china_sentiment_analyst",
    "create_china_fundamentals_analyst",
    
    # 工具和状态
    "ChinaToolkit",
    "ChinaAgentState",
    "ChinaInvestDebateState",
    "ChinaRiskDebateState",
    "ChinaMarketMetrics",
    "ChinaPolicyImpact",
    "ChinaConceptAnalysis",
    
    # 数据接口
    "get_china_stock_data_online",
    "get_china_stockstats_indicators_report_online",
    "get_china_stock_news_online",
    "get_china_fundamentals_online",
    "get_china_market_sentiment_online",
    
    # 配置和LLM
    "CHINA_CONFIG",
    "ChinaLLMManager"
]


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
    print("中国A股交易代理系统初始化完成")
    
    # 创建系统实例
    china_system = create_china_trading_system()
    
    # 显示系统状态
    status = china_system.get_system_status()
    print(f"系统状态: {status}")
    
    # 显示可用代理
    agents = china_system.get_available_agents()
    print(f"可用代理: {agents}")
    
    print("系统就绪，可以开始分析A股股票！") 