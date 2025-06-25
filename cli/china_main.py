#!/usr/bin/env python3
"""
中国A股TradingAgents CLI
适配中国A股市场和国产LLM的命令行界面
"""

from typing import Optional
import datetime
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

# 导入中国版本的模块
from tradingagents.china_config import CHINA_DEFAULT_CONFIG, format_stock_code, is_valid_china_stock_code
from cli.china_models import ChinaAnalystType
from cli.china_utils import *

console = Console()

app = typer.Typer(
    name="中国A股TradingAgents",
    help="中国A股TradingAgents CLI: 多代理LLM金融交易框架",
    add_completion=True,  # 启用shell补全
)


# 创建消息缓冲区来存储最近的消息
class ChinaMessageBuffer:
    def __init__(self, max_length=100):
        self.messages = deque(maxlen=max_length)
        self.tool_calls = deque(maxlen=max_length)
        self.current_report = None
        self.final_report = None  # 存储完整的最终报告
        self.agent_status = {
            # 分析师团队
            "市场技术分析师": "pending",
            "新闻分析师": "pending", 
            "基本面分析师": "pending",
            "情绪分析师": "pending",
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
            "news_report": None,
            "fundamentals_report": None,
            "sentiment_report": None,
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
                "news_report": "新闻分析",
                "fundamentals_report": "基本面分析",
                "sentiment_report": "市场情绪分析",
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
                "news_report", 
                "fundamentals_report",
                "sentiment_report",
            ]
        ):
            report_parts.append("## 分析师团队报告")
            if self.report_sections["market_report"]:
                report_parts.append(
                    f"### 市场技术分析\n{self.report_sections['market_report']}"
                )
            if self.report_sections["news_report"]:
                report_parts.append(
                    f"### 新闻分析\n{self.report_sections['news_report']}"
                )
            if self.report_sections["fundamentals_report"]:
                report_parts.append(
                    f"### 基本面分析\n{self.report_sections['fundamentals_report']}"
                )
            if self.report_sections["sentiment_report"]:
                report_parts.append(
                    f"### 市场情绪分析\n{self.report_sections['sentiment_report']}"
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
    progress_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    progress_table.add_column("代理", style="cyan", no_wrap=True)
    progress_table.add_column("状态", justify="center")

    for agent, status in message_buffer.agent_status.items():
        if status == "pending":
            status_display = "[yellow]等待中[/yellow]"
        elif status == "in_progress":
            status_display = "[blue]进行中[/blue]"
        elif status == "completed":
            status_display = "[green]已完成[/green]"
        else:
            status_display = "[red]错误[/red]"
        
        progress_table.add_row(agent, status_display)

    layout["progress"].update(
        Panel(
            progress_table,
            title="代理进度",
            border_style="blue",
            padding=(1, 1),
        )
    )

    # 消息面板
    if message_buffer.messages:
        messages_content = []
        # 只显示最近的10条消息
        recent_messages = list(message_buffer.messages)[-10:]
        for timestamp, msg_type, content in recent_messages:
            # 限制内容长度以适应显示
            display_content = content[:200] + "..." if len(content) > 200 else content
            messages_content.append(f"[dim]{timestamp}[/dim] [{msg_type}]: {display_content}")
        
        messages_text = "\n".join(messages_content)
    else:
        messages_text = "[dim]等待消息...[/dim]"

    layout["messages"].update(
        Panel(
            messages_text,
            title="实时消息",
            border_style="yellow",
            padding=(1, 1),
        )
    )

    # 分析结果面板
    if message_buffer.current_report:
        analysis_content = Markdown(message_buffer.current_report)
    else:
        analysis_content = "[dim]等待分析结果...[/dim]"

    layout["analysis"].update(
        Panel(
            analysis_content,
            title="分析报告",
            border_style="green",
            padding=(1, 1),
        )
    )

    # 底部状态栏
    if spinner_text:
        footer_content = f"[bold blue]{spinner_text}[/bold blue]"
    else:
        footer_content = "[bold green]就绪[/bold green]"

    layout["footer"].update(
        Panel(
            footer_content,
            border_style="bright_blue",
            padding=(0, 2),
        )
    )


def get_user_selections():
    """获取用户选择"""
    import sys
    
    # 检查是否为交互式终端
    if not sys.stdin.isatty():
        # 非交互式模式，使用默认值
        console.print("[yellow]检测到非交互式模式，使用默认配置[/yellow]")
        return {
            "ticker": "000725",
            "analysis_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "analysts": [ChinaAnalystType.MARKET, ChinaAnalystType.FUNDAMENTALS],
            "research_depth": ChinaResearchDepth.MEDIUM,
            "llm_provider": ChinaLLMProvider.QWEN,
            "backend_url": None,
            "shallow_thinker": "qwen",
            "deep_thinker": "qwen"
        }
    
    console.print(Panel.fit(
        "[bold green]🏮 中国A股TradingAgents 配置向导[/bold green]",
        border_style="green"
    ))
    
    # 获取股票代码
    ticker = get_china_stock_code()
    
    # 获取分析日期
    analysis_date = get_analysis_date()
    
    # 选择分析师
    analysts = select_china_analysts()
    
    # 选择研究深度
    research_depth = select_research_depth()
    
    # 选择LLM提供商
    llm_provider, backend_url = select_china_llm_provider()
    
    # 选择快速思考LLM
    shallow_thinker = select_shallow_thinking_agent(llm_provider)
    
    # 选择深度思考LLM
    deep_thinker = select_deep_thinking_agent(llm_provider)
    
    return {
        "ticker": ticker,
        "analysis_date": analysis_date,
        "analysts": analysts,
        "research_depth": research_depth,
        "llm_provider": llm_provider,
        "backend_url": backend_url,
        "shallow_thinker": shallow_thinker,
        "deep_thinker": deep_thinker,
    }


def get_china_stock_code():
    """获取中国股票代码"""
    import questionary
    
    def validate_china_stock(code_str: str) -> bool:
        """验证中国股票代码"""
        code = code_str.strip()
        if not code:
            return False
        
        # 格式化股票代码
        formatted_code = format_stock_code(code)
        return is_valid_china_stock_code(formatted_code)
    
    code = questionary.text(
        "请输入股票代码（如：000001、600000、000001.SZ、600000.SH）:",
        validate=lambda x: validate_china_stock(x) or "请输入有效的中国A股股票代码",
        style=questionary.Style([
            ("text", "fg:green"),
            ("highlighted", "noinherit"),
        ]),
    ).ask()
    
    if not code:
        console.print("\n[red]未提供股票代码，退出...[/red]")
        exit(1)
    
    # 格式化并返回
    return format_stock_code(code.strip())


def get_analysis_date():
    """获取分析日期"""
    import re
    import questionary
    from datetime import datetime
    
    def validate_date(date_str: str) -> bool:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    date = questionary.text(
        "请输入分析日期（YYYY-MM-DD格式）:",
        default=datetime.now().strftime("%Y-%m-%d"),
        validate=lambda x: validate_date(x.strip()) or "请输入有效的日期格式 YYYY-MM-DD",
        style=questionary.Style([
            ("text", "fg:green"),
            ("highlighted", "noinherit"),
        ]),
    ).ask()
    
    if not date:
        console.print("\n[red]未提供日期，退出...[/red]")
        exit(1)
    
    return date.strip()


def display_complete_report(analysis_result):
    """显示完整的分析报告"""
    console.print("\n" + "="*80)
    console.print(Panel.fit(
        "[bold green]🎯 中国A股完整分析报告[/bold green]",
        border_style="green"
    ))
    
    if message_buffer.final_report:
        console.print(Markdown(message_buffer.final_report))
    else:
        console.print("[yellow]报告生成中...[/yellow]")
    
    console.print("="*80 + "\n")


def update_research_team_status(status):
    """更新研究团队状态"""
    research_team = ["看涨研究员", "看跌研究员", "研究经理"]
    for agent in research_team:
        message_buffer.update_agent_status(agent, status)


def extract_content_string(content):
    """提取内容字符串"""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # 处理列表内容
        text_parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                text_parts.append(item["text"])
            elif isinstance(item, str):
                text_parts.append(item)
            else:
                text_parts.append(str(item))
        return " ".join(text_parts)
    elif hasattr(content, "content"):
        return extract_content_string(content.content)
    else:
        return str(content)


def run_china_analysis():
    """运行中国A股分析"""
    # 首先获取所有用户选择
    selections = get_user_selections()
    
    # 导入中国版本的分析系统
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from china_trading_agents import ChinaAShareTradingAgents
    
    # 创建配置
    config = CHINA_DEFAULT_CONFIG.copy()
    
    # 初始化中国A股分析系统
    china_system = ChinaAShareTradingAgents(
        environment="default",
        debug=True,
        selected_analysts=[analyst.value for analyst in selections["analysts"]],
        llm_provider=selections["llm_provider"]
    )
    
    # 开始显示布局
    layout = create_layout()
    
    with Live(layout, refresh_per_second=4) as live:
        # 初始显示
        update_display(layout)
        
        # 添加初始消息
        message_buffer.add_message("系统", f"选择的股票: {selections['ticker']}")
        message_buffer.add_message("系统", f"分析日期: {selections['analysis_date']}")
        message_buffer.add_message(
            "系统", 
            f"选择的分析师: {', '.join(analyst.value for analyst in selections['analysts'])}"
        )
        message_buffer.add_message("系统", f"LLM提供商: {selections['llm_provider']}")
        update_display(layout)
        
        # 重置代理状态
        for agent in message_buffer.agent_status:
            message_buffer.update_agent_status(agent, "pending")
        
        # 重置报告部分
        for section in message_buffer.report_sections:
            message_buffer.report_sections[section] = None
        message_buffer.current_report = None
        message_buffer.final_report = None
        
        # 更新第一个分析师状态为进行中
        if selections["analysts"]:
            first_analyst = f"{selections['analysts'][0].value}分析师"
            message_buffer.update_agent_status(first_analyst, "in_progress")
        update_display(layout)
        
        # 创建spinner文本
        spinner_text = f"正在分析 {selections['ticker']} ({selections['analysis_date']})..."
        update_display(layout, spinner_text)
        
        try:
            # 运行分析
            message_buffer.add_message("系统", "开始多维度分析...")
            update_display(layout)
            
            # 模拟分析过程中的状态更新
            analysis_steps = [
                ("市场技术分析师", "in_progress", "获取股票数据和技术指标..."),
                ("市场技术分析师", "completed", "市场技术分析完成"),
                ("新闻分析师", "in_progress", "获取和分析相关新闻..."),
                ("新闻分析师", "completed", "新闻分析完成"),
                ("基本面分析师", "in_progress", "分析基本面数据..."),
                ("基本面分析师", "completed", "基本面分析完成"),
                ("情绪分析师", "in_progress", "分析市场情绪..."),
                ("情绪分析师", "completed", "市场情绪分析完成"),
            ]
            
            for agent, status, message in analysis_steps:
                message_buffer.update_agent_status(agent, status)
                message_buffer.add_message("进度", message)
                update_display(layout)
                time.sleep(1)  # 模拟处理时间
            
            # 执行实际分析
            message_buffer.add_message("系统", "正在执行深度AI分析...")
            update_display(layout)
            
            analysis_result = china_system.analyze_stock(
                selections["ticker"], 
                selections["analysis_date"]
            )
            
            # 更新报告部分
            if analysis_result.get("reports"):
                reports = analysis_result["reports"]
                
                if "market_analysis" in reports:
                    message_buffer.update_report_section(
                        "market_report", 
                        reports["market_analysis"].get("analysis", "")
                    )
                
                if "news_analysis" in reports:
                    message_buffer.update_report_section(
                        "news_report",
                        reports["news_analysis"].get("analysis", "")
                    )
                
                if "fundamentals_analysis" in reports:
                    message_buffer.update_report_section(
                        "fundamentals_report",
                        reports["fundamentals_analysis"].get("analysis", "")
                    )
                
                if "sentiment_analysis" in reports:
                    message_buffer.update_report_section(
                        "sentiment_report",
                        reports["sentiment_analysis"].get("analysis", "")
                    )
            
            # 更新最终建议
            if analysis_result.get("final_recommendation"):
                message_buffer.update_report_section(
                    "final_trade_decision",
                    analysis_result["final_recommendation"]
                )
            
            # 标记所有代理为完成
            for agent in message_buffer.agent_status:
                message_buffer.update_agent_status(agent, "completed")
            
            message_buffer.add_message("系统", "分析完成！")
            update_display(layout, "分析完成")
            
            # 等待用户查看结果
            time.sleep(3)
            
        except Exception as e:
            message_buffer.add_message("错误", f"分析过程中发生错误: {str(e)}")
            update_display(layout, f"错误: {str(e)}")
            time.sleep(2)
            analysis_result = {"error": str(e)}
    
    # 显示完整报告
    display_complete_report(analysis_result)
    
    return analysis_result


@app.command()
def analyze():
    """
    🏮 启动中国A股TradingAgents多代理分析
    
    这将启动一个交互式会话来分析中国A股股票。
    """
    console.print(Panel.fit(
        "[bold green]🚀 启动中国A股TradingAgents分析系统[/bold green]",
        border_style="green"
    ))
    
    try:
        result = run_china_analysis()
        
        if result.get("status") == "success":
            console.print("\n[bold green]✅ 分析成功完成！[/bold green]")
        else:
            console.print(f"\n[bold red]❌ 分析失败: {result.get('error', '未知错误')}[/bold red]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ 用户中断分析[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]❌ 发生错误: {str(e)}[/bold red]")


@app.command()
def version():
    """显示版本信息"""
    console.print(Panel.fit(
        "[bold green]中国A股TradingAgents CLI v2.0.0[/bold green]\n"
        "[dim]适配中国A股市场和国产LLM的多代理金融交易框架[/dim]",
        border_style="green"
    ))


if __name__ == "__main__":
    app() 