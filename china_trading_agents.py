#!/usr/bin/env python3
"""
中国A股TradingAgents主程序
整合国产数据源和LLM，专门用于中国A股市场分析和交易决策
简化版本，直接调用分析函数
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tradingagents.china_config import (
    create_china_config, 
    validate_china_config,
    format_stock_code,
    is_valid_china_stock_code,
    CHINA_DEFAULT_CONFIG
)

# 导入数据接口
from tradingagents.dataflows.china_interface import (
    get_china_stock_data_online,
    get_china_stockstats_indicators_report_online,
    get_china_stock_news_online,
    get_china_fundamentals_online,
    get_china_market_sentiment_online
)

# 导入LLM提供商
from tradingagents.llm_providers.china_llm_provider import ChinaLLMManager

# 导入日志工具
from tradingagents.utils.logger import StockAnalysisLogger
from functools import wraps

def log_analysis_method(func):
    """简化的分析方法装饰器"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        method_name = func.__name__
        start_time = time.time()
        
        self.logger.log_analysis_step(f"开始执行{method_name}")
        
        try:
            result = func(self, *args, **kwargs)
            duration = time.time() - start_time
            self.logger.log_analysis_step(f"{method_name}执行成功")
            self.logger.log_performance(method_name, duration)
            return result
        except Exception as e:
            duration = time.time() - start_time
            self.logger.log_error(f"{method_name}执行失败", str(e))
            self.logger.log_performance(f"{method_name}(失败)", duration)
            raise
    
    return wrapper

class ChinaAShareTradingAgents:
    """中国A股交易代理系统 - 简化版本"""
    
    def __init__(self, environment: str = "default", debug: bool = False, 
                 log_file: Optional[str] = None, selected_analysts: Optional[List[str]] = None,
                 llm_provider: str = "qwen"):
        """
        初始化中国A股交易代理系统
        
        Args:
            environment: 运行环境
            debug: 是否开启调试模式
            log_file: 日志文件路径
            selected_analysts: 选择的分析师列表
            llm_provider: LLM提供商
        """
        # 创建配置
        self.config = create_china_config(environment)
        
        # 验证配置
        is_valid, errors = validate_china_config(self.config)
        if not is_valid:
            print(f"⚠️ 配置验证失败: {', '.join(errors)}")
        
        # 初始化LLM管理器
        self.llm_manager = ChinaLLMManager(self.config)
        
        # 设置分析师 - 支持中英文名称映射
        if selected_analysts:
            # 中文到英文的映射
            analyst_mapping = {
                "市场技术": "market",
                "新闻": "news", 
                "基本面": "fundamentals",
                "情绪": "sentiment",
                # 英文名称直接保留
                "market": "market",
                "news": "news",
                "fundamentals": "fundamentals", 
                "sentiment": "sentiment"
            }
            
            # 转换中文名称为英文
            self.selected_analysts = []
            for analyst in selected_analysts:
                if analyst in analyst_mapping:
                    self.selected_analysts.append(analyst_mapping[analyst])
                else:
                    # 如果不在映射中，直接使用原名称
                    self.selected_analysts.append(analyst)
        else:
            self.selected_analysts = ["market", "news", "fundamentals", "sentiment"]
        
        # 初始化日志系统 - 只在控制台显示，不保存到文件
        log_level = logging.DEBUG if debug else logging.INFO
        self.logger = StockAnalysisLogger(
            log_level=log_level,
            log_file=None,  # 不保存到文件
            enable_console=True
        )
        
        print(f"✅ 中国A股TradingAgents系统初始化完成")
        print(f"📊 LLM提供商: {llm_provider}")
        print(f"🔍 分析师团队: {', '.join(self.selected_analysts)}")
    
    @log_analysis_method
    def analyze_stock(self, stock_code: str, trade_date: str = None) -> Dict[str, Any]:
        """
        分析股票 - 使用多个分析师的综合分析
        
        Args:
            stock_code: 股票代码
            trade_date: 交易日期
            
        Returns:
            分析结果字典
        """
        start_time = time.time()
        
        # 设置默认日期
        if not trade_date:
            trade_date = datetime.now().strftime("%Y-%m-%d")
        
        # 格式化股票代码
        formatted_code = format_stock_code(stock_code)
        
        # 验证股票代码
        if not is_valid_china_stock_code(formatted_code):
            return {
                "error": f"无效的股票代码: {stock_code}",
                "stock_code": formatted_code,
                "trade_date": trade_date
            }
        
        self.logger.log_analysis_start(formatted_code, trade_date)
        
        analysis_result = {
            "stock_code": formatted_code,
            "trade_date": trade_date,
            "analysis_time": datetime.now().isoformat(),
            "analysts_used": self.selected_analysts,
            "reports": {}
        }
        
        try:
            # 1. 获取基础数据
            if "market" in self.selected_analysts:
                self.logger.log_analysis_step("获取股票基础数据和技术指标")
                market_data = get_china_stock_data_online(formatted_code, trade_date, trade_date)
                technical_indicators = get_china_stockstats_indicators_report_online(formatted_code, trade_date)
                
                # 使用LLM进行技术分析
                market_analysis = self._analyze_with_llm(
                    "市场技术分析师",
                    f"请对以下股票数据进行专业的技术分析：\n\n{market_data}\n\n技术指标：\n{technical_indicators}",
                    formatted_code
                )
                
                analysis_result["reports"]["market_analysis"] = {
                    "raw_data": market_data,
                    "technical_indicators": technical_indicators,
                    "analysis": market_analysis
                }
            
            # 2. 新闻分析
            if "news" in self.selected_analysts:
                self.logger.log_analysis_step("获取和分析相关新闻")
                news_data = get_china_stock_news_online(formatted_code, trade_date)
                
                news_analysis = self._analyze_with_llm(
                    "新闻分析师",
                    f"请分析以下新闻对股票{formatted_code}的影响：\n\n{news_data}",
                    formatted_code
                )
                
                analysis_result["reports"]["news_analysis"] = {
                    "raw_data": news_data,
                    "analysis": news_analysis
                }
            
            # 3. 基本面分析
            if "fundamentals" in self.selected_analysts:
                self.logger.log_analysis_step("获取和分析基本面数据")
                fundamentals_data = get_china_fundamentals_online(formatted_code, trade_date)
                
                fundamentals_analysis = self._analyze_with_llm(
                    "基本面分析师",
                    f"请对以下基本面数据进行分析：\n\n{fundamentals_data}",
                    formatted_code
                )
                
                analysis_result["reports"]["fundamentals_analysis"] = {
                    "raw_data": fundamentals_data,
                    "analysis": fundamentals_analysis
                }
            
            # 4. 市场情绪分析
            if "sentiment" in self.selected_analysts:
                self.logger.log_analysis_step("分析市场情绪")
                sentiment_data = get_china_market_sentiment_online(trade_date)
                
                sentiment_analysis = self._analyze_with_llm(
                    "情绪分析师",
                    f"请分析当前市场情绪对股票{formatted_code}的影响：\n\n{sentiment_data}",
                    formatted_code
                )
                
                analysis_result["reports"]["sentiment_analysis"] = {
                    "raw_data": sentiment_data,
                    "analysis": sentiment_analysis
                }
            
            # 5. 综合投资建议
            self.logger.log_analysis_step("生成综合投资建议")
            
            # 整合所有分析报告
            all_reports = "\n\n".join([
                f"=== {report_type.upper()} ===\n{report_data['analysis']}"
                for report_type, report_data in analysis_result["reports"].items()
            ])
            
            final_recommendation = self._analyze_with_llm(
                "首席投资顾问",
                f"""基于以下多维度分析报告，请给出对股票{formatted_code}的最终投资建议：

{all_reports}

请提供：
1. 综合评级（买入/持有/卖出）
2. 目标价位
3. 风险提示
4. 投资建议
5. 关键因素分析""",
                formatted_code
            )
            
            analysis_result["final_recommendation"] = final_recommendation
            analysis_result["status"] = "success"
            
            # 计算分析耗时
            analysis_result["analysis_duration"] = time.time() - start_time
            
            # 保存分析结果到markdown文件
            self._save_analysis_to_markdown(analysis_result)
            
            self.logger.log_analysis_step(f"分析完成，耗时 {analysis_result['analysis_duration']:.2f} 秒")
            
            # 打印完整结果
            print("\n📊 多代理分析结果:")
            print(json.dumps(analysis_result, ensure_ascii=False, indent=2))
            
            return analysis_result
            
        except Exception as e:
            error_msg = f"分析过程中发生错误: {str(e)}"
            self.logger.log_analysis_step(error_msg)
            analysis_result["status"] = "error"
            analysis_result["error"] = error_msg
            return analysis_result
    
    def _analyze_with_llm(self, analyst_role: str, prompt: str, stock_code: str) -> str:
        """
        使用LLM进行分析
        
        Args:
            analyst_role: 分析师角色
            prompt: 分析提示
            stock_code: 股票代码
            
        Returns:
            分析结果
        """
        self.logger.log_llm_request("qwen", "qwen-max", analyst_role)
        
        try:
            # 构建系统提示
            system_prompt = f"""你是一位专业的{analyst_role}，专门分析中国A股市场。
            
请用专业、客观的态度进行分析，提供有价值的投资洞察。
分析应该包含具体的数据支撑和明确的结论。

特别注意中国A股市场的特点：
- T+1交易制度
- 涨跌停板限制
- 政策敏感性
- 散户比例较高
- 题材炒作特征
"""
            
            # 调用LLM
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            response = self.llm_manager.chat_completion(
                provider_name="qwen",
                messages=messages,
                model="qwen-max"
            )
            
            return response
            
        except Exception as e:
            error_msg = f"{analyst_role}分析失败: {str(e)}"
            self.logger.log_analysis_step(error_msg)
            return error_msg
    
    def _save_analysis_to_markdown(self, analysis_result: Dict[str, Any]) -> None:
        """
        保存分析结果到Markdown文件
        
        Args:
            analysis_result: 分析结果
        """
        try:
            # 创建results目录
            os.makedirs("results", exist_ok=True)
            
            # 生成文件名
            stock_code_clean = analysis_result["stock_code"].replace(".", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{stock_code_clean}_{timestamp}_multiagent.markdown"
            filepath = os.path.join("results", filename)
            
            # 生成简化的markdown内容
            markdown_content = self._format_simple_analysis_as_markdown(analysis_result)
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"📁 分析结果已保存到: {os.path.abspath(filepath)}")
            self.logger.log_analysis_step("分析报告保存成功", {"文件路径": os.path.abspath(filepath)})
            
        except Exception as e:
            self.logger.log_error("保存分析结果失败", str(e))
    
    def _extract_analysis_from_state(self, final_state: Dict[str, Any]) -> Dict[str, Any]:
        """从最终状态中提取分析结果"""
        extracted = {}
        
        # 基本信息
        if "stock_code" in final_state:
            extracted["analyzed_stock_code"] = final_state["stock_code"]
        if "trade_date" in final_state:
            extracted["analyzed_trade_date"] = final_state["trade_date"]
        
        # 各类分析报告
        if "market_report" in final_state:
            extracted["market_analysis"] = final_state["market_report"]
        if "news_report" in final_state:
            extracted["news_analysis"] = final_state["news_report"]
        if "fundamentals_report" in final_state:
            extracted["fundamental_analysis"] = final_state["fundamentals_report"]
        if "sentiment_report" in final_state:
            extracted["sentiment_analysis"] = final_state["sentiment_report"]
        
        # 投资辩论结果
        if "investment_debate_state" in final_state:
            debate_state = final_state["investment_debate_state"]
            extracted["investment_debate"] = {
                "bull_arguments": debate_state.get("bull_history", []),
                "bear_arguments": debate_state.get("bear_history", []),
                "debate_history": debate_state.get("history", []),
                "final_recommendation": debate_state.get("current_response", "")
            }
        
        # 风险管理辩论结果
        if "risk_debate_state" in final_state:
            risk_state = final_state["risk_debate_state"]
            extracted["risk_analysis"] = {
                "aggressive_view": risk_state.get("aggressive_history", []),
                "conservative_view": risk_state.get("conservative_history", []),
                "neutral_view": risk_state.get("neutral_history", []),
                "risk_assessment": risk_state.get("current_response", "")
            }
        
        # 最终交易决策
        if "final_trade_decision" in final_state:
            extracted["final_decision"] = final_state["final_trade_decision"]
        
        # 交易员分析
        if "trader_report" in final_state:
            extracted["trader_analysis"] = final_state["trader_report"]
        
        return extracted
    
    def _generate_comprehensive_report(self, final_state: Dict[str, Any], processed_signal: str) -> str:
        """生成综合分析报告"""
        try:
            # 收集所有分析结果
            reports = []
            
            if "market_report" in final_state:
                reports.append(f"📈 **市场技术分析**:\n{final_state['market_report']}")
            
            if "news_report" in final_state:
                reports.append(f"📰 **新闻面分析**:\n{final_state['news_report']}")
            
            if "fundamentals_report" in final_state:
                reports.append(f"💰 **基本面分析**:\n{final_state['fundamentals_report']}")
            
            if "sentiment_report" in final_state:
                reports.append(f"😊 **市场情绪分析**:\n{final_state['sentiment_report']}")
            
            # 投资辩论总结
            if "investment_debate_state" in final_state:
                debate_state = final_state["investment_debate_state"]
                reports.append(f"🎯 **投资决策辩论**:\n{debate_state.get('current_response', '无辩论结果')}")
            
            # 风险评估总结
            if "risk_debate_state" in final_state:
                risk_state = final_state["risk_debate_state"]
                reports.append(f"⚠️ **风险管理评估**:\n{risk_state.get('current_response', '无风险评估')}")
            
            # 交易员决策
            if "trader_report" in final_state:
                reports.append(f"💼 **交易员决策**:\n{final_state['trader_report']}")
            
            # 最终决策
            if "final_trade_decision" in final_state:
                reports.append(f"🎯 **最终交易决策**:\n{final_state['final_trade_decision']}")
            
            # 处理后的信号
            reports.append(f"📊 **处理后信号**: {processed_signal}")
            
            # 组合报告
            comprehensive_report = "\n\n" + "="*50 + "\n\n".join(reports)
            
            return comprehensive_report
            
        except Exception as e:
            self.logger.log_error("生成综合报告失败", str(e))
            return f"综合报告生成失败: {str(e)}"
    
    def batch_analyze(self, stock_codes: List[str], trade_date: str = None) -> Dict[str, Any]:
        """
        批量分析多只股票
        
        Args:
            stock_codes: 股票代码列表
            trade_date: 交易日期
            
        Returns:
            Dict: 批量分析结果
        """
        print(f"\n🎯 开始批量多代理分析 {len(stock_codes)} 只股票...")
        
        results = {}
        for i, code in enumerate(stock_codes, 1):
            print(f"\n进度: {i}/{len(stock_codes)} - {code}")
            results[code] = self.analyze_stock(code, trade_date)
        
        print("\n✅ 批量分析完成!")
        return results
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        try:
            graph_status = self.trading_graph.get_current_portfolio_status()
            analysis_summary = self.trading_graph.get_analysis_summary()
        except:
            graph_status = {}
            analysis_summary = {}
        
        return {
            "system": "中国A股TradingAgents多代理系统",
            "version": "2.0.0",
            "environment": self.environment,
            "llm_provider": self.llm_provider,
            "selected_analysts": self.selected_analysts,
            "config_valid": validate_china_config(self.config)[0],
            "graph_status": graph_status,
            "analysis_summary": analysis_summary
        }
    
    def reflect_and_remember(self, returns_losses: float):
        """
        反思和记忆交易结果
        
        Args:
            returns_losses: 收益或损失
        """
        try:
            self.trading_graph.reflect_and_remember(returns_losses)
            self.logger.log_analysis_step("反思和记忆完成", {"收益损失": returns_losses})
            print(f"🧠 反思和记忆完成，收益/损失: {returns_losses}")
        except Exception as e:
            error_msg = f"反思和记忆失败: {str(e)}"
            self.logger.log_error("反思记忆失败", error_msg)
            print(f"❌ {error_msg}")
    
    def switch_llm_provider(self, provider: str):
        """
        切换LLM提供商
        
        Args:
            provider: 新的LLM提供商
        """
        try:
            self.trading_graph.switch_llm_provider(provider)
            self.llm_provider = provider
            self.logger.log_analysis_step("LLM提供商切换", {"新提供商": provider})
            print(f"🔄 LLM提供商已切换为: {provider}")
        except Exception as e:
            error_msg = f"LLM提供商切换失败: {str(e)}"
            self.logger.log_error("LLM切换失败", error_msg)
            print(f"❌ {error_msg}")
    
    def update_config(self, new_config: Dict[str, Any]):
        """
        更新系统配置
        
        Args:
            new_config: 新的配置字典
        """
        try:
            self.config.update(new_config)
            self.trading_graph.update_config(new_config)
            self.logger.log_analysis_step("配置更新", {"更新项": list(new_config.keys())})
            print(f"⚙️ 配置已更新: {list(new_config.keys())}")
        except Exception as e:
            error_msg = f"配置更新失败: {str(e)}"
            self.logger.log_error("配置更新失败", error_msg)
            print(f"❌ {error_msg}")
    
    def _format_simple_analysis_as_markdown(self, analysis_result: Dict[str, Any]) -> str:
        """
        将分析结果格式化为markdown格式
        
        Args:
            analysis_result: 分析结果字典
            
        Returns:
            str: markdown格式的内容
        """
        # 获取各个分析报告
        reports = analysis_result.get('reports', {})
        
        # 市场分析
        market_analysis = reports.get('market_analysis', {}).get('analysis', '暂无数据')
        market_data = reports.get('market_analysis', {}).get('raw_data', '暂无数据')
        technical_indicators = reports.get('market_analysis', {}).get('technical_indicators', '暂无数据')
        
        # 新闻分析
        news_analysis = reports.get('news_analysis', {}).get('analysis', '暂无数据')
        news_data = reports.get('news_analysis', {}).get('raw_data', '暂无数据')
        
        # 基本面分析
        fundamentals_analysis = reports.get('fundamentals_analysis', {}).get('analysis', '暂无数据')
        fundamentals_data = reports.get('fundamentals_analysis', {}).get('raw_data', '暂无数据')
        
        # 情绪分析
        sentiment_analysis = reports.get('sentiment_analysis', {}).get('analysis', '暂无数据')
        sentiment_data = reports.get('sentiment_analysis', {}).get('raw_data', '暂无数据')
        
        content = f"""# 🏮 中国A股分析报告

## 📊 基本信息

- **股票代码**: {analysis_result.get('stock_code', 'N/A')}
- **分析日期**: {analysis_result.get('trade_date', 'N/A')}
- **生成时间**: {analysis_result.get('analysis_time', 'N/A')}
- **参与分析师**: {', '.join(analysis_result.get('analysts_used', []))}
- **执行时间**: {analysis_result.get('analysis_duration', 'N/A'):.2f}秒

---

## 📈 市场技术分析

### 原始数据
```
{market_data}
```

### 技术指标
```
{technical_indicators}
```

### AI分析结果
{market_analysis}

---

## 📰 新闻面分析

### 新闻数据
```
{news_data}
```

### AI分析结果
{news_analysis}

---

## 💰 基本面分析

### 基本面数据
```
{fundamentals_data}
```

### AI分析结果
{fundamentals_analysis}

---

## 😊 市场情绪分析

### 情绪数据
```
{sentiment_data}
```

### AI分析结果
{sentiment_analysis}

---

## 🎯 最终投资建议

{analysis_result.get('final_recommendation', '暂无最终建议')}

---

## ⚠️ 免责声明

本分析报告由AI系统生成，仅供参考，不构成投资建议。股市有风险，投资需谨慎。请根据自身情况和风险承受能力做出投资决策。

---

*报告生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}*  
*系统版本: 中国A股TradingAgents v2.0.0*  
*分析状态: {analysis_result.get('status', 'N/A')}*
"""
        return content
    
    def _format_debate_history(self, history: List[str]) -> str:
        """格式化辩论历史"""
        if not history:
            return "暂无相关观点"
        
        formatted = []
        for i, item in enumerate(history, 1):
            formatted.append(f"{i}. {item}")
        
        return "\n".join(formatted)


def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="中国A股TradingAgents多代理分析系统")
    parser.add_argument("stock_code", nargs="?", help="股票代码，如：000001 或 600000")
    parser.add_argument("--date", "-d", help="分析日期，格式：YYYY-MM-DD")
    parser.add_argument("--env", "-e", choices=["default", "production", "test"], 
                       default="default", help="运行环境")
    parser.add_argument("--debug", action="store_true", help="开启调试模式")
    parser.add_argument("--batch", "-b", help="批量分析文件（每行一个股票代码）")
    parser.add_argument("--status", "-s", action="store_true", help="显示系统状态")
    parser.add_argument("--output", "-o", help="输出文件路径（JSON格式）")
    parser.add_argument("--analysts", "-a", nargs="+", 
                       choices=["market", "news", "fundamentals"],
                       default=["market", "news", "fundamentals"],
                       help="选择参与的分析师")
    parser.add_argument("--llm", "-l", choices=["qwen", "zhipu", "baichuan", "ernie"],
                       default="qwen", help="选择LLM提供商")
    parser.add_argument("--reflect", "-r", type=float, help="反思交易结果（收益/损失）")
    
    args = parser.parse_args()
    
    # 创建系统实例
    system = ChinaAShareTradingAgents(
        environment=args.env, 
        debug=args.debug,
        selected_analysts=args.analysts,
        llm_provider=args.llm
    )
    
    # 反思和记忆
    if args.reflect is not None:
        system.reflect_and_remember(args.reflect)
        return
    
    # 显示系统状态
    if args.status:
        status = system.get_system_status()
        print("\n📊 多代理系统状态:")
        print(json.dumps(status, indent=2, ensure_ascii=False))
        return
    
    # 批量分析
    if args.batch:
        try:
            with open(args.batch, 'r', encoding='utf-8') as f:
                stock_codes = [line.strip() for line in f if line.strip()]
            
            results = system.batch_analyze(stock_codes, args.date)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                print(f"📁 结果已保存到: {args.output}")
            else:
                print("\n📊 批量分析结果:")
                print(json.dumps(results, indent=2, ensure_ascii=False))
                
        except FileNotFoundError:
            print(f"❌ 找不到批量分析文件: {args.batch}")
        return
    
    # 单只股票分析
    if args.stock_code:
        result = system.analyze_stock(args.stock_code, args.date)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"📁 结果已保存到: {args.output}")
        else:
            print("\n📊 多代理分析结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # 交互式模式
        print("🚀 欢迎使用中国A股TradingAgents多代理分析系统!")
        print("请输入股票代码进行分析，或输入 'quit' 退出")
        print(f"当前分析师团队: {', '.join(args.analysts)}")
        print(f"当前LLM提供商: {args.llm}")
        
        while True:
            try:
                stock_code = input("\n请输入股票代码: ").strip()
                if stock_code.lower() in ['quit', 'exit', 'q']:
                    print("👋 再见!")
                    break
                
                if not stock_code:
                    continue
                
                result = system.analyze_stock(stock_code, args.date)
                print("\n📊 多代理分析结果:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
            except KeyboardInterrupt:
                print("\n👋 再见!")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    main() 