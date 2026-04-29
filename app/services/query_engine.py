# 查询引擎模块

from llama_index.core import VectorStoreIndex, get_response_synthesizer
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from app.services.model_adapter import ModelAdapterFactory, BaseAdapter
from config import MODEL_TYPE, OLLAMA_MODEL_NAME, OLLAMA_EMBEDDING_MODEL, HF_EMBEDDING_MODEL
from typing import Optional, Any
from app.utils.logger import logger


class QueryEngine:
    """
    查询引擎，用于处理用户查询和检索相关文档
    """
    
    def __init__(self) -> None:
        # 初始化模型适配器
        self.adapter: Optional[BaseAdapter] = None
        try:
            if MODEL_TYPE == "ollama":
                self.adapter = ModelAdapterFactory.get_adapter(
                    "ollama",
                    model_name=OLLAMA_MODEL_NAME,
                    embedding_model_name=OLLAMA_EMBEDDING_MODEL
                )
            elif MODEL_TYPE == "hybrid":
                self.adapter = ModelAdapterFactory.get_adapter(
                    "hybrid",
                    llm_model_name=OLLAMA_MODEL_NAME,
                    hf_embedding_model=HF_EMBEDDING_MODEL
                )
            else:
                self.adapter = ModelAdapterFactory.get_adapter("qianfan")
        except Exception as e:
            logger.error(f"模型适配器初始化失败: {str(e)}")
        
        # 延迟加载 LLM
        self.llm: Optional[Any] = None
        self.query_engine: Optional[RetrieverQueryEngine] = None
    
    def create_query_engine(self, index: VectorStoreIndex) -> Optional[RetrieverQueryEngine]:
        """
        创建查询引擎
        
        Args:
            index: 向量索引
            
        Returns:
            查询引擎
        """
        try:
            if not index:
                logger.warning("索引为None，无法创建查询引擎")
                return None
            
            # 检查模型适配器是否初始化成功
            if not self.adapter:
                logger.warning("模型适配器未初始化，无法创建查询引擎")
                return None
            
            # 延迟加载 LLM
            if not self.llm:
                logger.info("初始化 LLM...")
                self.llm = self.adapter.get_llm()
                if not self.llm:
                    logger.error("LLM 初始化失败，无法创建查询引擎")
                    return None
                logger.info("LLM 初始化成功")
            
            # 创建检索器
            retriever: VectorIndexRetriever = VectorIndexRetriever(
                index=index,
                similarity_top_k=3
            )
            
            # 创建响应合成器
            response_synthesizer = get_response_synthesizer(
                llm=self.llm
            )
            
            # 创建查询引擎
            self.query_engine = RetrieverQueryEngine(
                retriever=retriever,
                response_synthesizer=response_synthesizer
            )
            logger.info("成功创建查询引擎")
            return self.query_engine
        except Exception as e:
            logger.error(f"创建查询引擎时出错: {str(e)}")
            return None
    
    def query(self, question: str) -> str:
        """
        执行查询
        
        Args:
            question: 用户问题
            
        Returns:
            查询结果
        """
        if not self.query_engine:
            return "查询引擎未初始化，请先上传文档并等待索引创建完成"
        
        max_retries: int = 2
        for attempt in range(max_retries + 1):
            try:
                response = self.query_engine.query(question)
                return str(response)
            except Exception as e:
                error_msg: str = str(e)
                logger.error(f"执行查询时出错 (第 {attempt + 1}/{max_retries + 1} 次): {error_msg}")
                
                # 判断是否是 Ollama 进程崩溃，尝试重建连接
                if "llama runner" in error_msg.lower() or "terminated" in error_msg.lower():
                    if attempt < max_retries:
                        logger.warning("检测到 Ollama 进程崩溃，尝试重新初始化 LLM...")
                        try:
                            # 重新获取 LLM 实例
                            self.llm = self.adapter.get_llm()
                            # 重建查询引擎需要 index，这里只能重置 LLM
                            import time
                            time.sleep(2)  # 等待 Ollama 服务恢复
                            continue
                        except Exception as rebuild_err:
                            logger.error(f"重建 LLM 失败: {str(rebuild_err)}")
                
                if attempt == max_retries:
                    return f"查询出错（已重试 {max_retries} 次）: {error_msg}\n\n建议检查：\n1. Ollama 服务是否正常运行 (ollama serve)\n2. 是否有足够的内存运行 {self.adapter.model_name if self.adapter else ''} 模型\n3. 尝试使用较小的模型或切换到千帆 API"
        
        return "查询失败，请重试"
