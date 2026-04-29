# 模型适配器模块

import os
from abc import ABC, abstractmethod
from typing import Optional, Any

# 使用 HuggingFace 国内镜像站（解决国内访问 huggingface.co 超时问题）
os.environ["HF_ENDPOINT"] = "https://ai.gitcode.com/models"

from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.ollama import OllamaEmbedding
from config import QIANFAN_API_KEY, QIANFAN_BASE_URL, MODEL_NAME, TEMPERATURE, MAX_TOKENS
from app.utils.logger import logger


class BaseAdapter(ABC):
    """
    基础适配器接口，定义通用方法
    """
    
    @abstractmethod
    def get_llm(self) -> Any:
        """
        获取 LLM 实例
        """
        pass
    
    @abstractmethod
    def get_embedding_model(self) -> Any:
        """
        获取嵌入模型实例
        """
        pass


class QIANFANAdapter(BaseAdapter):
    """
    百度千帆适配器
    """
    
    def __init__(self) -> None:
        self._llm: Optional[OpenAI] = None
        self._embedding_model: Optional[OpenAIEmbedding] = None
    
    def get_llm(self) -> OpenAI:
        """
        获取百度千帆 LLM 实例
        """
        if not self._llm:
            logger.info("初始化百度千帆 LLM...")
            self._llm = OpenAI(
                api_key=QIANFAN_API_KEY,
                base_url=QIANFAN_BASE_URL,
                model=MODEL_NAME,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            logger.info("百度千帆 LLM 初始化成功")
        return self._llm
    
    def get_embedding_model(self) -> OpenAIEmbedding:
        """
        获取百度千帆嵌入模型实例
        """
        if not self._embedding_model:
            logger.info("初始化百度千帆嵌入模型...")
            self._embedding_model = OpenAIEmbedding(
                api_key=QIANFAN_API_KEY,
                base_url=QIANFAN_BASE_URL
            )
            logger.info("百度千帆嵌入模型初始化成功")
        return self._embedding_model


class OllamaAdapter(BaseAdapter):
    """
    Ollama 适配器
    """
    
    def __init__(self, model_name: str = "llama3.1:8b", embedding_model_name: str = "BAAI/bge-small-en-v1.5") -> None:
        self.model_name: str = model_name
        self.embedding_model_name: str = embedding_model_name
        self._llm: Optional[Ollama] = None
        self._embedding_model: Optional[Any] = None
    
    def get_llm(self) -> Ollama:
        """
        获取 Ollama LLM 实例
        """
        if not self._llm:
            logger.info(f"初始化 Ollama LLM (模型: {self.model_name})...")
            self._llm = Ollama(
                model=self.model_name,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                request_timeout=120.0  # 设置 120 秒超时，防止长时间挂起
            )
            logger.info("Ollama LLM 初始化成功")
        return self._llm
    
    def get_embedding_model(self) -> Any:
        """
        获取本地嵌入模型实例
        """
        if not self._embedding_model:
            try:
                # 使用 Ollama 嵌入模型（本地运行，不需要网络下载）
                logger.info(f"初始化 Ollama 嵌入模型 (模型: {self.embedding_model_name})...")
                self._embedding_model = OllamaEmbedding(
                    model_name=self.embedding_model_name
                )
                logger.info("Ollama 嵌入模型初始化成功")
            except Exception as e:
                logger.error(f"Ollama 嵌入模型初始化失败: {str(e)}")
                # 回退到简单的嵌入模型
                logger.warning("使用简单的嵌入模型...")
                from llama_index.embeddings.simple import SimpleEmbeddingModel
                self._embedding_model = SimpleEmbeddingModel()
        return self._embedding_model


class HybridAdapter(BaseAdapter):
    """
    混合适配器：LLM 使用 Ollama（本地），Embedding 使用 HuggingFace 本地模型
    优点：Embedding 稳定不走 Ollama 进程，降低 Ollama 负担，避免崩溃
    """
    
    def __init__(self, llm_model_name: str = "llama3.1:8b", embedding_model_name: str = "BAAI/bge-small-zh-v1.5") -> None:
        self.model_name: str = llm_model_name  # 用于统一接口
        self.llm_model_name: str = llm_model_name
        self.embedding_model_name: str = embedding_model_name
        self._llm: Optional[Ollama] = None
        self._embedding_model: Optional[Any] = None
    
    def get_llm(self) -> Ollama:
        """获取 Ollama LLM 实例"""
        if not self._llm:
            logger.info(f"初始化混合模式 - Ollama LLM (模型: {self.llm_model_name})...")
            self._llm = Ollama(
                model=self.llm_model_name,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                request_timeout=120.0
            )
            logger.info("混合模式 - Ollama LLM 初始化成功")
        return self._llm
    
    def get_embedding_model(self) -> Any:
        """获取 HuggingFace 本地嵌入模型实例（稳定，不依赖 Ollama 服务进程）"""
        if not self._embedding_model:
            try:
                logger.info(f"初始化混合模式 - HuggingFace 嵌入模型 (模型: {self.embedding_model_name})...")
                from llama_index.embeddings.huggingface import HuggingFaceEmbedding
                self._embedding_model = HuggingFaceEmbedding(
                    model_name=self.embedding_model_name
                )
                logger.info("混合模式 - HuggingFace 嵌入模型初始化成功")
            except Exception as e:
                logger.error(f"HuggingFace 嵌入模型初始化失败: {str(e)}")
                # 回退到 Ollama 嵌入模型
                logger.warning("回退到 Ollama 嵌入模型...")
                try:
                    self._embedding_model = OllamaEmbedding(
                        model_name=self.llm_model_name
                    )
                    logger.info("回退到 Ollama 嵌入模型成功")
                except Exception as fallback_err:
                    logger.error(f"Ollama 回退也失败: {str(fallback_err)}")
                    raise

        return self._embedding_model


class ModelAdapterFactory:
    """
    模型适配器工厂
    """
    _instance: Optional[BaseAdapter] = None
    
    @classmethod
    def get_adapter(cls, model_type: str = "qianfan", **kwargs) -> BaseAdapter:
        """
        获取模型适配器（单例模式）
        
        Args:
            model_type: 模型类型，可选值："qianfan", "ollama", "hybrid"
            **kwargs: 额外参数
            
        Returns:
            模型适配器实例
        """
        if cls._instance is None:
            logger.info(f"初始化模型适配器 (类型: {model_type})...")
            if model_type == "qianfan":
                cls._instance = QIANFANAdapter()
            elif model_type == "ollama":
                model_name: str = kwargs.get("model_name", "llama3.1:8b")
                embedding_model_name: str = kwargs.get("embedding_model_name", "BAAI/bge-small-en-v1.5")
                cls._instance = OllamaAdapter(model_name, embedding_model_name)
            elif model_type == "hybrid":
                llm_model_name: str = kwargs.get("llm_model_name", "llama3.1:8b")
                hf_embedding_model: str = kwargs.get("hf_embedding_model", "BAAI/bge-small-zh-v1.5")
                cls._instance = HybridAdapter(llm_model_name, hf_embedding_model)
            else:
                raise ValueError(f"不支持的模型类型: {model_type}")
            logger.info("模型适配器初始化成功")
        return cls._instance
