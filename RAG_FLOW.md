# RAG 执行流程详解

## 概述

本项目基于 **LlamaIndex** 构建了一个完整的检索增强生成（Retrieval-Augmented Generation, RAG）系统。RAG 通过将外部知识检索与语言模型生成相结合，使模型能够基于用户上传的文档内容进行精准回答。

---

## 一、整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          RAG 系统架构                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐     ┌──────────────┐     ┌───────────────┐               │
│   │  文档上传   │ ──▶ │ 文档预处理   │ ──▶ │ 向量索引创建   │               │
│   │  (Upload)   │     │ (Processing) │     │ (Vector Index)│               │
│   └─────────────┘     └──────────────┘     └───────┬───────┘               │
│                                                     │                       │
│                                                     ▼                       │
│   ┌─────────────┐     ┌──────────────┐     ┌───────────────┐               │
│   │  用户查询   │ ──▶ │  语义检索    │ ──▶ │  LLM 生成答案  │               │
│   │  (Query)    │     │ (Retrieval)  │     │  (Generation) │               │
│   └─────────────┘     └──────────────┘     └───────────────┘               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 二、RAG 执行流程详解

### 阶段一：系统初始化

#### 1.1 依赖注入容器初始化

```python
# app/di/container.py
class Container:
    def __init__(self):
        self.vector_store = VectorStore()  # 向量存储服务
        self.query_engine = QueryEngine()   # 查询引擎服务
```

**作用**：采用单例模式管理核心服务实例，确保资源复用。

#### 1.2 模型适配器初始化

根据配置文件中的 `MODEL_TYPE` 参数，初始化对应的模型适配器：

| 模型类型 | LLM 来源 | Embedding 来源 | 适用场景 |
|---------|---------|---------------|---------|
| `qianfan` | 百度千帆 API | 百度千帆 API | 无 GPU 环境 |
| `ollama` | Ollama 本地 | Ollama 本地 | 有 GPU 环境 |
| `hybrid` | Ollama 本地 | HuggingFace 本地 | 稳定性优先 |

**初始化流程**：

```python
# app/services/model_adapter.py
# 根据 MODEL_TYPE 创建对应的适配器
if MODEL_TYPE == "ollama":
    adapter = OllamaAdapter(model_name="qwen2:0.5b", embedding_model_name="llama3.1:8b")
elif MODEL_TYPE == "hybrid":
    adapter = HybridAdapter(llm_model_name="qwen2:0.5b", hf_embedding_model="BAAI/bge-small-zh-v1.5")
else:
    adapter = QIANFANAdapter()
```

---

### 阶段二：文档上传与预处理

#### 2.1 文件上传流程

```
前端上传 → 安全检查 → 存储文件 → 触发索引更新
```

**安全检查机制**（`app/routes.py`）：

1. **文件扩展名验证**：仅允许 PDF/DOCX/MD/TXT
2. **MIME 类型验证**：通过 `mimetypes.guess_type()` 验证
3. **文件大小限制**：最大 50MB（`MAX_FILE_SIZE` 配置）
4. **路径遍历防护**：验证目标路径在允许目录下

```python
def is_safe_path(base_path, filename):
    abs_base = os.path.abspath(base_path)
    abs_target = os.path.abspath(os.path.join(base_path, filename))
    return abs_target.startswith(abs_base + os.sep) or abs_target == abs_base
```

#### 2.2 文档加载

```python
# app/services/vector_store.py
reader = SimpleDirectoryReader(input_files=[file_path])
documents = reader.load_data()  # 返回 Document 对象列表
```

**支持的文档格式**：
- PDF（使用 PyPDF2）
- DOCX（使用 python-docx）
- Markdown（使用 markdown 库）
- TXT（直接读取）

#### 2.3 文本分块

**分块策略**（`app/services/vector_store.py`）：

```python
self.node_parser = SentenceSplitter(
    chunk_size=1024,      # 每个块 1024 字符
    chunk_overlap=200     # 块之间重叠 200 字符
)

nodes = self.node_parser.get_nodes_from_documents(documents)
```

**分块目的**：
- 突破 LLM 上下文窗口限制
- 提高检索精度（更小的语义单元）
- 降低嵌入计算成本

---

### 阶段三：向量索引创建

#### 3.1 嵌入模型初始化

**延迟加载策略**：仅在首次创建索引时初始化嵌入模型

```python
# app/services/vector_store.py
self.embedding_model = self.adapter.get_embedding_model()
```

**嵌入模型选择**：
- **OllamaAdapter**：使用 `OllamaEmbedding`
- **HybridAdapter**：使用 `HuggingFaceEmbedding`（BAAI/bge-small-zh-v1.5）
- **QIANFANAdapter**：使用百度千帆嵌入 API

#### 3.2 向量索引构建

```python
# app/services/vector_store.py
self.index = VectorStoreIndex(
    nodes=nodes,
    embed_model=self.embedding_model
)
```

**内部流程**：
1. 对每个 Node 调用嵌入模型生成向量
2. 使用 FAISS 构建向量索引
3. 将索引存储在内存中（可配置持久化）

---

### 阶段四：查询阶段

#### 4.1 查询引擎创建

```python
# app/services/query_engine.py
# 创建检索器（Top-K 相似度搜索）
retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=3  # 返回最相关的 3 个节点
)

# 创建响应合成器
response_synthesizer = get_response_synthesizer(llm=self.llm)

# 组装查询引擎
self.query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_synthesizer
)
```

#### 4.2 普通查询流程（`POST /api/chat`）

```python
# app/services/query_engine.py
def query(self, question: str) -> str:
    response = self.query_engine.query(question)
    return str(response)
```

**内部流程**：

```
用户问题 ──▶ 生成问题向量 ──▶ 向量检索（Top-3） ──▶ 构建 Prompt ──▶ LLM 生成 ──▶ 返回答案
```

#### 4.3 流式查询流程（`POST /api/chat/stream`）

```python
# app/services/query_engine.py
def query_stream(self, question: str):
    streaming_response = self.streaming_query_engine.query(question)
    for token in streaming_response.response_gen:
        yield token  # 逐词返回
```

**流式响应合成器**：

```python
streaming_response_synthesizer = get_response_synthesizer(
    llm=self.llm,
    streaming=True  # 关键参数：启用流式输出
)
```

---

## 三、核心组件交互关系

```
┌──────────────────────────────────────────────────────────────────────┐
│                         组件交互关系图                               │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   用户请求                                                            │
│      │                                                               │
│      ▼                                                               │
│   ┌──────────────┐    HTTP POST    ┌──────────────┐                  │
│   │   前端页面   │ ──────────────▶ │   routes.py  │                  │
│   │ (index.html) │                 │  (API路由)   │                  │
│   └──────────────┘                 └──────┬───────┘                  │
│                                           │                          │
│                                           ▼                          │
│   ┌───────────────────────────────────────────────────────┐          │
│   │              Container (依赖注入容器)                   │          │
│   │  ┌──────────────┐              ┌──────────────────┐   │          │
│   │  │ VectorStore  │              │  QueryEngine     │   │          │
│   │  │ ┌──────────┐ │              │ ┌──────────────┐ │   │          │
│   │  │ │Index     │ │              │ │Retriever     │ │   │          │
│   │  │ │(FAISS)   │ │◀────────────▶│ │(Top-K搜索)   │ │   │          │
│   │  │ └──────────┘ │              │ └──────┬───────┘ │   │          │
│   │  └──────┬───────┘              │        │          │   │          │
│   │         │                      │        ▼          │   │          │
│   │         │                      │ ┌──────────────┐ │   │          │
│   │         │                      │ │Response      │ │   │          │
│   │         │                      │ │Synthesizer   │ │   │          │
│   │         │                      │ └──────┬───────┘ │   │          │
│   │         │                      └────────┼─────────┘   │          │
│   │         │                               │              │          │
│   │         ▼                               ▼              │          │
│   │  ┌──────────────────────────────────────────────┐      │          │
│   │  │           ModelAdapter (模型适配器)            │      │          │
│   │  │  ┌──────────┐          ┌─────────────────┐   │      │          │
│   │  │  │  LLM     │          │ EmbeddingModel  │   │      │          │
│   │  │  │(Ollama/  │          │(Ollama/HF/Qianfan)│   │      │          │
│   │  │  │ Qianfan) │          │                 │   │      │          │
│   │  │  └──────────┘          └─────────────────┘   │      │          │
│   │  └──────────────────────────────────────────────┘      │          │
│   └─────────────────────────────────────────────────────────┘          │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 四、数据流转详细说明

### 4.1 文档上传阶段数据流转

| 步骤 | 组件 | 数据格式 | 说明 |
|-----|------|---------|-----|
| 1 | 前端 | `multipart/form-data` | 用户上传文件 |
| 2 | routes.py | `FileStorage` | Flask 文件对象 |
| 3 | routes.py | 安全验证通过 | 文件名、大小、MIME 验证 |
| 4 | DocumentProcessor | `List[Document]` | 解析后的文档对象 |
| 5 | VectorStore | `List[Node]` | 分块后的节点列表 |
| 6 | VectorStore | `VectorStoreIndex` | 向量索引 |

### 4.2 查询阶段数据流转（普通模式）

| 步骤 | 组件 | 数据格式 | 说明 |
|-----|------|---------|-----|
| 1 | 前端 | `{"question": "..."}` | 用户问题 JSON |
| 2 | routes.py | `str` | 提取问题文本 |
| 3 | QueryEngine | `str` | 执行查询 |
| 4 | Retriever | `List[Node]` | 返回 Top-3 相关节点 |
| 5 | ResponseSynthesizer | `str` | 构建 Prompt + 调用 LLM |
| 6 | LLM | `CompletionResponse` | LLM 生成结果 |
| 7 | routes.py | `{"code":0,"data":{"answer":"..."}}` | 统一响应格式 |

### 4.3 查询阶段数据流转（流式模式）

| 步骤 | 组件 | 数据格式 | 说明 |
|-----|------|---------|-----|
| 1 | 前端 | `{"question": "..."}` | 用户问题 JSON |
| 2 | routes.py | SSE Response | `text/event-stream` 响应头 |
| 3 | QueryEngine | Generator | 流式响应生成器 |
| 4 | StreamingResponseSynthesizer | `StreamingResponse` | 流式响应对象 |
| 5 | LLM | 逐 token 输出 | 实时返回生成结果 |
| 6 | 前端 | SSE Event | `data: <token>` 格式 |

---

## 五、关键配置参数说明

### 5.1 文档处理配置

| 参数 | 默认值 | 说明 |
|-----|-------|-----|
| `CHUNK_SIZE` | 1024 | 文本分块大小（字符） |
| `CHUNK_OVERLAP` | 200 | 块之间重叠字符数 |

### 5.2 检索配置

| 参数 | 默认值 | 说明 |
|-----|-------|-----|
| `similarity_top_k` | 3 | 返回最相关的文档数量 |

### 5.3 LLM 配置

| 参数 | 默认值 | 说明 |
|-----|-------|-----|
| `TEMPERATURE` | 0.7 | 生成温度（0=确定性，1=随机性） |
| `MAX_TOKENS` | 1000 | 最大生成 token 数 |

---

## 六、错误处理与重试机制

### 6.1 Ollama 崩溃处理

```python
# app/services/query_engine.py
max_retries = 2
for attempt in range(max_retries + 1):
    try:
        response = self.query_engine.query(question)
        return str(response)
    except Exception as e:
        error_msg = str(e)
        # 检测 Ollama 进程崩溃
        if "llama runner" in error_msg.lower() or "terminated" in error_msg.lower():
            if attempt < max_retries:
                # 重新初始化 LLM
                self.llm = self.adapter.get_llm()
                time.sleep(2)  # 等待服务恢复
                continue
```

### 6.2 统一错误响应

```python
# app/routes.py
def api_response(code: int, msg: str = '', data: dict = None) -> dict:
    return {
        'code': code,
        'timestamp': int(time.time()),
        'msg': msg,
        'data': data
    }
```

---

## 七、性能优化策略

### 7.1 延迟加载

- **LLM 延迟加载**：仅在首次查询时初始化
- **嵌入模型延迟加载**：仅在首次创建索引时初始化

### 7.2 节点数量限制

```python
max_nodes = 20
if len(nodes) > max_nodes:
    nodes = nodes[:max_nodes]  # 限制最大节点数
```

### 7.3 流式输出优势

- 减少用户等待时间（实时反馈）
- 降低内存占用（边生成边传输）

---

## 八、总结

本 RAG 系统的核心执行流程可概括为：

1. **文档入库**：上传 → 解析 → 分块 → 嵌入 → 索引
2. **查询回答**：问题 → 检索 → 合成 → 生成 → 返回

系统设计亮点：
- **模块化架构**：各组件职责清晰，易于扩展
- **多模型支持**：灵活切换 Ollama/Qianfan/Hybrid 模式
- **错误容错**：完善的重试机制和错误处理
- **流式输出**：提升用户体验的实时响应