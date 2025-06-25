# TradingAgents/graph/china_trading_graph.py

import os
from pathlib import Path
import json
from datetime import date
from typing import Dict, Any, Tuple, List, Optional

from tradingagents.llm_providers.china_llm_provider import ChinaLLMManager
from langgraph.prebuilt import ToolNode

from tradingagents.agents.china_agents_init import *
from tradingagents.china_config import CHINA_DEFAULT_CONFIG
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.agents.utils.china_agent_states import (
    ChinaAgentState,
    ChinaInvestDebateState,
    ChinaRiskDebateState,
)
from tradingagents.dataflows.china_interface import set_china_config

from .conditional_logic import ConditionalLogic
from .china_setup import ChinaGraphSetup
from .propagation import Propagator
from .reflection import Reflector
from .signal_processing import SignalProcessor


class ChinaTradingAgentsGraph:
    """中国A股交易代理系统的主要编排类。"""

    def __init__(
        self,
        selected_analysts=["market", "news", "fundamentals"],
        debug=False,
        config: Dict[str, Any] = None,
        llm_provider="qwen",  # 默认使用通义千问
    ):
        """初始化中国交易代理图和组件。

        Args:
            selected_analysts: 要包含的分析师类型列表
            debug: 是否运行在调试模式
            config: 配置字典。如果为None，使用默认配置
            llm_provider: LLM提供商，可选: qwen, zhipu, baichuan, ernie
        """
        self.debug = debug
        self.config = config or CHINA_DEFAULT_CONFIG
        self.llm_provider = llm_provider

        # 更新接口配置
        set_china_config(self.config)

        # 创建必要的目录
        os.makedirs(
            os.path.join(self.config["project_dir"], "dataflows/china_data_cache"),
            exist_ok=True,
        )

        # 初始化中国LLM管理器
        self.llm_manager = ChinaLLMManager()
        
        # 根据配置获取LLM实例
        self.deep_thinking_llm = self.llm_manager.get_llm(
            provider=llm_provider,
            model_type="advanced"
        )
        self.quick_thinking_llm = self.llm_manager.get_llm(
            provider=llm_provider,
            model_type="fast"
        )
        
        # 初始化中国工具包
        self.toolkit = ChinaToolkit(config=self.config)

        # 初始化记忆系统
        self.bull_memory = FinancialSituationMemory("china_bull_memory", self.config)
        self.bear_memory = FinancialSituationMemory("china_bear_memory", self.config)
        self.trader_memory = FinancialSituationMemory("china_trader_memory", self.config)
        self.invest_judge_memory = FinancialSituationMemory("china_invest_judge_memory", self.config)
        self.risk_manager_memory = FinancialSituationMemory("china_risk_manager_memory", self.config)

        # 创建工具节点
        self.tool_nodes = self._create_china_tool_nodes()

        # 初始化组件
        self.conditional_logic = ConditionalLogic()
        self.graph_setup = ChinaGraphSetup(
            self.quick_thinking_llm,
            self.deep_thinking_llm,
            self.toolkit,
            self.tool_nodes,
            self.bull_memory,
            self.bear_memory,
            self.trader_memory,
            self.invest_judge_memory,
            self.risk_manager_memory,
            self.conditional_logic,
        )

        self.propagator = Propagator()
        self.reflector = Reflector(self.quick_thinking_llm)
        self.signal_processor = SignalProcessor(self.quick_thinking_llm)

        # 状态跟踪
        self.curr_state = None
        self.stock_code = None
        self.log_states_dict = {}  # 日期到完整状态字典

        # 设置图
        self.graph = self.graph_setup.setup_china_graph(selected_analysts)

    def _create_china_tool_nodes(self) -> Dict[str, ToolNode]:
        """创建中国A股市场的工具节点。"""
        return {
            "market": ToolNode(
                [
                    # 在线工具
                    self.toolkit.get_china_stock_data_online,
                    self.toolkit.get_china_technical_indicators_online,
                    # 离线工具
                    self.toolkit.get_china_stock_data,
                    self.toolkit.get_china_technical_indicators,
                ]
            ),
            "news": ToolNode(
                [
                    # 在线工具
                    self.toolkit.get_china_stock_news_online,
                    self.toolkit.get_china_market_news_online,
                    # 离线工具
                    self.toolkit.get_china_stock_news,
                    self.toolkit.get_china_policy_news,
                ]
            ),
            "fundamentals": ToolNode(
                [
                    # 在线工具
                    self.toolkit.get_china_fundamentals_online,
                    self.toolkit.get_china_financial_reports_online,
                    # 离线工具
                    self.toolkit.get_china_company_info,
                    self.toolkit.get_china_financial_data,
                ]
            ),
        }

    def propagate(self, stock_code, trade_date):
        """为指定股票在特定日期运行中国交易代理图。
        
        Args:
            stock_code: 股票代码，格式如 '000001.SZ' 或 '600000.SH'
            trade_date: 交易日期
        """

        self.stock_code = stock_code

        # 初始化状态
        init_agent_state = self.propagator.create_china_initial_state(
            stock_code, trade_date
        )
        args = self.propagator.get_graph_args()

        if self.debug:
            # 调试模式带跟踪
            trace = []
            for chunk in self.graph.stream(init_agent_state, **args):
                if len(chunk["messages"]) == 0:
                    pass
                else:
                    chunk["messages"][-1].pretty_print()
                    trace.append(chunk)

            final_state = trace[-1]
        else:
            # 标准模式无跟踪
            final_state = self.graph.invoke(init_agent_state, **args)

        # 存储当前状态用于反思
        self.curr_state = final_state

        # 记录状态
        self._log_china_state(trade_date, final_state)

        # 返回决策和处理后的信号
        return final_state, self.process_signal(final_state["final_trade_decision"])

    def _log_china_state(self, trade_date, final_state):
        """将最终状态记录到JSON文件。"""
        self.log_states_dict[str(trade_date)] = {
            "stock_code": final_state["stock_code"],
            "trade_date": final_state["trade_date"],
            "market_report": final_state["market_report"],
            "news_report": final_state["news_report"],
            "fundamentals_report": final_state["fundamentals_report"],
            "investment_debate_state": {
                "bull_history": final_state["investment_debate_state"]["bull_history"],
                "bear_history": final_state["investment_debate_state"]["bear_history"],
                "history": final_state["investment_debate_state"]["history"],
                "current_response": final_state["investment_debate_state"]["current_response"],
                "judge_decision": final_state["investment_debate_state"]["judge_decision"],
            },
            "trader_investment_decision": final_state["trader_investment_plan"],
            "risk_debate_state": {
                "risky_history": final_state["risk_debate_state"]["risky_history"],
                "safe_history": final_state["risk_debate_state"]["safe_history"],
                "neutral_history": final_state["risk_debate_state"]["neutral_history"],
                "history": final_state["risk_debate_state"]["history"],
                "judge_decision": final_state["risk_debate_state"]["judge_decision"],
            },
            "investment_plan": final_state["investment_plan"],
            "final_trade_decision": final_state["final_trade_decision"],
        }

        # 保存到文件
        directory = Path(f"eval_results/{self.stock_code}/ChinaTradingAgentsStrategy_logs/")
        directory.mkdir(parents=True, exist_ok=True)

        with open(
            f"eval_results/{self.stock_code}/ChinaTradingAgentsStrategy_logs/full_states_log.json",
            "w",
            encoding='utf-8'
        ) as f:
            json.dump(self.log_states_dict, f, indent=4, ensure_ascii=False)

    def reflect_and_remember(self, returns_losses):
        """基于收益反思决策并更新记忆。"""
        self.reflector.reflect_china_bull_researcher(
            self.curr_state, returns_losses, self.bull_memory
        )
        self.reflector.reflect_china_bear_researcher(
            self.curr_state, returns_losses, self.bear_memory
        )
        self.reflector.reflect_china_trader(
            self.curr_state, returns_losses, self.trader_memory
        )
        self.reflector.reflect_china_invest_judge(
            self.curr_state, returns_losses, self.invest_judge_memory
        )
        self.reflector.reflect_china_risk_manager(
            self.curr_state, returns_losses, self.risk_manager_memory
        )

    def process_signal(self, full_signal):
        """处理交易信号为具体操作。"""
        # 基础信号处理逻辑
        if "买入" in full_signal or "建仓" in full_signal:
            return "BUY"
        elif "卖出" in full_signal or "清仓" in full_signal:
            return "SELL"
        elif "持有" in full_signal:
            return "HOLD"
        else:
            return "HOLD"  # 默认持有

    def get_current_portfolio_status(self):
        """获取当前投资组合状态。"""
        if self.curr_state:
            return {
                "stock_code": self.stock_code,
                "investment_plan": self.curr_state.get("investment_plan", {}),
                "final_decision": self.curr_state.get("final_trade_decision", ""),
                "risk_assessment": self.curr_state.get("risk_debate_state", {}).get("judge_decision", ""),
            }
        return None

    def get_analysis_summary(self):
        """获取分析摘要。"""
        if self.curr_state:
            return {
                "market_analysis": self.curr_state.get("market_report", ""),
                "news_analysis": self.curr_state.get("news_report", ""),
                "fundamentals_analysis": self.curr_state.get("fundamentals_report", ""),
                "investment_reasoning": self.curr_state.get("investment_debate_state", {}).get("judge_decision", ""),
            }
        return None

    def update_config(self, new_config: Dict[str, Any]):
        """更新配置。"""
        self.config.update(new_config)
        set_china_config(self.config)

    def switch_llm_provider(self, provider: str):
        """切换LLM提供商。
        
        Args:
            provider: 新的LLM提供商，可选: qwen, zhipu, baichuan, ernie
        """
        if provider not in ["qwen", "zhipu", "baichuan", "ernie"]:
            raise ValueError(f"不支持的LLM提供商: {provider}")
            
        self.llm_provider = provider
        self.deep_thinking_llm = self.llm_manager.get_llm(provider=provider, model_type="advanced")
        self.quick_thinking_llm = self.llm_manager.get_llm(provider=provider, model_type="fast")
        
        # 重新设置图
        self.graph_setup = ChinaGraphSetup(
            self.quick_thinking_llm,
            self.deep_thinking_llm,
            self.toolkit,
            self.tool_nodes,
            self.bull_memory,
            self.bear_memory,
            self.trader_memory,
            self.invest_judge_memory,
            self.risk_manager_memory,
            self.conditional_logic,
        ) 