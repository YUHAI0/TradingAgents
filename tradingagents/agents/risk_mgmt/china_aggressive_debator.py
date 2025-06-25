"""
中国A股激进风险辩手
倡导高风险高回报的投资策略，强调激进投资机会
"""

import time
import json


def create_china_aggressive_debator(llm):
    """
    创建中国A股激进风险辩手
    
    Args:
        llm: 大语言模型实例
        
    Returns:
        function: 激进风险辩手节点函数
    """
    def china_aggressive_node(state) -> dict:
        """
        中国A股激进风险辩手节点
        
        积极倡导高回报、高风险机会，强调大胆策略和竞争优势
        """
        
        # 提取状态信息
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        risky_history = risk_debate_state.get("risky_history", "")
        
        # 获取其他辩手的观点
        current_safe_response = risk_debate_state.get("current_safe_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        # 获取各分析报告
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        trader_decision = state["trader_investment_plan"]

        # A股激进投资策略提示词
        prompt = f"""作为中国A股市场的激进风险分析师，您的职责是积极倡导高回报、高风险的投资机会，强调大胆策略和竞争优势。在评估交易员的决策或计划时，重点关注潜在的上行空间、成长潜力和创新收益——即使这些伴随着较高的风险。利用提供的市场数据和情绪分析加强您的论据，挑战对立观点。

## 交易员决策：
{trader_decision}

## A股激进投资理念：

### 高风险高回报机会：
- **政策风口**：抢占政策红利先机，如"碳中和"、"专精特新"、"数字经济"等
- **题材炒作**：积极参与热点概念炒作，如元宇宙、新能源、军工等
- **重组并购**：关注重组预期股票，追求重组套利收益
- **次新股机会**：新股上市后的炒作机会和成长空间
- **ST摘帽**：困境反转的高弹性机会

### A股特色激进策略：
- **涨停板追击**：追涨停板，把握强势股的连板机会
- **板块轮动**：快速切换热点板块，追逐短期爆发力
- **资金推动**：跟随北向资金、游资动向进行投资
- **消息驱动**：基于内幕消息、市场传言的快速反应
- **技术突破**：重仓突破关键技术位的股票

### 挑战保守观点：
具体针对保守和中性分析师提出的每个观点进行反驳，用数据驱动的反驳和有说服力的推理进行回应。突出他们的谨慎可能错失的关键机会，或者他们的假设可能过于保守的地方。

### 强调收益潜力：
- **爆发性增长**：强调公司业绩爆发的可能性
- **估值修复**：被低估股票的价值回归空间
- **技术创新**：新技术带来的颠覆性机会
- **市场扩张**：新市场开拓的想象空间

### 激进风险管理：
虽然承认风险，但强调通过以下方式可以管控：
- **止损策略**：设定合理止损位，控制单笔损失
- **仓位管理**：集中投资优势标的，提高收益率
- **趋势跟踪**：顺势而为，及时调整策略
- **信息优势**：利用信息差获取超额收益

## 使用资源进行论证：
- 市场研究报告：{market_research_report}
- 社交媒体情绪报告：{sentiment_report}
- 最新财经新闻：{news_report}
- 公司基本面报告：{fundamentals_report}
- 当前对话历史：{history}
- 保守分析师的最后论据：{current_safe_response}
- 中性分析师的最后论据：{current_neutral_response}

**分析标的：** {state.get("company_of_interest", "目标股票")}

如果其他观点没有回应，请不要虚构，只需提出您的观点。

积极参与辩论，解决提出的任何具体担忧，反驳他们逻辑中的弱点，并主张承担风险的好处，以超越市场常规表现。保持专注于辩论和说服，而不仅仅是提供数据。挑战每个反对观点，以强调为什么高风险方法是最优的。

请以对话方式输出，如同自然讲话，无需特殊格式。重点强调A股市场的高弹性和爆发力特征，以及激进策略在A股环境中的适用性。"""

        # 调用LLM生成激进观点
        response = llm.invoke(prompt)

        # 格式化论据
        argument = f"激进风险分析师：{response.content}"

        # 更新风险辩论状态
        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risky_history + "\n" + argument,
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "激进派",
            "current_risky_response": argument,
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": risk_debate_state.get("current_neutral_response", ""),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return china_aggressive_node 