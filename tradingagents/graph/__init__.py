# TradingAgents/graph/__init__.py

from .trading_graph import TradingAgentsGraph
from .conditional_logic import ConditionalLogic
from .setup import GraphSetup
from .propagation import Propagator
from .reflection import Reflector
from .signal_processing import SignalProcessor

# 中国版本组件
from .china_trading_graph import ChinaTradingAgentsGraph
from .china_setup import ChinaGraphSetup
from .china_reflection import ChinaReflector
from .china_signal_processing import ChinaSignalProcessor

__all__ = [
    # 原版组件
    "TradingAgentsGraph",
    "ConditionalLogic",
    "GraphSetup",
    "Propagator",
    "Reflector",
    "SignalProcessor",
    # 中国版组件
    "ChinaTradingAgentsGraph",
    "ChinaGraphSetup", 
    "ChinaReflector",
    "ChinaSignalProcessor",
]
