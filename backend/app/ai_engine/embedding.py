import math
from typing import List
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer
from openai import AsyncOpenAI
import jieba
from app.core.config import settings


class LocalSemanticEmbedder:
    """
    基于 Scikit-Learn 官方 HashingVectorizer 的工业级稠密语义向量生成器
    
    算法特性:
    1. 特征哈希 (Feature Hashing): 依托 sklearn.feature_extraction.text.HashingVectorizer，
       结合 Jieba 中文分词与 Subword N-Gram，高效将任意长度文本投影至固定维度的稠密向量空间；
    2. 无状态与低开销 (Stateless & Low-memory): 无需维护庞大的词表字典，内存开销极低，支持任意未登录词 (OOV)；
    3. L2 模长归一化 (Unit Normalization): 输出严格满足 ||v||_2 = 1，向量点积等价于高精度余弦相似度。
    """

    def __init__(self, dimension: int = 128):
        self.dimension = dimension
        self.vectorizer = HashingVectorizer(
            n_features=self.dimension,
            alternate_sign=True,
            norm="l2",
            analyzer="char_wb",
            ngram_range=(1, 3)
        )

    def embed_text(self, text: str) -> List[float]:
        """将任意文本编码为指定维度的归一化稠密浮点向量"""
        if not text or not text.strip():
            return [0.0] * self.dimension

        cleaned = text.lower().strip()
        # 结合 jieba 中文分词与字符级 n-gram 增强语义特征
        words = list(jieba.cut(cleaned))
        tokenized_input = " ".join(words)

        sparse_vec = self.vectorizer.transform([tokenized_input])
        dense_vec = sparse_vec.toarray()[0]

        # 确保范数不为 0
        norm = np.linalg.norm(dense_vec)
        if norm > 1e-6:
            dense_vec = dense_vec / norm
        else:
            dense_vec[0] = 1.0

        return [round(float(x), 6) for x in dense_vec]


class RemoteAPIEmbedder:
    """基于官方 OpenAI SDK 的远程商业向量接口适配器 (如 text-embedding-3-small, 智谱 embedding-3 等)"""
    def __init__(self, api_key: str, base_url: str, model_name: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    async def embed_text(self, text: str) -> List[float]:
        """调用官方 OpenAI SDK 生成高维语义嵌入向量"""
        resp = await self.client.embeddings.create(
            model=self.model_name,
            input=text[:4000]
        )
        return resp.data[0].embedding


_local_embedder = LocalSemanticEmbedder(dimension=128)


def get_embedding(text: str) -> List[float]:
    """统一向量获取门面方法 (使用基于 Scikit-Learn 标准库的特征向量化器)"""
    return _local_embedder.embed_text(text)
