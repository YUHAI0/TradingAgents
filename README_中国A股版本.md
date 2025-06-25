# 中国A股TradingAgents系统

专门针对中国A股市场的多代理交易分析系统，整合国产数据源和大语言模型。

## 🌟 系统特点

### 💡 核心优势
- **🏮 完全国产化**：使用通义千问、智谱AI等国产大模型
- **📊 A股专业化**：针对A股市场特点深度定制
- **🔄 多维度分析**：技术面、基本面、新闻面、情绪面全覆盖
- **⚡ 实时数据**：集成tushare、akshare等国内权威数据源
- **🎯 智能建议**：基于多代理协作生成投资建议

### 🚀 主要功能
1. **技术分析**：KDJ、MACD、RSI等A股常用指标
2. **基本面分析**：财务数据、估值分析、行业对比
3. **新闻分析**：政策解读、公司公告、行业动态
4. **情绪分析**：散户情绪、机构态度、资金流向
5. **综合建议**：买入/持有/卖出建议及操作策略

## 📦 安装指南

### 环境要求
- Python 3.8+
- 互联网连接（获取实时数据）

### 1. 克隆项目
```bash
git clone <项目地址>
cd TradingAgents
```

### 2. 安装依赖
```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装中国数据源依赖
pip install tushare akshare
```

### 3. 配置API密钥
创建环境变量文件或直接设置：

```bash
# 必需的API密钥
export TUSHARE_TOKEN="你的tushare token"
export QWEN_API_KEY="你的通义千问API密钥"

# 可选的API密钥（提供更多LLM选择）
export ZHIPU_API_KEY="你的智谱AI密钥"
export BAICHUAN_API_KEY="你的百川智能密钥"
export ERNIE_API_KEY="你的文心一言API密钥"
export ERNIE_SECRET_KEY="你的文心一言Secret密钥"
```

## 🔑 API密钥获取指南

### 数据源API
1. **Tushare Pro**（必需）
   - 访问：https://tushare.pro/
   - 注册并获取token
   - 免费额度足够基本使用

### LLM API密钥
1. **通义千问**（推荐，主要LLM）
   - 访问：https://dashscope.aliyuncs.com/
   - 阿里云账号登录
   - 创建API密钥

2. **智谱AI**（备用LLM）
   - 访问：https://open.bigmodel.cn/
   - 注册并获取API密钥

3. **百川智能**（可选）
   - 访问：https://platform.baichuan-ai.com/
   - 注册并获取API密钥

4. **文心一言**（可选）
   - 访问：https://cloud.baidu.com/
   - 百度云控制台创建应用

## 🚀 使用方法

### 基本使用

#### 1. 命令行分析单只股票
```bash
# 分析平安银行
python china_trading_agents.py 000001

# 指定日期分析
python china_trading_agents.py 000001 --date 2024-01-15

# 使用生产环境配置
python china_trading_agents.py 000001 --env production
```

#### 2. 批量分析
```bash
# 创建股票列表文件
echo "000001" > stocks.txt
echo "600000" >> stocks.txt
echo "000858" >> stocks.txt

# 批量分析
python china_trading_agents.py --batch stocks.txt --output results.json
```

#### 3. 交互式模式
```bash
# 启动交互式分析
python china_trading_agents.py

# 按提示输入股票代码
请输入股票代码: 000001
请输入股票代码: 600036
请输入股票代码: quit  # 退出
```

#### 4. 系统状态检查
```bash
# 检查系统配置和API状态
python china_trading_agents.py --status
```

### 代码调用

```python
from china_trading_agents import ChinaAShareTradingAgents

# 创建系统实例
system = ChinaAShareTradingAgents(environment="production")

# 分析单只股票
result = system.analyze_stock("000001", "2024-01-15")
print(result)

# 批量分析
stocks = ["000001", "600000", "000858"]
results = system.batch_analyze(stocks)

# 查看系统状态
status = system.get_system_status()
print(status)
```

## 📊 输出结果示例

### 完整分析报告
```json
{
  "stock_code": "000001.SZ",
  "trade_date": "2024-01-15",
  "timestamp": "2024-01-15T10:30:00",
  "environment": "production",
  "technical_analysis": "技术分析：当前RSI为45.2，处于中性区间...",
  "fundamental_analysis": "基本面分析：公司ROE为13.5%，行业内位置...",
  "news_analysis": "新闻分析：近期政策利好银行股...",
  "sentiment_analysis": "情绪分析：当前市场情绪偏乐观...",
  "investment_advice": "综合建议：买入评级，目标价位..."
}
```

## ⚙️ 配置说明

### 环境配置
- **default**：默认配置，平衡性能和成本
- **production**：生产环境，使用最强模型
- **test**：测试环境，使用便宜模型节省成本

### 自定义配置
```python
from tradingagents.china_config import create_china_config

# 创建自定义配置
config = create_china_config("production")
config["max_debate_rounds"] = 5  # 增加分析深度
config["primary_llm_provider"] = "zhipu"  # 更换主要LLM

system = ChinaAShareTradingAgents(config=config)
```

## 🎯 A股市场特色功能

### 1. 涨跌停分析
- 自动识别涨跌停股票
- 分析涨停原因（题材、业绩、资金）
- 预测后续走势

### 2. 北向资金分析
- 沪深股通资金流向
- 外资持股变化
- 对个股影响评估

### 3. 政策影响分析
- 监管政策解读
- 行业政策影响
- 宏观政策传导

### 4. 概念板块分析
- 热点概念挖掘
- 板块联动效应
- 题材炒作识别

## 🛡️ 风险提示

### ⚠️ 重要声明
- 本系统仅供研究和学习使用
- 所有分析结果不构成投资建议
- 股市有风险，投资需谨慎
- 请结合自身风险承受能力做出投资决策

### 🔒 使用限制
- 请遵守相关法律法规
- 不得用于非法金融活动
- 注意保护API密钥安全
- 合理控制API调用频率

## 🔧 故障排除

### 常见问题

#### 1. API密钥错误
```bash
# 检查环境变量
echo $TUSHARE_TOKEN
echo $QWEN_API_KEY

# 重新设置
export TUSHARE_TOKEN="your_token_here"
```

#### 2. 数据获取失败
- 检查网络连接
- 确认API密钥有效
- 检查API调用次数限制

#### 3. LLM调用失败
- 检查LLM API密钥
- 切换到备用LLM提供商
- 降低并发调用频率

#### 4. 依赖包问题
```bash
# 重新安装依赖
pip uninstall tushare akshare -y
pip install tushare akshare --upgrade
```

## 📈 性能优化

### 1. 成本控制
- 测试阶段使用test环境
- 合理选择模型档次
- 缓存重复查询结果

### 2. 速度优化
- 使用快速模型处理简单任务
- 并行处理多个分析任务
- 预加载常用数据

### 3. 准确性提升
- 增加辩论轮数
- 使用更强的深度思考模型
- 结合多个数据源交叉验证

## 🤝 贡献指南

### 欢迎贡献
- 🐛 报告Bug
- 💡 提出新功能建议
- 📝 完善文档
- 🔧 提交代码改进

### 开发环境设置
```bash
# 克隆开发分支
git clone -b develop <项目地址>

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/
```

## 📞 支持与反馈

- 📧 邮箱：support@trading-agents.cn
- 💬 微信群：扫描二维码加入
- 🐛 Issue：GitHub Issues页面
- 📖 文档：详见docs目录

---

## 🎉 更新日志

### v1.0.0 (2024-01-15)
- 🎉 首次发布中国A股版本
- 🏮 完成国产化改造
- 📊 支持A股特色分析
- 🤖 集成国产大模型

---

**Happy Trading! 祝投资顺利！** 🚀📈 