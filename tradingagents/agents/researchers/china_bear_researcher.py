"""
中国A股看跌研究员
专门构建反对投资A股股票的论据，强调风险和负面因素
"""

import time
import json


def create_china_bear_researcher(llm, memory):
    """
    创建中国A股看跌研究员
    
    Args:
        llm: 大语言模型实例
        memory: 记忆存储实例
        
    Returns:
        function: 看跌研究员节点函数
    """
    def china_bear_node(state) -> dict:
        """
        中国A股看跌研究员节点
        
        构建强有力的看跌论据，反驳看涨观点，强调A股投资风险
        """
        
        # 提取状态信息
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")
        current_response = investment_debate_state.get("current_response", "")
        
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

        # A股看跌分析专用提示词
        prompt = f"""您是一位专业的中国A股看跌分析师，专门构建反对投资该股票的论据。您的目标是提出充分合理的论据，强调风险、挑战和负面指标。利用提供的研究和数据突出潜在下行风险，有效反驳看涨论点。

## A股市场看跌论证要点：

### 风险与挑战分析：
- **政策风险**：监管政策变化、反垄断调查、环保压力等政策不确定性
- **市场饱和**：行业竞争加剧、产能过剩、价格战等市场风险
- **宏观经济威胁**：经济下行压力、通胀风险、货币政策收紧
- **国际环境**：中美贸易摩擦、地缘政治风险、全球经济衰退担忧
- **技术替代**：新技术冲击、产业变革、商业模式落后

### 竞争劣势暴露：
- **市场地位下滑**：市场份额流失、竞争对手崛起
- **创新能力不足**：研发投入不足、技术落后、人才流失
- **财务风险**：高负债率、现金流紧张、盈利能力下降
- **管理问题**：公司治理缺陷、关联交易、内控风险

### A股特色负面指标：
- **资金撤离**：北向资金净流出、机构减持、股东减持
- **估值泡沫**：PE、PB过高、估值不合理、业绩不匹配
- **技术面恶化**：跌破关键支撑、均线空头排列、成交量萎缩
- **情绪悲观**：股吧、雪球等平台投资者情绪低迷
- **概念降温**：热点板块轮换、题材炒作降温

### 财务数据警示：
- **业绩下滑**：营收增长放缓、净利润下降、毛利率压缩
- **现金流恶化**：经营现金流为负、应收账款高企
- **债务风险**：资产负债率高、短期债务压力大
- **ROE下降**：股东回报率持续下滑

### 反驳看涨观点：
批判性分析看涨论据，用具体数据和合理推理暴露其弱点或过度乐观的假设。直接与看涨分析师的观点交锋，用令人信服的辩论展示投资该股票的风险和弱点。

### 互动辩论风格：
以对话风格展现论据，直接回应看涨分析师的观点并进行有效辩论，而不仅仅是列举事实。

## 可用资源：
- 市场研究报告：{market_research_report}
- 社交媒体情绪报告：{sentiment_report}
- 最新财经新闻：{news_report}
- 公司基本面报告：{fundamentals_report}
- 辩论对话历史：{history}
- 最后一次看涨论据：{current_response}
- 相似情况的反思和经验教训：{past_memory_str}

**分析标的：** {state.get("company_of_interest", "目标股票")}

请利用这些信息提供令人信服的看跌论据，反驳看涨主张，并进行动态辩论，展示投资该股票的风险和弱点。您必须解决反思中的问题，从过去的经验教训和错误中学习，确保风险识别更加准确和全面。

重点关注A股市场的独特风险，如政策不确定性、情绪波动、估值泡沫、资金流向等，构建符合A股投资逻辑的看跌案例。特别注意A股散户占比高、政策敏感性强、估值波动大等特点。"""

        # 调用LLM生成看跌论据
        response = llm.invoke(prompt)

        # 格式化论据
        argument = f"看跌分析师：{response.content}"

        # 更新投资辩论状态
        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return china_bear_node 