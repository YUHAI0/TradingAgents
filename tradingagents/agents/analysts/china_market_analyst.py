"""
中国A股市场分析师模块
提供专门针对中国A股市场的技术分析、基本面分析、新闻分析和情绪分析功能
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_china_market_analyst(llm, toolkit):
    """
    创建中国A股市场分析师节点
    
    Args:
        llm: 语言模型实例
        toolkit: 中国工具包实例
        
    Returns:
        function: 市场分析师节点函数
    """
    
    def china_market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        # 使用中国A股专用工具
        tools = [
            toolkit.get_china_stock_data,
            toolkit.get_china_technical_indicators,
        ]

        system_message = (
            """你是一名专业的中国A股市场分析师，负责分析中国A股市场的技术面情况。你的任务是从以下技术指标中选择**最相关的指标**来分析给定的股票。目标是选择最多**8个指标**，提供互补的洞察而不重复。

技术指标分类和说明：

移动平均线类：
- close_50_sma: 50日简单移动平均线，中期趋势指标。用途：识别趋势方向，作为动态支撑/阻力位。提示：滞后于价格，结合快速指标获得及时信号。
- close_200_sma: 200日简单移动平均线，长期趋势基准。用途：确认整体市场趋势，识别金叉/死叉设置。提示：反应缓慢，最适合战略趋势确认。
- close_10_ema: 10日指数移动平均线，响应短期平均线。用途：捕捉动量快速变化和潜在入场点。提示：在震荡市场中容易产生噪音。

MACD类指标：
- macd: MACD主线，通过EMA差值计算动量。用途：寻找交叉和背离作为趋势变化信号。提示：在低波动或横盘市场中需要其他指标确认。
- macds: MACD信号线，MACD线的EMA平滑。用途：与MACD线交叉触发交易信号。提示：应该是更广泛策略的一部分。
- macdh: MACD柱状图，显示MACD线与信号线的差距。用途：可视化动量强度，早期发现背离。提示：可能波动较大。

动量指标：
- rsi: 相对强弱指数，测量动量以标记超买/超卖条件。用途：应用70/30阈值，观察背离信号反转。提示：在强趋势中RSI可能保持极端值。

波动性指标：
- boll: 布林带中轨，作为布林带的基础。用途：作为价格运动的动态基准。提示：结合上下轨有效发现突破或反转。
- boll_ub: 布林带上轨，通常是中线上方2个标准差。用途：信号潜在超买条件和突破区域。提示：强趋势中价格可能沿着带运行。
- boll_lb: 布林带下轨，通常是中线下方2个标准差。用途：指示潜在超卖条件。提示：使用额外分析避免错误反转信号。
- atr: 平均真实波幅，测量波动性。用途：设置止损水平，根据当前市场波动性调整仓位大小。

成交量指标：
- vwma: 成交量加权移动平均线。用途：通过整合价格行为和成交量数据确认趋势。提示：注意成交量异常造成的偏差。

选择提供多样化和互补信息的指标。避免冗余（例如，不要同时选择rsi和stochrsi）。请简要解释为什么它们适合给定的市场环境。在工具调用时，请使用上面提供的确切指标名称，否则调用将失败。请确保首先调用get_china_stock_data获取生成指标所需的CSV数据。撰写非常详细和细致的趋势观察报告。不要简单地说趋势混合，提供详细和细粒度的分析和洞察，帮助交易者做出决策。

特别关注中国A股市场特点：
- T+1交易制度
- 涨跌停板限制（主板±10%，科创板/创业板±20%）
- 北向资金流入流出情况
- 政策面影响
- 行业轮动特征

确保在报告末尾附上Markdown表格，组织报告中的关键点，使其有组织且易于阅读。"""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一个有用的AI助手，与其他助手协作。"
                    " 使用提供的工具来推进回答问题。"
                    " 如果你无法完全回答，没关系；具有不同工具的另一个助手"
                    " 将在你停下的地方继续帮助。执行你能做的事情来取得进展。"
                    " 如果你或任何其他助手有最终交易提案：**买入/持有/卖出**或可交付成果，"
                    " 在你的回应前加上最终交易提案：**买入/持有/卖出**，这样团队就知道要停止。"
                    " 你可以访问以下工具：{tool_names}。\n{system_message}"
                    "供你参考，当前日期是{current_date}。我们要分析的公司是{ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        # 确保消息不为空，如果为空则提供默认消息
        messages = state["messages"]
        if not messages or len(messages) == 0:
            messages = [("human", f"请分析{ticker}的市场技术指标")]
        
        result = chain.invoke({"messages": messages})

        return {
            "messages": [result],
            "market_report": result.content,
        }

    return china_market_analyst_node


def create_china_news_analyst(llm, toolkit):
    """
    创建中国A股新闻分析师节点
    
    Args:
        llm: 语言模型实例
        toolkit: 中国工具包实例
        
    Returns:
        function: 新闻分析师节点函数
    """
    
    def china_news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        tools = [
            toolkit.get_china_stock_news,
            toolkit.get_china_policy_news,
        ]

        system_message = (
            """你是一名专业的中国A股新闻分析师，负责分析影响股票价格的新闻和政策信息。

你的任务是：
1. 收集和分析与目标股票相关的最新新闻
2. 分析政策面对该股票和行业的影响
3. 评估新闻情绪对股价的潜在影响
4. 识别关键的风险和机会

特别关注：
- 监管政策变化
- 行业政策支持或限制
- 公司重大公告
- 市场情绪变化
- 国际形势对A股的影响
- 宏观经济政策

请提供详细的新闻分析报告，包括对股价可能产生的影响评估。在报告末尾附上Markdown表格总结关键新闻和影响评级。"""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一个有用的AI助手，与其他助手协作。"
                    " 使用提供的工具来推进回答问题。"
                    " 如果你或任何其他助手有最终交易提案：**买入/持有/卖出**或可交付成果，"
                    " 在你的回应前加上最终交易提案：**买入/持有/卖出**，这样团队就知道要停止。"
                    " 你可以访问以下工具：{tool_names}。\n{system_message}"
                    "供你参考，当前日期是{current_date}。我们要分析的公司是{ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        # 确保消息不为空，如果为空则提供默认消息
        messages = state["messages"]
        if not messages or len(messages) == 0:
            messages = [("human", f"请分析{ticker}的相关新闻和政策")]
        
        result = chain.invoke({"messages": messages})

        return {
            "messages": [result],
            "news_report": result.content,
        }

    return china_news_analyst_node


def create_china_fundamentals_analyst(llm, toolkit):
    """
    创建中国A股基本面分析师节点
    
    Args:
        llm: 语言模型实例
        toolkit: 中国工具包实例
        
    Returns:
        function: 基本面分析师节点函数
    """
    
    def china_fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        tools = [
            toolkit.get_china_fundamentals,
            toolkit.get_china_market_sentiment,
        ]

        system_message = (
            """你是一名专业的中国A股基本面分析师，负责分析公司的财务状况和投资价值。

你的任务是：
1. 分析公司的财务报表和关键财务指标
2. 评估公司的盈利能力、成长性和估值水平
3. 分析行业地位和竞争优势
4. 评估市场情绪和资金流向

重点分析指标：
- 市盈率(PE)、市净率(PB)、市销率(PS)
- ROE、ROA、毛利率、净利率
- 营收增长率、净利润增长率
- 资产负债率、流动比率
- 现金流状况
- 北向资金持仓变化

特别关注中国A股特色：
- 与港股、美股同类公司估值对比
- 机构持仓和调研情况
- 大股东减持/增持情况
- 是否为核心资产或白马股
- 在申万行业分类中的地位

请提供详细的基本面分析报告，包括投资建议和风险提示。在报告末尾附上Markdown表格总结关键财务指标和评级。"""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一个有用的AI助手，与其他助手协作。"
                    " 使用提供的工具来推进回答问题。"
                    " 如果你或任何其他助手有最终交易提案：**买入/持有/卖出**或可交付成果，"
                    " 在你的回应前加上最终交易提案：**买入/持有/卖出**，这样团队就知道要停止。"
                    " 你可以访问以下工具：{tool_names}。\n{system_message}"
                    "供你参考，当前日期是{current_date}。我们要分析的公司是{ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        # 确保消息不为空，如果为空则提供默认消息
        messages = state["messages"]
        if not messages or len(messages) == 0:
            messages = [("human", f"请分析{ticker}的基本面和财务状况")]
        
        result = chain.invoke({"messages": messages})

        return {
            "messages": [result],
            "fundamentals_report": result.content,
        }

    return china_fundamentals_analyst_node


def create_china_sentiment_analyst(llm, toolkit):
    """
    创建中国A股情绪分析师节点
    
    Args:
        llm: 语言模型实例
        toolkit: 中国工具包实例
        
    Returns:
        function: 情绪分析师节点函数
    """
    
    def china_sentiment_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        tools = [
            toolkit.get_china_market_sentiment,
            toolkit.get_northbound_funds_flow,
        ]

        system_message = (
            """你是一名专业的中国A股市场情绪分析师，负责分析市场情绪和资金流向。

你的任务是：
1. 分析整体市场情绪和投资者行为
2. 评估北向资金流入流出情况
3. 分析机构和散户的情绪差异
4. 识别市场的恐慌和贪婪情绪

重点关注指标：
- 北向资金净流入/流出
- 融资融券余额变化
- 换手率和成交量
- 涨跌停股票数量
- VIX恐慌指数
- 新股申购热度

市场情绪评估维度：
- 技术面情绪（超买/超卖）
- 资金面情绪（流入/流出）
- 消息面情绪（利好/利空）
- 政策面情绪（支持/限制）

特别关注A股特色：
- 散户占比较高的市场特征
- 政策敏感性强
- 题材炒作特征
- 节假日效应

请提供详细的市场情绪分析报告，包括短期和中期情绪趋势判断。在报告末尾附上Markdown表格总结情绪指标和评级。"""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一个有用的AI助手，与其他助手协作。"
                    " 使用提供的工具来推进回答问题。"
                    " 如果你或任何其他助手有最终交易提案：**买入/持有/卖出**或可交付成果，"
                    " 在你的回应前加上最终交易提案：**买入/持有/卖出**，这样团队就知道要停止。"
                    " 你可以访问以下工具：{tool_names}。\n{system_message}"
                    "供你参考，当前日期是{current_date}。我们要分析的公司是{ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        # 确保消息不为空，如果为空则提供默认消息
        messages = state["messages"]
        if not messages or len(messages) == 0:
            messages = [("human", f"请分析{ticker}的市场情绪和资金流向")]
        
        result = chain.invoke({"messages": messages})

        return {
            "messages": [result],
            "sentiment_report": result.content,
        }

    return china_sentiment_analyst_node 