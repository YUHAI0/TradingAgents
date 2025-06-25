#!/usr/bin/env python3
"""
中国A股TradingAgents CLI启动脚本
简化版本，直接调用分析系统
"""

import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def print_banner():
    """打印欢迎横幅"""
    banner = """
🏮 ================================= 🏮
   中国A股TradingAgents CLI v2.0.0
   多代理LLM金融交易框架 - 中国版
🏮 ================================= 🏮

🎯 功能特点:
• 🔍 多维度分析：技术面、基本面、新闻面、情绪面
• 🤖 国产LLM支持：通义千问、智谱AI、百川智能、文心一言
• 📊 实时数据：tushare、akshare等国内数据源
• 🇨🇳 A股优化：涨跌停、T+1、申万行业分类等

🚀 开始您的A股智能分析之旅！
"""
    print(banner)


def get_stock_input():
    """获取股票代码输入"""
    while True:
        stock_code = input("\n📈 请输入股票代码（如：000001、600000、000001.SZ）: ").strip()
        if not stock_code:
            print("❌ 股票代码不能为空，请重新输入")
            continue
        
        # 简单验证股票代码格式
        if len(stock_code) == 6 and stock_code.isdigit():
            # 自动添加交易所后缀
            if stock_code.startswith(('000', '002', '300')):
                stock_code = f"{stock_code}.SZ"
            elif stock_code.startswith(('600', '601', '603', '605', '688')):
                stock_code = f"{stock_code}.SH"
            else:
                stock_code = f"{stock_code}.SZ"
        elif stock_code.upper().endswith(('.SZ', '.SH')):
            stock_code = stock_code.upper()
        else:
            print("❌ 请输入有效的股票代码格式")
            continue
        
        return stock_code


def get_date_input():
    """获取分析日期输入"""
    default_date = datetime.now().strftime("%Y-%m-%d")
    date_input = input(f"\n📅 请输入分析日期（YYYY-MM-DD格式，默认今天 {default_date}）: ").strip()
    
    if not date_input:
        return default_date
    
    try:
        datetime.strptime(date_input, "%Y-%m-%d")
        return date_input
    except ValueError:
        print("❌ 日期格式错误，使用默认日期")
        return default_date


def select_analysts():
    """选择分析师"""
    analysts_options = {
        "1": "市场技术",
        "2": "新闻", 
        "3": "基本面",
        "4": "情绪",
        "5": "全部"
    }
    
    print("\n🤖 请选择分析师类型:")
    for key, value in analysts_options.items():
        print(f"  {key}. {value}分析师")
    
    while True:
        choice = input("\n请输入选择（1-5，默认5-全部）: ").strip()
        if not choice:
            choice = "5"
        
        if choice in analysts_options:
            if choice == "5":
                return ["市场技术", "新闻", "基本面", "情绪"]
            else:
                return [analysts_options[choice]]
        else:
            print("❌ 无效选择，请输入1-5")


def select_llm_provider():
    """选择LLM提供商"""
    providers = {
        "1": "qwen",
        "2": "zhipu", 
        "3": "baichuan",
        "4": "ernie"
    }
    
    print("\n🤖 请选择LLM提供商:")
    print("  1. 通义千问 (阿里云)")
    print("  2. 智谱AI (清华)")
    print("  3. 百川智能")
    print("  4. 文心一言 (百度)")
    
    while True:
        choice = input("\n请输入选择（1-4，默认1-通义千问）: ").strip()
        if not choice:
            choice = "1"
        
        if choice in providers:
            return providers[choice]
        else:
            print("❌ 无效选择，请输入1-4")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="中国A股TradingAgents CLI")
    parser.add_argument("--stock", "-s", help="股票代码")
    parser.add_argument("--date", "-d", help="分析日期 (YYYY-MM-DD)")
    parser.add_argument("--analysts", "-a", help="分析师类型（逗号分隔）")
    parser.add_argument("--provider", "-p", help="LLM提供商")
    parser.add_argument("--quiet", "-q", action="store_true", help="静默模式")
    
    args = parser.parse_args()
    
    if not args.quiet:
        print_banner()
    
    # 获取参数
    if args.stock:
        stock_code = args.stock
        if len(stock_code) == 6 and stock_code.isdigit():
            if stock_code.startswith(('000', '002', '300')):
                stock_code = f"{stock_code}.SZ"
            elif stock_code.startswith(('600', '601', '603', '605', '688')):
                stock_code = f"{stock_code}.SH"
            else:
                stock_code = f"{stock_code}.SZ"
    else:
        stock_code = get_stock_input()
    
    if args.date:
        analysis_date = args.date
    else:
        analysis_date = get_date_input()
    
    if args.analysts:
        selected_analysts = args.analysts.split(",")
    else:
        selected_analysts = select_analysts()
    
    if args.provider:
        llm_provider = args.provider
    else:
        llm_provider = select_llm_provider()
    
    print(f"\n🔍 分析配置:")
    print(f"  📈 股票代码: {stock_code}")
    print(f"  📅 分析日期: {analysis_date}")
    print(f"  🤖 分析师: {', '.join(selected_analysts)}")
    print(f"  🧠 LLM提供商: {llm_provider}")
    
    # 确认执行
    if not args.quiet:
        confirm = input("\n🚀 是否开始分析？(Y/n): ").strip().lower()
        if confirm and confirm != 'y' and confirm != 'yes':
            print("❌ 分析已取消")
            return
    
    print("\n🚀 正在启动中国A股TradingAgents分析系统...")
    
    try:
        # 导入并运行分析系统
        from china_trading_agents import ChinaAShareTradingAgents
        
        # 创建分析系统实例
        system = ChinaAShareTradingAgents(
            environment="default",
            debug=True,
            selected_analysts=selected_analysts,
            llm_provider=llm_provider
        )
        
        print(f"✅ 系统初始化成功")
        print(f"🔄 开始分析 {stock_code}...")
        
        # 执行分析
        result = system.analyze_stock(stock_code, analysis_date)
        
        if result.get("status") == "success":
            print("\n✅ 分析完成！")
            print(f"📄 报告已保存到: {result.get('report_file', 'results目录')}")
        else:
            print(f"\n❌ 分析失败: {result.get('error', '未知错误')}")
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已正确安装中国版TradingAgents模块")
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        print("请检查配置和网络连接")


if __name__ == "__main__":
    main() 