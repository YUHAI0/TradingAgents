"""
中国A股数据获取工具
支持tushare、akshare、efinance、新浪财经等多种国内数据源
"""

import tushare as ts
import akshare as ak
import pandas as pd
from typing import Annotated, Dict, List, Optional
from datetime import datetime, timedelta
import requests
import json
import os
from .config import get_config

class ChinaStockDataProvider:
    """中国A股数据提供器 - 支持多数据源"""
    
    def __init__(self):
        self.config = get_config()
        # 初始化tushare - 优先从环境变量读取
        tushare_token = os.getenv('TUSHARE_TOKEN') or self.config.get('tushare_token')
        if tushare_token:
            ts.set_token(tushare_token)
            self.ts_pro = ts.pro_api()
            print(f"✅ Tushare已初始化，Token: {tushare_token[:10]}...")
        else:
            self.ts_pro = None
            print("⚠️ Tushare Token未配置，部分功能不可用")
            
        # 检查efinance是否可用
        try:
            import efinance as ef
            self.efinance = ef
            self.efinance_available = True
        except ImportError:
            self.efinance = None
            self.efinance_available = False
            print("⚠️ efinance未安装，部分功能不可用。安装命令: pip install efinance")
            
    def get_stock_basic_info(self, ts_code: str) -> Dict:
        """获取股票基本信息 - 多数据源支持"""
        try:
            # 方案1: 使用tushare获取基本信息
            if self.ts_pro:
                try:
                    df = self.ts_pro.stock_basic(ts_code=ts_code)
                    if not df.empty:
                        return df.iloc[0].to_dict()
                except Exception as e:
                    print(f"tushare获取失败: {e}")
            
            # 方案2: 使用efinance获取
            if self.efinance_available:
                try:
                    symbol = ts_code.split('.')[0]
                    stock_info = self.efinance.stock.get_base_info(symbol)
                    if stock_info:
                        return {"name": stock_info.get('股票简称', symbol)}
                except Exception as e:
                    print(f"efinance获取失败: {e}")
            
            # 方案3: 使用新浪财经接口
            try:
                symbol = ts_code.split('.')[0]
                if ts_code.endswith('.SH'):
                    sina_code = f"sh{symbol}"
                else:
                    sina_code = f"sz{symbol}"
                    
                url = f"http://hq.sinajs.cn/list={sina_code}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.text.strip()
                    if data and '=' in data:
                        info = data.split('=')[1].strip('"').split(',')
                        if len(info) > 0 and info[0]:
                            return {"name": info[0]}
            except Exception as e:
                print(f"新浪财经接口获取失败: {e}")
            
            # 方案4: 备用akshare方案
            try:
                symbol = ts_code.split('.')[0]
                df = ak.stock_individual_info_em(symbol=symbol)
                if not df.empty:
                    # 安全地查找公司名称
                    name_rows = df.loc[df['item'] == '公司名称', 'value']
                    if not name_rows.empty:
                        return {"name": name_rows.iloc[0]}
                    else:
                        # 如果没有找到公司名称，尝试其他可能的字段
                        possible_names = ['股票简称', '证券简称', '名称']
                        for name_field in possible_names:
                            name_rows = df.loc[df['item'] == name_field, 'value']
                            if not name_rows.empty:
                                return {"name": name_rows.iloc[0]}
                        return {"name": symbol}  # 如果都没有找到，返回股票代码
                else:
                    return {"name": symbol}
            except Exception as akshare_error:
                print(f"akshare获取失败: {akshare_error}")
                return {"name": symbol}
                
        except Exception as e:
            print(f"获取股票基本信息失败: {e}")
            return {"name": ts_code}
    
    def get_stock_price_data(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票价格数据 - 多数据源支持"""
        try:
            # 方案1: 使用tushare获取日线数据
            if self.ts_pro:
                try:
                    df = self.ts_pro.daily(ts_code=ts_code, start_date=start_date.replace('-', ''), 
                                         end_date=end_date.replace('-', ''))
                    if not df.empty:
                        df['trade_date'] = pd.to_datetime(df['trade_date'])
                        return df.sort_values('trade_date')
                except Exception as e:
                    print(f"tushare价格数据获取失败: {e}")
            
            # 方案2: 使用efinance获取
            if self.efinance_available:
                try:
                    symbol = ts_code.split('.')[0]
                    df = self.efinance.stock.get_quote_history(symbol, start=start_date, end=end_date)
                    if not df.empty:
                        # 标准化列名
                        df = df.rename(columns={
                            '日期': 'trade_date',
                            '开盘': 'open',
                            '收盘': 'close',
                            '最高': 'high',
                            '最低': 'low',
                            '成交量': 'vol'
                        })
                        return df
                except Exception as e:
                    print(f"efinance价格数据获取失败: {e}")
            
            # 方案3: 备用akshare方案
            try:
                symbol = ts_code.split('.')[0]
                df = ak.stock_zh_a_hist(symbol=symbol, period="daily", 
                                      start_date=start_date.replace('-', ''), 
                                      end_date=end_date.replace('-', ''))
                if not df.empty:
                    # 标准化akshare的列名（中文转英文）
                    column_mapping = {
                        '日期': 'trade_date',
                        '开盘': 'open', 
                        '收盘': 'close',
                        '最高': 'high',
                        '最低': 'low',
                        '成交量': 'vol',
                        '成交额': 'amount',
                        '振幅': 'amplitude',
                        '涨跌幅': 'pct_chg',
                        '涨跌额': 'change',
                        '换手率': 'turnover'
                    }
                    
                    # 重命名存在的列
                    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
                    
                    # 确保trade_date是datetime类型
                    if 'trade_date' in df.columns:
                        df['trade_date'] = pd.to_datetime(df['trade_date'])
                        
                return df
            except Exception as e:
                print(f"akshare价格数据获取失败: {e}")
            
            return pd.DataFrame()
            
        except Exception as e:
            print(f"获取股票价格数据失败: {e}")
            return pd.DataFrame()
    
    def get_stock_realtime_data(self, ts_code: str) -> Dict:
        """获取股票实时数据"""
        try:
            # 方案1: efinance实时数据
            if self.efinance_available:
                try:
                    symbol = ts_code.split('.')[0]
                    df = self.efinance.stock.get_realtime_quotes([symbol])
                    if not df.empty:
                        return df.iloc[0].to_dict()
                except Exception as e:
                    print(f"efinance实时数据获取失败: {e}")
            
            # 方案2: 新浪财经实时数据
            try:
                symbol = ts_code.split('.')[0]
                if ts_code.endswith('.SH'):
                    sina_code = f"sh{symbol}"
                else:
                    sina_code = f"sz{symbol}"
                    
                url = f"http://hq.sinajs.cn/list={sina_code}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.text.strip()
                    if data and '=' in data:
                        info = data.split('=')[1].strip('"').split(',')
                        if len(info) >= 31:
                            return {
                                "name": info[0],
                                "open": float(info[1]) if info[1] else 0,
                                "pre_close": float(info[2]) if info[2] else 0,
                                "current": float(info[3]) if info[3] else 0,
                                "high": float(info[4]) if info[4] else 0,
                                "low": float(info[5]) if info[5] else 0,
                                "volume": int(info[8]) if info[8] else 0,
                                "amount": float(info[9]) if info[9] else 0,
                                "date": info[30],
                                "time": info[31]
                            }
            except Exception as e:
                print(f"新浪财经实时数据获取失败: {e}")
            
            return {}
            
        except Exception as e:
            print(f"获取实时数据失败: {e}")
            return {}

def get_china_stock_data(
    ts_code: Annotated[str, "股票代码，如 '000001.SZ' 或 '600000.SH'"],
    start_date: Annotated[str, "开始日期，格式：YYYY-MM-DD"],
    end_date: Annotated[str, "结束日期，格式：YYYY-MM-DD"]
) -> str:
    """
    获取中国A股股票数据
    
    Args:
        ts_code: 股票代码，支持深交所(.SZ)和上交所(.SH)
        start_date: 开始日期
        end_date: 结束日期
    
    Returns:
        str: 格式化的股票数据报告
    """
    provider = ChinaStockDataProvider()
    
    # 获取基本信息
    basic_info = provider.get_stock_basic_info(ts_code)
    stock_name = basic_info.get('name', ts_code)
    
    # 获取价格数据
    df = provider.get_stock_price_data(ts_code, start_date, end_date)
    
    if df.empty:
        return f"## {ts_code} ({stock_name}) 无法获取数据"
    
    # 计算技术指标摘要
    if len(df) > 0:
        latest_price = df.iloc[-1]['close'] if 'close' in df.columns else 0
        price_change = ((latest_price - df.iloc[0]['close']) / df.iloc[0]['close'] * 100) if len(df) > 1 else 0
        
        result = f"""## {ts_code} ({stock_name}) 股票数据报告

### 基本信息
- 最新价格: {latest_price:.2f}
- 期间涨跌幅: {price_change:.2f}%
- 数据时间范围: {start_date} 至 {end_date}

### 价格走势数据
{df.to_string(index=False)}

### 市场表现分析
"""
        
        if price_change > 5:
            result += "- 股价表现强势，呈现明显上涨趋势\n"
        elif price_change < -5:
            result += "- 股价承压，呈现下跌态势\n"
        else:
            result += "- 股价相对稳定，震荡运行\n"
        
        return result
    
    return f"## {ts_code} ({stock_name}) 数据获取失败"

def get_china_stock_technical_indicators(
    ts_code: Annotated[str, "股票代码"],
    indicator: Annotated[str, "技术指标名称：sma, ema, macd, rsi, kdj, boll"],
    curr_date: Annotated[str, "当前交易日期，格式：YYYY-MM-DD"],
    period: Annotated[int, "计算周期，默认20日"] = 20
) -> str:
    """
    获取中国A股技术指标分析
    """
    provider = ChinaStockDataProvider()
    
    # 获取足够的历史数据
    end_date = datetime.strptime(curr_date, '%Y-%m-%d')
    start_date = end_date - timedelta(days=period * 3)  # 获取更多数据确保指标计算准确
    
    df = provider.get_stock_price_data(ts_code, start_date.strftime('%Y-%m-%d'), curr_date)
    
    if df.empty:
        return f"## {ts_code} 技术指标分析：数据获取失败"
    
    # 检查必要的数据列是否存在
    required_columns = ['close']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        # 尝试映射中文列名
        chinese_mapping = {
            'close': ['收盘', '收盘价', 'close'],
            'open': ['开盘', '开盘价', 'open'],  
            'high': ['最高', '最高价', 'high'],
            'low': ['最低', '最低价', 'low'],
            'vol': ['成交量', 'volume', 'vol']
        }
        
        for eng_col, chinese_options in chinese_mapping.items():
            for chinese_col in chinese_options:
                if chinese_col in df.columns and eng_col not in df.columns:
                    df[eng_col] = df[chinese_col]
                    break
    
    # 再次检查必要列
    if 'close' not in df.columns:
        return f"## {ts_code} 技术指标分析：数据格式不正确，缺少收盘价字段。可用字段：{list(df.columns)}"
    
    result = f"## {ts_code} {indicator.upper()}技术指标分析\n\n"
    
    try:
        if indicator.lower() == 'sma':
            # 简单移动平均线
            df[f'SMA_{period}'] = df['close'].rolling(window=period).mean()
            latest_sma = df[f'SMA_{period}'].iloc[-1]
            latest_price = df['close'].iloc[-1]
            
            result += f"### {period}日简单移动平均线(SMA)\n"
            result += f"- 当前SMA值: {latest_sma:.2f}\n"
            result += f"- 当前股价: {latest_price:.2f}\n"
            
            if latest_price > latest_sma:
                result += f"- 分析结论: 股价位于SMA{period}之上，呈现多头趋势\n"
            else:
                result += f"- 分析结论: 股价位于SMA{period}之下，呈现空头趋势\n"
        
        elif indicator.lower() == 'rsi':
            # RSI相对强弱指标
            try:
                delta = df['close'].diff()
                gain = delta.where(delta > 0, 0).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                
                # 安全的RSI计算，避免除零错误
                valid_indices = (loss != 0) & pd.notna(loss) & pd.notna(gain)
                if valid_indices.any():
                    rs = pd.Series(index=df.index, dtype=float)
                    rs[valid_indices] = gain[valid_indices] / loss[valid_indices]
                    rsi = 100 - (100 / (1 + rs))
                    
                    # 获取最后一个有效的RSI值
                    rsi_valid = rsi.dropna()
                    if len(rsi_valid) > 0:
                        latest_rsi = float(rsi_valid.iloc[-1])
                        result += f"### {period}日相对强弱指标(RSI)\n"
                        result += f"- 当前RSI值: {latest_rsi:.2f}\n"
                        
                        if latest_rsi > 70:
                            result += "- 分析结论: RSI超过70，股票可能超买，注意回调风险\n"
                        elif latest_rsi < 30:
                            result += "- 分析结论: RSI低于30，股票可能超卖，关注反弹机会\n"
                        else:
                            result += "- 分析结论: RSI处于正常区间，无明显超买超卖信号\n"
                    else:
                        result += f"### {period}日相对强弱指标(RSI)\n"
                        result += "- 数据不足，无法计算有效RSI值\n"
                else:
                    result += f"### {period}日相对强弱指标(RSI)\n"
                    result += "- 数据不足，无法计算RSI指标\n"
            except Exception as rsi_error:
                result += f"### {period}日相对强弱指标(RSI)\n"
                result += f"- RSI计算失败: {rsi_error}\n"
        
        else:
            result += f"### 技术指标 {indicator}\n"
            result += "- 暂不支持该技术指标，目前仅支持SMA和RSI\n"
            
    except Exception as e:
        result += f"### 技术指标计算失败\n"
        result += f"- 错误信息: {str(e)}\n"
        result += f"- 数据列: {list(df.columns)}\n"
    
    return result

def get_china_stock_news(
    ts_code: Annotated[str, "股票代码"],
    curr_date: Annotated[str, "当前日期"],
    days_back: Annotated[int, "回看天数"] = 7
) -> str:
    """
    获取中国A股相关新闻（使用akshare）
    """
    try:
        # 获取股票代码（去除交易所后缀）
        symbol = ts_code.split('.')[0]
        
        # 使用akshare获取个股新闻
        news_df = ak.stock_news_em(symbol=symbol)
        
        if news_df.empty:
            return f"## {ts_code} 新闻资讯：暂无相关新闻"
        
        # 取最新的新闻
        news_df = news_df.head(10)
        
        result = f"## {ts_code} 最新新闻资讯\n\n"
        
        for _, news in news_df.iterrows():
            result += f"### {news.get('新闻标题', '无标题')}\n"
            result += f"- 发布时间: {news.get('发布时间', '未知')}\n"
            result += f"- 新闻来源: {news.get('新闻来源', '未知')}\n"
            if '新闻内容' in news and pd.notna(news['新闻内容']):
                result += f"- 内容摘要: {str(news['新闻内容'])[:200]}...\n"
            result += "\n"
        
        return result
        
    except Exception as e:
        print(f"获取新闻失败: {e}")
        return f"## {ts_code} 新闻资讯获取失败: {str(e)}"

def get_china_market_sentiment(
    curr_date: Annotated[str, "当前日期"]
) -> str:
    """
    获取中国A股市场情绪指标
    """
    try:
        # 获取沪深300指数
        hs300_df = ak.stock_zh_index_daily(symbol="sh000300")
        
        if hs300_df.empty:
            return "## A股市场情绪分析：数据获取失败"
        
        # 取最近20个交易日数据
        recent_data = hs300_df.tail(20)
        
        # 计算涨跌比例
        up_days = (recent_data['close'] > recent_data['open']).sum()
        total_days = len(recent_data)
        up_ratio = up_days / total_days * 100
        
        # 计算波动率
        returns = recent_data['close'].pct_change().dropna()
        volatility = returns.std() * 100
        
        result = f"""## A股市场情绪分析报告

### 市场走势概况
- 分析基准: 沪深300指数
- 统计周期: 最近{total_days}个交易日
- 上涨交易日: {up_days}天
- 市场情绪指数: {up_ratio:.1f}%

### 情绪判断
"""
        
        if up_ratio >= 60:
            result += "- 市场情绪: 乐观偏强，多头情绪较为浓厚\n"
            result += "- 投资建议: 可适度参与，但需防范回调风险\n"
        elif up_ratio >= 40:
            result += "- 市场情绪: 中性震荡，多空力量相对平衡\n"
            result += "- 投资建议: 保持谨慎，选择性参与优质标的\n"
        else:
            result += "- 市场情绪: 偏向悲观，空头情绪相对占优\n"
            result += "- 投资建议: 降低仓位，等待市场企稳信号\n"
        
        result += f"\n### 风险提示\n- 市场波动率: {volatility:.2f}%\n"
        
        if volatility > 2:
            result += "- 市场波动较大，注意控制风险\n"
        else:
            result += "- 市场波动相对温和\n"
        
        return result
        
    except Exception as e:
        print(f"获取市场情绪失败: {e}")
        return f"## A股市场情绪分析失败: {str(e)}"

def get_china_stock_fundamentals(
    ts_code: Annotated[str, "股票代码"],
    curr_date: Annotated[str, "当前日期"]
) -> str:
    """
    获取中国A股基本面数据（使用tushare）
    """
    try:
        provider = ChinaStockDataProvider()
        
        # 获取基本信息
        basic_info = provider.get_stock_basic_info(ts_code)
        stock_name = basic_info.get('name', ts_code)
        
        result = f"## {ts_code} ({stock_name}) 基本面分析报告\n\n"
        
        # 使用tushare获取财务数据
        if provider.ts_pro:
            try:
                # 计算查询的年份范围（最近2年的年报数据）
                from datetime import datetime
                current_year = datetime.now().year
                start_date = f"{current_year-2}1231"
                end_date = f"{current_year}1231"
                
                # 1. 获取财务指标数据
                try:
                    fina_indicator = provider.ts_pro.fina_indicator(
                        ts_code=ts_code, 
                        start_date=start_date, 
                        end_date=end_date,
                        fields='ts_code,ann_date,end_date,eps,roe,roa,gross_profit_margin,net_profit_margin,debt_to_assets,current_ratio,quick_ratio'
                    )
                    
                    if not fina_indicator.empty:
                        latest_fina = fina_indicator.iloc[0]  # 最新一期数据
                        result += "### 📊 主要财务指标\n"
                        result += f"- **报告期**: {latest_fina.get('end_date', 'N/A')}\n"
                        result += f"- **每股收益(EPS)**: {latest_fina.get('eps', 'N/A')}\n"
                        result += f"- **净资产收益率(ROE)**: {latest_fina.get('roe', 'N/A')}%\n"
                        result += f"- **总资产收益率(ROA)**: {latest_fina.get('roa', 'N/A')}%\n"
                        result += f"- **毛利率**: {latest_fina.get('gross_profit_margin', 'N/A')}%\n"
                        result += f"- **净利率**: {latest_fina.get('net_profit_margin', 'N/A')}%\n"
                        result += f"- **资产负债率**: {latest_fina.get('debt_to_assets', 'N/A')}%\n"
                        result += f"- **流动比率**: {latest_fina.get('current_ratio', 'N/A')}\n"
                        result += f"- **速动比率**: {latest_fina.get('quick_ratio', 'N/A')}\n"
                        
                except Exception as e:
                    result += f"### 📊 主要财务指标\n- 财务指标获取失败: {str(e)}\n"
                
                # 2. 获取资产负债表数据
                try:
                    balance_sheet = provider.ts_pro.balancesheet(
                        ts_code=ts_code,
                        start_date=start_date,
                        end_date=end_date,
                        fields='ts_code,ann_date,end_date,total_assets,total_liab,total_hldr_eqy_exc_min_int'
                    )
                    
                    if not balance_sheet.empty:
                        latest_balance = balance_sheet.iloc[0]
                        result += "\n### 💰 资产负债状况\n"
                        
                        total_assets = latest_balance.get('total_assets', 0)
                        total_liab = latest_balance.get('total_liab', 0) 
                        total_equity = latest_balance.get('total_hldr_eqy_exc_min_int', 0)
                        
                        if total_assets and total_assets != 'N/A':
                            result += f"- **总资产**: {float(total_assets)/100000000:.2f}亿元\n"
                        else:
                            result += f"- **总资产**: N/A\n"
                            
                        if total_liab and total_liab != 'N/A':
                            result += f"- **总负债**: {float(total_liab)/100000000:.2f}亿元\n"
                        else:
                            result += f"- **总负债**: N/A\n"
                            
                        if total_equity and total_equity != 'N/A':
                            result += f"- **股东权益**: {float(total_equity)/100000000:.2f}亿元\n"
                        else:
                            result += f"- **股东权益**: N/A\n"
                            
                except Exception as e:
                    result += f"\n### 💰 资产负债状况\n- 资产负债数据获取失败: {str(e)}\n"
                
                # 3. 获取利润表数据
                try:
                    income = provider.ts_pro.income(
                        ts_code=ts_code,
                        start_date=start_date,
                        end_date=end_date,
                        fields='ts_code,ann_date,end_date,total_revenue,revenue,n_income,n_income_attr_p'
                    )
                    
                    if not income.empty:
                        latest_income = income.iloc[0]
                        result += "\n### 📈 盈利能力\n"
                        
                        revenue = latest_income.get('total_revenue', 0)
                        net_profit = latest_income.get('n_income_attr_p', 0)
                        
                        if revenue and revenue != 'N/A':
                            result += f"- **营业收入**: {float(revenue)/100000000:.2f}亿元\n"
                        else:
                            result += f"- **营业收入**: N/A\n"
                            
                        if net_profit and net_profit != 'N/A':
                            result += f"- **归母净利润**: {float(net_profit)/100000000:.2f}亿元\n"
                        else:
                            result += f"- **归母净利润**: N/A\n"
                        
                except Exception as e:
                    result += f"\n### 📈 盈利能力\n- 利润数据获取失败: {str(e)}\n"
                
                # 4. 基本面评估
                result += "\n### 🎯 投资价值评估\n"
                if not fina_indicator.empty:
                    latest_fina = fina_indicator.iloc[0]
                    roe = latest_fina.get('roe', 0)
                    eps = latest_fina.get('eps', 0)
                    debt_ratio = latest_fina.get('debt_to_assets', 0)
                    
                    try:
                        if roe and float(roe) > 15:
                            result += "- ✅ **ROE表现**: 净资产收益率较高，盈利能力较强\n"
                        elif roe and float(roe) > 8:
                            result += "- ⚠️ **ROE表现**: 净资产收益率中等，盈利能力一般\n"  
                        else:
                            result += "- ❌ **ROE表现**: 净资产收益率偏低，盈利能力较弱\n"
                            
                        if debt_ratio and float(debt_ratio) < 60:
                            result += "- ✅ **财务杠杆**: 资产负债率适中，财务风险可控\n"
                        elif debt_ratio and float(debt_ratio) < 80:
                            result += "- ⚠️ **财务杠杆**: 资产负债率偏高，需关注偿债能力\n"
                        else:
                            result += "- ❌ **财务杠杆**: 资产负债率过高，财务风险较大\n"
                            
                    except (ValueError, TypeError):
                        result += "- ⚠️ **数据质量**: 部分财务指标数据异常，建议详细核实\n"
                        
                result += "- 📝 **投资建议**: 基于财务数据分析，建议结合行业对比和市场环境进行综合判断\n"
                result += "- ⚠️ **风险提示**: 财务数据存在滞后性，请关注最新的经营动态和市场变化\n"
                
                return result
                
            except Exception as e:
                return f"## {ts_code} tushare基本面数据获取失败: {str(e)}"
        else:
            # 如果tushare不可用，提供基础信息
            result += "### ⚠️ 数据源状态\n"
            result += "- Tushare数据源不可用，无法获取详细财务数据\n"
            result += "- 请配置TUSHARE_TOKEN环境变量后重试\n"
            result += "\n### 📝 建议\n"
            result += "- 获取tushare积分和token: https://tushare.pro/\n"
            result += "- 基本面分析需要详细的财务数据支持\n"
            
            return result
            
    except Exception as e:
        return f"## {ts_code} 基本面分析失败: {str(e)}" 