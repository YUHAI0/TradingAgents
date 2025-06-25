"""
多数据源配置文件
支持配置和管理多种中国A股数据接口
"""

from typing import Dict, List, Optional
import os
from enum import Enum

class DataSource(Enum):
    """数据源枚举"""
    TUSHARE = "tushare"
    AKSHARE = "akshare"
    EFINANCE = "efinance"
    SINA = "sina"
    EASTMONEY = "eastmoney"
    BAIDU = "baidu"
    WIND = "wind"
    JQDATA = "jqdata"

class MultiSourceConfig:
    """多数据源配置管理器"""
    
    def __init__(self):
        self.data_sources = {
            DataSource.TUSHARE: {
                "name": "Tushare Pro",
                "priority": 1,  # 优先级（数字越小优先级越高）
                "requires_token": True,
                "is_free": False,
                "install_cmd": "pip install tushare",
                "features": ["股票基本信息", "历史行情", "财务数据", "宏观数据"],
                "reliability": 5,  # 可靠性评分 1-5
                "speed": 4,
                "data_quality": 5
            },
            DataSource.EFINANCE: {
                "name": "EFinance",
                "priority": 2,
                "requires_token": False,
                "is_free": True,
                "install_cmd": "pip install efinance",
                "features": ["实时行情", "历史行情", "基本信息"],
                "reliability": 4,
                "speed": 5,
                "data_quality": 4
            },
            DataSource.SINA: {
                "name": "新浪财经",
                "priority": 3,
                "requires_token": False,
                "is_free": True,
                "install_cmd": "内置requests",
                "features": ["实时行情", "基本信息"],
                "reliability": 3,
                "speed": 5,
                "data_quality": 3
            },
            DataSource.AKSHARE: {
                "name": "AkShare",
                "priority": 4,
                "requires_token": False,
                "is_free": True,
                "install_cmd": "pip install akshare",
                "features": ["历史行情", "基本信息", "新闻数据", "财务数据"],
                "reliability": 3,
                "speed": 3,
                "data_quality": 4
            },
            DataSource.EASTMONEY: {
                "name": "东方财富",
                "priority": 5,
                "requires_token": False,
                "is_free": True,
                "install_cmd": "自建爬虫",
                "features": ["实时行情", "新闻数据", "研报数据"],
                "reliability": 3,
                "speed": 4,
                "data_quality": 4
            }
        }
        
        # 根据不同数据类型配置首选数据源
        self.preferred_sources = {
            "stock_basic_info": [DataSource.TUSHARE, DataSource.EFINANCE, DataSource.SINA, DataSource.AKSHARE],
            "stock_price_data": [DataSource.TUSHARE, DataSource.EFINANCE, DataSource.AKSHARE],
            "realtime_data": [DataSource.EFINANCE, DataSource.SINA],
            "news_data": [DataSource.AKSHARE, DataSource.EASTMONEY],
            "financial_data": [DataSource.TUSHARE, DataSource.AKSHARE]
        }
    
    def get_available_sources(self) -> List[DataSource]:
        """获取当前可用的数据源"""
        available = []
        
        # 检查tushare
        try:
            import tushare
            if os.getenv("TUSHARE_TOKEN"):
                available.append(DataSource.TUSHARE)
        except ImportError:
            pass
        
        # 检查efinance
        try:
            import efinance
            available.append(DataSource.EFINANCE)
        except ImportError:
            pass
        
        # 检查akshare
        try:
            import akshare
            available.append(DataSource.AKSHARE)
        except ImportError:
            pass
        
        # 新浪财经（使用requests）
        try:
            import requests
            available.append(DataSource.SINA)
        except ImportError:
            pass
        
        return available
    
    def get_source_priority(self, data_type: str) -> List[DataSource]:
        """根据数据类型获取数据源优先级顺序"""
        preferred = self.preferred_sources.get(data_type, [])
        available = self.get_available_sources()
        
        # 返回可用且按优先级排序的数据源
        return [source for source in preferred if source in available]
    
    def get_installation_guide(self) -> Dict[str, str]:
        """获取数据源安装指南"""
        guide = {}
        for source, config in self.data_sources.items():
            guide[config["name"]] = config["install_cmd"]
        return guide
    
    def generate_recommendations(self) -> Dict[str, str]:
        """生成数据源推荐"""
        available = self.get_available_sources()
        unavailable = set(self.data_sources.keys()) - set(available)
        
        recommendations = {
            "当前可用": [self.data_sources[s]["name"] for s in available],
            "推荐安装": []
        }
        
        # 推荐安装高优先级的数据源
        for source in [DataSource.TUSHARE, DataSource.EFINANCE]:
            if source not in available:
                config = self.data_sources[source]
                recommendations["推荐安装"].append({
                    "name": config["name"],
                    "reason": f"可靠性: {config['reliability']}/5, 速度: {config['speed']}/5",
                    "install": config["install_cmd"]
                })
        
        return recommendations

# 全局配置实例
multi_source_config = MultiSourceConfig()

def get_recommended_sources_info():
    """获取推荐的数据源信息"""
    return {
        "tushare_pro": {
            "name": "Tushare Pro",
            "description": "最权威的A股数据源，适合专业量化分析",
            "pros": ["数据最权威", "接口稳定", "功能全面"],
            "cons": ["需要付费", "有积分限制"],
            "url": "https://tushare.pro/",
            "setup": """
# 安装
pip install tushare

# 配置
import tushare as ts
ts.set_token('你的token')  # 从tushare.pro获取
pro = ts.pro_api()
"""
        },
        "efinance": {
            "name": "EFinance",
            "description": "基于东方财富的免费数据接口，数据质量好",
            "pros": ["完全免费", "数据质量高", "接口简单"],
            "cons": ["功能相对有限", "可能不稳定"],
            "url": "https://github.com/microacup/efinance",
            "setup": """
# 安装
pip install efinance

# 使用
import efinance as ef
df = ef.stock.get_quote_history('000001')
"""
        },
        "sina_finance": {
            "name": "新浪财经接口",
            "description": "免费的实时数据接口，响应速度快",
            "pros": ["完全免费", "响应快速", "实时性好"],
            "cons": ["可能不稳定", "数据有限"],
            "url": "http://hq.sinajs.cn/",
            "setup": """
# 使用requests即可
import requests
url = "http://hq.sinajs.cn/list=sh000001"
response = requests.get(url)
"""
        }
    } 