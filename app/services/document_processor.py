# 文档处理模块

from llama_index.core import SimpleDirectoryReader
import os
from config import UPLOAD_FOLDER

class DocumentProcessor:
    """
    文档处理器，用于加载和解析不同类型的文档
    """
    
    def __init__(self):
        self.upload_folder = UPLOAD_FOLDER
    
    def load_documents(self, file_path=None):
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
            
            documents = reader.load_data()
            print(f"成功加载 {len(documents)} 个文档")
            return documents
        except Exception as e:
            print(f"加载文档时出错: {str(e)}")
            return []
    
    def get_uploaded_files(self):
        """
        获取上传目录中的文件列表
        
        Returns:
            文件列表
        """
        try:
            if not os.path.exists(self.upload_folder):
                return []
            
            files = []
            for filename in os.listdir(self.upload_folder):
                if os.path.isfile(os.path.join(self.upload_folder, filename)):
                    files.append(filename)
            return files
        except Exception as e:
            print(f"获取上传文件列表时出错: {str(e)}")
            return []
    
    def delete_file(self, filename):
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
            print(f"删除文件时出错: {str(e)}")
            return False