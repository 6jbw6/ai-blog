import json
from typing import List, Dict, Any, AsyncGenerator
from sqlalchemy.orm import Session
from app.models.article import Article
from app.models.article_chunk import ArticleChunk
from app.ai_engine.chunking import MarkdownChunker
from app.ai_engine.embedding import get_embedding
from app.ai_engine.vector_store import hybrid_search
from app.ai_engine.llm_client import UnifiedLLMClient
from app.core.config import settings
import logging

logger = logging.getLogger("app.rag")


class RAGService:
    """
    RAG (检索增强生成) 全生命周期服务体系
    
    架构全流程:
    1. 知识录入阶段 (Ingestion): Markdown 解析 -> 语义感知识别切块 -> 128维特征向量化 -> MySQL 切片持久化
    2. 检索阶段 (Retrieval): 用户 Query 向量化 -> 多路召回与混合加权排序 -> 提取 Top-K 知识切片
    3. 上下文合成 (Augmentation): 注入博主 Persona、防幻觉提示词与知识溯源锚点
    4. 生成阶段 (Generation): 大模型流式输出 (SSE) + 结构化引用卡片直达联动
    """

    def __init__(self):
        self.chunker = MarkdownChunker(target_chunk_size=450, chunk_overlap=60)
        self.llm = UnifiedLLMClient()

    def index_article(self, db: Session, article_id: int) -> int:
        """为单篇文章构建向量索引切片"""
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article or not article.content:
            return 0

        # 1. 标题感知递归切块
        raw_chunks = self.chunker.split_text(article.title, article.content)
        
        # 2. 清理旧切片
        db.query(ArticleChunk).filter(ArticleChunk.article_id == article_id).delete()

        # 3. 逐块生成向量并存储
        chunk_objects = []
        for idx, item in enumerate(raw_chunks):
            embedding = get_embedding(item["content"])
            chunk_obj = ArticleChunk(
                article_id=article.id,
                chunk_index=idx,
                chunk_title=item.get("title", article.title),
                content=item["content"],
                embedding_json=json.dumps(embedding),
                token_count=item.get("token_count", len(item["content"]))
            )
            chunk_objects.append(chunk_obj)

        db.add_all(chunk_objects)
        article.vector_status = "indexed"
        db.commit()

        logger.info(f"Article '{article.title}' (ID: {article.id}) indexed successfully with {len(chunk_objects)} chunks.")
        return len(chunk_objects)

    def reindex_all_articles(self, db: Session) -> Dict[str, int]:
        """全量重建所有已发布博文的向量索引"""
        articles = db.query(Article).filter(Article.is_published == True).all()
        total_chunks = 0
        for art in articles:
            count = self.index_article(db, art.id)
            total_chunks += count
        return {"articles_indexed": len(articles), "total_chunks": total_chunks}

    def semantic_search(self, db: Session, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """自然语言语义检索 (突破传统关键词硬匹配)"""
        # 1. 向量化用户 Query
        query_vec = get_embedding(query)

        # 2. 读取所有已发布文章的切片
        chunks = (
            db.query(ArticleChunk, Article.title, Article.slug, Article.summary)
            .join(Article, ArticleChunk.article_id == Article.id)
            .filter(Article.is_published == True)
            .all()
        )

        if not chunks:
            return []

        chunk_data = []
        for c, art_title, art_slug, art_summary in chunks:
            chunk_data.append({
                "chunk_id": c.id,
                "article_id": c.article_id,
                "title": art_title,
                "slug": art_slug,
                "summary": art_summary,
                "content": c.content,
                "embedding": json.loads(c.embedding_json)
            })

        # 3. 混合多路召回与重排
        scored = hybrid_search(
            query_vec=query_vec,
            query_text=query,
            chunks=chunk_data,
            top_k=top_k * 2,
            threshold=settings.RAG_SIMILARITY_THRESHOLD
        )

        # 4. 按文章去重聚合 (同一篇文章取相关度最高的一段)
        seen_articles = set()
        results = []
        for item in scored:
            art_id = item["article_id"]
            if art_id not in seen_articles:
                seen_articles.add(art_id)
                results.append({
                    "article_id": art_id,
                    "title": item["title"],
                    "slug": item["slug"],
                    "summary": item["summary"],
                    "similarity": item["similarity"],
                    "matched_snippet": item["content"][:200] + "..."
                })
            if len(results) >= top_k:
                break

        return results

    async def stream_rag_chat(
        self,
        db: Session,
        question: str,
        history: List[Dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        """
        RAG 知识库问答核心引擎 (全链路 SSE 流式生成 + 知识溯源)
        """
        # 1. 检索与读者提问最相关的博文切片
        query_vec = get_embedding(question)

        chunks = (
            db.query(ArticleChunk, Article.title, Article.slug)
            .join(Article, ArticleChunk.article_id == Article.id)
            .filter(Article.is_published == True)
            .all()
        )

        retrieved_chunks: List[Dict[str, Any]] = []
        if chunks:
            chunk_data = [{
                "chunk_id": c.id,
                "article_id": c.article_id,
                "title": art_title,
                "slug": art_slug,
                "content": c.content,
                "embedding": json.loads(c.embedding_json)
            } for c, art_title, art_slug in chunks]

            retrieved_chunks = hybrid_search(
                query_vec=query_vec,
                query_text=question,
                chunks=chunk_data,
                top_k=settings.RAG_TOP_K,
                threshold=settings.RAG_SIMILARITY_THRESHOLD
            )

        # 2. 组装溯源引用卡片列表 (Frontend 引用直达组件)
        citations = []
        context_blocks = []
        for idx, item in enumerate(retrieved_chunks, start=1):
            citations.append({
                "citation_index": idx,
                "chunk_id": item["chunk_id"],
                "article_id": item["article_id"],
                "article_title": item["title"],
                "article_slug": item["slug"],
                "similarity": item["similarity"],
                "snippet": item["content"][:160] + "..."
            })
            context_blocks.append(
                f"【博文片段 {idx} (来自: 《{item['title']}》)】:\n{item['content']}"
            )

        context_text = "\n\n".join(context_blocks)

        # 3. 构造强化 Prompt (带 Persona、知识边界、防幻觉机制)
        system_prompt = (
            "你叫小智，是博主的 AI 智能体与个人博客知识库智能助手。\n"
            "你的职责：友好、专业、清晰地向读者解答有关软件工程、AI 算法、大模型和博客技术内容的问题。\n"
            "原则要求：\n"
            "1. 充分依据下方提供的【参考博文知识库片段】进行回答，言简意赅，逻辑清晰，排版格式良好（使用 Markdown）；\n"
            "2. 如果参考片段中包含答案，请自然融入回答，并在合适处引用博文观点；\n"
            "3. 如果问题超出了博文知识库范围，基于你作为AI算法工程师的技术知识给予严谨且具有指导性的专业回答，并坦诚指出该内容尚未在博主博客中成文发布；\n"
            "4. 严禁无中生有编造博客中不存在的事实。\n\n"
            f"【参考博文知识库片段】:\n{context_text if context_text else '（暂无直接相关的博文切片）'}"
        )

        messages = [{"role": "system", "content": system_prompt}]
        
        # 拼接最近历史会话
        for h in history[-4:]:
            messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})

        messages.append({"role": "user", "content": question})

        # 4. 流式生成 Token 并封装 SSE 协议包
        async for token in self.llm.stream_chat(messages):
            yield f"data: {json.dumps({'type': 'token', 'content': token}, ensure_ascii=False)}\n\n"

        # 5. 生成结束后，发射引用溯源元数据包
        yield f"data: {json.dumps({'type': 'citations', 'citations': citations}, ensure_ascii=False)}\n\n"
        yield "data: {\"type\": \"done\"}\n\n"


rag_service = RAGService()
