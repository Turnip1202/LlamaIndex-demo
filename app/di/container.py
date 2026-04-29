# 依赖注入容器模块

from typing import Optional, Any
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStore
from app.services.query_engine import QueryEngine
from app.services.model_adapter import ModelAdapterFactory, BaseAdapter
from config import MODEL_TYPE, OLLAMA_MODEL_NAME, OLLAMA_EMBEDDING_MODEL, HF_EMBEDDING_MODEL


class Container:
    """
    依赖注入容器，管理服务实例的创建和生命周期
    """
    
    def __init__(self) -> None:
        # 延迟初始化服务
        self._document_processor: Optional[DocumentProcessor] = None
        self._vector_store: Optional[VectorStore] = None
        self._query_engine: Optional[QueryEngine] = None
        self._model_adapter: Optional[BaseAdapter] = None
    
    def get_model_adapter(self) -> BaseAdapter:
        """获取模型适配器实例"""
        if self._model_adapter is None:
            self._model_adapter = ModelAdapterFactory.get_adapter(
                model_type=MODEL_TYPE,
                model_name=OLLAMA_MODEL_NAME,
                embedding_model_name=OLLAMA_EMBEDDING_MODEL,
                llm_model_name=OLLAMA_MODEL_NAME,
                hf_embedding_model=HF_EMBEDDING_MODEL
            )
        return self._model_adapter
    
    def get_document_processor(self) -> DocumentProcessor:
        """获取文档处理器实例"""
        if self._document_processor is None:
            self._document_processor = DocumentProcessor()
        return self._document_processor
    
    def get_vector_store(self) -> VectorStore:
        """获取向量存储实例"""
        if self._vector_store is None:
            self._vector_store = VectorStore()
        return self._vector_store
    
    def get_query_engine(self) -> QueryEngine:
        """获取查询引擎实例"""
        if self._query_engine is None:
            self._query_engine = QueryEngine()
        return self._query_engine
    
    def init_index(self, upload_dir: str) -> None:
        """初始化索引"""
        from app.utils.logger import logger
        try:
            import os
            if os.path.exists(upload_dir) and len(os.listdir(upload_dir)) > 0:
                logger.info("初始化索引...")
                vector_store = self.get_vector_store()
                query_engine = self.get_query_engine()
                index = vector_store.load_from_documents(input_dir=upload_dir)
                if index:
                    query_engine.create_query_engine(index)
                    logger.info("索引初始化成功")
                else:
                    logger.error("索引初始化失败")
            else:
                logger.info("上传目录为空，跳过索引初始化")
        except Exception as e:
            logger.error(f"初始化索引时出错: {str(e)}")
    
    def shutdown(self) -> None:
        """关闭容器，清理资源"""
        self._document_processor = None
        self._vector_store = None
        self._query_engine = None
        self._model_adapter = None


# 创建全局容器实例
container = Container()


def get_container() -> Container:
    """获取全局容器实例"""
    return container
