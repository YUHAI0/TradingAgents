"""
中国A股TradingAgents配置文件
包含国产数据源和LLM提供商的配置
"""

import os
from pathlib import Path
from typing import Union, Optional, Tuple, List

# 自动加载.env文件
try:
    from dotenv import load_dotenv
    # 查找.env文件路径
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ 已加载环境变量文件: {env_path}")
    else:
        print("⚠️ 未找到.env文件，使用系统环境变量")
except ImportError:
    print("⚠️ python-dotenv未安装，请运行: pip install python-dotenv")
    print("   或手动设置环境变量")

# 中国A股默认配置
CHINA_DEFAULT_CONFIG = {
    # 项目基础配置
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "data_dir": "/data/china_stock_data",  # 中国股票数据目录
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/china_data_cache",
    ),
    
    # 市场配置
    "market": "china_a_stock",  # 中国A股市场
    "exchanges": ["SH", "SZ"],  # 支持的交易所：上交所、深交所
    "trading_calendar": "china_a_stock",  # 中国A股交易日历
    
    # LLM配置 - 国产大模型
    "llm_provider": "china",  # 使用中国LLM提供商
    "primary_llm_provider": "qwen",  # 主要LLM提供商：通义千问
    "fallback_llm_provider": "zhipu",  # 备用LLM提供商：智谱AI
    
    # 深度思考模型（用于复杂分析任务）
    "deep_think_llm": "qwen-max",  # 通义千问最强模型
    "deep_think_provider": "qwen",
    
    # 快速思考模型（用于简单任务）
    "quick_think_llm": "qwen-turbo",  # 通义千问快速模型
    "quick_think_provider": "qwen",
    
    # 辩论和讨论设置
    "max_debate_rounds": 2,  # 适应中文语境，增加辩论轮数
    "max_risk_discuss_rounds": 2,
    "max_recur_limit": 100,
    
    # 工具设置
    "online_tools": True,
    "use_china_data_sources": True,  # 使用中国数据源
    
    # 数据源配置
    "data_sources": {
        "primary": "tushare",  # 主要数据源：tushare
        "secondary": "akshare",  # 备用数据源：akshare
        "news": "eastmoney",  # 新闻源：东财
        "sentiment": "xueqiu"  # 情感分析：雪球
    },
    
    # API密钥配置（从环境变量获取）
    "api_keys": {
        # 数据源API密钥
        "tushare_token": os.getenv("TUSHARE_TOKEN"),
        
        # LLM API密钥
        "qwen_api_key": os.getenv("QWEN_API_KEY"),
        "zhipu_api_key": os.getenv("ZHIPU_API_KEY"), 
        "baichuan_api_key": os.getenv("BAICHUAN_API_KEY"),
        "ernie_api_key": os.getenv("ERNIE_API_KEY"),
        "ernie_secret_key": os.getenv("ERNIE_SECRET_KEY"),
    },
    
    # 模型映射配置
    "model_mapping": {
        # 通义千问模型
        "qwen": {
            "fast": "qwen-turbo",
            "standard": "qwen-plus", 
            "advanced": "qwen-max"
        },
        # 智谱AI模型
        "zhipu": {
            "fast": "glm-4-flash",
            "standard": "glm-4",
            "advanced": "glm-4"
        },
        # 百川智能模型
        "baichuan": {
            "fast": "Baichuan2-Turbo",
            "standard": "Baichuan2-53B",
            "advanced": "Baichuan2-53B"
        },
        # 文心一言模型
        "ernie": {
            "fast": "ernie-bot-turbo",
            "standard": "ernie-bot",
            "advanced": "ernie-bot"
        }
    },
    
    # 中国股市特色配置
    "china_market_config": {
        # 交易时间配置
        "trading_hours": {
            "morning": {"start": "09:30", "end": "11:30"},
            "afternoon": {"start": "13:00", "end": "15:00"}
        },
        
        # 涨跌停限制
        "price_limit": {
            "main_board": 0.10,  # 主板10%
            "star_board": 0.20,  # 科创板20%
            "gem_board": 0.20,   # 创业板20%
            "st_stocks": 0.05    # ST股票5%
        },
        
        # T+1交易制度
        "settlement": "T+1",
        
        # 最小交易单位
        "min_order_unit": 100,  # 100股为一手
        
        # 股票代码格式
        "stock_code_format": {
            "shanghai": "6",     # 上交所以6开头
            "shenzhen": ["0", "3"], # 深交所以0或3开头
            "beijing": "8"       # 北交所以8开头
        }
    },
    
    # 分析师配置（适应A股市场）
    "analysts_config": {
        "market_analyst": {
            "indicators": ["sma", "ema", "macd", "rsi", "kdj", "boll", "volume"],
            "focus": "technical_analysis"
        },
        "news_analyst": {
            "sources": ["eastmoney", "sina_finance", "163_money"],
            "focus": "policy_impact"  # 重点关注政策影响
        },
        "sentiment_analyst": {
            "sources": ["xueqiu", "taoguba", "weibo"],
            "focus": "retail_investor_sentiment"  # 关注散户情绪
        },
        "fundamentals_analyst": {
            "metrics": ["pe", "pb", "roe", "debt_ratio", "revenue_growth"],
            "focus": "value_analysis"
        }
    },
    
    # 风险管理配置（适应A股特点）
    "risk_management": {
        "max_position_size": 0.3,  # 单只股票最大仓位30%
        "stop_loss_ratio": 0.08,   # 止损比例8%
        "take_profit_ratio": 0.15, # 止盈比例15%
        "max_daily_trades": 3,     # 每日最大交易次数
        "risk_free_rate": 0.025,   # 无风险利率2.5%（10年期国债）
    },
    
    # 行业分类配置（申万行业分类）
    "industry_classification": "shenwan",
    
    # 指数基准配置
    "benchmark_indices": {
        "broad_market": "000001.SH",  # 上证指数
        "large_cap": "000300.SH",     # 沪深300
        "mid_cap": "000905.SH",       # 中证500
        "small_cap": "399006.SZ",     # 创业板指
        "tech": "588000.SH"           # 科创50
    }
}

# 环境配置检查
def validate_china_config(config: dict) -> Tuple[bool, List[str]]:
    """
    验证中国A股配置的完整性
    
    Returns:
        tuple: (是否有效, 错误信息列表)
    """
    errors = []
    
    # 检查必需的API密钥
    required_keys = ["tushare_token", "qwen_api_key"]
    for key in required_keys:
        if not config["api_keys"].get(key):
            errors.append(f"缺少必需的API密钥: {key}")
    
    # 检查LLM提供商配置
    llm_provider = config.get("primary_llm_provider")
    if llm_provider and not config["api_keys"].get(f"{llm_provider}_api_key"):
        errors.append(f"LLM提供商 {llm_provider} 的API密钥未配置")
    
    # 检查数据目录
    if not os.path.exists(config.get("data_cache_dir", "")):
        try:
            os.makedirs(config["data_cache_dir"], exist_ok=True)
        except Exception as e:
            errors.append(f"无法创建数据缓存目录: {e}")
    
    return len(errors) == 0, errors

# 获取推荐的生产环境配置
def get_production_china_config() -> dict:
    """获取生产环境的中国A股配置"""
    config = CHINA_DEFAULT_CONFIG.copy()
    
    # 生产环境优化
    config.update({
        "deep_think_llm": "qwen-max",
        "quick_think_llm": "qwen-plus",  # 提升快速模型性能
        "max_debate_rounds": 3,          # 增加辩论轮数提升质量
        "max_risk_discuss_rounds": 3,
        "online_tools": True,
    })
    
    return config

# 获取测试环境配置
def get_test_china_config() -> dict:
    """获取测试环境的中国A股配置（节省API调用）"""
    config = CHINA_DEFAULT_CONFIG.copy()
    
    # 测试环境优化
    config.update({
        "deep_think_llm": "qwen-turbo",     # 使用较便宜的模型
        "quick_think_llm": "qwen-turbo",
        "max_debate_rounds": 1,             # 减少辩论轮数节省成本
        "max_risk_discuss_rounds": 1,
        "online_tools": True,
    })
    
    return config

# 股票代码工具函数
def format_stock_code(code: str, exchange: Optional[str] = None) -> str:
    """
    格式化股票代码为tushare格式
    
    Args:
        code: 股票代码，如 '000001' 或 '000001.SZ'
        exchange: 交易所，'SH' 或 'SZ'
    
    Returns:
        str: 格式化后的代码，如 '000001.SZ'
    """
    # 如果已经包含交易所后缀，直接返回
    if '.' in code:
        return code.upper()
    
    # 根据代码开头判断交易所
    if code.startswith('6'):
        return f"{code}.SH"
    elif code.startswith(('0', '3')):
        return f"{code}.SZ"
    elif code.startswith('8'):
        return f"{code}.BJ"  # 北交所
    
    # 如果指定了交易所，使用指定的
    if exchange:
        return f"{code}.{exchange.upper()}"
    
    # 默认深交所
    return f"{code}.SZ"

def is_valid_china_stock_code(code: str) -> bool:
    """
    验证是否为有效的中国股票代码
    
    Args:
        code: 股票代码
        
    Returns:
        bool: 是否有效
    """
    # 移除交易所后缀
    base_code = code.split('.')[0]
    
    # 检查长度
    if len(base_code) != 6:
        return False
    
    # 检查是否为数字
    if not base_code.isdigit():
        return False
    
    # 检查开头数字
    valid_prefixes = ['0', '1', '2', '3', '6', '8', '9']
    if base_code[0] not in valid_prefixes:
        return False
    
    return True

# 导出配置创建函数
def create_china_config(environment: str = "default") -> dict:
    """
    创建中国A股配置
    
    Args:
        environment: 环境类型 - 'default', 'production', 'test'
        
    Returns:
        dict: 配置字典
    """
    if environment == "production":
        return get_production_china_config()
    elif environment == "test":
        return get_test_china_config()
    else:
        return CHINA_DEFAULT_CONFIG.copy() 