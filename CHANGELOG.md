# 项目修改说明文档

## 📅 修改日期
2026年4月29日

## 📋 修改概述

本次修改针对 LlamaIndex RAG 应用进行了全面系统的优化，主要包括以下三个核心方向：

1. **安全性优化** - 增强文件上传、输入验证、路径遍历防护
2. **代码质量优化** - 添加类型提示、完善日志系统、优化异常处理
3. **架构优化** - 引入依赖注入模式，实现模块解耦

---

## 🔒 一、安全性优化

### 1.1 文件上传安全检查

**修改文件**: `app/routes.py`

**修改内容**:
- 添加文件大小限制（最大50MB），通过 `MAX_FILE_SIZE` 环境变量配置
- 添加 MIME 类型白名单验证，支持的类型包括：
  - `application/pdf` - PDF文件
  - `application/vnd.openxmlformats-officedocument.wordprocessingml.document` - DOCX文件
  - `text/markdown` - Markdown文件
  - `text/plain` - 纯文本文件
  - `application/octet-stream` - 通用二进制文件（兜底）

**关键代码**:
```python
# 文件大小检查
if file.content_length and file.content_length > MAX_FILE_SIZE:
    max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
    return jsonify({'code': -1, 'msg': f'文件大小超过限制，最大允许 {max_size_mb:.0f}MB'})

# MIME类型验证
def validate_mime_type(file):
    mime_type, _ = mimetypes.guess_type(file.filename)
    if mime_type and mime_type in ALLOWED_MIME_TYPES:
        return True
    return False
```

### 1.2 输入验证与请求限制

**修改文件**: `app/routes.py`

**修改内容**:
- 添加请求格式验证（必须为 JSON 格式）
- 添加请求体非空检查
- 添加参数存在性验证
- 添加问题长度限制（最大2000字符）

**关键代码**:
```python
MAX_QUESTION_LENGTH = 2000

# 请求格式验证
if not request.is_json:
    return jsonify({'code': -1, 'msg': '请求格式错误，需要 JSON 格式'})

# 参数验证
if 'question' not in data:
    return jsonify({'code': -1, 'msg': '缺少 question 参数'})

# 长度限制
if len(question) > MAX_QUESTION_LENGTH:
    return jsonify({'code': -1, 'msg': f'问题长度超过限制（最大 {MAX_QUESTION_LENGTH} 字符）'})
```

### 1.3 路径遍历防护

**修改文件**: `app/routes.py`

**修改内容**:
- 添加 `is_safe_path()` 函数进行路径规范化验证
- 确保文件操作仅限于允许的目录内

**关键代码**:
```python
def is_safe_path(base_path, filename):
    """验证文件路径是否安全，防止路径遍历攻击"""
    abs_base = os.path.abspath(base_path)
    abs_target = os.path.abspath(os.path.join(base_path, filename))
    return abs_target.startswith(abs_base + os.sep) or abs_target == abs_base
```

---

## 📝 二、代码质量优化

### 2.1 添加类型提示

**修改文件**:
- `app/services/document_processor.py`
- `app/services/vector_store.py`
- `app/services/query_engine.py`
- `app/services/model_adapter.py`

**修改内容**:
- 为所有类、方法、函数添加完整的类型注解
- 添加函数文档（docstring），包含 Args 和 Returns
- 统一使用 `typing` 模块的类型提示

**示例**:
```python
def load_documents(self, file_path: Optional[str] = None) -> List[Document]:
    """
    加载文档
    
    Args:
        file_path: 可选，指定文件路径
        
    Returns:
        加载的文档列表
    """
```

### 2.2 完善日志系统

**新增文件**: `app/utils/logger.py`

**修改内容**:
- 创建统一的日志配置模块
- 支持控制台和文件双输出
- 可配置日志级别（通过 `LOG_LEVEL` 环境变量）
- 将所有 `print` 语句替换为 `logger.info/error/warning`

**日志配置**:
```python
def setup_logger(name: str = 'llamaindex-rag') -> logging.Logger:
    logger = logging.getLogger(name)
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)
    
    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # 文件输出（如果配置了日志文件）
    if LOG_FILE:
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
    
    return logger
```

### 2.3 异常处理优化

**修改文件**: `app/routes.py`

**修改内容**:
- 为各接口添加具体异常类型处理
- 区分不同异常类型，返回更精确的错误信息
- 添加日志记录，便于问题排查

**异常类型覆盖**:
| 接口 | 异常类型 |
|------|---------|
| 上传 | IOError, PermissionError, ValueError |
| 删除 | FileNotFoundError, PermissionError, OSError |
| 聊天 | ConnectionError, TimeoutError, ValueError |
| 状态 | OSError |

---

## 🏗️ 三、架构优化

### 3.1 依赖注入模式

**新增文件**: `app/di/container.py`

**修改内容**:
- 创建依赖注入容器 `Container` 类
- 实现服务实例的延迟初始化
- 统一管理服务生命周期

**容器提供的服务**:
- `get_document_processor()` - 文档处理器
- `get_vector_store()` - 向量存储
- `get_query_engine()` - 查询引擎
- `get_model_adapter()` - 模型适配器
- `init_index(upload_dir)` - 初始化索引
- `shutdown()` - 清理资源

**修改文件**:
- `app/routes.py` - 使用容器获取服务实例
- `run.py` - 使用容器初始化索引

**关键代码**:
```python
class Container:
    def __init__(self) -> None:
        self._document_processor: Optional[DocumentProcessor] = None
        self._vector_store: Optional[VectorStore] = None
        self._query_engine: Optional[QueryEngine] = None
    
    def get_document_processor(self) -> DocumentProcessor:
        if self._document_processor is None:
            self._document_processor = DocumentProcessor()
        return self._document_processor
```

---

## 📁 四、新增文件清单

| 文件路径 | 说明 | 状态 |
|---------|------|------|
| `app/utils/logger.py` | 统一日志配置模块 | 新增 |
| `app/di/container.py` | 依赖注入容器 | 新增 |
| `.env.example` | 环境变量配置示例 | 新增 |
| `.gitignore` | Git 忽略配置 | 新增 |
| `CHANGELOG.md` | 修改说明文档 | 新增 |

---

## 🔄 五、修改文件清单

| 文件路径 | 修改内容 |
|---------|---------|
| `config.py` | 添加环境变量支持，使用 `python-dotenv` |
| `requirements.txt` | 添加 `python-dotenv` 依赖 |
| `app/routes.py` | 安全检查、异常处理、依赖注入 |
| `app/services/document_processor.py` | 类型提示、日志替换 |
| `app/services/vector_store.py` | 类型提示、日志替换 |
| `app/services/query_engine.py` | 类型提示、日志替换 |
| `app/services/model_adapter.py` | 类型提示、日志替换、统一基类 |
| `run.py` | 使用依赖注入容器 |

---

## ⚙️ 六、环境变量配置

**新增文件**: `.env.example`

**配置项说明**:

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `SECRET_KEY` | string | - | 应用密钥，用于安全加密 |
| `QIANFAN_API_KEY` | string | - | 百度千帆 API 密钥 |
| `QIANFAN_BASE_URL` | string | `https://qianfan.baidubce.com/v2` | 千帆 API 基础 URL |
| `MODEL_TYPE` | string | `hybrid` | 模型类型：qianfan/ollama/hybrid |
| `MODEL_NAME` | string | `glm-5.1` | 千帆模型名称 |
| `OLLAMA_MODEL_NAME` | string | `qwen2:0.5b` | Ollama LLM 模型 |
| `OLLAMA_EMBEDDING_MODEL` | string | `llama3.1:8b` | Ollama 嵌入模型 |
| `HF_EMBEDDING_MODEL` | string | `BAAI/bge-small-zh-v1.5` | HuggingFace 嵌入模型 |
| `CHUNK_SIZE` | int | 1024 | 文档分块大小 |
| `CHUNK_OVERLAP` | int | 200 | 分块重叠大小 |
| `TEMPERATURE` | float | 0.7 | 生成温度参数 |
| `MAX_TOKENS` | int | 1000 | 最大生成 token 数 |
| `UPLOAD_FOLDER` | string | `static/uploads` | 文件上传目录 |
| `MAX_FILE_SIZE` | int | 52428800 | 最大文件大小（50MB） |
| `FLASK_DEBUG` | bool | false | 调试模式 |
| `FLASK_HOST` | string | `127.0.0.1` | 绑定地址 |
| `FLASK_PORT` | int | 5000 | 端口号 |
| `LOG_LEVEL` | string | INFO | 日志级别 |
| `LOG_FILE` | string | `app.log` | 日志文件路径 |

---

## 🧪 七、测试建议

### 7.1 安全测试

1. **文件上传测试**
   - 上传超大文件（超过50MB）
   - 上传非法文件类型（.exe, .php 等）
   - 上传包含路径遍历字符的文件名（`../../etc/passwd`）

2. **输入验证测试**
   - 发送非 JSON 格式请求
   - 发送空请求体
   - 发送超长问题（超过2000字符）
   - 发送缺少必要参数的请求

### 7.2 功能测试

1. **文档上传** - 上传各种格式文档（PDF, DOCX, MD, TXT）
2. **文档删除** - 删除已上传的文档
3. **智能问答** - 上传文档后进行问答测试
4. **系统状态** - 检查 `/api/status` 返回正确状态

### 7.3 日志测试

1. 启动应用，检查日志是否正常输出
2. 执行各种操作，检查日志级别是否正确
3. 检查日志文件是否正确生成

---

## 🔍 八、问题排查指南

### 8.1 常见问题

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 文件上传失败 | 大小超限/MIME类型不允许 | 检查日志中的错误信息 |
| 问答接口返回错误 | Ollama服务未启动/模型未下载 | 检查 `ollama serve` 是否运行 |
| 索引创建失败 | 嵌入模型初始化失败 | 检查模型配置和网络连接 |
| 权限错误 | 上传目录无写入权限 | 检查目录权限设置 |

### 8.2 日志位置

- 控制台输出：直接查看终端
- 文件日志：`app.log`（可通过 `LOG_FILE` 配置）

### 8.3 调试模式

设置 `FLASK_DEBUG=true` 开启调试模式，获取更详细的错误信息。

---

## 📝 九、版本信息

| 组件 | 版本 |
|------|------|
| Python | 3.8+ |
| Flask | 最新 |
| LlamaIndex | 最新 |
| python-dotenv | 最新 |

---

*文档创建日期：2026年4月29日*
*文档版本：v1.0*
