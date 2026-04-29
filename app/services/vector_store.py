# 向量存储模块

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Node
from app.services.model_adapter import ModelAdapterFactory, BaseAdapter
from config import CHUNK_SIZE, CHUNK_OVERLAP, MODEL_TYPE, OLLAMA_MODEL_NAME, OLLAMA_EMBEDDING_MODEL, HF_EMBEDDING_MODEL
import os
from typing import List, Optional, Any
from app.utils.logger import logger


class VectorStore:
    """
    向量存储，用于处理文本分块和向量嵌入
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
        
        # 延迟加载嵌入模型
        self.embedding_model: Optional[Any] = None
        
        # 初始化文本分块器
        self.node_parser: SentenceSplitter = SentenceSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        
        self.index: Optional[VectorStoreIndex] = None
    
    def create_index(self, documents: List[Document]) -> Optional[VectorStoreIndex]:
        """
        创建向量索引
        
        Args:
            documents: 文档列表
            
        Returns:
            向量索引
        """
        try:
            # 检查模型适配器是否初始化成功
            if not self.adapter:
                logger.warning("模型适配器未初始化，无法创建索引")
                return None
            
            # 延迟加载嵌入模型
            if not self.embedding_model:
                logger.info("初始化嵌入模型...")
                self.embedding_model = self.adapter.get_embedding_model()
                if not self.embedding_model:
                    logger.error("嵌入模型初始化失败，无法创建索引")
                    return None
                logger.info("嵌入模型初始化成功")
            
            # 分割文档为节点
            nodes: List[Node] = self.node_parser.get_nodes_from_documents(documents)
            logger.info(f"成功分割为 {len(nodes)} 个节点")
            
            # 限制节点数量，避免内存不足
            max_nodes: int = 20
            if len(nodes) > max_nodes:
                logger.warning(f"节点数量过多，只使用前 {max_nodes} 个节点")
                nodes = nodes[:max_nodes]
            
            # 创建向量索引
            logger.info("开始创建向量索引...")
            self.index = VectorStoreIndex(
                nodes=nodes,
                embed_model=self.embedding_model
            )
            logger.info("成功创建向量索引")
            return self.index
        except Exception as e:
            logger.error(f"创建索引时出错: {str(e)}")
            return None
    
    def load_from_documents(self, file_path: Optional[str] = None, input_dir: str = "static/uploads") -> Optional[VectorStoreIndex]:
        """
        从文档加载并创建索引
        
        Args:
            file_path: 可选，指定文件路径
            input_dir: 可选，指定输入目录
            
        Returns:
            向量索引
        """
        try:
            # 加载文档
            reader: SimpleDirectoryReader
            if file_path:
                reader = SimpleDirectoryReader(
                    input_files=[file_path]
                )
            else:
                reader = SimpleDirectoryReader(
                    input_dir=input_dir
                )
            
            documents: List[Document] = reader.load_data()
            logger.info(f"成功加载 {len(documents)} 个文档")
            
            # 创建索引
            return self.create_index(documents)
        except Exception as e:
            logger.error(f"加载文档并创建索引时出错: {str(e)}")
            return None
    
    def get_query_engine(self) -> Optional[Any]:
        """
        获取查询引擎
        
        Returns:
            查询引擎
        """
        if self.index:
            return self.index.as_query_engine()
        return None
