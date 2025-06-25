# TradingAgents/graph/china_reflection.py

from typing import Dict, Any


class ChinaReflector:
    """处理中国A股交易决策的反思和记忆更新。"""

    def __init__(self, quick_thinking_llm):
        """使用LLM初始化反思器。"""
        self.quick_thinking_llm = quick_thinking_llm
        self.reflection_system_prompt = self._get_china_reflection_prompt()

    def _get_china_reflection_prompt(self) -> str:
        """获取中国A股反思的系统提示。"""
        return """
你是一位专业的中国A股投资分析专家，负责回顾交易决策/分析并提供全面的、逐步的分析。
你的目标是提供对投资决策的详细见解，并突出改进机会，严格遵循以下指导原则：

1. 推理分析：
   - 对于每个交易决策，判断其是否正确。正确的决策会带来收益增加，错误的决策则相反。
   - 分析每个成功或错误的促成因素，考虑：
     - 技术指标分析（KDJ、MACD、RSI等）
     - 涨跌停板影响和量价关系
     - 政策分析和监管环境变化
     - 新闻事件影响（尤其是政策导向类新闻）
     - 市场情绪和资金流向分析
     - 基本面数据分析（适应中国会计准则）
     - 北向资金和机构资金动向
     - 行业板块轮动和题材热点
     - 评估每个因素在决策过程中的重要性权重

2. 改进建议：
   - 对于任何错误决策，提出修正建议以最大化收益
   - 提供详细的纠正措施或改进清单，包括具体建议（例如，在特定日期将决策从持有改为买入）
   - 特别关注中国A股市场特有的风险点：
     * T+1交易制度的影响
     * 涨跌停板限制下的操作策略
     * 政策敏感性和突发事件应对
     * 散户情绪化交易的影响

3. 总结经验：
   - 总结从成功和错误中学到的经验教训
   - 强调这些经验如何适用于未来的交易场景
   - 在相似情况之间建立联系，以应用所获得的知识
   - 特别关注中国A股市场的周期性特征

4. 关键洞察：
   - 从总结中提取关键见解，形成不超过1000个字符的简洁句子
   - 确保压缩后的句子捕捉到经验教训和推理的精髓，便于参考

严格遵循这些指导原则，确保你的输出详细、准确且可操作。你还将获得从价格走势、技术指标、新闻和情绪角度对市场的客观描述，为你的分析提供更多背景信息。
"""

    def _extract_china_current_situation(self, current_state: Dict[str, Any]) -> str:
        """从状态中提取当前中国A股市场情况。"""
        curr_market_report = current_state.get("market_report", "")
        curr_news_report = current_state.get("news_report", "")
        curr_fundamentals_report = current_state.get("fundamentals_report", "")

        return f"市场技术分析报告：\n{curr_market_report}\n\n新闻政策分析报告：\n{curr_news_report}\n\n基本面分析报告：\n{curr_fundamentals_report}"

    def _reflect_on_china_component(
        self, component_type: str, report: str, situation: str, returns_losses
    ) -> str:
        """为中国A股组件生成反思。"""
        messages = [
            ("system", self.reflection_system_prompt),
            (
                "human",
                f"收益情况：{returns_losses}\n\n分析/决策：{report}\n\n客观市场报告参考：{situation}",
            ),
        ]

        result = self.quick_thinking_llm.invoke(messages).content
        return result

    def reflect_china_bull_researcher(self, current_state, returns_losses, bull_memory):
        """反思多头研究员的分析并更新记忆。"""
        situation = self._extract_china_current_situation(current_state)
        bull_debate_history = current_state.get("investment_debate_state", {}).get("bull_history", "")

        result = self._reflect_on_china_component(
            "多头研究员", bull_debate_history, situation, returns_losses
        )
        bull_memory.add_situations([(situation, result)])

    def reflect_china_bear_researcher(self, current_state, returns_losses, bear_memory):
        """反思空头研究员的分析并更新记忆。"""
        situation = self._extract_china_current_situation(current_state)
        bear_debate_history = current_state.get("investment_debate_state", {}).get("bear_history", "")

        result = self._reflect_on_china_component(
            "空头研究员", bear_debate_history, situation, returns_losses
        )
        bear_memory.add_situations([(situation, result)])

    def reflect_china_trader(self, current_state, returns_losses, trader_memory):
        """反思交易员的决策并更新记忆。"""
        situation = self._extract_china_current_situation(current_state)
        trader_decision = current_state.get("trader_investment_plan", "")

        result = self._reflect_on_china_component(
            "交易员", trader_decision, situation, returns_losses
        )
        trader_memory.add_situations([(situation, result)])

    def reflect_china_invest_judge(self, current_state, returns_losses, invest_judge_memory):
        """反思投资总监的决策并更新记忆。"""
        situation = self._extract_china_current_situation(current_state)
        judge_decision = current_state.get("investment_debate_state", {}).get("judge_decision", "")

        result = self._reflect_on_china_component(
            "投资总监", judge_decision, situation, returns_losses
        )
        invest_judge_memory.add_situations([(situation, result)])

    def reflect_china_risk_manager(self, current_state, returns_losses, risk_manager_memory):
        """反思风险总监的决策并更新记忆。"""
        situation = self._extract_china_current_situation(current_state)
        judge_decision = current_state.get("risk_debate_state", {}).get("judge_decision", "")

        result = self._reflect_on_china_component(
            "风险总监", judge_decision, situation, returns_losses
        )
        risk_manager_memory.add_situations([(situation, result)])

    def generate_performance_summary(self, historical_states: list, total_returns: float) -> str:
        """生成绩效总结报告。"""
        messages = [
            (
                "system",
                """请根据历史交易状态和总收益，生成一份中国A股投资绩效总结报告。

报告应包括：
1. 整体绩效评估
2. 成功交易的共同特征
3. 失败交易的教训总结
4. 适合中国A股市场的策略建议
5. 风险管理改进建议

请用中文输出详细的分析报告。""",
            ),
            (
                "human",
                f"历史交易状态数量：{len(historical_states)}\n总收益率：{total_returns}%"
            ),
        ]

        return self.quick_thinking_llm.invoke(messages).content 