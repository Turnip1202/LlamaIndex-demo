# 文档处理模块

from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import Document
import os
from typing import List, Optional
from config import UPLOAD_FOLDER
from app.utils.logger import logger


class DocumentProcessor:
    """
    文档处理器，用于加载和解析不同类型的文档
    """
    
    def __init__(self) -> None:
        self.upload_folder: str = UPLOAD_FOLDER
    
    def load_documents(self, file_path: Optional[str] = None) -> List[Document]:
        """
        加载文档
        
        Args:
            file_path: 可选，指定文件路径
            
        Returns:
            加载的文档列表
        """
        try:
            if file_path:
                # 加载单个文件
                reader = SimpleDirectoryReader(
                    input_files=[file_path]
                )
            else:
                # 加载上传目录中的所有文件
                reader = SimpleDirectoryReader(
                    input_dir=self.upload_folder
                )
            
            documents: List[Document] = reader.load_data()
            logger.info(f"成功加载 {len(documents)} 个文档")
            return documents
        except Exception as e:
            logger.error(f"加载文档时出错: {str(e)}")
            return []
    
    def get_uploaded_files(self) -> List[str]:
        """
        获取上传目录中的文件列表
        
        Returns:
            文件列表
        """
        try:
            if not os.path.exists(self.upload_folder):
                return []
            
            files: List[str] = []
            for filename in os.listdir(self.upload_folder):
                filepath = os.path.join(self.upload_folder, filename)
                if os.path.isfile(filepath):
                    files.append(filename)
            return files
        except Exception as e:
            logger.error(f"获取上传文件列表时出错: {str(e)}")
            return []
    
    def delete_file(self, filename: str) -> bool:
        """
        删除指定文件
        
        Args:
            filename: 文件名
            
        Returns:
            是否删除成功
        """
        try:
            file_path = os.path.join(self.upload_folder, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"删除文件时出错: {str(e)}")
            return False
