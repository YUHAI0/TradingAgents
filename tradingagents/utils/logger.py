"""
股票分析日志工具
提供详细的输入输出日志记录功能
"""

import logging
import json
import time
import inspect
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from functools import wraps
import traceback

def get_caller_info():
    """获取调用者信息"""
    stack = inspect.stack()
    
    # 从第3层开始查找（跳过当前函数和直接调用者）
    for i in range(2, len(stack)):
        frame_info = stack[i]
        filename = os.path.basename(frame_info.filename)
        
        # 跳过logger.py文件
        if filename != 'logger.py':
            return f"{filename}:{frame_info.lineno}"
    
    return "unknown:0"

class StockAnalysisLogger:
    """股票分析专用日志记录器"""
    
    def __init__(self, log_level=logging.INFO, log_file=None, enable_console=True):
        """
        初始化日志记录器
        
        Args:
            log_level: 日志级别
            log_file: 日志文件路径（可选）
            enable_console: 是否启用控制台输出
        """
        self.logger = logging.getLogger('StockAnalysis')
        self.logger.setLevel(log_level)
        
        # 清除已有的处理器
        self.logger.handlers.clear()
        
        # 设置日志格式（简化版本）
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # 文件处理器
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def log_analysis_start(self, stock_code: str, trade_date: str, analysis_type: str = "完整分析"):
        """记录分析开始"""
        caller = get_caller_info()
        self.logger.info("=" * 80)
        self.logger.info(f"[{caller}] 🚀 开始{analysis_type}: {stock_code}")
        self.logger.info(f"[{caller}] 📅 分析日期: {trade_date}")
        self.logger.info(f"[{caller}] ⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 80)
    
    def log_data_request(self, data_type: str, stock_code: str, params: Dict = None):
        """记录数据请求"""
        caller = get_caller_info()
        self.logger.info(f"[{caller}] 📊 请求{data_type}数据")
        self.logger.info(f"[{caller}]    股票代码: {stock_code}")
        if params:
            self.logger.info(f"[{caller}]    请求参数: {json.dumps(params, ensure_ascii=False, indent=2)}")
    
    def log_data_response(self, data_type: str, success: bool, data_size: int = 0, error: str = None, parsed_data: Dict = None):
        """记录数据响应"""
        caller = get_caller_info()
        if success:
            self.logger.info(f"[{caller}] ✅ {data_type}数据获取成功")
            self.logger.info(f"[{caller}]    数据量: {data_size} 字符")
            
            # 如果有解析后的数据，显示具体数值
            if parsed_data:
                self.logger.info(f"[{caller}]    📊 解析数据详情:")
                self._log_parsed_data(parsed_data, caller)
        else:
            self.logger.error(f"[{caller}] ❌ {data_type}数据获取失败")
            if error:
                self.logger.error(f"[{caller}]    错误信息: {error}")
    
    def _log_parsed_data(self, data: Dict, caller: str = None, indent: str = "      "):
        """记录解析后的数据详情"""
        prefix = f"[{caller}] " if caller else ""
        for key, value in data.items():
            if isinstance(value, dict):
                self.logger.info(f"{prefix}{indent}{key}:")
                self._log_parsed_data(value, caller, indent + "  ")
            elif isinstance(value, list):
                self.logger.info(f"{prefix}{indent}{key}: {value[:3]}{'...' if len(value) > 3 else ''}")
            elif isinstance(value, (int, float)):
                # 格式化数值显示
                if isinstance(value, float):
                    self.logger.info(f"{prefix}{indent}{key}: {value:.4f}")
                else:
                    self.logger.info(f"{prefix}{indent}{key}: {value:,}")
            else:
                # 限制字符串长度
                str_value = str(value)
                if len(str_value) > 50:
                    self.logger.info(f"{prefix}{indent}{key}: {str_value[:50]}...")
                else:
                    self.logger.info(f"{prefix}{indent}{key}: {str_value}")
    
    def log_llm_request(self, provider: str, model: str, prompt_type: str, input_tokens: int = 0):
        """记录LLM请求"""
        caller = get_caller_info()
        self.logger.info(f"[{caller}] 🤖 LLM分析请求")
        self.logger.info(f"[{caller}]    提供商: {provider}")
        self.logger.info(f"[{caller}]    模型: {model}")
        self.logger.info(f"[{caller}]    分析类型: {prompt_type}")
        if input_tokens > 0:
            self.logger.info(f"[{caller}]    输入token数: {input_tokens}")
    
    def log_llm_response(self, provider: str, success: bool, output_tokens: int = 0, cost: float = 0, error: str = None):
        """记录LLM响应"""
        if success:
            self.logger.info(f"✅ LLM分析完成")
            self.logger.info(f"   提供商: {provider}")
            if output_tokens > 0:
                self.logger.info(f"   输出token数: {output_tokens}")
            if cost > 0:
                self.logger.info(f"   预估成本: ¥{cost:.4f}")
        else:
            self.logger.error(f"❌ LLM分析失败")
            self.logger.error(f"   提供商: {provider}")
            if error:
                self.logger.error(f"   错误信息: {error}")
    
    def log_analysis_step(self, step_name: str, input_data: Any = None, output_data: Any = None):
        """记录分析步骤"""
        caller = get_caller_info()
        self.logger.info(f"[{caller}] 🔍 {step_name}")
        
        if input_data is not None:
            if isinstance(input_data, str) and len(input_data) > 200:
                self.logger.info(f"[{caller}]    输入数据: {input_data[:200]}... (截断)")
            else:
                self.logger.info(f"[{caller}]    输入数据: {input_data}")
        
        if output_data is not None:
            if isinstance(output_data, str) and len(output_data) > 200:
                self.logger.info(f"[{caller}]    输出结果: {output_data[:200]}... (截断)")
            else:
                self.logger.info(f"[{caller}]    输出结果: {output_data}")
    
    def log_analysis_complete(self, stock_code: str, success: bool, total_time: float, summary: Dict = None):
        """记录分析完成"""
        self.logger.info("=" * 80)
        if success:
            self.logger.info(f"✅ 股票分析完成: {stock_code}")
        else:
            self.logger.error(f"❌ 股票分析失败: {stock_code}")
        
        self.logger.info(f"⏱️  总耗时: {total_time:.2f}秒")
        
        if summary:
            self.logger.info("📋 分析摘要:")
            for key, value in summary.items():
                self.logger.info(f"   {key}: {value}")
        
        self.logger.info("=" * 80)
    
    def log_error(self, error_type: str, error_msg: str, stack_trace: bool = False):
        """记录错误"""
        self.logger.error(f"💥 {error_type}: {error_msg}")
        if stack_trace:
            self.logger.error(f"   堆栈跟踪:\n{traceback.format_exc()}")
    
    def log_debug(self, message: str, data: Any = None):
        """记录调试信息"""
        self.logger.debug(f"🔧 {message}")
        if data is not None:
            self.logger.debug(f"   数据: {data}")
    
    def log_performance(self, operation: str, duration: float, details: Dict = None):
        """记录性能信息"""
        self.logger.info(f"⚡ 性能统计 - {operation}: {duration:.3f}秒")
        if details:
            for key, value in details.items():
                self.logger.info(f"   {key}: {value}")
    
    def log_stock_indicators(self, stock_code: str, indicators: Dict):
        """记录股票技术指标数值"""
        caller = get_caller_info()
        self.logger.info(f"[{caller}] 📈 {stock_code} 技术指标详情:")
        
        # 价格相关指标
        if 'price' in indicators:
            price_data = indicators['price']
            self.logger.info(f"[{caller}]    💰 价格信息:")
            for key, value in price_data.items():
                if isinstance(value, (int, float)):
                    self.logger.info(f"[{caller}]       {key}: {value:.2f}")
                else:
                    self.logger.info(f"[{caller}]       {key}: {value}")
        
        # 技术指标
        if 'technical' in indicators:
            tech_data = indicators['technical']
            self.logger.info(f"[{caller}]    🔢 技术指标:")
            for key, value in tech_data.items():
                if isinstance(value, (int, float)):
                    if 'volume' in key.lower():
                        self.logger.info(f"[{caller}]       {key}: {value:,.0f}")
                    elif 'percent' in key.lower() or 'rate' in key.lower():
                        self.logger.info(f"[{caller}]       {key}: {value:.2f}%")
                    else:
                        self.logger.info(f"[{caller}]       {key}: {value:.4f}")
                else:
                    self.logger.info(f"[{caller}]       {key}: {value}")
        
        # 移动平均线
        if 'ma' in indicators:
            ma_data = indicators['ma']
            self.logger.info(f"[{caller}]    📊 移动平均线:")
            for period, value in ma_data.items():
                if isinstance(value, (int, float)):
                    self.logger.info(f"[{caller}]       MA{period}: {value:.2f}")
    
    def log_financial_metrics(self, stock_code: str, metrics: Dict):
        """记录财务指标数值"""
        self.logger.info(f"💼 {stock_code} 财务指标详情:")
        
        # 盈利能力
        if 'profitability' in metrics:
            profit_data = metrics['profitability']
            self.logger.info("   💹 盈利能力:")
            for key, value in profit_data.items():
                if isinstance(value, (int, float)):
                    if 'revenue' in key.lower() or 'income' in key.lower():
                        self.logger.info(f"      {key}: {value:,.2f} 万元")
                    elif 'rate' in key.lower() or 'ratio' in key.lower():
                        self.logger.info(f"      {key}: {value:.2f}%")
                    else:
                        self.logger.info(f"      {key}: {value:.4f}")
                else:
                    self.logger.info(f"      {key}: {value}")
        
        # 财务健康度
        if 'health' in metrics:
            health_data = metrics['health']
            self.logger.info("   🏥 财务健康:")
            for key, value in health_data.items():
                if isinstance(value, (int, float)):
                    if 'ratio' in key.lower() or 'rate' in key.lower():
                        self.logger.info(f"      {key}: {value:.2f}%")
                    else:
                        self.logger.info(f"      {key}: {value:.4f}")
                else:
                    self.logger.info(f"      {key}: {value}")
    
    def log_market_sentiment(self, sentiment_data: Dict):
        """记录市场情绪数据"""
        self.logger.info("😊 市场情绪分析详情:")
        
        # 情绪指标
        if 'sentiment_scores' in sentiment_data:
            scores = sentiment_data['sentiment_scores']
            self.logger.info("   📊 情绪评分:")
            for source, score in scores.items():
                if isinstance(score, (int, float)):
                    self.logger.info(f"      {source}: {score:.2f}/10")
                else:
                    self.logger.info(f"      {source}: {score}")
        
        # 新闻统计
        if 'news_stats' in sentiment_data:
            news = sentiment_data['news_stats']
            self.logger.info("   📰 新闻统计:")
            for key, value in news.items():
                if isinstance(value, (int, float)):
                    if 'count' in key.lower():
                        self.logger.info(f"      {key}: {value:,} 条")
                    elif 'percent' in key.lower():
                        self.logger.info(f"      {key}: {value:.1f}%")
                    else:
                        self.logger.info(f"      {key}: {value}")
                else:
                    self.logger.info(f"      {key}: {value}")
    
    def log_investment_advice(self, stock_code: str, advice: Dict):
        """记录投资建议详情"""
        self.logger.info(f"🎯 {stock_code} 投资建议详情:")
        
        # 评级和目标价
        if 'rating' in advice:
            self.logger.info(f"   📊 综合评级: {advice['rating']}")
        
        if 'target_price' in advice:
            target = advice['target_price']
            if isinstance(target, dict):
                self.logger.info("   🎯 目标价位:")
                for key, value in target.items():
                    if isinstance(value, (int, float)):
                        self.logger.info(f"      {key}: {value:.2f} 元")
                    else:
                        self.logger.info(f"      {key}: {value}")
            elif isinstance(target, (int, float)):
                self.logger.info(f"   🎯 目标价位: {target:.2f} 元")
        
        # 风险评估
        if 'risk_assessment' in advice:
            risk = advice['risk_assessment']
            self.logger.info("   ⚠️ 风险评估:")
            for key, value in risk.items():
                if isinstance(value, (int, float)):
                    self.logger.info(f"      {key}: {value:.2f}")
                else:
                    self.logger.info(f"      {key}: {value}")
        
        # 操作建议
        if 'operations' in advice:
            ops = advice['operations']
            self.logger.info("   📈 操作建议:")
            for key, value in ops.items():
                self.logger.info(f"      {key}: {value}")

def log_analysis_method(logger: StockAnalysisLogger, method_name: str):
    """装饰器：自动记录分析方法的输入输出"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # 记录方法开始
            logger.log_analysis_step(f"开始执行{method_name}")
            
            # 记录输入参数
            if args:
                logger.log_debug(f"{method_name}输入参数", {"args": args[1:], "kwargs": kwargs})  # 跳过self
            
            try:
                # 执行方法
                result = func(*args, **kwargs)
                
                # 记录成功
                duration = time.time() - start_time
                logger.log_analysis_step(f"{method_name}执行成功", output_data=str(result)[:100] if result else None)
                logger.log_performance(method_name, duration)
                
                return result
                
            except Exception as e:
                # 记录错误
                duration = time.time() - start_time
                logger.log_error(f"{method_name}执行失败", str(e), stack_trace=True)
                logger.log_performance(f"{method_name}(失败)", duration)
                raise
        
        return wrapper
    return decorator

# 全局日志实例
default_logger = StockAnalysisLogger()

def get_logger(custom_config: Dict = None) -> StockAnalysisLogger:
    """获取日志记录器实例"""
    if custom_config:
        return StockAnalysisLogger(**custom_config)
    return default_logger 