"""
中国LLM提供商接口
支持通义千问、智谱、百川、文心一言等国产大模型
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

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
        super().__init__(api_key, "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation")
        
    def chat_completion(self, messages: List[Dict], model: str = "qwen-turbo", **kwargs) -> str:
        """
        通义千问聊天完成
        支持模型: qwen-turbo, qwen-plus, qwen-max
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 转换消息格式
        qwen_messages = []
        for msg in messages:
            if msg.get("role") == "user":
                qwen_messages.append({"role": "user", "content": msg["content"]})
            elif msg.get("role") == "assistant":
                qwen_messages.append({"role": "assistant", "content": msg["content"]})
            elif msg.get("role") == "system":
                qwen_messages.append({"role": "system", "content": msg["content"]})
        
        payload = {
            "model": model,
            "input": {
                "messages": qwen_messages
            },
            "parameters": {
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2000),
                "top_p": kwargs.get("top_p", 0.9)
            }
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            if "output" in result and "text" in result["output"]:
                return result["output"]["text"]
            else:
                return f"通义千问响应错误: {result}"
                
        except Exception as e:
            return f"通义千问API调用失败: {str(e)}"

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
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
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
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
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
            response = requests.post(url, headers=headers, json=payload, timeout=60)
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