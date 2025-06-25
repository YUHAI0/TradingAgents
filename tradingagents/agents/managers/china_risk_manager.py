"""
中国A股风险管理器
负责评估风险分析师的辩论并做出最终的风险管理决策
"""

import time
import json


def create_china_risk_manager(llm, memory):
    """
    创建中国A股风险管理器
    
    Args:
        llm: 大语言模型实例
        memory: 记忆存储实例
        
    Returns:
        function: 风险管理器节点函数
    """
    def china_risk_manager_node(state) -> dict:
        """
        中国A股风险管理器节点
        
        评估三个风险分析师（激进、中性、保守）的辩论，
        结合A股市场特点做出最终的风险管理决策
        """
        
        # 提取状态信息
        company_name = state["company_of_interest"]
        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        
        # 获取各分析报告
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        sentiment_report = state["sentiment_report"]
        trader_plan = state["investment_plan"]

        # 构建当前市场情况描述
        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        
        # 获取相似情况的历史记忆
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        # A股风险管理专用提示词
        prompt = f"""作为中国A股市场的风险管理总监和辩论评委，您的目标是评估三位风险分析师——激进派、中性派和保守派——之间的辩论，并确定对交易员最佳的行动方案。您的决策必须明确：买入、卖出或持有。只有在有强有力理由支撑时才选择持有，避免因为各方观点都有道理就选择持有的懒惰做法。力求清晰和果断。

## A股市场特色考虑因素：
1. **涨跌停限制**：主板±10%，科创板/创业板±20%，ST股票±5%
2. **T+1交易制度**：当日买入次日才能卖出，需考虑隔夜风险
3. **政策敏感性**：A股受政策影响较大，需重点关注监管政策变化
4. **散户占比高**：市场情绪波动较大，需考虑群体性行为
5. **资金流向**：关注北向资金、融资融券、大宗交易等资金动向
6. **板块轮动**：A股常有明显的板块轮动和题材炒作特征

## 决策指导原则：
1. **总结关键论点**：提取每位分析师的最强观点，重点关注与A股市场相关的论据
2. **提供理由支撑**：用辩论中的直接引述和反驳论据支持您的建议
3. **完善交易员计划**：以交易员的原始计划**{trader_plan}**为基础，根据分析师的见解进行A股市场化调整
4. **吸取历史教训**：利用过往经验**{past_memory_str}**中的教训，解决以前的误判，确保不犯导致亏损的错误买入/卖出/持有决策

## 输出要求：
- 明确且可执行的建议：买入、卖出或持有
- 基于辩论和历史反思的详细推理
- 结合A股市场特点的风险评估
- 具体的仓位管理和止损止盈建议

---

**风险分析师辩论历史：**  
{history}

---

**当前股票代码：** {company_name}

请专注于可执行的见解和持续改进。基于历史教训，批判性评估所有观点，确保每个决策都能推动更好的A股投资结果。特别注意A股市场的独特风险和机会。"""

        # 调用LLM生成风险管理决策
        response = llm.invoke(prompt)

        # 更新风险辩论状态
        new_risk_debate_state = {
            "judge_decision": response.content,
            "history": risk_debate_state["history"],
            "risky_history": risk_debate_state["risky_history"],
            "safe_history": risk_debate_state["safe_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "风险管理总监",
            "current_risky_response": risk_debate_state["current_risky_response"],
            "current_safe_response": risk_debate_state["current_safe_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response.content,
        }

    return china_risk_manager_node 