"""
中国A股代理状态管理
定义各种代理状态和数据结构
"""

from typing import Annotated, Sequence
from datetime import date, timedelta, datetime
from typing_extensions import TypedDict, Optional
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph, START, MessagesState


class ChinaInvestDebateState(TypedDict):
    """
    中国A股投资辩论状态
    
    管理看涨分析师和看跌分析师之间的辩论状态
    """
    bull_history: Annotated[str, "看涨分析师对话历史"]
    bear_history: Annotated[str, "看跌分析师对话历史"]
    history: Annotated[str, "完整对话历史"]
    current_response: Annotated[str, "最新回应"]
    judge_decision: Annotated[str, "最终裁判决定"]
    count: Annotated[int, "当前对话长度"]


class ChinaRiskDebateState(TypedDict):
    """
    中国A股风险辩论状态
    
    管理三个风险分析师（激进、保守、中性）之间的辩论状态
    """
    risky_history: Annotated[str, "激进分析师对话历史"]
    safe_history: Annotated[str, "保守分析师对话历史"]
    neutral_history: Annotated[str, "中性分析师对话历史"]
    history: Annotated[str, "完整对话历史"]
    latest_speaker: Annotated[str, "最后发言的分析师"]
    current_risky_response: Annotated[str, "激进分析师最新回应"]
    current_safe_response: Annotated[str, "保守分析师最新回应"]
    current_neutral_response: Annotated[str, "中性分析师最新回应"]
    judge_decision: Annotated[str, "风险管理总监决定"]
    count: Annotated[int, "当前对话长度"]


class ChinaAgentState(MessagesState):
    """
    中国A股代理主状态
    
    定义整个A股交易分析系统的状态结构
    """
    # 基础信息
    company_of_interest: Annotated[str, "我们感兴趣的股票代码"]
    trade_date: Annotated[str, "交易日期"]
    sender: Annotated[str, "发送此消息的代理"]

    # 研究报告阶段
    market_report: Annotated[str, "市场分析师报告"]
    sentiment_report: Annotated[str, "情绪分析师报告"]
    news_report: Annotated[str, "新闻分析师报告"]
    fundamentals_report: Annotated[str, "基本面分析师报告"]

    # 研究团队讨论阶段
    investment_debate_state: Annotated[
        ChinaInvestDebateState, "投资辩论的当前状态"
    ]
    investment_plan: Annotated[str, "研究管理器生成的投资计划"]

    # 交易员决策阶段
    trader_investment_plan: Annotated[str, "交易员生成的交易计划"]

    # 风险管理团队讨论阶段
    risk_debate_state: Annotated[
        ChinaRiskDebateState, "风险评估辩论的当前状态"
    ]
    final_trade_decision: Annotated[str, "风险分析师做出的最终交易决策"]

    # A股特色字段
    china_market_features: Annotated[dict, "A股市场特色数据"]  # 涨跌停、北向资金等
    policy_impact: Annotated[str, "政策影响分析"]  # 政策对股价的影响分析
    capital_flow: Annotated[str, "资金流向分析"]  # 北向资金、机构资金流向
    concept_analysis: Annotated[str, "概念题材分析"]  # 热点概念分析


class ChinaMarketMetrics(TypedDict):
    """
    中国A股市场指标
    
    定义A股特有的市场指标和数据结构
    """
    # 基础价格数据
    current_price: Annotated[float, "当前价格"]
    price_change: Annotated[float, "价格变化"]
    price_change_pct: Annotated[float, "价格变化百分比"]
    
    # A股特色指标
    limit_up_price: Annotated[float, "涨停价"]
    limit_down_price: Annotated[float, "跌停价"]
    northbound_flow: Annotated[float, "北向资金流入"]
    margin_balance: Annotated[float, "融资余额"]
    
    # 技术指标
    ma5: Annotated[float, "5日均线"]
    ma10: Annotated[float, "10日均线"]
    ma20: Annotated[float, "20日均线"]
    ma60: Annotated[float, "60日均线"]
    
    # 估值指标
    pe_ratio: Annotated[float, "市盈率"]
    pb_ratio: Annotated[float, "市净率"]
    ps_ratio: Annotated[float, "市销率"]
    
    # 成交数据
    volume: Annotated[int, "成交量"]
    turnover: Annotated[float, "成交额"]
    turnover_rate: Annotated[float, "换手率"]


class ChinaPolicyImpact(TypedDict):
    """
    中国政策影响评估
    
    评估政策变化对股票的影响
    """
    policy_type: Annotated[str, "政策类型"]  # 产业政策、货币政策、监管政策等
    impact_level: Annotated[str, "影响程度"]  # 高/中/低
    impact_direction: Annotated[str, "影响方向"]  # 利好/利空/中性
    time_horizon: Annotated[str, "影响时间范围"]  # 短期/中期/长期
    confidence_level: Annotated[float, "置信度"]  # 0-1之间
    policy_details: Annotated[str, "政策详情"]
    market_reaction: Annotated[str, "市场反应预期"]


class ChinaConceptAnalysis(TypedDict):
    """
    中国A股概念分析
    
    分析热点概念和题材对股票的影响
    """
    concept_name: Annotated[str, "概念名称"]
    concept_strength: Annotated[float, "概念强度"]  # 0-1之间
    market_attention: Annotated[float, "市场关注度"]  # 0-1之间
    concept_lifecycle: Annotated[str, "概念生命周期"]  # 萌芽/成长/成熟/衰退
    related_stocks_count: Annotated[int, "相关股票数量"]
    leading_stocks: Annotated[list, "龙头股票列表"]
    concept_catalysts: Annotated[str, "概念催化剂"]
    risk_factors: Annotated[str, "风险因素"] 