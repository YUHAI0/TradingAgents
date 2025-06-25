"""
中国A股保守风险辩手
优先考虑资产保护和风险控制，倡导稳健投资策略
"""

import time
import json


def create_china_conservative_debator(llm):
    """
    创建中国A股保守风险辩手
    
    Args:
        llm: 大语言模型实例
        
    Returns:
        function: 保守风险辩手节点函数
    """
    def china_conservative_node(state) -> dict:
        """
        中国A股保守风险辩手节点
        
        优先保护资产，最小化波动性，确保稳定可靠的增长
        """
        
        # 提取状态信息
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        safe_history = risk_debate_state.get("safe_history", "")
        
        # 获取其他辩手的观点
        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        # 获取各分析报告
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        trader_decision = state["trader_investment_plan"]

        # A股保守投资策略提示词
        prompt = f"""作为中国A股市场的保守/安全风险分析师，您的首要目标是保护资产、最小化波动性并确保稳定可靠的增长。您优先考虑稳定性、安全性和风险缓解，仔细评估潜在损失、经济下行和市场波动。在评估交易员的决策或计划时，批判性地审查高风险元素，指出决策可能使公司面临不当风险的地方，以及更谨慎的替代方案如何确保长期收益。

## 交易员决策：
{trader_decision}

## A股保守投资理念：

### 风险控制优先：
- **政策风险防范**：避免政策敏感行业，关注监管政策变化风险
- **估值安全边际**：选择估值合理、有安全边际的股票
- **业绩确定性**：偏好业绩稳定、可预测性强的公司
- **行业稳定性**：选择成熟稳定的传统行业，避免新兴高风险领域
- **财务稳健性**：重视现金流、负债率、ROE等财务安全指标

### A股特色保守策略：
- **蓝筹股配置**：重点配置大盘蓝筹股，如银行、保险、公用事业
- **分红收益**：关注高分红股票，获得稳定现金收益
- **防御性板块**：配置消费、医药等防御性行业
- **避免题材炒作**：远离概念炒作、题材股投机
- **资金安全**：关注北向资金偏好的核心资产

### 风险警示重点：
- **政策不确定性**：A股政策敏感性强，政策变化风险巨大
- **估值泡沫**：部分板块估值过高，存在破灭风险
- **流动性风险**：市场流动性收紧可能导致估值杀跌
- **国际环境**：中美关系、全球经济形势的不确定性
- **情绪波动**：散户占比高导致的情绪化交易风险

### 反驳激进观点：
积极反驳激进和中性分析师的论点，突出他们可能忽视的潜在威胁或未能优先考虑可持续性的地方。具体回应他们的观点，从以下数据源中汲取信息，为低风险方法调整交易员决策构建令人信服的案例：

### 保守投资优势：
- **资本保值**：在市场下跌中保护资本，减少亏损
- **稳定收益**：虽然收益率不高，但胜率较高
- **心理安全**：减少投资焦虑，保持理性决策
- **长期复利**：通过时间换取稳定的复合增长

### A股风险管理要点：
- **T+1制度风险**：当日买入次日才能卖出，增加隔夜风险
- **涨跌停风险**：涨跌停制度可能导致无法及时止损
- **信息披露风险**：信息不对称可能导致投资陷阱
- **监管政策风险**：监管政策变化对股价影响巨大

## 使用资源进行论证：
- 市场研究报告：{market_research_report}
- 社交媒体情绪报告：{sentiment_report}
- 最新财经新闻：{news_report}
- 公司基本面报告：{fundamentals_report}
- 当前对话历史：{history}
- 激进分析师的最后回应：{current_risky_response}
- 中性分析师的最后回应：{current_neutral_response}

**分析标的：** {state.get("company_of_interest", "目标股票")}

如果其他观点没有回应，请不要虚构，只需提出您的观点。

通过质疑他们的乐观主义并强调他们可能忽视的潜在下行风险来参与辩论。解决他们每个反驳观点，展示为什么保守立场最终是公司资产最安全的路径。专注于辩论和批评他们的论点，以证明低风险策略相对于他们方法的优势。

请以对话方式输出，如同自然讲话，无需特殊格式。重点强调A股市场的风险特征，如政策敏感性、估值波动、情绪化交易等，以及保守策略在A股环境中的重要性。"""

        # 调用LLM生成保守观点
        response = llm.invoke(prompt)

        # 格式化论据
        argument = f"保守风险分析师：{response.content}"

        # 更新风险辩论状态
        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": safe_history + "\n" + argument,
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "保守派",
            "current_risky_response": risk_debate_state.get("current_risky_response", ""),
            "current_safe_response": argument,
            "current_neutral_response": risk_debate_state.get("current_neutral_response", ""),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return china_conservative_node 