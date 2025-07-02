# TradingAgents/graph/china_setup.py

from typing import Dict, Any
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode

from tradingagents.agents.china_agents_init import *
from tradingagents.agents.utils.china_agent_states import ChinaAgentState
from tradingagents.agents.utils.china_agent_utils import ChinaToolkit

from .china_conditional_logic import ChinaConditionalLogic


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
        conditional_logic: ChinaConditionalLogic,
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

    def setup_china_graph(self, selected_analysts=["市场技术"]):
        """设置并编译中国A股代理工作流图。

        Args:
            selected_analysts (list): 要包含的分析师类型列表。选项包括:
                - "市场技术": 市场技术分析师
                - "新闻": 新闻分析师（政策与新闻）
                - "基本面": 基本面分析师（财务分析）
                - "情绪": 社交情绪分析师
        """
        if len(selected_analysts) == 0:
            raise ValueError("中国交易代理图设置错误：未选择任何分析师！")

        # 创建分析师节点
        analyst_nodes = {}
        delete_nodes = {}
        tool_nodes = {}

        # 分析师类型映射
        analyst_mapping = {
            "市场技术": "market",
            "新闻": "news", 
            "基本面": "fundamentals",
            "情绪": "social"
        }

        for analyst_type in selected_analysts:
            if analyst_type == "市场技术":
                analyst_nodes["market"] = create_china_market_analyst(
                    self.quick_thinking_llm, self.toolkit
                )
                delete_nodes["market"] = create_china_msg_delete()
                tool_nodes["market"] = self.tool_nodes["market"]

            elif analyst_type == "新闻":
                analyst_nodes["news"] = create_china_news_analyst(
                    self.quick_thinking_llm, self.toolkit
                )
                delete_nodes["news"] = create_china_msg_delete()
                tool_nodes["news"] = self.tool_nodes["news"]

            elif analyst_type == "基本面":
                analyst_nodes["fundamentals"] = create_china_fundamentals_analyst(
                    self.quick_thinking_llm, self.toolkit
                )
                delete_nodes["fundamentals"] = create_china_msg_delete()
                tool_nodes["fundamentals"] = self.tool_nodes["fundamentals"]

            elif analyst_type == "情绪":
                # 暂时使用新闻分析师代替社交情绪分析师
                analyst_nodes["social"] = create_china_news_analyst(
                    self.quick_thinking_llm, self.toolkit
                )
                delete_nodes["social"] = create_china_msg_delete()
                tool_nodes["social"] = self.tool_nodes["news"]  # 使用新闻工具

        # 创建研究员和管理节点
        bull_researcher_node = create_china_bull_researcher(
            self.quick_thinking_llm, self.bull_memory
        )
        bear_researcher_node = create_china_bear_researcher(
            self.quick_thinking_llm, self.bear_memory
        )
        research_manager_node = create_china_research_manager(
            self.deep_thinking_llm, self.invest_judge_memory
        )
        trader_node = create_china_trader(self.quick_thinking_llm, self.trader_memory)

        # 创建风险分析节点
        risky_analyst = create_china_aggressive_debator(self.quick_thinking_llm)
        neutral_analyst = create_china_neutral_debator(self.quick_thinking_llm)
        safe_analyst = create_china_conservative_debator(self.quick_thinking_llm)
        risk_manager_node = create_china_risk_manager(
            self.deep_thinking_llm, self.risk_manager_memory
        )

        # 创建工作流
        workflow = StateGraph(ChinaAgentState)

        # 将分析师节点添加到图中
        for analyst_key, node in analyst_nodes.items():
            # 中文节点名称映射
            chinese_names = {
                "market": "市场技术分析师",
                "news": "新闻分析师",
                "fundamentals": "基本面分析师", 
                "social": "社交情绪分析师"
            }
            chinese_name = chinese_names[analyst_key]
            
            workflow.add_node(chinese_name, node)
            workflow.add_node(f"消息清理_{analyst_key}", delete_nodes[analyst_key])
            workflow.add_node(f"工具_{analyst_key}", tool_nodes[analyst_key])

        # 添加其他节点
        workflow.add_node("看涨研究员", bull_researcher_node)
        workflow.add_node("看跌研究员", bear_researcher_node)
        workflow.add_node("研究经理", research_manager_node)
        workflow.add_node("交易员", trader_node)
        workflow.add_node("激进分析师", risky_analyst)
        workflow.add_node("中性分析师", neutral_analyst)
        workflow.add_node("保守分析师", safe_analyst)
        workflow.add_node("风险评判", risk_manager_node)

        # 定义边
        # 从第一个分析师开始
        first_analyst_type = selected_analysts[0]
        analyst_key = analyst_mapping[first_analyst_type]
        chinese_names = {
            "market": "市场技术分析师",
            "news": "新闻分析师", 
            "fundamentals": "基本面分析师",
            "social": "社交情绪分析师"
        }
        first_analyst_name = chinese_names[analyst_key]
        workflow.add_edge(START, first_analyst_name)

        # 按顺序连接分析师
        for i, analyst_type in enumerate(selected_analysts):
            analyst_key = analyst_mapping[analyst_type]
            current_analyst = chinese_names[analyst_key]
            current_tools = f"工具_{analyst_key}"
            current_clear = f"消息清理_{analyst_key}"

            # 为当前分析师添加条件边
            # 创建节点名称映射
            node_mapping = {
                f"tools_{analyst_key}": current_tools,
                f"Msg Clear {analyst_key.title()}": current_clear
            }
            workflow.add_conditional_edges(
                current_analyst,
                getattr(self.conditional_logic, f"should_continue_{analyst_key}"),
                node_mapping,
            )
            workflow.add_edge(current_tools, current_analyst)

            # 连接到下一个分析师或看涨研究员（如果这是最后一个分析师）
            if i < len(selected_analysts) - 1:
                next_analyst_type = selected_analysts[i+1]
                next_analyst_key = analyst_mapping[next_analyst_type]
                next_analyst_name = chinese_names[next_analyst_key]
                workflow.add_edge(current_clear, next_analyst_name)
            else:
                workflow.add_edge(current_clear, "看涨研究员")

        # 添加剩余边
        workflow.add_conditional_edges(
            "看涨研究员",
            self.conditional_logic.should_continue_debate,
            {
                "看跌研究员": "看跌研究员",
                "研究经理": "研究经理",
            },
        )
        workflow.add_conditional_edges(
            "看跌研究员",
            self.conditional_logic.should_continue_debate,
            {
                "看涨研究员": "看涨研究员",
                "研究经理": "研究经理",
            },
        )
        workflow.add_edge("研究经理", "交易员")
        workflow.add_edge("交易员", "激进分析师")
        workflow.add_conditional_edges(
            "激进分析师",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "保守分析师": "保守分析师",
                "风险评判": "风险评判",
            },
        )
        workflow.add_conditional_edges(
            "保守分析师",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "中性分析师": "中性分析师",
                "风险评判": "风险评判",
            },
        )
        workflow.add_conditional_edges(
            "中性分析师",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "激进分析师": "激进分析师",
                "风险评判": "风险评判",
            },
        )
        workflow.add_edge("风险评判", END)

        return workflow.compile()