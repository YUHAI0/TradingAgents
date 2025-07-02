# TradingAgents/graph/propagation.py

from typing import Dict, Any
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)

# 导入中国版本的状态类
try:
    from tradingagents.agents.utils.china_agent_states import (
        ChinaAgentState,
        ChinaInvestDebateState,
        ChinaRiskDebateState,
    )
    CHINA_STATES_AVAILABLE = True
except ImportError:
    CHINA_STATES_AVAILABLE = False


class Propagator:
    """Handles state initialization and propagation through the graph."""

    def __init__(self, max_recur_limit=100):
        """Initialize with configuration parameters."""
        self.max_recur_limit = max_recur_limit

    def create_initial_state(
        self, company_name: str, trade_date: str
    ) -> Dict[str, Any]:
        """Create the initial state for the agent graph."""
        return {
            "messages": [("human", company_name)],
            "company_of_interest": company_name,
            "trade_date": str(trade_date),
            "investment_debate_state": {
                "bull_history": "",
                "bear_history": "",
                "judge_decision": "",
                "history": "",
                "current_response": "",
                "count": 0
            },
            "risk_debate_state": {
                "risky_history": "",
                "safe_history": "",
                "neutral_history": "",
                "judge_decision": "",
                "history": "",
                "latest_speaker": "",
                "current_risky_response": "",
                "current_safe_response": "",
                "current_neutral_response": "",
                "count": 0,
            },
            "market_report": "",
            "fundamentals_report": "",
            "sentiment_report": "",
            "news_report": "",
        }

    def create_china_initial_state(
        self, stock_code: str, trade_date: str
    ) -> Dict[str, Any]:
        """Create the initial state for the Chinese A-share agent graph."""
        if not CHINA_STATES_AVAILABLE:
            # 如果中国状态类不可用，使用标准状态类
            return self.create_initial_state(stock_code, trade_date)
        
        return {
            "messages": [("human", stock_code)],
            "company_of_interest": stock_code,
            "trade_date": str(trade_date),
            "investment_debate_state": {
                "bull_history": "",
                "bear_history": "",
                "judge_decision": "",
                "history": "",
                "current_response": "",
                "count": 0
            },
            "risk_debate_state": {
                "risky_history": "",
                "safe_history": "",
                "neutral_history": "",
                "judge_decision": "",
                "history": "",
                "latest_speaker": "",
                "current_risky_response": "",
                "current_safe_response": "",
                "current_neutral_response": "",
                "count": 0,
            },
            "market_report": "",
            "fundamentals_report": "",
            "sentiment_report": "",
            "news_report": "",
            "trader_investment_plan": "",
            "final_trade_decision": "",
        }

    def get_graph_args(self) -> Dict[str, Any]:
        """Get arguments for the graph invocation."""
        return {
            "stream_mode": "values",
            "config": {"recursion_limit": self.max_recur_limit},
        }
