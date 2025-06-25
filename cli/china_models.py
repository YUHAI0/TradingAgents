"""
中国A股TradingAgents CLI模型定义
"""

from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel


class ChinaAnalystType(str, Enum):
    """中国A股分析师类型"""
    MARKET = "市场技术"
    NEWS = "新闻"
    FUNDAMENTALS = "基本面"
    SENTIMENT = "情绪"


class ChinaLLMProvider(str, Enum):
    """中国LLM提供商"""
    QWEN = "qwen"  # 通义千问
    ZHIPU = "zhipu"  # 智谱AI
    BAICHUAN = "baichuan"  # 百川智能
    ERNIE = "ernie"  # 文心一言


class ChinaResearchDepth(str, Enum):
    """研究深度"""
    SHALLOW = "shallow"  # 浅层
    MEDIUM = "medium"   # 中等
    DEEP = "deep"      # 深度


class ChinaAnalysisConfig(BaseModel):
    """中国A股分析配置"""
    ticker: str
    analysis_date: str
    analysts: List[ChinaAnalystType]
    research_depth: ChinaResearchDepth
    llm_provider: ChinaLLMProvider
    shallow_thinker: str
    deep_thinker: str
    backend_url: Optional[str] = None
    
    class Config:
        use_enum_values = True


class ChinaStockInfo(BaseModel):
    """中国股票信息"""
    code: str
    name: Optional[str] = None
    market: str  # SZ/SH
    industry: Optional[str] = None
    
    class Config:
        use_enum_values = True 