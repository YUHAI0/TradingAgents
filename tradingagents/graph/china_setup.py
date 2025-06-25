# TradingAgents/graph/china_setup.py

from typing import Dict, Any
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode

from tradingagents.agents.china_agents_init import *
from tradingagents.agents.utils.china_agent_states import ChinaAgentState
from tradingagents.agents.utils.china_agent_utils import ChinaToolkit

from .conditional_logic import ConditionalLogic


class ChinaGraphSetup:
    """处理中国A股代理图的设置和配置。"""

    def __init__(
        self,
        quick_thinking_llm,
        deep_thinking_llm,
        toolkit,
        tool_nodes: Dict[str, ToolNode],
        bull_memory,
        bear_memory,
        trader_memory,
        invest_judge_memory,
        risk_manager_memory,
        conditional_logic: ConditionalLogic,
    ):
        """使用必需组件初始化。"""
        self.quick_thinking_llm = quick_thinking_llm
        self.deep_thinking_llm = deep_thinking_llm
        self.toolkit = toolkit
        self.tool_nodes = tool_nodes
        self.bull_memory = bull_memory
        self.bear_memory = bear_memory
        self.trader_memory = trader_memory
        self.invest_judge_memory = invest_judge_memory
        self.risk_manager_memory = risk_manager_memory
        self.conditional_logic = conditional_logic

    def setup_china_graph(self, selected_analysts=["market", "news", "fundamentals"]):
        """设置并编译中国A股代理工作流图。

        Args:
            selected_analysts (list): 要包含的分析师类型列表。选项包括:
                - "market": 市场分析师（技术分析）
                - "news": 新闻分析师（政策与新闻）
                - "fundamentals": 基本面分析师（财务分析）
        """
        if len(selected_analysts) == 0:
            raise ValueError("中国交易代理图设置错误：未选择任何分析师！")

        # 这里需要根据实际的中国代理来实现图的构建
        # 当前返回一个基础的StateGraph实例
        from tradingagents.agents.utils.agent_states import AgentState
        workflow = StateGraph(AgentState)
        
        # 添加一个简单的开始节点
        def start_node(state):
            return {"messages": []}
            
        workflow.add_node("start", start_node)
        workflow.add_edge(START, "start")
        workflow.add_edge("start", END)
        
        return workflow.compile() 