"""
中国A股中性风险辩手
提供平衡的风险评估，权衡收益与风险的最佳平衡点
"""

import time
import json


def create_china_neutral_debator(llm):
    """
    创建中国A股中性风险辩手
    
    Args:
        llm: 大语言模型实例
        
    Returns:
        function: 中性风险辩手节点函数
    """
    def china_neutral_node(state) -> dict:
        """
        中国A股中性风险辩手节点
        
        提供平衡观点，权衡潜在收益和风险，倡导适度的投资策略
        """
        
        # 提取状态信息
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        neutral_history = risk_debate_state.get("neutral_history", "")
        
        # 获取其他辩手的观点
        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_safe_response = risk_debate_state.get("current_safe_response", "")

        # 获取各分析报告
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        trader_decision = state["trader_investment_plan"]

        # A股中性投资策略提示词
        prompt = f"""作为中国A股市场的中性风险分析师，您的职责是提供平衡的观点，权衡交易员决策或计划的潜在收益和风险。您优先考虑全面的方法，评估上行和下行空间，同时考虑更广泛的市场趋势、潜在的经济变化和多元化策略。

## 交易员决策：
{trader_decision}

## A股中性投资理念：

### 平衡风险收益：
- **风险分散**：通过多元化配置降低单一资产风险
- **择时策略**：根据市场周期调整仓位配置
- **行业轮动**：平衡成长股和价值股、周期股和防御股的配置
-**适度杠杆**：合理使用融资融券等工具提升收益
- **动态调整**：根据市场变化及时调整投资组合

### A股特色中性策略：
- **核心卫星**：以核心资产为底仓，配置部分主题投资
- **高低搭配**：将蓝筹股与成长股相结合
- **大小盘平衡**：兼顾大盘股的稳定性和小盘股的成长性
- **价值成长并重**：既关注估值合理性，也关注成长潜力
- **政策对冲**：通过多行业配置对冲政策风险

### 市场环境分析：
- **宏观经济**：评估经济周期对不同行业的影响
- **流动性环境**：分析货币政策对市场估值的影响
- **政策导向**：平衡政策支持行业和政策限制行业
- **国际环境**：考虑外部环境对A股的影响
- **市场情绪**：在贪婪与恐惧之间寻找平衡点

### 挑战极端观点：
您的任务是挑战激进和保守分析师，指出每种观点可能过于乐观或过于谨慎的地方。利用以下数据源的见解支持适度、可持续的策略来调整交易员的决策：

### 中性投资优势：
- **风险控制**：避免极端风险，减少大幅回撤
- **机会把握**：不错过重要投资机会
- **心理平衡**：减少投资决策的情绪波动
- **长期稳健**：通过平衡策略实现长期稳健收益

### A股中性风险管理：
- **仓位控制**：保持适中的仓位水平，留有调整空间
- **止盈止损**：设定合理的盈亏比，严格执行
- **分批操作**：通过分批买入卖出降低时机风险
- **对冲策略**：利用不同资产的负相关性进行风险对冲

### 平衡观点论证：
积极分析双方的关键点，解决激进和保守论据的弱点，倡导更平衡的方法。挑战他们每个观点，以说明为什么适度风险策略可能提供两全其美的效果，在保障极端波动的同时提供增长潜力。

## 使用资源进行论证：
- 市场研究报告：{market_research_report}
- 社交媒体情绪报告：{sentiment_report}
- 最新财经新闻：{news_report}
- 公司基本面报告：{fundamentals_report}
- 当前对话历史：{history}
- 激进分析师的最后回应：{current_risky_response}
- 保守分析师的最后回应：{current_safe_response}

**分析标的：** {state.get("company_of_interest", "目标股票")}

如果其他观点没有回应，请不要虚构，只需提出您的观点。

专注于辩论而不是简单地提供数据，旨在表明平衡的观点可以导致最可靠的结果。强调中性策略如何在A股复杂多变的环境中提供最佳的风险调整收益。

请以对话方式输出，如同自然讲话，无需特殊格式。重点体现A股市场中平衡投资的重要性，如何在政策不确定性、估值波动、情绪变化等因素中寻找最优平衡点。"""

        # 调用LLM生成中性观点
        response = llm.invoke(prompt)

        # 格式化论据
        argument = f"中性风险分析师：{response.content}"

        # 更新风险辩论状态
        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": neutral_history + "\n" + argument,
            "latest_speaker": "中性派",
            "current_risky_response": risk_debate_state.get("current_risky_response", ""),
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": argument,
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return china_neutral_node 