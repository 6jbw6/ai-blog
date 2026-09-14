from typing import List, Dict, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
from rank_bm25 import BM25Okapi
import jieba


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    基于 Scikit-Learn 官方标准库计算两个特征向量的余弦相似度 (Cosine Similarity)
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    arr_a = np.array(vec_a, dtype=np.float32).reshape(1, -1)
    arr_b = np.array(vec_b, dtype=np.float32).reshape(1, -1)

    sim = float(sklearn_cosine_similarity(arr_a, arr_b)[0][0])
    # 归一化到 [0, 1] 方便综合评分与阈值过滤
    normalized_sim = (sim + 1.0) / 2.0
    return max(0.0, min(1.0, normalized_sim))


def calculate_bm25_scores(query: str, texts: List[str]) -> np.ndarray:
    """
    基于行业标准 rank-bm25 与 Jieba 中文分词计算 BM25 稀疏检索相关度得分
    """
    if not texts or not query.strip():
        return np.zeros(len(texts), dtype=np.float32)

    # 1. 中文分词构建词袋语料库
    tokenized_corpus = [jieba.lcut(t.lower()) for t in texts]
    tokenized_query = jieba.lcut(query.lower())

    # 2. 调用标准 BM25Okapi 算法
    bm25 = BM25Okapi(tokenized_corpus)
    raw_scores = np.array(bm25.get_scores(tokenized_query), dtype=np.float32)

    # 3. Min-Max 归一化至 [0, 1] 区间
    max_score = float(np.max(raw_scores)) if len(raw_scores) > 0 else 0.0
    if max_score > 1e-6:
        return raw_scores / max_score
    return np.zeros(len(texts), dtype=np.float32)


def hybrid_search(
    query_vec: List[float],
    query_text: str,
    chunks: List[Dict[str, Any]],
    top_k: int = 4,
    threshold: float = 0.30,
    dense_weight: float = 0.75,
    sparse_weight: float = 0.25
) -> List[Dict[str, Any]]:
    """
    工业级多路召回与混合重排检索器 (Hybrid Dense-Sparse Reranking)
    
    架构依赖:
    - 稠密向量计算: Scikit-Learn 矩阵级余弦相似度批量计算；
    - 稀疏关键词计算: Jieba 分词 + Rank-BM25 (BM25Okapi) 工业级文本检索模型；
    - 融合策略: 标准化评分融合矩阵 (Dense Weight + BM25 Weight)。
    """
    if not chunks:
        return []

    # 1. 稠密向量矩阵级快速内积计算 (利用 Scikit-Learn 优化底层 BLAS)
    query_matrix = np.array([query_vec], dtype=np.float32)
    chunk_vectors = np.array([item["embedding"] for item in chunks], dtype=np.float32)
    
    dense_sims = sklearn_cosine_similarity(query_matrix, chunk_vectors)[0]
    dense_scores = np.clip((dense_sims + 1.0) / 2.0, 0.0, 1.0)

    # 2. 稀疏检索：调用 Rank-BM25 计算关键词精准度
    chunk_contents = [item["content"] for item in chunks]
    sparse_scores = calculate_bm25_scores(query_text, chunk_contents)

    # 3. 混合加权得分计算
    scored_results = []
    for idx, item in enumerate(chunks):
        dense_score = float(dense_scores[idx])
        sparse_score = float(sparse_scores[idx])

        final_score = (dense_score * dense_weight) + (sparse_score * sparse_weight)

        if final_score >= threshold:
            scored_results.append({
                **item,
                "similarity": round(final_score, 4),
                "dense_score": round(dense_score, 4),
                "sparse_score": round(sparse_score, 4)
            })

    # 按综合得分降序排列并截取 Top-K
    scored_results.sort(key=lambda x: x["similarity"], reverse=True)
    return scored_results[:top_k]
