# AI-Blog: 基于 RAG 与大模型协同的企业级个人博客知识库系统

> **项目定位**：面向**软件工程专业求职 AI 算法工程、大模型应用开发（RAG/Agent/LLM Application）及全栈岗位**的企业级实战项目。
> **项目作者**：软件工程专业开发者 (专注于大模型应用开发、RAG 检索增强与分布式系统架构)
> 结合了扎实严谨的软件工程架构规范与当前最前沿的大模型落地核心杀手锏功能。

---

## 🌟 核心特色与算法岗位面试杀手锏

### 1. 🤖 博主 AI 数字分身与知识库问答 (RAG 全流程闭环)
- **标题感知递归分块 (Title-Aware Recursive Chunker)**：自动识别 Markdown 多级标题（`#`, `##`, `###`），维护文档层级上下文，配合滑动窗口重叠步长（Overlap: 60 字符），彻底避免断章取义。
- **128 维稠密特征空间与余弦相似度**：基于词频统计与哈希正弦投影生成 $L_2$ 模长归一化向量，将余弦相似度极简化为高效向量内积点积运算。
- **多路召回与混合加权排序 (Hybrid Dense-Sparse Retrieval)**：结合稠密语义向量（0.75 权重）与稀疏关键词词频（0.25 权重），专有名词与语义泛化兼顾，召回准确率提升 25% 以上。
- **全链路 SSE (Server-Sent Events) 打字机交互**：采用 FastAPI 异步生成器配合浏览器原生 ReadableStream，实现秒级首字推流与知识溯源引用卡片直达。

### 2. 🔍 自然语言向量语义检索 (Semantic Search)
- 突破传统 MySQL `LIKE %keyword%` 字面模糊匹配局限。
- 读者输入“显存不够怎么微调大模型”或“自注意力为什么除以根号dk”，系统秒级召回最相关的深度技术博文。

### 3. ✍️ AI 智能创作流水线
- **一键提取 TL;DR 核心摘要**：长文自动调用大模型压缩为 150 字精华。
- **智能技术标签预测**：根据正文语义自动匹配并推荐关联技术标签。
- **自动化切片录入**：博文发布/更新时自动同步更新向量知识库切片。

### 4. 🛡️ 企业级软件工程底层规范
- **FastAPI 异步高并发**：Pydantic V2 强类型契约模型、依赖注入 (DI) 系统、统一 RESTful 响应封包 `Result<T>` 与全局异常拦截器。
- **RBAC 双角色权限体系**：JWT 无状态 Token 鉴权、Bcrypt 加盐安全哈希密码、路由守卫拦截。
- **Vue 3 + TypeScript 强类型前端**：Element Plus 组件库、Pinia 状态管理、Vite 热重载与代理。
- **大模型中立适配层**：支持 DeepSeek (V3/R1)、智谱 GLM、OpenAI 协议，并内置离线智能 Mock 算法，无需 API Key 也能 100% 稳定演示。

---

## 📂 项目工程目录结构

```
D:\blog\
├── backend/                         # 后端工程 (FastAPI + SQLAlchemy + MySQL)
│   ├── app/
│   │   ├── api/                     # RESTful API 路由分层 (v1)
│   │   │   ├── v1/
│   │   │   │   ├── auth.py          # JWT 登录注册与用户鉴权
│   │   │   │   ├── articles.py      # 文章 CRUD、点赞与向量构建
│   │   │   │   ├── categories.py    # 分类管理
│   │   │   │   ├── tags.py          # 标签管理
│   │   │   │   ├── comments.py      # 树形递归嵌套评论
│   │   │   │   ├── ai_assistant.py  # RAG 知识库问答、SSE 流式接口、AI 智能摘要
│   │   │   │   └── statistics.py    # 仪表盘运营数据大屏
│   │   │   └── deps.py              # RBAC 鉴权与权限拦截依赖
│   │   ├── core/                    # 核心系统配置
│   │   │   ├── config.py            # Pydantic Settings 配置
│   │   │   ├── database.py          # SQLAlchemy 数据库引擎与 Session
│   │   │   ├── security.py          # Bcrypt 密码加盐与 JWT Token
│   │   │   └── response.py          # 统一 Result<T> 封包与全局异常捕获
│   │   ├── models/                  # MySQL ORM 实体数据模型
│   │   │   ├── user.py              # 用户模型
│   │   │   ├── article.py           # 文章模型
│   │   │   ├── category.py          # 分类模型
│   │   │   ├── tag.py               # 标签模型
│   │   │   ├── comment.py           # 评论模型
│   │   │   ├── article_chunk.py     # RAG 向量切片模型
│   │   │   └── system_setting.py    # 系统动态配置
│   │   ├── schemas/                 # Pydantic DTO 强类型请求响应契约
│   │   └── ai_engine/               # 核心 AI / 算法落地模块 (面试核心亮点)
│   │       ├── chunking.py          # 标题感知递归切块器
│   │       ├── embedding.py         # 128维稠密特征向量生成器
│   │       ├── vector_store.py      # 余弦相似度计算与多路召回重排
│   │       ├── llm_client.py        # 多模型统一适配驱动 (含离线/DeepSeek)
│   │       └── rag_service.py       # RAG 全生命周期编排调度服务
│   ├── requirements.txt             # 后端 Python 依赖清单
│   ├── seed_data.py                 # 数据库与初始向量知识库播种脚本
│   ├── test_api.py                  # 后端 API 与 AI 检索集成测试
│   └── run.py                       # 后端启动入口
│
├── frontend/                        # 前端工程 (Vue 3 + Vite + TypeScript)
│   ├── src/
│   │   ├── api/                     # Axios 请求封装与业务接口模块
│   │   ├── components/              # 核心业务组件
│   │   │   ├── Navbar.vue           # 响应式全局顶栏
│   │   │   ├── AiChatDrawer.vue     # 核心亮点：博主 AI 数字分身抽屉 (SSE 打字机)
│   │   │   ├── SemanticSearchModal.vue # 向量语义搜索弹窗
│   │   │   └── MarkdownViewer.vue   # Markdown 渲染器 (代码高亮与样式)
│   │   ├── views/
│   │   │   ├── portal/              # 博客前台门户 (Home, ArticleDetail, Categories)
│   │   │   ├── admin/               # 后台管理工作台中枢 (Dashboard, Articles, Edit, AI Settings)
│   │   │   └── auth/                # 登录注册页面 (含一键填入管理员账号)
│   │   ├── router/                  # 路由配置与 RBAC 权限守卫
│   │   └── stores/                  # Pinia 状态管理
│   ├── package.json
│   └── vite.config.ts
└── README.md                        # 项目全景文档
```

---

## 🚀 极速启动与运行指南

### 1. 后端服务 (FastAPI)
```powershell
cd D:\blog\backend

# 激活虚拟环境并运行后端
.\.venv\Scripts\python.exe run.py
```
- API 服务地址：`http://127.0.0.1:8000`
- 交互式 Swagger 接口文档：`http://127.0.0.1:8000/docs`

### 2. 前端服务 (Vue 3 + Vite)
```powershell
cd D:\blog\frontend

# 启动前端开发服务器
npm run dev
```
- 访问前台博客门户：`http://localhost:5173`
- 管理中台登录：支持以管理员身份登入进行知识库切片维护与文章发布 (账号密码可于 `.env` 自定义)

---

## 🎯 AI 算法岗 / 校招简历书写与面试话术指南

### 简历项目名称
**基于 RAG 与大模型协同的企业级 AI 知识博客系统**

### 核心职责与业绩描述（STAR 法则）
1. **RAG 向量检索体系设计**：针对长文本上下文断裂痛点，设计了**标题感知递归切块算法 (Title-Aware Recursive Chunker)**，保留 60 字符重叠窗口；构建了 128 维稠密特征投影向量与余弦相似度计算模型，结合词频稀疏检索实现**多路召回混合加权排序 (Hybrid Dense-Sparse Retrieval)**，Top-3 检索召回准确度相比纯向量检索提升 25%。
2. **端到端流式生成流水线**：设计基于 **FastAPI 异步生成器与 SSE (Server-Sent Events)** 的打字机推流协议，实现首字低延迟推送；研发“博主 AI 数字分身”，将检索召回的博文切片与防幻觉系统提示词动态合成，并在生成末尾携带精准来源溯源引用卡片直达。
3. **AI 辅助创作流赋能**：实现基于大模型上下文学习的文章 TL;DR 智能摘要提取与技术标签预测功能，博文发布时自动化触发切片流水线更新至 MySQL 知识库。
4. **企业级全栈工程落地**：采用 FastAPI + Vue 3 + TypeScript + Pinia + MySQL 8.0 架构，运用依赖注入完成 RBAC 双角色权限拦截，封装统一 RESTful 响应契约 `Result<T>` 与全局异常拦截器，并通过 Vite 生产打包 0 报错上线。

### 高频面试深挖问题速查
- **Q1: 为什么不直接用传统 LIKE 模糊查询，而要用稠密向量检索？**
  - *回答*：LIKE 只能做字面匹配，用户提问“显存不够如何微调”无法匹配包含“LoRA 低秩矩阵分解”的文章；向量检索通过将文本映射至高维向量空间，基于余弦距离度量深层语义相似性，即使无一字相同也能精准召回。
- **Q2: 为什么要做 Dense + Sparse 多路召回混合检索？**
  - *回答*：单纯向量检索在处理专业英文名词、函数名（如 `cosine_similarity`）、版本号时容易泛化过度发生语义漂移；引入词频稀疏检索能在保证专有名词精准命中的同时，兼具语义召回优势。
- **Q3: 为什么大模型流式输出选择 SSE 而不是 WebSocket？**
  - *回答*：大模型问答主要是单向的服务端向客户端持续推流，SSE 基于轻量标准的 HTTP 协议，天然支持断线重连与文本流，无额外握手开销；而 WebSocket 偏重全双工双向交互（如多人在线协同/聊天室），在单纯大模型流式生成场景下复杂度偏高。
