"""
中国A股研究管理器
负责评估看涨和看跌研究员的辩论并制定投资计划
"""

import time
import json


def create_china_research_manager(llm, memory):
    """
    创建中国A股研究管理器
    
    Args:
        llm: 大语言模型实例
        memory: 记忆存储实例
        
    Returns:
        function: 研究管理器节点函数
    """
    def china_research_manager_node(state) -> dict:
        """
        中国A股研究管理器节点
        
        评估看涨和看跌研究员的辩论，做出投资决策并制定详细的投资计划
        """
        
        # 提取状态信息
        history = state["investment_debate_state"].get("history", "")
        investment_debate_state = state["investment_debate_state"]
        
        # 获取各分析报告
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        # 构建当前市场情况描述
        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        
        # 获取相似情况的历史记忆
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        # A股投资管理专用提示词
        prompt = f"""作为中国A股市场的投资组合经理和辩论主持人，您的职责是批判性评估本轮辩论并做出明确决策：支持看跌分析师、看涨分析师，或者只有在强有力论据支撑的情况下选择持有。

## A股市场投资决策框架：

### 市场特性考量：
1. **政策导向**：重点关注国家政策、行业政策对股价的影响
2. **资金面分析**：北向资金流向、融资融券余额、大宗交易情况
3. **估值体系**：A股特有的PE、PB估值区间和行业比较
4. **技术面特征**：涨跌停板、缺口理论、均线系统在A股中的应用
5. **题材概念**：热点概念炒作、板块轮动规律
6. **散户情绪**：雪球、东财股吧等平台的投资者情绪变化

### 投资决策要求：
简明扼要地总结双方关键观点，重点关注最具说服力的证据或推理。您的建议——买入、卖出或持有——必须清晰且可执行。避免因为双方都有有效观点就默认选择持有；要基于辩论中最强有力的论据做出承诺性立场。

### 详细投资计划制定：
制定详细的投资计划供交易员执行，应包括：

1. **明确建议**：基于最有说服力论据的决定性立场
2. **投资逻辑**：解释为什么这些论据导致您的结论
3. **具体策略**：实施建议的具体步骤
4. **仓位管理**：
   - 建议仓位比例（考虑A股T+1制度）
   - 分批建仓或减仓策略
   - 止损止盈位设置
5. **时间周期**：持有期预期和关键时间节点
6. **风险控制**：
   - 政策风险应对预案
   - 市场情绪变化的应对策略
   - 涨跌停情况的处理方案

### 历史经验借鉴：
考虑您在类似情况下的过往错误，利用这些见解完善决策制定，确保不断学习和改进。请以对话方式展现分析，如同自然交流，无需特殊格式。

**历史反思和错误教训：**
\"{past_memory_str}\"

**辩论历史：**
{history}

**当前分析标的：** {state.get("company_of_interest", "未知股票")}

请基于A股市场特点，结合技术面、基本面、政策面、资金面的综合分析，做出专业的投资决策和详细的执行计划。"""

        # 调用LLM生成投资决策和计划
        response = llm.invoke(prompt)

        # 更新投资辩论状态
        new_investment_debate_state = {
            "judge_decision": response.content,
            "history": investment_debate_state.get("history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": response.content,
            "count": investment_debate_state["count"],
        }

        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": response.content,
        }

    return china_research_manager_node 