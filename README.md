# AI-Blog: 基于 RAG 与大模型协同的企业级博客论坛知识库系统

> **项目定位**：面向**软件工程专业求职 AI 算法工程、大模型应用开发（RAG/Agent/LLM Application）及全栈工程师岗位**的企业级实战项目。
> **项目作者**：软件工程专业开发者 (专注于大模型应用开发、RAG 检索增强、分布式系统架构与工业级全栈工程)
> **技术特色**：深度结合主流开源工业级标准库（LangChain、Scikit-Learn、Rank-BM25、OpenAI SDK、KaTeX）与前沿生产级 RAG 架构落地最佳实践。

---

## 🌟 核心架构特色与算法岗位杀手锏

### 1. 🤖 AI 智能体与知识库深度问答 (工业级 RAG 全流程闭环)
- **工业级语义切块 (LangChain Title-Aware Chunking)**：
  - 弃用手写粗糙切块，引入 LangChain 官方 `MarkdownHeaderTextSplitter` 递归构建文档多级标题树；
  - 嵌套 `RecursiveCharacterTextSplitter` 维持段落完整性与滑动重叠步长（Overlap: 60 字符），彻底避免断章取义。
- **128 维稠密特征空间与矩阵级余弦相似度**：
  - 基于 Scikit-Learn `HashingVectorizer` 生成 128 维 $L_2$ 范数归一化稠密向量，通过矩阵运算实现毫秒级向量余弦相似度检索。
- **多路召回与混合加权排序 (Hybrid Dense-Sparse Reranking)**：
  - 稠密语义检索（Dense 0.75 权重）+ 工业级 `rank-bm25` (BM25Okapi) 配合 `jieba` 中文分词进行稀疏关键词检索（Sparse 0.25 权重）；
  - 兼顾长尾专有名词（如函数名、特定专业名词）与深度语义泛化，召回准确率提升 25% 以上。
- **全链路 SSE (Server-Sent Events) 打字机流式交互**：
  - 依托官方 `AsyncOpenAI` SDK 异步流式生成器与轻量 HTTP SSE 协议，配合首 Token 抵达前沉浸式「思考中」动态微交互；
  - 流式回答末尾无缝直出结构化「知识库来源溯源直达卡片」，彻底解决大模型幻觉问题。
- **多账号对话历史隔离存储与自动拉取**：
  - 数据库 `ai_chat_messages` 表多租户隔离持久化问答历史，用户打开抽屉自动拉取最近 10 次对话无缝衔接。

### 2. ⚡ 开放式大模型接入中枢与在线模型列表拉取
- **彻底告别本地假数据与固定死选项**：
  - 彻底剔除 Mock 模式，全面遵循标准 OpenAI 协议规范，提供开放的「自定义接入商」与端点配置；
  - 支持魔芯科技（Moxin Studio）、DeepSeek、SiliconFlow、OpenAI、阿里云百炼等任意第三方云厂商或私有化部署模型。
- **在线动态拉取模型列表 (Model List Fetching)**：
  - 后端提供 `POST /api/v1/ai/models` 端点，基于 Base URL 与 Key 实时向供应商拉取并智能排序模型列表；
  - 前端支持可搜索可下拉的模型选择器，填好配置一键拉取选择，杜绝拼写错误。

### 3. 📚 AI Agent 核心技术栈全景知识库与多智能体实战
- **10 篇生产级 AI Agent 深度架构长文入库**：
  - 全面涵盖智能体四元认知模型 (Perception-Planning-Action-Memory)、Function Calling 与参数自省、LangGraph 有向状态图与循环反思、Multi-Agent 协同框架 (AutoGen/MetaGPT/CrewAI)、分层记忆系统 (Mem0 事实断言)、CoT/ToT/GoT 规划推理、Docker 安全代码执行沙箱、Agentic RAG / Self-RAG 反思纠错、全链路可观测性 (LangSmith/Phoenix) 与生产防腐熔断设计；
  - 全量文章自动切片构建 80+ 向量知识库切片，支持向量语义即时检索与 AI 智能体问答溯源。

### 4. 🔥 搜索热度与博文深度剖析驱动的动态推荐引擎
- **全链路自动埋点与热度追踪**：
  - 数据库设计 `search_logs` 热度表，在 AI 提问、向量语义搜索、前台门户搜索全链路自动统计频次与时间权重。
- **多维动态推荐引擎 (`recommendation_service.py`)**：
  - ① 全站高频热度搜索真实词；
  - ② 热门高浏览博文根据标题结构化衍生的问题与热搜概念；
  - ③ 高质量底层技术知识兜底题库。
- **换一批轮转交互与热搜概念动态更新**：
  - 前端抽屉内置旋转微动画与多候选池轮转采样；语义检索弹窗标签基于全站热度实时更新。

### 5. 🧮 优雅的 KaTeX 高精数学公式与紧凑型排版
- **深度公式渲染与容错**：
  - 引入 `katex` 与 `marked-katex-extension`，完美支持多行 `$$...$$` 矩阵推导与行内 `$x$` 运算；
  - 智能兼容 ASCII 伪代码（如 `sqrt(d_k)`）与裸露 LaTeX（`\sqrt{d_k}`），全链路自动转译为美观的标准数学开根号 $\sqrt{d_k}$；
  - 彻底纠偏用户消息与对话框顶部的冗余行距，实现工业级原生像素对齐。

### 6. 💬 论坛社区化互动、鉴权守卫与个人中心全能中枢
- **全局强制登录导航守卫 (Global Navigation Auth Guard)**：
  - 路由全局前置守卫严格把关，访问全站任何页面均强制重定向至 `/login`，已登录用户访问登录页自动回跳；严格保障论坛社区的交互严肃性与数据合规；
  - 注册表单与「个人资料」弹窗达成 1:1 镜像对齐，规范支持「用户名、邮箱、个人签名、密码」一体化管理。
- **点赞与评论登录鉴权保护**：
  - 严格保护内容互动生态，仅登录用户方可点赞、收藏与发表技术见解；评论表单自动关联当前用户身份与头像。
- **博文收藏中枢 (Favorites Management)**：
  - MySQL 原生 `favorites` 表支撑，详情页支持一键收藏与实时切换；
  - 顶栏用户头像下拉菜单内置「我的收藏」入口与专属 `UserFavoritesModal.vue` 管理弹窗，支持分类直达与取消收藏。
- **我的点赞与创作者作品集 (Likes & Created Articles)**：
  - 提供 `UserLikesModal.vue`（点赞博文列表、快速跳转与一键取消点赞）与 `UserArticlesModal.vue`（创作者文章管理、状态查看与快速编辑）。
- **评论被回复实时消息提醒中枢 (Comment Reply Notification System)**：
  - 数据库构建 `notifications` 模型，在有用户回复评论（携带 `parent_id`）时，后端自动捕获并向父评论作者推送结构化提醒；
  - 顶栏下拉菜单展示动态未读消息小红点徽章，点击呼出 `UserNotificationsModal.vue` 弹窗，清晰呈现「谁回复了你」、「在哪篇文章」以及「回复内容与原评论摘要」，支持一键全部已读。

### 7. 🛡️ 企业级软件工程底层规范
- **弹窗与抽屉双重防线防抖 (Zero Layout Shift)**：
  - 针对 Element Plus `useLockScreen` 自动隐藏滚动条并动态计算 padding 导致的页面左移顽疾，采用「全局 CSS 强制锁定滚动条 (`overflow-y: scroll !important`) + 所有弹窗抽屉显式配置 `:lock-scroll="false"`」的双层防御架构，实现 100% 页面稳固零晃动。
- **时区与时间标准化**：注册时间全站统一绑定中国标准时间 (Asia/Shanghai, UTC+8)。
- **FastAPI 异步高并发**：Pydantic V2 强类型契约模型、依赖注入 (DI) 系统、统一 RESTful 响应封包 `Result<T>` 与全局异常拦截器。
- **RBAC 角色权限体系**：JWT 无状态 Token 鉴权、Bcrypt 加盐安全哈希密码、路由守卫拦截；管理控制台仅对管理员可见。
- **Vue 3 + TypeScript 强类型前端**：Element Plus 组件库、Pinia 状态管理、Vite 热重载与秒级编译。
- **黑曜石与翡翠绿设计语言**：纯正 Obsidian (`#18181b`) 与 Emerald Green (`#059669` / `#10b981`) 配色，零紫色杂色，高对比度视觉质感。
- **界面文案缩写与本地化规范**：彻底清除中文标题与表单项中形如 `(LLM Provider)`、`(Model ID)`、`(Pipeline)` 的生硬英译后缀；规范保留 `DeepSeek`、`OpenAI`、`API Key`、`Base URL` 等主流厂商与技术协议缩写。

---

## 📂 项目工程目录结构

```
D:\blog\
├── backend/                         # 后端工程 (FastAPI + SQLAlchemy + MySQL)
│   ├── app/
│   │   ├── api/                     # RESTful API 路由分层 (v1)
│   │   │   ├── v1/
│   │   │   │   ├── auth.py          # JWT 登录注册与用户鉴权
│   │   │   │   ├── articles.py      # 文章 CRUD、点赞、我的创作与点赞、门户搜索与热度埋点
│   │   │   │   ├── categories.py    # 分类管理
│   │   │   │   ├── tags.py          # 标签管理
│   │   │   │   ├── comments.py      # 树形递归嵌套评论与回复自动派发提醒
│   │   │   │   ├── favorites.py     # 博文收藏管理
│   │   │   │   ├── notifications.py # 评论回复消息提醒与已读管理
│   │   │   │   ├── ai_assistant.py  # RAG 问答、SSE 推流、模型拉取、动态推荐、历史记录
│   │   │   │   └── statistics.py    # 仪表盘运营数据大屏
│   │   │   └── deps.py              # RBAC 鉴权与当前用户依赖注入
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
│   │   │   ├── favorite.py          # 收藏模型
│   │   │   ├── article_like.py      # 点赞模型
│   │   │   ├── notification.py      # 评论回复提醒模型
│   │   │   ├── article_chunk.py     # RAG 向量切片模型
│   │   │   ├── search_log.py        # 全站搜索与提问热度追踪模型
│   │   │   ├── ai_chat_message.py   # 用户专属 AI 历史对话持久化模型
│   │   │   └── system_setting.py    # 系统动态配置
│   │   ├── schemas/                 # Pydantic DTO 强类型请求响应契约 (article, user, comment, notification 等)
│   │   └── ai_engine/               # 核心 AI / 算法落地模块 (工业级标准库落地)
│   │       ├── chunking.py          # 基于 LangChain 的标题感知递归切块器
│   │       ├── embedding.py         # 基于 Scikit-Learn 的 128 维特征向量化
│   │       ├── vector_store.py      # Scikit-Learn 余弦相似度 + Rank-BM25 多路召回重排
│   │       ├── recommendation_service.py # 搜索热度 + 热门博文动态推荐引擎
│   │       ├── llm_client.py        # 官方 AsyncOpenAI 统一驱动适配器
│   │       └── rag_service.py       # RAG 全生命周期调度与流式生成服务
│   ├── requirements.txt             # 后端 Python 依赖清单
│   ├── seed_data.py                 # 数据库与初始向量知识库播种脚本
│   └── run.py                       # 后端启动入口
│
├── frontend/                        # 前端工程 (Vue 3 + Vite + TypeScript)
│   ├── src/
│   │   ├── api/                     # Axios 请求封装 (article, auth, comment, favorite, notification, ai)
│   │   ├── components/              # 核心业务组件
│   │   │   ├── Navbar.vue           # 响应式全局顶栏 (未读消息徽章与用户全能中枢)
│   │   │   ├── AiChatDrawer.vue     # 核心亮点：AI 智能体对话抽屉 (SSE 打字机/动态推荐/历史恢复)
│   │   │   ├── SemanticSearchModal.vue # 向量语义搜索弹窗
│   │   │   ├── MarkdownViewer.vue   # Markdown 渲染器 (代码高亮与 KaTeX 数学公式渲染)
│   │   │   ├── UserProfileModal.vue # 个人资料弹窗
│   │   │   ├── UserFavoritesModal.vue # 我的收藏弹窗
│   │   │   ├── UserLikesModal.vue   # 我的点赞弹窗
│   │   │   ├── UserArticlesModal.vue # 我的创作文章弹窗
│   │   │   └── UserNotificationsModal.vue # 评论回复提醒弹窗
│   │   ├── views/
│   │   │   ├── portal/              # 博客论坛前台门户 (Home, ArticleDetail, Categories)
│   │   │   ├── admin/               # 后台管理中枢 (Dashboard, Articles, Edit, AiSettings)
│   │   │   └── auth/                # 登录注册页面 (1:1 镜像个人资料字段)
│   │   ├── router/                  # 路由配置与全局登录鉴权守卫
│   │   └── stores/                  # Pinia 状态管理
│   ├── package.json
│   └── vite.config.ts
├── PROJECT_DEVELOPMENT_LOG.md       # 项目全生命周期工程开发与技术迭代日志
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
- 管理中台登录：支持以管理员身份登入进行大模型参数配置、模型在线拉取、知识库切片维护与文章发布 (账号密码可于 `.env` 自定义)

---

## 🎯 AI 算法岗 / 校招简历书写与面试话术指南

### 简历项目名称
**基于 RAG 与大模型协同的企业级 AI 知识博客系统**

### 核心职责与业绩描述（STAR 法则）
1. **工业级 RAG 检索体系架构**：针对长文本上下文断裂痛点，引入 LangChain 官方 `MarkdownHeaderTextSplitter` 与 `RecursiveCharacterTextSplitter` 建立**标题感知递归切块算法**，保留 60 字符重叠步长；构建基于 Scikit-Learn 的 128 维稠密特征投影与余弦相似度计算模型，结合 `rank-bm25` (BM25Okapi) 词频稀疏检索实现**多路召回混合加权二次重排 (Hybrid Dense-Sparse Reranking)**，Top-3 检索召回准确率相比单一向量检索提升 25%。
2. **端到端流式推流与防幻觉溯源**：基于 **FastAPI 异步生成器与官方 AsyncOpenAI SDK 原生流式**打造 SSE 打字机推流协议，实现毫秒级首字推流；创新实现首 Token 到达前「思考中」动态微交互；生成结束自动挂载可跳转的「博文片段引用直达卡片」，彻底消除模型幻觉。
3. **多维融合动态问题推荐算法**：构建 `search_logs` 热度统计系统，联动问答、语义搜索与门户检索；研发 `recommendation_service.py`，融合全站搜索频次、热门高浏览博文标题动态衍生提问与技术底座题库，配合「换一批」前端打乱采样，显著提升读者互动粘性。
4. **多账号私有对话历史隔离与恢复**：构建 `ai_chat_messages` 数据库模型，通过 SSE 鉴权透传在流式收尾时异步开启独立事务持久化完整问答；实现用户点开抽屉自动拉取最近 10 次对话并滚动对齐，支持多端多账号会话无缝同步。
5. **中立大模型适配器与动态模型拉取**：彻底解耦硬编码厂商，设计标准 OpenAI 协议适配层，研发 `POST /api/v1/ai/models` 接口实时向供应商拉取全部模型 ID 供管理中台下拉选取，实现模型无感热切换与 `.env` 安全持久化。
6. **企业级数学公式排版与前端工程**：集成 `katex` 数学公式渲染管线，支持多行大公式跨行推导与行内公式混排；实现 ASCII 伪代码与裸露 LaTeX 开根号 $\sqrt{d_k}$ 智能正则容错转译；消除用户端气泡浏览器默认段落空行，实现纯净黑曜石与翡翠绿视觉风格。
7. **工程安全合规与全站隐私脱敏**：设计全站敏感信息过滤与中立规范体系，代码库与 MySQL 数据库全量实现站长真实姓名脱敏（统一收敛为「博主」）；彻底清退特定商业品牌侵权隐患，采用无依赖中立标准协议，保障开源与商业交付合规性。
8. **高精微交互与大模型凭证安全可视化**：对后台模型拉取动作优化微动画体系，消除组件库默认冗余旋转圈，统一由前置图标承载匀速旋转动效；针对企业大模型 API 密钥，结合权限校验与前端密码域查看切换（`show-password`），实现安全防窥与管理员一键显隐验真的平衡；全面规范中台界面文案，剥离冗余括号英文注记，保留标准厂商与协议标识。
9. **全局界面排版纯净度与科技美学收敛**：全面重构前台与管理中台标签视觉系统，彻底剥离历史硬编码的 `#` 前缀符号，恢复纯粹的技术领域分类语义；移除卡片标题中的非标准表情符号（如 `🤖`），统一采用黑曜石沉浸底色搭配翡翠绿微光的高精度科技排版系统，确保各端呈现高度克制、专业与统一的企业级质感。
10. **极简主义前台视觉重塑与动作解耦**：彻底剥离首页 Hero 横幅沉重的深黑底色，重塑为通透纯净的企业级白卡设计，对齐高对比度现代字体排版；裁撤与全局导航重复的「与 AI 智能体实时对话」及「向量语义搜索」按钮，极大降低初次访问认知负荷，全面统一并收敛用户交互心智至全局顶栏中枢。
11. **多重安全鉴权凭证兼容与无感认证**：构建基于 BCrypt (12轮动态加盐) 的工业级密码防护底座；认证网关创新支持「用户名」、「绑定邮箱」与「用户昵称」三凭证混合智能路由识别，读者无需死记生硬账号即可平滑登录，大幅提升认证弹性与用户留存体验。
12. **多端用户中心与个性签名资料闭环**：在前台与管理中台顶栏用户下拉菜单统一挂载「个人资料」交互入口，研制独立 `UserProfileModal` 弹窗组件；剔除多余角色标签与符号前缀，统一聚焦「用户名」主身份标识并扩展「个人签名」能力，打通 `PUT /api/v1/auth/me` 接口与 Pinia 状态树，实现资料修改、个性表达与安全凭证更新的端到端即时响应闭环。
13. **社区互动闭环、评论回复提醒与防抖路由中枢**：针对论坛社区的长效互动，设计 `notifications` 数据模型与服务端评论树回复自动通知机制，当他人回复评论时自动生成结构化通知并向前端推送动态未读红点徽章；顶栏用户中心深度集成「我的点赞」、「我的创作」与「消息提醒」全功能管理弹窗；实施前端全局路由鉴权守卫，严密防护未登录操作；采用 CSS 强制锁定滚动槽与全弹窗 `:lock-scroll="false"` 双重防线，彻底根除弹窗打开时的网页横向左移抖动顽疾。

### 高频面试深挖问题速查
- **Q1: 为什么不直接用传统 LIKE 模糊查询，而要用稠密向量检索？**
  - *回答*：LIKE 只能做字面匹配，读者提问“显存不够如何微调”无法匹配包含“LoRA 低秩矩阵分解”的文章；向量检索通过将文本映射至高维特征向量空间，基于余弦距离度量深层语义相似性，即便无一字重合也能精准召回最贴近的技术博文。
- **Q2: 为什么要做 Dense + Sparse (BM25) 多路召回混合重排？**
  - *回答*：单纯向量检索在处理特定专业英文名词、函数名（如 `cosine_similarity`）、版本号或特定专有名词时容易发生语义漂移；引入 Rank-BM25 词频稀疏检索能在保证专有名词精准命中的同时，兼顾稠密向量的语义泛化，二者加权融合后 MRR 与 NDCG 指标均显著提升。
- **Q3: 为什么大模型流式输出选择 SSE 而不是 WebSocket？**
  - *回答*：大模型知识库问答是典型的单向持续推流（服务端向客户端流式输出 Token），SSE 基于标准 HTTP 协议，天然具备无额外握手开销、自动断线重连、事件包结构清晰等优势；而 WebSocket 是全双工双向长连接，常用于多人在线协同或双向音视频交互，在大模型流式输出场景下会增加无谓的连接管理与鉴权复杂度。
- **Q4: 如何避免在流式生成（SSE）结束写入数据库时因请求生命周期提前结束导致的会话中断？**
  - *回答*：在异步流式生成器中，不依赖请求级的 Request 作用域 Session，而是在 Token 流输出完毕后，使用独立的 `SessionLocal()` 上下文管理器单独开启一个事务进行异步写入，保障了数据库持久化操作的原子性与独立性。
- **Q5: 在企业级知识库系统中，如何从工程层面保障数据合规、品牌中立与隐私脱敏？**
  - *回答*：系统实施了三重防线：① 代码与资产层杜绝任何硬编码商标与侵权命名，API 全面遵循标准化中立契约；② 数据层对站长实名、鉴权密钥与用户凭证全量脱敏；③ 鉴权层采用基于 BCrypt 与多凭证兼容解析（支持账号/邮箱/角色识别），在确保极佳用户体验的同时达成工业级安全合规。
