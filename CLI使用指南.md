# 中国A股TradingAgents CLI使用指南

## 概述

中国A股TradingAgents CLI是一个基于多代理LLM的金融交易框架命令行界面，专门针对中国A股市场进行了优化。

## 功能特点

- 🔍 **多维度分析**：技术面、基本面、新闻面、情绪面分析
- 🤖 **国产LLM支持**：通义千问、智谱AI、百川智能、文心一言
- 📊 **实时数据**：tushare、akshare等国内数据源
- 🇨🇳 **A股优化**：涨跌停、T+1、申万行业分类等
- 🎨 **丰富界面**：基于Rich的美观终端界面
- 📝 **报告保存**：自动保存分析结果为Markdown文件

## 安装依赖

确保已安装所有必要的依赖：

```bash
pip install -r requirements_china.txt
```

## 使用方法

### 方法1：使用完整CLI模块（推荐）

```bash
# 启动交互式分析
python -m cli.china_main analyze

# 查看帮助
python -m cli.china_main --help
python -m cli.china_main analyze --help
```

### 方法2：使用简化版CLI

```bash
# 启动交互式分析
python china_cli.py

# 使用命令行参数
python china_cli.py --stock 000725 --date 2025-06-25 --analysts "市场技术,基本面" --provider qwen

# 查看帮助
python china_cli.py --help
```

## 配置要求

### 环境变量

创建`.env`文件并配置以下环境变量：

```bash
# Tushare Pro Token（必需）
TUSHARE_TOKEN=your_tushare_token_here

# 通义千问API Key（推荐）
QWEN_API_KEY=your_qwen_api_key_here

# 其他LLM API Keys（可选）
ZHIPU_API_KEY=your_zhipu_api_key_here
BAICHUAN_API_KEY=your_baichuan_api_key_here
ERNIE_API_KEY=your_ernie_api_key_here
```

### 获取API Keys

1. **Tushare Pro Token**：
   - 访问 [tushare.pro](https://tushare.pro)
   - 注册账号并获取Token

2. **通义千问API Key**：
   - 访问 [阿里云百炼](https://bailian.console.aliyun.com/)
   - 开通服务并获取API Key

## 交互式配置

CLI会引导您完成以下配置：

1. **股票代码**：输入6位数字代码（如：000725、600000）
2. **分析日期**：选择分析日期（YYYY-MM-DD格式）
3. **分析师团队**：选择多个分析师类型
   - 市场技术分析师
   - 新闻分析师
   - 基本面分析师
   - 市场情绪分析师
4. **研究深度**：选择分析深度
   - 浅层：快速分析
   - 中等：平衡分析
   - 深度：全面研究
5. **LLM提供商**：选择AI模型提供商
6. **思考引擎**：选择快速和深度思考模型

## 输出结果

### 实时界面

CLI提供美观的实时界面，包含：
- **代理进度**：显示各分析师的工作状态
- **实时消息**：显示分析过程中的关键信息
- **分析报告**：实时显示分析结果

### 保存文件

分析完成后，结果会自动保存为：
```
results/{股票代码}_{时间戳}_multiagent.markdown
```

### 报告内容

完整的分析报告包含：
- **分析师团队报告**
  - 市场技术分析
  - 新闻分析
  - 基本面分析
  - 市场情绪分析
- **研究团队决策**
- **交易团队计划**
- **投资组合管理决策**

## 故障排除

### 常见问题

1. **依赖缺失**：
   ```bash
   pip install typer rich questionary tushare akshare stockstats
   ```

2. **API Key问题**：
   - 检查`.env`文件是否存在
   - 确认API Key格式正确
   - 验证API Key有效性

3. **网络问题**：
   - 确保网络连接正常
   - 检查防火墙设置
   - 考虑使用代理

4. **数据获取失败**：
   - 检查Tushare Token是否有效
   - 确认股票代码格式正确
   - 验证交易日期是否为工作日

### 调试模式

启用调试模式查看详细信息：
```bash
# 在代码中设置debug=True
python china_cli.py --debug
```

## 支持的股票代码格式

- 6位数字：`000725`、`600000`
- 带后缀：`000725.SZ`、`600000.SH`
- 系统会自动格式化和验证

## 技术架构

- **前端**：Rich + Typer 命令行界面
- **后端**：LangGraph多代理框架
- **数据源**：Tushare Pro + AkShare
- **AI模型**：国产LLM（通义千问等）
- **存储**：本地Markdown文件

## 版本信息

- 版本：v2.0.0
- 适用市场：中国A股
- Python版本：3.9+

---

© [涛锐研究](https://github.com/TauricResearch) - 中国A股TradingAgents CLI 