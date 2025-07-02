#!/usr/bin/env python3
"""中国A股LLM提供商管理器"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

# 尝试导入langchain，如果不可用则使用本地定义
try:
    from langchain_core.runnables import Runnable
    from langchain_core.messages import AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # 如果langchain不可用，定义简单的基类
    print("⚠️ 未找到langchain，使用简化版本")
    
    class Runnable:  # type: ignore
        def invoke(self, input, config=None, **kwargs):
            raise NotImplementedError
    
    class AIMessage:  # type: ignore
        def __init__(self, content):
            self.content = content
    
    LANGCHAIN_AVAILABLE = False

class BaseChinaLLMProvider(ABC):
    """中国LLM提供商基类"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        
    @abstractmethod
    def chat_completion(self, messages: List[Dict], model: str, **kwargs) -> str:
        """聊天完成接口"""
        pass

class QwenProvider(BaseChinaLLMProvider):
    """阿里通义千问提供商"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
        
    def chat_completion(self, messages: List[Dict], model: str = "qwen-turbo", **kwargs) -> str:
        """
        通义千问聊天完成 - 使用OpenAI兼容格式
        支持模型: qwen-turbo, qwen-plus, qwen-max
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 转换消息格式为OpenAI兼容格式
        qwen_messages = []
        for msg in messages:
            # 确保msg是字典格式
            if isinstance(msg, tuple) and len(msg) == 2:
                role, content = msg
                if role == "human":
                    role = "user"
                elif role == "ai":
                    role = "assistant"
                msg = {"role": role, "content": content}
            elif not isinstance(msg, dict):
                msg = {"role": "user", "content": str(msg)}
            
            if msg.get("role") == "user":
                qwen_messages.append({"role": "user", "content": msg["content"]})
            elif msg.get("role") == "assistant":
                qwen_messages.append({"role": "assistant", "content": msg["content"]})
            elif msg.get("role") == "system":
                qwen_messages.append({"role": "system", "content": msg["content"]})
        
        # OpenAI兼容格式的请求体
        payload = {
            "model": model,
            "messages": qwen_messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
            "top_p": kwargs.get("top_p", 0.9)
        }
        
        # 重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.base_url, 
                    headers=headers, 
                    json=payload, 
                    timeout=600,  # 增加超时时间到10分钟
                    verify=True  # 确保SSL验证
                )
                
                # 详细的错误调试信息
                if response.status_code != 200:
                    error_detail = ""
                    try:
                        error_json = response.json()
                        error_detail = f"错误详情: {error_json}"
                    except:
                        error_detail = f"响应内容: {response.text}"
                    
                    if attempt < max_retries - 1:
                        print(f"⚠️ 通义千问API调用失败，第{attempt + 1}次重试...")
                        continue
                    else:
                        return f"通义千问API调用失败: {response.status_code} {response.reason} - {error_detail}"
                
                result = response.json()
                # OpenAI兼容格式的响应解析
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    return f"通义千问响应错误: {result}"
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"⚠️ 通义千问API超时，第{attempt + 1}次重试...")
                    continue
                else:
                    return "通义千问API调用超时，请检查网络连接"
            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    print(f"⚠️ 通义千问API连接失败，第{attempt + 1}次重试...")
                    continue
                else:
                    return "通义千问API连接失败，请检查网络连接"
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ 通义千问网络请求失败，第{attempt + 1}次重试...")
                    continue
                else:
                    return f"通义千问网络请求失败: {str(e)}"
            except Exception as e:
                return f"通义千问API调用失败: {str(e)}"
        
        return "通义千问API调用失败: 所有重试都失败了"

class ZhipuProvider(BaseChinaLLMProvider):
    """智谱AI提供商"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://open.bigmodel.cn/api/paas/v4/chat/completions")
        
    def chat_completion(self, messages: List[Dict], model: str = "glm-4", **kwargs) -> str:
        """
        智谱AI聊天完成
        支持模型: glm-4, glm-4-flash, glm-3-turbo
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
            "top_p": kwargs.get("top_p", 0.9),
            "stream": False
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=600)
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return f"智谱AI响应错误: {result}"
                
        except Exception as e:
            return f"智谱AI API调用失败: {str(e)}"

class BaichuanProvider(BaseChinaLLMProvider):
    """百川智能提供商"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://api.baichuan-ai.com/v1/chat/completions")
        
    def chat_completion(self, messages: List[Dict], model: str = "Baichuan2-Turbo", **kwargs) -> str:
        """
        百川智能聊天完成
        支持模型: Baichuan2-Turbo, Baichuan2-53B
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
            "top_p": kwargs.get("top_p", 0.9)
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=600)
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return f"百川智能响应错误: {result}"
                
        except Exception as e:
            return f"百川智能API调用失败: {str(e)}"

class ErnieProvider(BaseChinaLLMProvider):
    """百度文心一言提供商"""
    
    def __init__(self, api_key: str, secret_key: str):
        self.secret_key = secret_key
        super().__init__(api_key, "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions")
        self.access_token = self._get_access_token()
        
    def _get_access_token(self) -> str:
        """获取百度API访问令牌"""
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            result = response.json()
            return result.get("access_token", "")
        except Exception as e:
            print(f"获取百度访问令牌失败: {e}")
            return ""
    
    def chat_completion(self, messages: List[Dict], model: str = "ernie-bot-turbo", **kwargs) -> str:
        """
        文心一言聊天完成
        支持模型: ernie-bot-turbo, ernie-bot
        """
        if not self.access_token:
            return "文心一言访问令牌获取失败"
            
        url = f"{self.base_url}?access_token={self.access_token}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 0.9),
            "penalty_score": kwargs.get("penalty_score", 1.0)
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=600)
            response.raise_for_status()
            
            result = response.json()
            if "result" in result:
                return result["result"]
            else:
                return f"文心一言响应错误: {result}"
                
        except Exception as e:
            return f"文心一言API调用失败: {str(e)}"

class ChinaLLMManager:
    """中国LLM管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """初始化所有可用的提供商 - 优先从环境变量读取API密钥"""
        
        # 通义千问 - 优先从环境变量读取
        qwen_api_key = os.getenv("QWEN_API_KEY") or self.config.get("qwen_api_key")
        if qwen_api_key:
            self.providers["qwen"] = QwenProvider(qwen_api_key)
            print(f"✅ 通义千问已初始化，API Key: {qwen_api_key[:10]}...")
        
        # 智谱AI
        zhipu_api_key = os.getenv("ZHIPU_API_KEY") or self.config.get("zhipu_api_key")
        if zhipu_api_key:
            self.providers["zhipu"] = ZhipuProvider(zhipu_api_key)
            print(f"✅ 智谱AI已初始化，API Key: {zhipu_api_key[:10]}...")
        
        # 百川智能
        baichuan_api_key = os.getenv("BAICHUAN_API_KEY") or self.config.get("baichuan_api_key")
        if baichuan_api_key:
            self.providers["baichuan"] = BaichuanProvider(baichuan_api_key)
            print(f"✅ 百川智能已初始化，API Key: {baichuan_api_key[:10]}...")
        
        # 文心一言
        ernie_api_key = os.getenv("ERNIE_API_KEY") or self.config.get("ernie_api_key")
        ernie_secret_key = os.getenv("ERNIE_SECRET_KEY") or self.config.get("ernie_secret_key")
        if ernie_api_key and ernie_secret_key:
            self.providers["ernie"] = ErnieProvider(ernie_api_key, ernie_secret_key)
            print(f"✅ 文心一言已初始化，API Key: {ernie_api_key[:10]}...")
        
        if not self.providers:
            print("⚠️ 没有可用的LLM提供商，请检查API密钥配置")
    
    def get_provider(self, provider_name: str) -> Optional[BaseChinaLLMProvider]:
        """获取指定的提供商"""
        return self.providers.get(provider_name)
    
    def chat_completion(self, provider_name: str, messages: List[Dict], model: str, **kwargs) -> str:
        """统一的聊天完成接口"""
        provider = self.get_provider(provider_name)
        if not provider:
            return f"提供商 {provider_name} 未配置或不可用"
        
        return provider.chat_completion(messages, model, **kwargs)
    
    def list_available_providers(self) -> List[str]:
        """列出所有可用的提供商"""
        return list(self.providers.keys())
    
    def get_llm(self, provider: str = "qwen", model_type: str = "standard"):
        """
        获取LLM实例 - 为了兼容现有代码
        
        Args:
            provider: 提供商名称 (qwen, zhipu, baichuan, ernie)
            model_type: 模型类型 (standard, fast, advanced)
        
        Returns:
            LLM提供商实例
        """
        # 根据model_type选择合适的模型
        model_mapping = {
            "qwen": {
                "fast": "qwen-turbo",
                "standard": "qwen-plus", 
                "advanced": "qwen-max"
            },
            "zhipu": {
                "fast": "glm-4-flash",
                "standard": "glm-4",
                "advanced": "glm-4"
            },
            "baichuan": {
                "fast": "Baichuan2-Turbo",
                "standard": "Baichuan2-Turbo",
                "advanced": "Baichuan2-53B"
            },
            "ernie": {
                "fast": "ernie-bot-turbo",
                "standard": "ernie-bot",
                "advanced": "ernie-bot"
            }
        }
        
        # 如果指定的提供商不可用，尝试使用第一个可用的
        if provider not in self.providers and self.providers:
            provider = list(self.providers.keys())[0]
            print(f"⚠️ 指定的提供商不可用，使用 {provider}")
        
        selected_provider = self.get_provider(provider)
        if selected_provider:
            # 创建一个包装类，使其兼容现有接口
            class LLMWrapper(Runnable):  # type: ignore
                def __init__(self, provider_instance, model):
                    self.provider = provider_instance
                    self.model = model
                    self.current_provider = provider
                    self._bound_tools = []
                
                def invoke(self, input, config=None, **kwargs):
                    # 处理不同的输入格式
                    if isinstance(input, dict) and "messages" in input:
                        # 直接传入字典格式: {"messages": [...]}
                        messages = input["messages"]
                    elif hasattr(input, 'to_messages'):
                        # ChatPromptValue对象，调用to_messages()方法
                        messages = input.to_messages()
                    elif isinstance(input, (list, tuple)):
                        # 直接传入消息列表
                        messages = input
                    else:
                        # 其他格式，尝试直接使用
                        messages = input
                    
                    # 统一消息格式处理
                    formatted_messages = self._format_messages(messages)
                    
                    # 调用提供商获取响应
                    response_text = self.provider.chat_completion(formatted_messages, self.model, **kwargs)
                    
                    # 始终返回AIMessage对象以保持一致性
                    return AIMessage(content=response_text)
                
                def _format_messages(self, messages):
                    """格式化消息为标准字典格式"""
                    if isinstance(messages, str):
                        return [{"role": "user", "content": messages}]
                    
                    if not messages:
                        # 如果消息为空，返回一个默认消息
                        return [{"role": "user", "content": "请继续分析"}]
                    
                    formatted = []
                    for msg in messages:
                        # 跳过RemoveMessage对象
                        if hasattr(msg, '__class__') and 'RemoveMessage' in str(msg.__class__):
                            continue
                            
                        if isinstance(msg, tuple) and len(msg) == 2:
                            # 处理元组格式: ("role", "content")
                            role, content = msg
                            if role == "human":
                                role = "user"
                            elif role == "ai":
                                role = "assistant"
                            formatted.append({"role": role, "content": content})
                        elif isinstance(msg, dict):
                            # 已经是字典格式，但要确保有role和content字段
                            if "role" in msg and "content" in msg:
                                formatted.append(msg)
                            else:
                                formatted.append({"role": "user", "content": str(msg)})
                        elif hasattr(msg, 'content'):
                            # 处理有content属性的消息对象（如HumanMessage, AIMessage等）
                            if hasattr(msg, 'type'):
                                role = "user" if msg.type == "human" else "assistant"
                            else:
                                # 根据类名判断角色
                                class_name = msg.__class__.__name__.lower()
                                if "human" in class_name:
                                    role = "user"
                                elif "ai" in class_name:
                                    role = "assistant"
                                elif "system" in class_name:
                                    role = "system"
                                else:
                                    role = "user"
                            formatted.append({"role": role, "content": str(msg.content)})
                        else:
                            # 其他格式，尝试转换为用户消息
                            formatted.append({"role": "user", "content": str(msg)})
                    
                    # 确保至少有一条消息
                    if not formatted:
                        formatted = [{"role": "user", "content": "请继续分析"}]
                    
                    return formatted
                
                def bind_tools(self, tools):
                    """绑定工具到LLM（中国版本的简化实现）"""
                    # 创建一个新的包装器实例，保存绑定的工具
                    new_wrapper = LLMWrapper(self.provider, self.model)
                    new_wrapper.current_provider = self.current_provider
                    new_wrapper._bound_tools = tools
                    return new_wrapper
                
                def chat_completion(self, messages, **kwargs):
                    return self.provider.chat_completion(messages, self.model, **kwargs)
            
            model = model_mapping.get(provider, {}).get(model_type, "standard")
            return LLMWrapper(selected_provider, model)
        else:
            raise ValueError(f"提供商 {provider} 不可用，请检查API密钥配置")
    
    @property
    def current_provider(self) -> str:
        """获取当前默认提供商"""
        if self.providers:
            return list(self.providers.keys())[0]
        return "none"

# 工具函数
def create_china_llm_manager(config: Dict[str, Any]) -> ChinaLLMManager:
    """创建中国LLM管理器实例"""
    return ChinaLLMManager(config)

def format_messages_for_chinese_context(messages: List[Dict], add_chinese_context: bool = True) -> List[Dict]:
    """为中文语境格式化消息"""
    if not add_chinese_context:
        return messages
    
    formatted_messages = []
    for msg in messages:
        content = msg.get("content", "")
        
        # 为系统消息添加中文语境提示
        if msg.get("role") == "system" and add_chinese_context:
            chinese_context = """你是一个专业的中国A股市场分析师，具有以下特点：
1. 熟悉中国A股市场的特殊性和监管环境
2. 了解中国投资者的投资习惯和市场情绪
3. 能够结合中国宏观经济政策分析股市
4. 使用专业的中文金融术语进行分析
5. 提供符合中国市场实际情况的投资建议

请基于以下要求进行分析：
"""
            content = chinese_context + content
        
        formatted_messages.append({
            "role": msg.get("role", "user"),
            "content": content
        })
    
    return formatted_messages 