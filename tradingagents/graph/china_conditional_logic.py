# TradingAgents/graph/china_conditional_logic.py

from tradingagents.agents.utils.china_agent_states import ChinaAgentState


class ChinaConditionalLogic:
    """处理中国A股代理图的条件逻辑，使用中文节点名称。"""

    def __init__(self, max_debate_rounds=1, max_risk_discuss_rounds=1):
        """初始化配置参数。"""
        self.max_debate_rounds = max_debate_rounds
        self.max_risk_discuss_rounds = max_risk_discuss_rounds

    def should_continue_market(self, state: ChinaAgentState):
        """确定市场分析是否应该继续。"""
        messages = state["messages"]
        last_message = messages[-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools_market"
        return "Msg Clear Market"

    def should_continue_social(self, state: ChinaAgentState):
        """确定社交媒体分析是否应该继续。"""
        messages = state["messages"]
        last_message = messages[-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools_social"
        return "Msg Clear Social"

    def should_continue_news(self, state: ChinaAgentState):
        """确定新闻分析是否应该继续。"""
        messages = state["messages"]
        last_message = messages[-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools_news"
        return "Msg Clear News"

    def should_continue_fundamentals(self, state: ChinaAgentState):
        """确定基本面分析是否应该继续。"""
        messages = state["messages"]
        last_message = messages[-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools_fundamentals"
        return "Msg Clear Fundamentals"

    def should_continue_debate(self, state: ChinaAgentState) -> str:
        """确定辩论是否应该继续。"""

        if (
            state["investment_debate_state"]["count"] >= 2 * self.max_debate_rounds
        ):  # 两个代理之间的3轮往返辩论
            return "研究经理"
        if state["investment_debate_state"]["current_response"].startswith("看涨"):
            return "看跌研究员"
        return "看涨研究员"

    def should_continue_risk_analysis(self, state: ChinaAgentState) -> str:
        """确定风险分析是否应该继续。"""
        if (
            state["risk_debate_state"]["count"] >= 3 * self.max_risk_discuss_rounds
        ):  # 三个代理之间的3轮往返讨论
            return "风险评判"
        if state["risk_debate_state"]["latest_speaker"].startswith("激进"):
            return "保守分析师"
        if state["risk_debate_state"]["latest_speaker"].startswith("保守"):
            return "中性分析师"
        return "激进分析师" 