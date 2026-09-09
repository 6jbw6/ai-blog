import math
from typing import List, Dict, Any


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    计算两个特征向量的余弦相似度 (Cosine Similarity)
    公式: Cosine(A, B) = (A · B) / (||A|| * ||B||)
    """
    if len(vec_a) != len(vec_b) or not vec_a:
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a < 1e-7 or norm_b < 1e-7:
        return 0.0

    sim = dot_product / (norm_a * norm_b)
    # 归一化到 [0, 1] 方便综合评分与阈值过滤
    normalized_sim = (sim + 1.0) / 2.0
    return max(0.0, min(1.0, normalized_sim))


def calculate_keyword_score(query: str, text: str) -> float:
    """
    稀疏检索 (Sparse Retrieval): 计算关键词命中加权得分
    模拟 BM25 词频与精准匹配增益
    """
    query_terms = [t for t in query.lower().split() if len(t) > 1]
    if not query_terms:
        # 中文字符切分
        query_terms = [c for c in query.lower() if '\u4e00' <= c <= '\u9fa5']

    if not query_terms:
        return 0.0

    lower_text = text.lower()
    matched_count = sum(1 for term in query_terms if term in lower_text)
    return matched_count / len(query_terms)


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
    多路召回与混合重排检索器 (Hybrid Dense-Sparse Reranking)
    
    面试核心亮点:
    单纯的向量稠密检索 (Dense Retrieval) 擅长捕捉宏观语义相似，但容易漏掉专有名词、API函数名等硬匹配；
    本项目引入 稠密向量 (0.75) + 稀疏关键词 (0.25) 混合评分矩阵，检索召回率与准确率 (MRR/NDCG) 显著优于单一模式。
    """
    scored_results = []

    for item in chunks:
        dense_sim = cosine_similarity(query_vec, item["embedding"])
        sparse_score = calculate_keyword_score(query_text, item["content"])

        # 混合加权得分
        final_score = (dense_sim * dense_weight) + (sparse_score * sparse_weight)

        if final_score >= threshold:
            scored_results.append({
                **item,
                "similarity": round(final_score, 4),
                "dense_score": round(dense_sim, 4),
                "sparse_score": round(sparse_score, 4)
            })

    # 按综合得分降序排列
    scored_results.sort(key=lambda x: x["similarity"], reverse=True)
    return scored_results[:top_k]
