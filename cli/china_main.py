#!/usr/bin/env python3
"""
中国A股TradingAgents CLI
适配中国A股市场和国产LLM的命令行界面
"""

from typing import Optional
import datetime
import sys
import typer
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.columns import Columns
from rich.markdown import Markdown
from rich.layout import Layout
from rich.text import Text
from rich.live import Live
from rich.table import Table
from collections import deque
import time
from rich.tree import Tree
from rich import box
from rich.align import Align
from rich.rule import Rule
import os

# 导入中国版本的模块
# 直接导入中国版本的图，避免通过__init__.py导入时的NumPy问题
try:
    from tradingagents.graph.china_trading_graph import ChinaTradingAgentsGraph
except ImportError as e:
    console.print(f"[red]无法导入ChinaTradingAgentsGraph: {e}[/red]")
    sys.exit(1)
from tradingagents.china_config import CHINA_DEFAULT_CONFIG
from cli.china_models import ChinaAnalystType
from cli.china_utils import *

console = Console()

app = typer.Typer(
    name="中国A股TradingAgents",
    help="中国A股TradingAgents CLI: 多代理LLM金融交易框架",
    add_completion=True,  # 启用shell补全
)


# 创建消息缓冲区来存储最近的消息，最大长度为100
class ChinaMessageBuffer:
    def __init__(self, max_length=100):
        self.messages = deque(maxlen=max_length)
        self.tool_calls = deque(maxlen=max_length)
        self.current_report = None
        self.final_report = None  # 存储完整的最终报告
        self.agent_status = {
            # 分析师团队
            "市场技术分析师": "pending",
            "社交情绪分析师": "pending",
            "新闻分析师": "pending", 
            "基本面分析师": "pending",
            # 研究团队
            "看涨研究员": "pending",
            "看跌研究员": "pending",
            "研究经理": "pending",
            # 交易团队
            "交易员": "pending",
            # 风险管理团队
            "激进分析师": "pending",
            "中性分析师": "pending",
            "保守分析师": "pending",
            # 投资组合管理团队
            "投资组合经理": "pending",
        }
        self.current_agent = None
        self.report_sections = {
            "market_report": None,
            "sentiment_report": None,
            "news_report": None,
            "fundamentals_report": None,
            "investment_plan": None,
            "trader_investment_plan": None,
            "final_trade_decision": None,
        }

    def add_message(self, message_type, content):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.messages.append((timestamp, message_type, content))

    def add_tool_call(self, tool_name, args):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.tool_calls.append((timestamp, tool_name, args))

    def update_agent_status(self, agent, status):
        if agent in self.agent_status:
            self.agent_status[agent] = status
            self.current_agent = agent

    def update_report_section(self, section_name, content):
        if section_name in self.report_sections:
            self.report_sections[section_name] = content
            self._update_current_report()

    def _update_current_report(self):
        # 对于面板显示，只显示最近更新的部分
        latest_section = None
        latest_content = None

        # 找到最近更新的部分
        for section, content in self.report_sections.items():
            if content is not None:
                latest_section = section
                latest_content = content

        if latest_section and latest_content:
            # 格式化当前部分用于显示
            section_titles = {
                "market_report": "市场技术分析",
                "sentiment_report": "社交情绪分析",
                "news_report": "新闻分析",
                "fundamentals_report": "基本面分析",
                "investment_plan": "研究团队决策",
                "trader_investment_plan": "交易团队计划",
                "final_trade_decision": "投资组合管理决策",
            }
            self.current_report = (
                f"### {section_titles[latest_section]}\n{latest_content}"
            )

        # 更新最终完整报告
        self._update_final_report()

    def _update_final_report(self):
        report_parts = []

        # 分析师团队报告
        if any(
            self.report_sections[section]
            for section in [
                "market_report",
                "sentiment_report",
                "news_report", 
                "fundamentals_report",
            ]
        ):
            report_parts.append("## 分析师团队报告")
            if self.report_sections["market_report"]:
                report_parts.append(
                    f"### 市场技术分析\n{self.report_sections['market_report']}"
                )
            if self.report_sections["sentiment_report"]:
                report_parts.append(
                    f"### 社交情绪分析\n{self.report_sections['sentiment_report']}"
                )
            if self.report_sections["news_report"]:
                report_parts.append(
                    f"### 新闻分析\n{self.report_sections['news_report']}"
                )
            if self.report_sections["fundamentals_report"]:
                report_parts.append(
                    f"### 基本面分析\n{self.report_sections['fundamentals_report']}"
                )

        # 研究团队报告
        if self.report_sections["investment_plan"]:
            report_parts.append("## 研究团队决策")
            report_parts.append(f"{self.report_sections['investment_plan']}")

        # 交易团队报告
        if self.report_sections["trader_investment_plan"]:
            report_parts.append("## 交易团队计划")
            report_parts.append(f"{self.report_sections['trader_investment_plan']}")

        # 投资组合管理决策
        if self.report_sections["final_trade_decision"]:
            report_parts.append("## 投资组合管理决策")
            report_parts.append(f"{self.report_sections['final_trade_decision']}")

        self.final_report = "\n\n".join(report_parts) if report_parts else None


message_buffer = ChinaMessageBuffer()


def create_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3),
    )
    layout["main"].split_column(
        Layout(name="upper", ratio=3), Layout(name="analysis", ratio=5)
    )
    layout["upper"].split_row(
        Layout(name="progress", ratio=2), Layout(name="messages", ratio=3)
    )
    return layout


def update_display(layout, spinner_text=None):
    # 头部欢迎信息
    layout["header"].update(
        Panel(
            "[bold green]欢迎使用中国A股TradingAgents CLI[/bold green]\n"
            "[dim]© [涛锐研究](https://github.com/TauricResearch)[/dim]",
            title="欢迎使用中国A股TradingAgents",
            border_style="green",
            padding=(1, 2),
            expand=True,
        )
    )

    # 进度面板显示代理状态
    progress_table = Table(
        show_header=True,
        header_style="bold magenta",
        show_footer=False,
        box=box.SIMPLE_HEAD,  # 使用简单的头部水平线
        title=None,  # 移除冗余的进度标题
        padding=(0, 2),  # 添加水平填充
        expand=True,  # 使表格扩展以填充可用空间
    )
    progress_table.add_column("团队", style="cyan", justify="center", width=20)
    progress_table.add_column("代理", style="green", justify="center", width=20)
    progress_table.add_column("状态", style="yellow", justify="center", width=20)

    # 按团队分组代理
    teams = {
        "分析师团队": [
            "市场技术分析师",
            "社交情绪分析师",
            "新闻分析师",
            "基本面分析师",
        ],
        "研究团队": ["看涨研究员", "看跌研究员", "研究经理"],
        "交易团队": ["交易员"],
        "风险管理": ["激进分析师", "中性分析师", "保守分析师"],
        "投资组合管理": ["投资组合经理"],
    }

    for team, agents in teams.items():
        # 添加第一个代理和团队名称
        first_agent = agents[0]
        status = message_buffer.agent_status[first_agent]
        if status == "in_progress":
            spinner = Spinner(
                "dots", text="[blue]进行中[/blue]", style="bold cyan"
            )
            status_cell = spinner
        else:
            status_color = {
                "pending": "yellow",
                "completed": "green",
                "error": "red",
            }.get(status, "white")
            status_chinese = {
                "pending": "等待中",
                "completed": "已完成",
                "error": "错误",
                "in_progress": "进行中"
            }.get(status, status)
            status_cell = f"[{status_color}]{status_chinese}[/{status_color}]"
        progress_table.add_row(team, first_agent, status_cell)

        # 添加团队中的其余代理
        for agent in agents[1:]:
            status = message_buffer.agent_status[agent]
            if status == "in_progress":
                spinner = Spinner(
                    "dots", text="[blue]进行中[/blue]", style="bold cyan"
                )
                status_cell = spinner
            else:
                status_color = {
                    "pending": "yellow",
                    "completed": "green",
                    "error": "red",
                }.get(status, "white")
                status_chinese = {
                    "pending": "等待中",
                    "completed": "已完成",
                    "error": "错误",
                    "in_progress": "进行中"
                }.get(status, status)
                status_cell = f"[{status_color}]{status_chinese}[/{status_color}]"
            progress_table.add_row("", agent, status_cell)

        # 在每个团队后添加水平线
        progress_table.add_row("─" * 20, "─" * 20, "─" * 20, style="dim")

    layout["progress"].update(
        Panel(progress_table, title="进度", border_style="cyan", padding=(1, 2))
    )

    # 消息面板显示最近的消息和工具调用
    messages_table = Table(
        show_header=True,
        header_style="bold magenta",
        show_footer=False,
        expand=True,  # 使表格扩展以填充可用空间
        box=box.MINIMAL,  # 使用最小的框样式以获得更轻的外观
        show_lines=True,  # 保持水平线
        padding=(0, 1),  # 在列之间添加一些填充
    )
    messages_table.add_column("时间", style="cyan", width=8, justify="center")
    messages_table.add_column("类型", style="green", width=10, justify="center")
    messages_table.add_column(
        "内容", style="white", no_wrap=False, ratio=1
    )  # 使内容列扩展

    # 合并工具调用和消息
    all_messages = []

    # 添加工具调用
    for timestamp, tool_name, args in message_buffer.tool_calls:
        # 如果工具调用参数太长，则截断
        if isinstance(args, str) and len(args) > 100:
            args = args[:97] + "..."
        all_messages.append((timestamp, "工具", f"{tool_name}: {args}"))

    # 添加常规消息
    for timestamp, msg_type, content in message_buffer.messages:
        # 将内容转换为字符串（如果还不是）
        content_str = content
        if isinstance(content, list):
            # 处理内容块列表（Anthropic格式）
            text_parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))
                    elif item.get('type') == 'tool_use':
                        text_parts.append(f"[工具: {item.get('name', 'unknown')}]")
                else:
                    text_parts.append(str(item))
            content_str = ' '.join(text_parts)
        elif not isinstance(content_str, str):
            content_str = str(content)
            
        # 如果消息内容太长，则截断
        if len(content_str) > 200:
            content_str = content_str[:197] + "..."
        
        # 翻译消息类型
        msg_type_chinese = {
            "System": "系统",
            "Reasoning": "推理",
            "Analysis": "分析",
            "Tool": "工具"
        }.get(msg_type, msg_type)
        
        all_messages.append((timestamp, msg_type_chinese, content_str))

    # 按时间戳排序
    all_messages.sort(key=lambda x: x[0])

    # 根据可用空间计算我们可以显示多少条消息
    # 从合理的数字开始，根据内容长度进行调整
    max_messages = 12  # 从8增加到12以更好地填充空间

    # 获取适合面板的最后N条消息
    recent_messages = all_messages[-max_messages:]

    # 将消息添加到表格
    for timestamp, msg_type, content in recent_messages:
        # 使用自动换行格式化内容
        wrapped_content = Text(content, overflow="fold")
        messages_table.add_row(timestamp, msg_type, wrapped_content)

    if spinner_text:
        messages_table.add_row("", "旋转器", spinner_text)

    # 添加页脚以指示消息是否被截断
    if len(all_messages) > max_messages:
        messages_table.footer = (
            f"[dim]显示最后{max_messages}条，共{len(all_messages)}条消息[/dim]"
        )

    layout["messages"].update(
        Panel(
            messages_table,
            title="消息与工具",
            border_style="blue",
            padding=(1, 2),
        )
    )

    # 分析面板显示当前报告
    if message_buffer.current_report:
        layout["analysis"].update(
            Panel(
                Markdown(message_buffer.current_report),
                title="当前报告",
                border_style="green",
                padding=(1, 2),
            )
        )
    else:
        layout["analysis"].update(
            Panel(
                "[italic]等待分析报告...[/italic]",
                title="当前报告",
                border_style="green",
                padding=(1, 2),
            )
        )

    # 页脚统计信息
    tool_calls_count = len(message_buffer.tool_calls)
    llm_calls_count = sum(
        1 for _, msg_type, _ in message_buffer.messages if msg_type == "推理"
    )
    reports_count = sum(
        1 for content in message_buffer.report_sections.values() if content is not None
    )

    stats_table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
    stats_table.add_column("统计", justify="center")
    stats_table.add_row(
        f"工具调用: {tool_calls_count} | LLM调用: {llm_calls_count} | 生成报告: {reports_count}"
    )

    layout["footer"].update(Panel(stats_table, border_style="grey50"))


def get_user_selections():
    """在开始分析显示之前获取所有用户选择。"""
    # 显示ASCII艺术欢迎信息
    with open("./cli/static/welcome.txt", "r") as f:
        welcome_ascii = f.read()

    # 创建欢迎框内容
    welcome_content = f"{welcome_ascii}\n"
    welcome_content += "[bold green]中国A股TradingAgents: 多代理LLM金融交易框架 - CLI[/bold green]\n\n"
    welcome_content += "[bold]工作流程步骤:[/bold]\n"
    welcome_content += "I. 分析师团队 → II. 研究团队 → III. 交易员 → IV. 风险管理 → V. 投资组合管理\n\n"
    welcome_content += (
        "[dim]由 [涛锐研究](https://github.com/TauricResearch) 构建[/dim]"
    )

    # 创建并居中欢迎框
    welcome_box = Panel(
        welcome_content,
        border_style="green",
        padding=(1, 2),
        title="欢迎使用中国A股TradingAgents",
        subtitle="多代理LLM金融交易框架",
    )
    console.print(Align.center(welcome_box))
    console.print()  # 在欢迎框后添加空行

    # 为每个步骤创建一个框式问卷
    def create_question_box(title, prompt, default=None):
        box_content = f"[bold]{title}[/bold]\n"
        box_content += f"[dim]{prompt}[/dim]"
        if default:
            box_content += f"\n[dim]默认值: {default}[/dim]"
        return Panel(box_content, border_style="blue", padding=(1, 2))

    # 步骤1: 股票代码
    console.print(
        create_question_box(
            "步骤1: 股票代码", "输入要分析的中国A股代码", "000001"
        )
    )
    selected_ticker = get_ticker()

    # 步骤2: 分析日期
    default_date = datetime.datetime.now().strftime("%Y-%m-%d")
    console.print(
        create_question_box(
            "步骤2: 分析日期",
            "输入分析日期 (YYYY-MM-DD)",
            default_date,
        )
    )
    analysis_date = get_analysis_date()
    
    # 步骤3: 选择分析师
    console.print(
        create_question_box(
            "步骤3: 分析师团队", "为分析选择您的LLM分析师代理"
        )
    )
    selected_analysts = select_china_analysts()
    console.print(
        f"[green]已选择分析师:[/green] {', '.join(analyst.value for analyst in selected_analysts)}"
    )

    # 步骤4: 研究深度
    console.print(
        create_question_box(
            "步骤4: 研究深度", "选择您的研究深度级别"
        )
    )
    selected_research_depth = select_research_depth()

    # 步骤5: 中国LLM后端
    console.print(
        create_question_box(
            "步骤5: 中国LLM后端", "选择要使用的中国LLM服务"
        )
    )
    selected_llm_provider, backend_url = select_china_llm_provider()
    
    # 步骤6: 思考代理
    console.print(
        create_question_box(
            "步骤6: 思考代理", "为分析选择您的思考代理"
        )
    )
    selected_shallow_thinker = select_shallow_thinking_agent(selected_llm_provider)
    selected_deep_thinker = select_deep_thinking_agent(selected_llm_provider)
    
    return {
        "ticker": selected_ticker,
        "analysis_date": analysis_date,
        "analysts": selected_analysts,
        "research_depth": selected_research_depth,
        "llm_provider": selected_llm_provider.lower(),
        "backend_url": backend_url,
        "shallow_thinker": selected_shallow_thinker,
        "deep_thinker": selected_deep_thinker,
    }


def get_ticker():
    """从用户输入获取股票代码。"""
    while True:
        ticker = typer.prompt("", default="000001")
        if validate_china_stock_code(ticker):
            return format_china_stock_code(ticker)
        else:
            console.print("[red]错误: 无效的中国A股代码格式。请使用6位数字代码（如000001、600000）[/red]")


def get_analysis_date():
    """从用户输入获取分析日期。"""
    while True:
        date_str = typer.prompt(
            "", default=datetime.datetime.now().strftime("%Y-%m-%d")
        )
        try:
            # 验证日期格式并确保不是未来日期
            analysis_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            if analysis_date.date() > datetime.datetime.now().date():
                console.print("[red]错误: 分析日期不能是未来日期[/red]")
                continue
            return date_str
        except ValueError:
            console.print(
                "[red]错误: 无效的日期格式。请使用YYYY-MM-DD格式[/red]"
            )


def display_complete_report(final_state):
    """显示基于团队的完整分析报告面板。"""
    console.print("\n[bold green]完整分析报告[/bold green]\n")

    # I. 分析师团队报告
    analyst_reports = []

    # 市场技术分析师报告
    if final_state.get("market_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["market_report"]),
                title="市场技术分析师",
                border_style="blue",
                padding=(1, 2),
            )
        )

    # 社交情绪分析师报告
    if final_state.get("sentiment_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["sentiment_report"]),
                title="社交情绪分析师",
                border_style="blue",
                padding=(1, 2),
            )
        )

    # 新闻分析师报告
    if final_state.get("news_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["news_report"]),
                title="新闻分析师",
                border_style="blue",
                padding=(1, 2),
            )
        )

    # 基本面分析师报告
    if final_state.get("fundamentals_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["fundamentals_report"]),
                title="基本面分析师",
                border_style="blue",
                padding=(1, 2),
            )
        )

    if analyst_reports:
        console.print(
            Panel(
                Columns(analyst_reports, equal=True, expand=True),
                title="I. 分析师团队报告",
                border_style="cyan",
                padding=(1, 2),
            )
        )

    # II. 研究团队报告
    if final_state.get("investment_debate_state"):
        research_reports = []
        debate_state = final_state["investment_debate_state"]

        # 看涨研究员分析
        if debate_state.get("bull_history"):
            research_reports.append(
                Panel(
                    Markdown(debate_state["bull_history"]),
                    title="看涨研究员",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # 看跌研究员分析
        if debate_state.get("bear_history"):
            research_reports.append(
                Panel(
                    Markdown(debate_state["bear_history"]),
                    title="看跌研究员",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # 研究经理决策
        if debate_state.get("judge_decision"):
            research_reports.append(
                Panel(
                    Markdown(debate_state["judge_decision"]),
                    title="研究经理",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        if research_reports:
            console.print(
                Panel(
                    Columns(research_reports, equal=True, expand=True),
                    title="II. 研究团队决策",
                    border_style="magenta",
                    padding=(1, 2),
                )
            )

    # III. 交易团队报告
    if final_state.get("trader_investment_plan"):
        console.print(
            Panel(
                Panel(
                    Markdown(final_state["trader_investment_plan"]),
                    title="交易员",
                    border_style="blue",
                    padding=(1, 2),
                ),
                title="III. 交易团队计划",
                border_style="yellow",
                padding=(1, 2),
            )
        )

    # IV. 风险管理团队报告
    if final_state.get("risk_debate_state"):
        risk_reports = []
        risk_state = final_state["risk_debate_state"]

        # 激进（风险）分析师分析
        if risk_state.get("risky_history"):
            risk_reports.append(
                Panel(
                    Markdown(risk_state["risky_history"]),
                    title="激进分析师",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # 保守（安全）分析师分析
        if risk_state.get("safe_history"):
            risk_reports.append(
                Panel(
                    Markdown(risk_state["safe_history"]),
                    title="保守分析师",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # 中性分析师分析
        if risk_state.get("neutral_history"):
            risk_reports.append(
                Panel(
                    Markdown(risk_state["neutral_history"]),
                    title="中性分析师",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        if risk_reports:
            console.print(
                Panel(
                    Columns(risk_reports, equal=True, expand=True),
                    title="IV. 风险管理团队决策",
                    border_style="red",
                    padding=(1, 2),
                )
            )

        # V. 投资组合经理决策
        if risk_state.get("judge_decision"):
            console.print(
                Panel(
                    Panel(
                        Markdown(risk_state["judge_decision"]),
                        title="投资组合经理",
                        border_style="blue",
                        padding=(1, 2),
                    ),
                    title="V. 投资组合经理决策",
                    border_style="green",
                    padding=(1, 2),
                )
            )


def update_research_team_status(status):
    """更新所有研究团队成员和交易员的状态。"""
    research_team = ["看涨研究员", "看跌研究员", "研究经理", "交易员"]
    for agent in research_team:
        message_buffer.update_agent_status(agent, status)

def extract_content_string(content):
    """从各种消息格式中提取字符串内容。"""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # 处理Anthropic的列表格式
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    text_parts.append(item.get('text', ''))
                elif item.get('type') == 'tool_use':
                    text_parts.append(f"[工具: {item.get('name', 'unknown')}]")
            else:
                text_parts.append(str(item))
        return ' '.join(text_parts)
    else:
        return str(content)

def save_final_report(final_state, selections):
    """保存最终分析报告到results目录"""
    try:
        # 确保results目录存在
        results_dir = "results"
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
            print(f"✅ [调试] 创建results目录: {results_dir}")
        
        # 生成文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{selections['ticker']}_{selections['analysis_date'].replace('-', '')}_{timestamp}_china_cli_report.md"
        filepath = os.path.join(results_dir, filename)
        
        # 生成完整的markdown报告
        report_content = generate_complete_markdown_report(final_state, selections)
        
        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ [调试] 最终分析报告已保存到: {filepath}")
        console.print(f"\n[bold green]📄 最终分析报告已保存到: {filepath}[/bold green]")
        
        return filepath
        
    except Exception as e:
        print(f"❌ [调试] 保存报告失败: {e}")
        console.print(f"[red]保存报告失败: {e}[/red]")
        return None

def generate_complete_markdown_report(final_state, selections):
    """生成完整的markdown格式分析报告"""
    
    # 报告头部
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"""# 中国A股TradingAgents分析报告

## 基本信息
- **股票代码**: {selections['ticker']}
- **分析日期**: {selections['analysis_date']}
- **报告生成时间**: {timestamp}
- **选择的分析师**: {', '.join(analyst.value for analyst in selections['analysts'])}
- **LLM提供商**: {selections['llm_provider']}
- **研究深度**: {selections['research_depth']}轮

---

"""

    # I. 分析师团队报告
    analyst_sections = []
    
    if final_state.get("market_report"):
        analyst_sections.append(f"""### 📈 市场技术分析师报告
{final_state["market_report"]}
""")

    if final_state.get("sentiment_report"):
        analyst_sections.append(f"""### 😊 社交情绪分析师报告
{final_state["sentiment_report"]}
""")

    if final_state.get("news_report"):
        analyst_sections.append(f"""### 📰 新闻分析师报告
{final_state["news_report"]}
""")

    if final_state.get("fundamentals_report"):
        analyst_sections.append(f"""### 💰 基本面分析师报告
{final_state["fundamentals_report"]}
""")

    if analyst_sections:
        report += "## I. 分析师团队报告\n\n"
        report += "\n".join(analyst_sections)
        report += "\n---\n\n"

    # II. 研究团队决策
    if final_state.get("investment_debate_state"):
        debate_state = final_state["investment_debate_state"]
        report += "## II. 研究团队决策\n\n"
        
        if debate_state.get("bull_history"):
            report += f"""### 🐂 看涨研究员分析
{debate_state["bull_history"]}

"""

        if debate_state.get("bear_history"):
            report += f"""### 🐻 看跌研究员分析
{debate_state["bear_history"]}

"""

        if debate_state.get("judge_decision"):
            report += f"""### 👨‍💼 研究经理决策
{debate_state["judge_decision"]}

"""
        
        report += "---\n\n"

    # III. 交易团队计划
    if final_state.get("trader_investment_plan"):
        report += f"""## III. 交易团队计划

### 💼 交易员计划
{final_state["trader_investment_plan"]}

---

"""

    # IV. 风险管理团队决策
    if final_state.get("risk_debate_state"):
        risk_state = final_state["risk_debate_state"]
        report += "## IV. 风险管理团队决策\n\n"
        
        if risk_state.get("risky_history"):
            report += f"""### ⚡ 激进分析师观点
{risk_state["risky_history"]}

"""

        if risk_state.get("safe_history"):
            report += f"""### 🛡️ 保守分析师观点
{risk_state["safe_history"]}

"""

        if risk_state.get("neutral_history"):
            report += f"""### ⚖️ 中性分析师观点
{risk_state["neutral_history"]}

"""
        
        report += "---\n\n"

    # V. 投资组合经理最终决策
    final_decision = None
    if final_state.get("final_trade_decision"):
        final_decision = final_state["final_trade_decision"]
    elif final_state.get("risk_debate_state", {}).get("judge_decision"):
        final_decision = final_state["risk_debate_state"]["judge_decision"]
    
    if final_decision:
        report += f"""## V. 投资组合经理最终决策

### 🎯 最终投资决策
{final_decision}

---

"""

    # 报告尾部
    report += f"""## 报告说明

本报告由中国A股TradingAgents系统生成，采用多代理协作模式：
1. **分析师团队**：负责技术面、基本面、新闻面、情绪面的专业分析
2. **研究团队**：包含看涨/看跌研究员的辩论和研究经理的综合判断
3. **交易团队**：基于研究结果制定具体的交易计划
4. **风险管理团队**：从不同风险偏好角度评估投资方案
5. **投资组合经理**：做出最终的投资决策

**风险提示**：本报告仅供参考，不构成投资建议。投资有风险，决策需谨慎。

---
*报告生成时间: {timestamp}*
*系统版本: 中国A股TradingAgents CLI v1.0*
"""

    return report

def run_analysis():
    # 首先获取所有用户选择
    print("🔍 [调试] 开始获取用户选择...")
    try:
        selections = get_user_selections()
        print(f"✅ [调试] 用户选择完成: {selections}")
    except Exception as e:
        print(f"❌ [调试] 获取用户选择失败: {e}")
        return
    
    # 使用选定的研究深度创建配置
    print("🔍 [调试] 开始创建配置...")
    try:
        config = CHINA_DEFAULT_CONFIG.copy()
        config["max_debate_rounds"] = selections["research_depth"]
        config["max_risk_discuss_rounds"] = selections["research_depth"]
        config["quick_think_llm"] = selections["shallow_thinker"]
        config["deep_think_llm"] = selections["deep_thinker"]
        config["backend_url"] = selections["backend_url"]
        config["llm_provider"] = selections["llm_provider"].lower()
        print(f"✅ [调试] 配置创建完成，LLM提供商: {config['llm_provider']}")
    except Exception as e:
        print(f"❌ [调试] 创建配置失败: {e}")
        return

    # 初始化图
    print("🔍 [调试] 开始初始化ChinaTradingAgentsGraph...")
    try:
        graph = ChinaTradingAgentsGraph(
            [analyst.value for analyst in selections["analysts"]], config=config, debug=True
        )
        print(f"✅ [调试] 图初始化完成，选择的分析师: {[analyst.value for analyst in selections['analysts']]}")
    except Exception as e:
        print(f"❌ [调试] 图初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 现在开始显示布局
    print("🔍 [调试] 开始创建显示布局...")
    try:
        layout = create_layout()
        print("✅ [调试] 布局创建完成")
    except Exception as e:
        print(f"❌ [调试] 布局创建失败: {e}")
        return
    
    with Live(layout, refresh_per_second=4) as live:
        print("🔍 [调试] 进入Live显示模式...")
        
        # 初始显示
        try:
            update_display(layout)
            print("✅ [调试] 初始显示更新完成")
        except Exception as e:
            print(f"❌ [调试] 初始显示更新失败: {e}")
        
        # 添加初始消息
        try:
            message_buffer.add_message("系统", f"选择的股票代码: {selections['ticker']}")
            message_buffer.add_message(
                "系统", f"分析日期: {selections['analysis_date']}"
            )
            message_buffer.add_message(
                "系统", 
                f"选择的分析师: {', '.join(analyst.value for analyst in selections['analysts'])}",
            )
            update_display(layout)
            print("✅ [调试] 初始消息添加完成")
        except Exception as e:
            print(f"❌ [调试] 添加初始消息失败: {e}")
        
        # 重置代理状态
        try:
            for agent in message_buffer.agent_status:
                message_buffer.update_agent_status(agent, "pending")
            print("✅ [调试] 代理状态重置完成")
        except Exception as e:
            print(f"❌ [调试] 代理状态重置失败: {e}")
        
        # 重置报告部分
        try:
            for section in message_buffer.report_sections:
                message_buffer.report_sections[section] = None
            message_buffer.current_report = None
            message_buffer.final_report = None
            print("✅ [调试] 报告部分重置完成")
        except Exception as e:
            print(f"❌ [调试] 报告部分重置失败: {e}")
        
        # 将第一个分析师的代理状态更新为进行中
        try:
            first_analyst_mapping = {
                "市场技术": "市场技术分析师",
                "新闻": "新闻分析师", 
                "基本面": "基本面分析师",
                "情绪": "社交情绪分析师"
            }
            first_analyst = first_analyst_mapping.get(selections['analysts'][0].value, "市场技术分析师")
            message_buffer.update_agent_status(first_analyst, "in_progress")
            update_display(layout)
            print(f"✅ [调试] 第一个分析师设置为进行中: {first_analyst}")
        except Exception as e:
            print(f"❌ [调试] 设置第一个分析师状态失败: {e}")
        
        # 创建旋转器文本
        try:
            spinner_text = (
                f"正在分析 {selections['ticker']} 在 {selections['analysis_date']} 的数据..."
            )
            update_display(layout, spinner_text)
            print(f"✅ [调试] 旋转器文本创建完成: {spinner_text}")
        except Exception as e:
            print(f"❌ [调试] 创建旋转器文本失败: {e}")
        
        # 初始化状态并获取图参数
        print("🔍 [调试] 开始初始化状态...")
        try:
            init_agent_state = graph.propagator.create_china_initial_state(
                selections["ticker"], selections["analysis_date"]
            )
            print(f"✅ [调试] 初始状态创建完成，状态键: {list(init_agent_state.keys())}")
            
            args = graph.propagator.get_graph_args()
            print(f"✅ [调试] 图参数获取完成: {args}")
        except Exception as e:
            print(f"❌ [调试] 初始化状态失败: {e}")
            import traceback
            traceback.print_exc()
            return

        # 流式分析
        print("🔍 [调试] 开始流式分析...")
        trace = []
        try:
            message_buffer.add_message("系统", "开始流式分析...")
            update_display(layout)
            print("✅ [调试] 流式分析开始消息已添加")
            
            chunk_count = 0
            print(f"🔍 [调试] 开始调用 graph.graph.stream()...")
            
            for chunk in graph.graph.stream(init_agent_state, **args):
                chunk_count += 1
                print(f"📦 [调试] 收到第 {chunk_count} 个数据块，键: {list(chunk.keys())}")
                
                message_buffer.add_message("系统", f"处理第 {chunk_count} 个数据块")
                update_display(layout)
                
                if len(chunk.get("messages", [])) > 0:
                    print(f"💬 [调试] 数据块包含 {len(chunk['messages'])} 条消息")
                    # 从块中获取最后一条消息
                    last_message = chunk["messages"][-1]

                    # 提取消息内容和类型
                    if hasattr(last_message, "content"):
                        content = extract_content_string(last_message.content)  # 使用辅助函数
                        msg_type = "推理"
                        print(f"💭 [调试] 提取到推理消息: {content}")
                    else:
                        content = str(last_message)
                        msg_type = "系统"
                        print(f"🔧 [调试] 提取到系统消息: {content}")

                    # 将消息添加到缓冲区
                    message_buffer.add_message(msg_type, content)

                    # 如果是工具调用，将其添加到工具调用中
                    if hasattr(last_message, "tool_calls"):
                        print(f"🛠️ [调试] 检测到 {len(last_message.tool_calls)} 个工具调用")
                        for tool_call in last_message.tool_calls:
                            # 处理字典和对象工具调用
                            if isinstance(tool_call, dict):
                                message_buffer.add_tool_call(
                                    tool_call["name"], tool_call["args"]
                                )
                                print(f"🔨 [调试] 工具调用: {tool_call['name']}")
                            else:
                                message_buffer.add_tool_call(tool_call.name, tool_call.args)
                                print(f"🔨 [调试] 工具调用: {tool_call.name}")
                else:
                    print(f"📭 [调试] 数据块不包含消息")

                # 检查各种报告状态并更新分析师状态
                report_to_analyst_mapping = {
                    "market_report": "市场技术分析师",
                    "sentiment_report": "社交情绪分析师", 
                    "news_report": "新闻分析师",
                    "fundamentals_report": "基本面分析师"
                }
                
                # 分析师映射（用于查找下一个分析师）
                analyst_mapping = {
                    "市场技术": "市场技术分析师",
                    "新闻": "新闻分析师", 
                    "基本面": "基本面分析师",
                    "情绪": "社交情绪分析师"
                }
                
                # 检查分析师报告完成情况
                for report_type in ["market_report", "sentiment_report", "news_report", "fundamentals_report"]:
                    if report_type in chunk and chunk[report_type]:
                        print(f"📊 [调试] 检测到 {report_type}: {chunk[report_type][:100]}...")
                        
                        # 更新对应分析师状态为已完成
                        if report_type in report_to_analyst_mapping:
                            analyst_name = report_to_analyst_mapping[report_type]
                            message_buffer.update_agent_status(analyst_name, "completed")
                            print(f"✅ [调试] {analyst_name} 状态更新为已完成")
                            
                            # 查找下一个待执行的分析师
                            found_next = False
                            for selected_analyst in selections['analysts']:
                                next_analyst_name = analyst_mapping.get(selected_analyst.value)
                                if (next_analyst_name and 
                                    message_buffer.agent_status.get(next_analyst_name) == "pending"):
                                    message_buffer.update_agent_status(next_analyst_name, "in_progress")
                                    print(f"🔄 [调试] {next_analyst_name} 状态更新为进行中")
                                    found_next = True
                                    break
                            
                            # 如果所有分析师都完成了，开始研究团队
                            if not found_next:
                                all_analysts_completed = all(
                                    message_buffer.agent_status.get(analyst_mapping.get(analyst.value)) == "completed"
                                    for analyst in selections['analysts']
                                    if analyst_mapping.get(analyst.value)
                                )
                                if all_analysts_completed:
                                    print("🎓 [调试] 所有分析师完成，开始研究团队")
                                    message_buffer.update_agent_status("看涨研究员", "in_progress")
                        
                        # 更新报告部分
                        message_buffer.update_report_section(report_type, chunk[report_type])
                
                # 检查研究团队状态
                if "investment_debate_state" in chunk:
                    debate_state = chunk["investment_debate_state"]
                    if debate_state:
                        print(f"🔍 [调试] 检测到研究团队辩论状态")
                        
                        # 检查看涨研究员
                        if debate_state.get("bull_history"):
                            message_buffer.update_agent_status("看涨研究员", "completed")
                            message_buffer.update_agent_status("看跌研究员", "in_progress")
                            print("🐂 [调试] 看涨研究员完成，看跌研究员开始")
                        
                        # 检查看跌研究员  
                        if debate_state.get("bear_history"):
                            message_buffer.update_agent_status("看跌研究员", "completed")
                            message_buffer.update_agent_status("研究经理", "in_progress")
                            print("🐻 [调试] 看跌研究员完成，研究经理开始")
                        
                        # 检查研究经理决策
                        if debate_state.get("judge_decision"):
                            message_buffer.update_agent_status("研究经理", "completed")
                            message_buffer.update_agent_status("交易员", "in_progress")
                            print("👨‍💼 [调试] 研究经理完成，交易员开始")
                
                # 检查交易员计划
                if "trader_investment_plan" in chunk and chunk["trader_investment_plan"]:
                    print(f"💼 [调试] 检测到交易员计划")
                    message_buffer.update_agent_status("交易员", "completed")
                    message_buffer.update_agent_status("激进分析师", "in_progress")
                    print("💼 [调试] 交易员完成，风险管理团队开始")
                
                # 检查风险管理团队状态
                if "risk_debate_state" in chunk:
                    risk_state = chunk["risk_debate_state"]
                    if risk_state:
                        print(f"⚖️ [调试] 检测到风险管理团队状态")
                        
                        # 检查激进分析师
                        if risk_state.get("risky_history"):
                            message_buffer.update_agent_status("激进分析师", "completed")
                            message_buffer.update_agent_status("保守分析师", "in_progress")
                            print("⚡ [调试] 激进分析师完成，保守分析师开始")
                        
                        # 检查保守分析师
                        if risk_state.get("safe_history"):
                            message_buffer.update_agent_status("保守分析师", "completed")
                            message_buffer.update_agent_status("中性分析师", "in_progress")
                            print("🛡️ [调试] 保守分析师完成，中性分析师开始")
                        
                        # 检查中性分析师
                        if risk_state.get("neutral_history"):
                            message_buffer.update_agent_status("中性分析师", "completed")
                            message_buffer.update_agent_status("投资组合经理", "in_progress")
                            print("⚖️ [调试] 中性分析师完成，投资组合经理开始")
                        
                        # 检查投资组合经理决策
                        if risk_state.get("judge_decision"):
                            message_buffer.update_agent_status("投资组合经理", "completed")
                            print("🎯 [调试] 投资组合经理完成最终决策")

                # 更新显示
                update_display(layout)
                trace.append(chunk)
            
            print(f"🏁 [调试] 流式分析完成，总共处理了 {chunk_count} 个数据块")
            
            if not trace:
                print("⚠️ [调试] 警告：没有收到任何数据块！")
                message_buffer.add_message("系统", "警告：分析过程没有产生任何数据")
                update_display(layout)
                return
            
            # 获取最终状态和决策
            print("🔍 [调试] 开始处理最终状态...")
            final_state = trace[-1]
            print(f"✅ [调试] 最终状态键: {list(final_state.keys())}")
            
            # 安全地获取最终交易决策
            final_trade_decision = final_state.get("final_trade_decision")
            if final_trade_decision:
                print(f"📈 [调试] 找到最终交易决策: {final_trade_decision}")
                decision = graph.process_signal(final_trade_decision)
            else:
                print("⚠️ [调试] 没有找到最终交易决策，尝试从风险辩论状态获取")
                # 如果没有最终交易决策，使用风险辩论状态中的决策
                risk_state = final_state.get("risk_debate_state", {})
                judge_decision = risk_state.get("judge_decision", "无最终决策")
                print(f"📋 [调试] 从风险辩论状态获取决策: {judge_decision}")
                decision = graph.process_signal(judge_decision)

            # 将所有代理状态更新为已完成
            for agent in message_buffer.agent_status:
                message_buffer.update_agent_status(agent, "completed")
            
            message_buffer.add_message(
                "分析", f"已完成 {selections['analysis_date']} 的分析"
            )

            # 更新最终报告部分
            for section in message_buffer.report_sections.keys():
                if section in final_state:
                    message_buffer.update_report_section(section, final_state[section])

            # 显示完整的最终报告
            print("🔍 [调试] 开始显示完整报告...")
            display_complete_report(final_state)

            # 保存最终分析报告到results目录
            print("🔍 [调试] 开始保存最终分析报告...")
            saved_filepath = save_final_report(final_state, selections)
            if saved_filepath:
                message_buffer.add_message("系统", f"报告已保存至: {saved_filepath}")

            update_display(layout)
            print("✅ [调试] 分析完成！")
            
        except Exception as e:
            print(f"❌ [调试] 分析过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
            console.print(f"[red]分析过程中发生错误: {e}[/red]")
            update_display(layout)


@app.command()
def analyze():
    """开始中国A股分析"""
    run_analysis()


if __name__ == "__main__":
    app() 