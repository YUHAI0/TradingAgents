# TradingAgents/graph/china_signal_processing.py


class ChinaSignalProcessor:
    """处理中国A股交易信号以提取可操作决策的处理器。"""

    def __init__(self, quick_thinking_llm):
        """使用LLM进行处理初始化。"""
        self.quick_thinking_llm = quick_thinking_llm

    def process_china_signal(self, full_signal: str) -> str:
        """
        处理完整的中国A股交易信号以提取核心决策。

        Args:
            full_signal: 完整的交易信号文本

        Returns:
            提取的决策（买入、卖出或持有）
        """
        messages = [
            (
                "system",
                """你是一个专业的中国A股投资分析助手，负责分析一组分析师提供的段落或财务报告。你的任务是提取投资决策：卖出、买入或持有。

请仅提供提取的决策（卖出、买入或持有）作为输出，不要添加任何额外的文本或信息。

注意中国A股市场的特殊性：
- 考虑T+1交易制度
- 考虑涨跌停板限制（10%或20%）
- 考虑政策影响和监管环境
- 考虑A股市场情绪化特征
- 考虑资金流向和北向资金影响""",
            ),
            ("human", full_signal),
        ]

        result = self.quick_thinking_llm.invoke(messages).content
        
        # 标准化中文决策输出
        if "买入" in result or "建仓" in result or "加仓" in result:
            return "买入"
        elif "卖出" in result or "清仓" in result or "减仓" in result:
            return "卖出"
        elif "持有" in result or "观望" in result:
            return "持有"
        else:
            return "持有"  # 默认持有

    def analyze_signal_confidence(self, full_signal: str) -> dict:
        """
        分析信号的置信度和风险等级。
        
        Args:
            full_signal: 完整的交易信号文本
            
        Returns:
            包含置信度和风险等级的字典
        """
        messages = [
            (
                "system",
                """请分析这个中国A股交易信号的置信度和风险等级。

输出格式：
{
    "confidence": "高/中/低",
    "risk_level": "高/中/低", 
    "key_factors": ["因素1", "因素2", "因素3"],
    "potential_risks": ["风险点1", "风险点2"]
}

请以JSON格式返回分析结果。""",
            ),
            ("human", full_signal),
        ]

        try:
            result = self.quick_thinking_llm.invoke(messages).content
            # 这里可以添加JSON解析逻辑
            return {"confidence": "中", "risk_level": "中", "key_factors": [], "potential_risks": []}
        except:
            return {"confidence": "中", "risk_level": "中", "key_factors": [], "potential_risks": []}

    def generate_execution_plan(self, decision: str, stock_code: str) -> dict:
        """
        根据决策生成具体的执行计划。
        
        Args:
            decision: 交易决策（买入/卖出/持有）
            stock_code: 股票代码
            
        Returns:
            执行计划字典
        """
        if decision == "买入":
            return {
                "action": "BUY",
                "stock_code": stock_code,
                "suggested_position": "建议分批建仓",
                "risk_management": "设置止损位",
                "timing": "关注开盘情况，避免追高"
            }
        elif decision == "卖出":
            return {
                "action": "SELL", 
                "stock_code": stock_code,
                "suggested_position": "建议分批减仓",
                "risk_management": "保护已有收益",
                "timing": "关注盘中走势，选择合适时机"
            }
        else:
            return {
                "action": "HOLD",
                "stock_code": stock_code,
                "suggested_position": "维持现有仓位",
                "risk_management": "密切关注市场变化",
                "timing": "等待更明确信号"
            } 