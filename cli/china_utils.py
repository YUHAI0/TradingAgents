"""
中国A股TradingAgents CLI工具函数
"""

import questionary
from typing import List, Optional, Tuple, Dict
from rich.console import Console

from cli.china_models import ChinaAnalystType, ChinaLLMProvider, ChinaResearchDepth

console = Console()

# 中国分析师顺序
CHINA_ANALYST_ORDER = [
    ("市场技术分析师", ChinaAnalystType.MARKET),
    ("新闻分析师", ChinaAnalystType.NEWS),
    ("基本面分析师", ChinaAnalystType.FUNDAMENTALS),
    ("市场情绪分析师", ChinaAnalystType.SENTIMENT),
]


def select_china_analysts() -> List[ChinaAnalystType]:
    """选择中国A股分析师"""
    choices = questionary.checkbox(
        "请选择您的【分析师团队】:",
        choices=[
            questionary.Choice(display, value=value) 
            for display, value in CHINA_ANALYST_ORDER
        ],
        instruction="\n- 按空格键选择/取消选择分析师\n- 按 'a' 键全选/全不选\n- 按回车键确认",
        validate=lambda x: len(x) > 0 or "您必须至少选择一个分析师。",
        style=questionary.Style([
            ("checkbox-selected", "fg:green"),
            ("selected", "fg:green noinherit"),
            ("highlighted", "noinherit"),
            ("pointer", "noinherit"),
        ]),
    ).ask()

    if not choices:
        console.print("\n[red]未选择分析师，退出...[/red]")
        exit(1)

    return choices


def select_research_depth() -> int:
    """选择研究深度"""
    
    # 定义研究深度选项及其对应值
    DEPTH_OPTIONS = [
        ("浅层 - 快速研究，少量辩论和策略讨论轮次", 1),
        ("中等 - 中等程度，适量辩论轮次和策略讨论", 3),
        ("深度 - 全面研究，深入辩论和策略讨论", 5),
    ]

    choice = questionary.select(
        "请选择您的【研究深度】:",
        choices=[
            questionary.Choice(display, value=value) 
            for display, value in DEPTH_OPTIONS
        ],
        instruction="\n- 使用方向键导航\n- 按回车键选择",
        style=questionary.Style([
            ("selected", "fg:yellow noinherit"),
            ("highlighted", "fg:yellow noinherit"),
            ("pointer", "fg:yellow noinherit"),
        ]),
    ).ask()

    if choice is None:
        console.print("\n[red]未选择研究深度，退出...[/red]")
        exit(1)

    return choice


def select_china_llm_provider() -> Tuple[str, str]:
    """选择中国LLM提供商"""
    
    # 定义中国LLM提供商选项
    CHINA_LLM_OPTIONS = [
        ("通义千问 (阿里云) - 中文优化，响应快速", "qwen", "https://dashscope.aliyuncs.com/api/v1/"),
        ("智谱AI (清华) - 强大的中文理解能力", "zhipu", "https://open.bigmodel.cn/api/paas/v4/"),
        ("百川智能 - 专业的中文大模型", "baichuan", "https://api.baichuan-ai.com/v1/"),
        ("文心一言 (百度) - 深度中文语言模型", "ernie", "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/"),
    ]

    choice = questionary.select(
        "请选择您的【LLM提供商】:",
        choices=[
            questionary.Choice(display, value=(provider, url)) 
            for display, provider, url in CHINA_LLM_OPTIONS
        ],
        instruction="\n- 使用方向键导航\n- 按回车键选择",
        style=questionary.Style([
            ("selected", "fg:cyan noinherit"),
            ("highlighted", "fg:cyan noinherit"),
            ("pointer", "fg:cyan noinherit"),
        ]),
    ).ask()

    if choice is None:
        console.print("\n[red]未选择LLM提供商，退出...[/red]")
        exit(1)

    provider, backend_url = choice
    return provider, backend_url


def select_shallow_thinking_agent(provider: str) -> str:
    """选择快速思考LLM引擎"""
    
    # 定义快速思考LLM引擎选项
    SHALLOW_AGENT_OPTIONS = {
        "qwen": [
            ("通义千问-Turbo - 快速高效，适合快速任务", "qwen-turbo"),
            ("通义千问-Plus - 平衡性能和速度", "qwen-plus"),
            ("通义千问-Max - 最强性能", "qwen-max"),
        ],
        "zhipu": [
            ("GLM-4-Flash - 快速推理模型", "glm-4-flash"),
            ("GLM-4-Air - 轻量级模型", "glm-4-air"),
            ("GLM-4 - 标准模型", "glm-4"),
        ],
        "baichuan": [
            ("Baichuan2-Turbo - 快速响应", "baichuan2-turbo"),
            ("Baichuan2-53B - 中型模型", "baichuan2-53b"),
        ],
        "ernie": [
            ("ERNIE-Speed - 快速版本", "ernie-speed"),
            ("ERNIE-Lite - 轻量版本", "ernie-lite"),
            ("ERNIE-3.5 - 标准版本", "ernie-3.5"),
        ],
    }

    options = SHALLOW_AGENT_OPTIONS.get(provider.lower(), [])
    if not options:
        console.print(f"\n[red]不支持的提供商: {provider}[/red]")
        exit(1)

    choice = questionary.select(
        "请选择您的【快速思考LLM引擎】:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in options
        ],
        instruction="\n- 使用方向键导航\n- 按回车键选择",
        style=questionary.Style([
            ("selected", "fg:magenta noinherit"),
            ("highlighted", "fg:magenta noinherit"),
            ("pointer", "fg:magenta noinherit"),
        ]),
    ).ask()

    if choice is None:
        console.print("\n[red]未选择快速思考LLM引擎，退出...[/red]")
        exit(1)

    return choice


def select_deep_thinking_agent(provider: str) -> str:
    """选择深度思考LLM引擎"""
    
    # 定义深度思考LLM引擎选项
    DEEP_AGENT_OPTIONS = {
        "qwen": [
            ("通义千问-Plus - 平衡性能和速度", "qwen-plus"),
            ("通义千问-Max - 最强性能和推理能力", "qwen-max"),
            ("通义千问-Long - 长文本处理专家", "qwen-long"),
        ],
        "zhipu": [
            ("GLM-4 - 标准深度推理模型", "glm-4"),
            ("GLM-4-Plus - 增强推理能力", "glm-4-plus"),
            ("GLM-4-0520 - 最新版本", "glm-4-0520"),
        ],
        "baichuan": [
            ("Baichuan2-53B - 中型深度模型", "baichuan2-53b"),
            ("Baichuan2-Turbo-192K - 长上下文模型", "baichuan2-turbo-192k"),
        ],
        "ernie": [
            ("ERNIE-3.5 - 标准深度推理", "ernie-3.5"),
            ("ERNIE-4.0 - 最强推理能力", "ernie-4.0"),
            ("ERNIE-Bot - 对话专家", "ernie-bot"),
        ],
    }

    options = DEEP_AGENT_OPTIONS.get(provider.lower(), [])
    if not options:
        console.print(f"\n[red]不支持的提供商: {provider}[/red]")
        exit(1)

    choice = questionary.select(
        "请选择您的【深度思考LLM引擎】:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in options
        ],
        instruction="\n- 使用方向键导航\n- 按回车键选择",
        style=questionary.Style([
            ("selected", "fg:blue noinherit"),
            ("highlighted", "fg:blue noinherit"),
            ("pointer", "fg:blue noinherit"),
        ]),
    ).ask()

    if choice is None:
        console.print("\n[red]未选择深度思考LLM引擎，退出...[/red]")
        exit(1)

    return choice


def validate_china_stock_code(code: str) -> bool:
    """验证中国股票代码格式"""
    import re
    
    # 支持的格式：
    # 000001, 600000 (6位数字)
    # 000001.SZ, 600000.SH (6位数字.交易所)
    patterns = [
        r"^[0-9]{6}$",           # 6位数字
        r"^[0-9]{6}\.(SZ|SH)$",  # 6位数字.交易所
    ]
    
    for pattern in patterns:
        if re.match(pattern, code.upper()):
            return True
    
    return False


def format_china_stock_code(code: str) -> str:
    """格式化中国股票代码"""
    code = code.strip().upper()
    
    # 如果是6位数字，自动添加交易所后缀
    if len(code) == 6 and code.isdigit():
        # 根据代码规则判断交易所
        if code.startswith(('000', '002', '300')):
            return f"{code}.SZ"  # 深交所
        elif code.startswith(('600', '601', '603', '605', '688')):
            return f"{code}.SH"  # 上交所
        else:
            # 默认深交所
            return f"{code}.SZ"
    
    return code


def get_stock_name_by_code(code: str) -> Optional[str]:
    """根据股票代码获取股票名称（简化版本）"""
    # 这里可以集成真实的股票名称查询API
    # 目前返回一个简化的映射
    STOCK_NAMES = {
        "000001.SZ": "平安银行",
        "000002.SZ": "万科A",
        "000725.SZ": "京东方A",
        "600000.SH": "浦发银行",
        "600036.SH": "招商银行",
        "600519.SH": "贵州茅台",
    }
    
    return STOCK_NAMES.get(code.upper())


def display_china_welcome():
    """显示中国版本欢迎信息"""
    from rich.panel import Panel
    
    welcome_text = """
🏮 欢迎使用中国A股TradingAgents CLI

🎯 功能特点:
• 🔍 多维度分析：技术面、基本面、新闻面、情绪面
• 🤖 国产LLM支持：通义千问、智谱AI、百川智能、文心一言
• 📊 实时数据：tushare、akshare等国内数据源
• 🇨🇳 A股优化：涨跌停、T+1、申万行业分类等

🚀 开始您的A股智能分析之旅！
    """
    
    console.print(Panel.fit(
        welcome_text,
        title="中国A股TradingAgents",
        border_style="green",
        padding=(1, 2)
    ))


def display_analysis_summary(config: Dict) -> None:
    """显示分析配置摘要"""
    from rich.table import Table
    from rich import box
    
    table = Table(title="分析配置摘要", box=box.ROUNDED)
    table.add_column("配置项", style="cyan", no_wrap=True)
    table.add_column("值", style="magenta")
    
    table.add_row("股票代码", config.get("ticker", "N/A"))
    table.add_row("分析日期", config.get("analysis_date", "N/A"))
    table.add_row("分析师团队", ", ".join([a.value for a in config.get("analysts", [])]))
    table.add_row("研究深度", str(config.get("research_depth", "N/A")))
    table.add_row("LLM提供商", config.get("llm_provider", "N/A"))
    table.add_row("快速模型", config.get("shallow_thinker", "N/A"))
    table.add_row("深度模型", config.get("deep_thinker", "N/A"))
    
    console.print(table) 