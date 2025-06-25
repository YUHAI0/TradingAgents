"""
中国A股交易员
基于多维度分析做出最终的A股交易决策
"""

import functools
import time
import json


def create_china_trader(llm, memory):
    """
    创建中国A股交易员
    
    Args:
        llm: 大语言模型实例
        memory: 记忆存储实例
        
    Returns:
        function: 交易员节点函数（偏函数）
    """
    def china_trader_node(state, name):
        """
        中国A股交易员节点
        
        基于分析师团队的综合分析做出A股投资决策
        """
        
        # 提取状态信息
        company_name = state["company_of_interest"]
        investment_plan = state["investment_plan"]
        
        # 获取各维度分析报告
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

        # 构建对话上下文
        context = {
            "role": "user",
            "content": f"""基于分析师团队的综合分析，这里是为 {company_name} 量身定制的投资计划。该计划整合了当前技术市场趋势、宏观经济指标和社交媒体情绪的见解。请以此计划为基础评估您的下一个交易决策。

**投资计划建议：** 
{investment_plan}

请利用这些见解做出明智和战略性的A股投资决策。"""
        }

        # 系统消息（A股交易员专用）
        system_message = {
            "role": "system",
            "content": f"""您是一位专业的中国A股交易代理，专门分析A股市场数据以做出投资决策。基于您的分析，请提供具体的买入、卖出或持有建议。请以坚定的决策结束，并始终以'最终交易提案：**买入/持有/卖出**'结束您的回应以确认您的建议。

## A股市场特色考虑：

### 交易制度特点：
- **T+1制度**：当日买入次日才能卖出，需考虑隔夜风险
- **涨跌停限制**：主板±10%，科创板/创业板±20%，ST股票±5%
- **竞价机制**：集合竞价和连续竞价的特殊规则
- **停牌制度**：重大事项可能导致长期停牌

### 市场环境因素：
- **政策敏感性**：监管政策变化对股价影响巨大
- **散户主导**：散户占比高，情绪化交易特征明显
- **资金流向**：北向资金、南向资金的流向指示意义
- **板块轮动**：明显的概念炒作和板块轮动特征

### 风险控制要点：
- **政策风险**：关注监管政策变化风险
- **流动性风险**：小盘股和ST股流动性风险
- **估值风险**：部分股票估值过高的泡沫风险
- **信息风险**：信息披露不充分的投资陷阱

### 投资决策框架：
1. **技术面分析**：关注A股特有的技术指标和形态
2. **基本面分析**：结合中国会计准则和行业特点
3. **政策面分析**：评估政策导向对行业的影响
4. **资金面分析**：关注资金流向和市场流动性
5. **情绪面分析**：评估市场情绪和投资者行为

请务必利用历史决策的经验教训来避免重复错误。以下是相似情况下的反思和经验教训：

**历史经验教训：**
{past_memory_str}

**分析标的：** {company_name}

请基于A股市场的独特特点，结合技术分析、基本面分析、政策分析和情绪分析，做出专业的投资决策。特别注意A股市场的风险特征和投资机会。"""
        }

        # 构建完整消息列表
        messages = [system_message, context]

        # 调用LLM生成交易决策
        result = llm.invoke(messages)

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    # 返回偏函数，固定name参数为"A股交易员"
    return functools.partial(china_trader_node, name="A股交易员") 