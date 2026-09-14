from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AiSummaryRequest(BaseModel):
    content: str = Field(..., min_length=10, description="Markdown 文章正文")
    title: Optional[str] = Field(default="", description="文章标题")


class AiSummaryResponse(BaseModel):
    summary: str
    suggested_tags: List[str] = []


class AiChatMessageItem(BaseModel):
    id: int
    role: str
    content: str
    citations: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[datetime] = None


class ChatMessage(BaseModel):
    role: str = Field(..., description="user | assistant | system")
    content: str


class AiAskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="读者提问内容")
    history: List[ChatMessage] = Field(default_factory=list, description="上下文历史对话")


class ChunkCitation(BaseModel):
    chunk_id: int
    article_id: int
    article_title: str
    article_slug: str
    similarity: float
    snippet: str


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=255, description="自然语言查询内容")
    top_k: int = Field(default=5, ge=1, le=20)


class SemanticSearchResultItem(BaseModel):
    article_id: int
    title: str
    slug: str
    summary: Optional[str] = None
    similarity: float
    matched_snippet: str


class LlmConfigSchema(BaseModel):
    provider: str = Field(..., description="mock | deepseek | zhipu | openai")
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    top_k: int = 4
    similarity_threshold: float = 0.30
