#!/usr/bin/env python3
"""
中国A股TradingAgents环境设置脚本
自动配置环境并验证系统可用性
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要Python 3.8+")
        return False
    print(f"✅ Python版本: {sys.version}")
    return True

def install_dependencies():
    """安装依赖包"""
    print("📦 正在安装依赖包...")
    
    try:
        # 安装基础依赖
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_china.txt"
        ])
        print("✅ 依赖包安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def setup_api_keys():
    """设置API密钥"""
    print("\n🔑 API密钥配置")
    print("请设置以下环境变量（至少需要前两个）：")
    
    required_keys = [
        ("TUSHARE_TOKEN", "Tushare Pro Token（必需）", "https://tushare.pro/"),
        ("QWEN_API_KEY", "通义千问API密钥（必需）", "https://dashscope.aliyuncs.com/")
    ]
    
    optional_keys = [
        ("ZHIPU_API_KEY", "智谱AI API密钥（可选）", "https://open.bigmodel.cn/"),
        ("BAICHUAN_API_KEY", "百川智能API密钥（可选）", "https://platform.baichuan-ai.com/"),
        ("ERNIE_API_KEY", "文心一言API密钥（可选）", "https://cloud.baidu.com/"),
        ("ERNIE_SECRET_KEY", "文心一言Secret密钥（可选）", "https://cloud.baidu.com/")
    ]
    
    env_file_content = []
    
    print("\n必需的API密钥:")
    for key, name, url in required_keys:
        current_value = os.getenv(key)
        if current_value:
            print(f"✅ {name}: 已设置")
            env_file_content.append(f"{key}={current_value}")
        else:
            print(f"❌ {name}: 未设置")
            print(f"   获取地址: {url}")
            value = input(f"   请输入{name}（可留空稍后设置）: ").strip()
            if value:
                env_file_content.append(f"{key}={value}")
                os.environ[key] = value
    
    print("\n可选的API密钥:")
    for key, name, url in optional_keys:
        current_value = os.getenv(key)
        if current_value:
            print(f"✅ {name}: 已设置")
            env_file_content.append(f"{key}={current_value}")
        else:
            print(f"💡 {name}: 未设置（可选）")
            value = input(f"   请输入{name}（可留空）: ").strip()
            if value:
                env_file_content.append(f"{key}={value}")
                os.environ[key] = value
    
    # 创建.env文件
    if env_file_content:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write('\n'.join(env_file_content))
        print("✅ 环境变量已保存到.env文件")

def test_system():
    """测试系统功能"""
    print("\n🧪 正在测试系统功能...")
    
    try:
        # 导入主模块
        from china_trading_agents import ChinaAShareTradingAgents
        
        # 创建系统实例
        system = ChinaAShareTradingAgents(environment="test", debug=True)
        
        # 获取系统状态
        status = system.get_system_status()
        
        print("✅ 系统初始化成功")
        print(f"📊 可用LLM提供商: {', '.join(status['llm_providers'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ 系统测试失败: {e}")
        return False

def create_sample_files():
    """创建示例文件"""
    print("\n📝 创建示例文件...")
    
    # 创建示例股票列表
    sample_stocks = """000001
600000
000858
600036
002415"""
    
    with open('sample_stocks.txt', 'w', encoding='utf-8') as f:
        f.write(sample_stocks)
    
    # 创建快速测试脚本
    test_script = """#!/usr/bin/env python3
# 快速测试脚本
from china_trading_agents import ChinaAShareTradingAgents

# 创建系统实例
system = ChinaAShareTradingAgents(environment="test")

# 测试分析平安银行
print("正在分析平安银行(000001)...")
result = system.analyze_stock("000001")

print("分析完成!")
print(f"股票代码: {result['stock_code']}")
print(f"分析日期: {result['trade_date']}")
"""
    
    with open('quick_test.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ 示例文件创建完成:")
    print("  - sample_stocks.txt: 示例股票列表")
    print("  - quick_test.py: 快速测试脚本")

def show_usage_guide():
    """显示使用指南"""
    print("\n🚀 使用指南")
    print("="*50)
    
    usage_examples = [
        ("分析单只股票", "python china_trading_agents.py 000001"),
        ("指定日期分析", "python china_trading_agents.py 000001 --date 2024-01-15"),
        ("批量分析", "python china_trading_agents.py --batch sample_stocks.txt"),
        ("交互式模式", "python china_trading_agents.py"),
        ("系统状态", "python china_trading_agents.py --status"),
        ("快速测试", "python quick_test.py")
    ]
    
    for desc, cmd in usage_examples:
        print(f"📌 {desc}:")
        print(f"   {cmd}")
        print()

def main():
    """主函数"""
    print("🏮 中国A股TradingAgents环境设置")
    print("="*50)
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 安装依赖
    if not install_dependencies():
        return
    
    # 设置API密钥
    setup_api_keys()
    
    # 测试系统
    if test_system():
        # 创建示例文件
        create_sample_files()
        
        # 显示使用指南
        show_usage_guide()
        
        print("🎉 环境设置完成！系统已准备就绪")
        print("\n💡 提示:")
        print("- 如需修改API密钥，请编辑.env文件")
        print("- 详细使用说明请查看README_中国A股版本.md")
        print("- 遇到问题请检查API密钥和网络连接")
    else:
        print("\n❌ 环境设置失败，请检查:")
        print("1. API密钥是否正确")
        print("2. 网络连接是否正常")
        print("3. 依赖包是否安装完整")

if __name__ == "__main__":
    main() 