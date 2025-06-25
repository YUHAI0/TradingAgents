"""
中国A股看涨研究员
专门构建支持投资A股股票的论据，强调成长潜力和积极因素
"""

import time
import json


def create_china_bull_researcher(llm, memory):
    """
    创建中国A股看涨研究员
    
    Args:
        llm: 大语言模型实例
        memory: 记忆存储实例
        
    Returns:
        function: 看涨研究员节点函数
    """
    def china_bull_node(state) -> dict:
        """
        中国A股看涨研究员节点
        
        构建强有力的看涨论据，反驳看跌观点，强调A股投资机会
        """
        
        # 提取状态信息
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")
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

        # A股看涨分析专用提示词
        prompt = f"""您是一位专业的中国A股看涨分析师，专门为投资该股票构建强有力的、基于证据的论据。您的任务是强调成长潜力、竞争优势和积极的市场指标，利用提供的研究和数据有效地解决担忧并反驳看跌论点。

## A股市场看涨论证要点：

### 成长潜力分析：
- **政策红利**：分析国家产业政策、"双碳"目标、"专精特新"等政策对公司的利好影响
- **市场空间**：强调中国庞大的内需市场和"双循环"发展格局带来的机会
- **技术创新**：突出公司在自主创新、"卡脖子"技术攻关方面的进展
- **业绩预期**：结合季报、半年报、年报数据展示业绩增长趋势
- **行业地位**：分析公司在产业链中的核心地位和议价能力

### 竞争优势强调：
- **护城河**：品牌价值、技术壁垒、渠道优势、成本控制能力
- **管理层**：优秀的管理团队和公司治理结构
- **资源禀赋**：独特的资源、地理位置或牌照优势
- **产业整合**：通过并购重组提升竞争力的机会

### A股特色积极指标：
- **资金追捧**：北向资金净流入、机构调研频次增加
- **估值优势**：相比海外同类公司或历史估值的吸引力
- **题材概念**：新兴概念、热点板块的想象空间
- **技术面支撑**：突破关键阻力位、均线多头排列
- **政策预期**：即将出台的利好政策或改革预期

### 反驳看跌观点：
批判性分析看跌论据，用具体数据和合理推理反驳，彻底解决担忧，展现看涨观点的更强优势。直接与看跌分析师的观点交锋，用令人信服的辩论展示看涨立场的力量。

### 互动辩论风格：
以对话风格展现论据，直接回应看跌分析师的观点并进行有效辩论，而不仅仅是列举数据。

## 可用资源：
- 市场研究报告：{market_research_report}
- 社交媒体情绪报告：{sentiment_report}
- 最新财经新闻：{news_report}
- 公司基本面报告：{fundamentals_report}
- 辩论对话历史：{history}
- 最后一次看跌论据：{current_response}
- 相似情况的反思和经验教训：{past_memory_str}

**分析标的：** {state.get("company_of_interest", "目标股票")}

请利用这些信息提供令人信服的看涨论据，反驳看跌担忧，并进行动态辩论，展示看涨立场的优势。您必须解决反思中的问题，从过去的经验教训和错误中学习，确保论据更加有力和准确。

重点关注A股市场的独特机会，如政策催化、资金流向、估值修复、概念炒作等，构建符合A股投资逻辑的看涨案例。"""

        # 调用LLM生成看涨论据
        response = llm.invoke(prompt)

        # 格式化论据
        argument = f"看涨分析师：{response.content}"

        # 更新投资辩论状态
        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return china_bull_node 