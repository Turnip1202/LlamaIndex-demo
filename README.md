# LlamaIndex RAG 应用

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Flask-2.0%2B-green.svg" alt="Flask Version">
  <img src="https://img.shields.io/badge/LlamaIndex-0.10%2B-purple.svg" alt="LlamaIndex Version">
  <img src="https://img.shields.io/badge/FAISS-1.7%2B-orange.svg" alt="FAISS Version">
</div>

---

## 🌟 项目简介

基于 **LlamaIndex** 构建的检索增强生成（RAG）智能问答系统，支持多种文档格式上传、智能检索和自然语言问答。

### 🔍 核心功能

| 功能模块 | 功能描述 | 支持格式 |
|---------|---------|---------|
| **文档管理** | 上传、删除、管理文档 | PDF / DOCX / MD / TXT |
| **智能检索** | 基于向量嵌入的相似度搜索 | FAISS 向量数据库 |
| **智能问答** | 结合检索结果生成精准答案 | 支持多轮对话 |
| **模型切换** | 灵活切换不同 LLM 后端 | Ollama / 百度千帆 / Hybrid |

### 🛠 技术栈

```
├── 核心框架: LlamaIndex 0.10+
├── Web 框架: Flask 2.0+
├── 向量存储: FAISS
├── 前端: Bootstrap 5 + jQuery
├── 模型支持: Ollama / 百度千帆 API
└── 嵌入模型: HuggingFace / Ollama Embedding
```

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip / conda
- Ollama（可选，用于本地模型）

### 安装步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd LlamaIndex-demo

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows
venv\Scripts\Activate.ps1
# Linux/macOS
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt
```

### 配置说明

#### 方式一：环境变量（推荐）

创建 `.env` 文件：

```env
# 百度千帆 API 配置（使用千帆模式时）
QIANFAN_API_KEY=your-api-key
QIANFAN_BASE_URL=https://qianfan.baidubce.com/v2

# 模型配置
MODEL_TYPE=hybrid  # qianfan / ollama / hybrid
MODEL_NAME=glm-5.1
OLLAMA_MODEL_NAME=qwen2:0.5b
OLLAMA_EMBEDDING_MODEL=llama3.1:8b
HF_EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5

# 文档处理配置
CHUNK_SIZE=1024
CHUNK_OVERLAP=200
TEMPERATURE=0.7
MAX_TOKENS=1000
```

#### 方式二：配置文件

编辑 `config.py` 文件，修改相关配置项。

### 启动应用

```bash
# 启动开发服务器
python run.py

# 访问地址
# http://127.0.0.1:5000
```

---

## 📖 使用指南

### 1. 上传文档

访问 **文档管理** 页面，支持以下操作：

- **点击上传**：点击上传区域选择本地文件
- **拖拽上传**：直接拖拽文件到上传区域
- **支持格式**：PDF、DOCX、Markdown、TXT

### 2. 智能问答

访问 **智能问答** 页面：

1. 在输入框中输入问题
2. 按 `Enter` 或点击「发送」按钮
3. 系统将从已上传文档中检索相关内容并生成答案

### 3. 快速提问

点击预设的快捷标签，快速发起常见问题查询：

- 文档摘要是什么？
- 关键信息提取
- 概念解释

---

## 📡 API 接口文档

### 文件管理

| 接口 | 方法 | 描述 |
|-----|------|-----|
| `/api/files` | GET | 获取已上传文件列表 |
| `/api/upload` | POST | 上传文档 |
| `/api/delete/<filename>` | DELETE | 删除指定文件 |

#### GET /api/files

**响应示例**：
```json
{
  "code": 0,
  "data": [
    {
      "name": "example.pdf",
      "size": 102400,
      "mtime": 1714444800
    }
  ]
}
```

#### POST /api/upload

**请求体**：`multipart/form-data`

| 字段 | 类型 | 描述 |
|-----|------|-----|
| `file` | File | 要上传的文件 |

**响应示例**：
```json
{
  "code": 0,
  "msg": "文件上传成功",
  "data": {
    "filename": "example.pdf"
  }
}
```

### 智能问答

#### POST /api/chat

**请求体**：
```json
{
  "question": "文档的主要内容是什么？"
}
```

**响应示例**：
```json
{
  "code": 0,
  "data": {
    "question": "文档的主要内容是什么？",
    "answer": "文档主要介绍了..."
  }
}
```

### 系统状态

#### GET /api/status

**响应示例**：
```json
{
  "code": 0,
  "data": {
    "file_count": 5,
    "engine_ready": true,
    "model_type": "hybrid"
  }
}
```

---

## 🏗 项目结构

```
LlamaIndex-demo/
├── app/                      # 应用核心模块
│   ├── __init__.py           # 应用初始化
│   ├── routes.py             # REST API 路由
│   └── services/             # 核心服务层
│       ├── document_processor.py  # 文档处理服务
│       ├── vector_store.py        # 向量存储服务
│       ├── query_engine.py        # 查询引擎服务
│       └── model_adapter.py       # 模型适配器
├── static/                   # 静态资源
│   ├── index.html            # SPA 前端页面
│   ├── libs/                 # 第三方库
│   └── uploads/              # 上传文件存储
├── config.py                 # 配置文件
├── requirements.txt          # 依赖列表
├── run.py                    # 启动脚本
└── README.md                 # 项目文档
```

---

## ⚙️ 配置参数

### 模型配置

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|-------|-----|
| `MODEL_TYPE` | str | hybrid | 模型类型：qianfan / ollama / hybrid |
| `MODEL_NAME` | str | glm-5.1 | 千帆模型名称 |
| `OLLAMA_MODEL_NAME` | str | qwen2:0.5b | Ollama 模型名称 |
| `HF_EMBEDDING_MODEL` | str | BAAI/bge-small-zh-v1.5 | HuggingFace 嵌入模型 |

### 文档处理配置

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|-------|-----|
| `CHUNK_SIZE` | int | 1024 | 文本分块大小（字符） |
| `CHUNK_OVERLAP` | int | 200 | 分块重叠大小（字符） |
| `TEMPERATURE` | float | 0.7 | LLM 生成温度 |
| `MAX_TOKENS` | int | 1000 | 最大生成 tokens |

---

## 🔧 故障排除

### 常见问题

| 问题 | 原因 | 解决方案 |
|-----|------|---------|
| API 连接失败 | 密钥配置错误 | 检查 `QIANFAN_API_KEY` 是否正确 |
| 文档上传失败 | 文件格式不支持 | 确保文件为 PDF/DOCX/MD/TXT 格式 |
| Ollama 连接失败 | Ollama 服务未启动 | 运行 `ollama serve` 启动服务 |
| 内存不足 | 模型过大 | 切换到更小的模型如 `qwen2:0.5b` |

### 日志查看

```bash
# 查看应用日志（默认输出到控制台）
python run.py

# 检查 Ollama 状态
ollama list
ollama ps
```

---

## 📋 开发指南

### 代码风格

- 使用 **PEP 8** 代码规范
- 使用 **Google 风格** 文档字符串
- 变量命名使用 `snake_case`
- 类命名使用 `PascalCase`

### 开发流程

```bash
# 安装开发依赖
pip install pytest flake8

# 运行测试
pytest tests/

# 代码检查
flake8 app/
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 贡献步骤

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交代码：`git commit -m "feat: add your feature"`
4. 推送到分支：`git push origin feature/your-feature`
5. 提交 Pull Request

### 提交规范

- `feat:` 新增功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试更新
- `chore:` 构建/工具更新

---

## 📄 许可证

MIT License

---

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件
- 加入讨论群

---

*Built with ❤️ using LlamaIndex*
