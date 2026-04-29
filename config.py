# 配置文件
# 优先从环境变量读取配置，支持 .env 文件

import os
from dotenv import load_dotenv

# 加载 .env 文件（如果存在）
load_dotenv()

# ------------------------------------------------
# 安全配置
# ------------------------------------------------
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')

# ------------------------------------------------
# 百度千帆 API 配置
# ------------------------------------------------
QIANFAN_API_KEY = os.getenv('QIANFAN_API_KEY', '')
QIANFAN_BASE_URL = os.getenv('QIANFAN_BASE_URL', 'https://qianfan.baidubce.com/v2')

# ------------------------------------------------
# 模型配置
# ------------------------------------------------
# 模型类型: qianfan / ollama / hybrid
MODEL_TYPE = os.getenv('MODEL_TYPE', 'hybrid')

# 千帆模型名称
MODEL_NAME = os.getenv('MODEL_NAME', 'glm-5.1')

# Ollama 模型配置
OLLAMA_MODEL_NAME = os.getenv('OLLAMA_MODEL_NAME', 'qwen2:0.5b')
OLLAMA_EMBEDDING_MODEL = os.getenv('OLLAMA_EMBEDDING_MODEL', 'llama3.1:8b')

# HuggingFace 嵌入模型
HF_EMBEDDING_MODEL = os.getenv('HF_EMBEDDING_MODEL', 'BAAI/bge-small-zh-v1.5')

# ------------------------------------------------
# 文档处理配置
# ------------------------------------------------
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1024))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 200))

# ------------------------------------------------
# LLM 生成配置
# ------------------------------------------------
TEMPERATURE = float(os.getenv('TEMPERATURE', 0.7))
MAX_TOKENS = int(os.getenv('MAX_TOKENS', 1000))

# ------------------------------------------------
# 文件上传配置
# ------------------------------------------------
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')
ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'pdf,docx,md,txt').split(','))
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 52428800))  # 50MB

# ------------------------------------------------
# 向量存储配置
# ------------------------------------------------
VECTOR_STORE_PATH = os.getenv('VECTOR_STORE_PATH', 'vector_store')

# ------------------------------------------------
# Flask 应用配置
# ------------------------------------------------
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))

# ------------------------------------------------
# 日志配置
# ------------------------------------------------
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'app.log')
