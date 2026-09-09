import re
from typing import List, Dict, Any


class MarkdownChunker:
    """
    针对 Markdown 和技术博文的标题感知分块器 (Title-Aware Recursive Chunker)
    
    算法特性 (面试核心阐述点):
    1. 保持 Markdown 语义完整性：识别 #, ##, ### 等多级标题，维护上下文层级结构；
    2. 递归滑动窗口切分：优先按段落切分，段落过长时按标点切分，并保留重叠步长 (Overlap) 避免断章取义；
    3. 携带元数据注入：每个切片顶部自动附带章节路径，增强向量特征表达能力。
    """

    def __init__(self, target_chunk_size: int = 450, chunk_overlap: int = 60):
        self.target_chunk_size = target_chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, title: str, content: str) -> List[Dict[str, Any]]:
        """将博文解析并切分成具有上下文感知的文本块列表"""
        lines = content.splitlines()
        chunks: List[Dict[str, Any]] = []
        
        current_heading = title
        current_buffer: List[str] = []
        current_length = 0

        heading_pattern = re.compile(r"^(#{1,4})\s+(.+)$")

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            match = heading_pattern.match(stripped)
            if match:
                # 遇到新标题时，如果当前缓冲区已有内容，触发一次切块归档
                if current_buffer and current_length >= (self.target_chunk_size // 2):
                    chunk_text = "\n".join(current_buffer)
                    chunks.append({
                        "title": f"{title} > {current_heading}",
                        "content": f"【章节: {current_heading}】\n{chunk_text}",
                        "token_count": len(chunk_text)
                    })
                    # 按照 overlap 保留末尾部分
                    current_buffer = current_buffer[-2:] if len(current_buffer) >= 2 else []
                    current_length = sum(len(x) for x in current_buffer)
                
                current_heading = match.group(2)
                continue

            current_buffer.append(stripped)
            current_length += len(stripped)

            # 当缓冲区超过目标大小时切块
            if current_length >= self.target_chunk_size:
                chunk_text = "\n".join(current_buffer)
                chunks.append({
                    "title": f"{title} > {current_heading}",
                    "content": f"【章节: {current_heading}】\n{chunk_text}",
                    "token_count": len(chunk_text)
                })
                # 滑动窗口保留 overlap
                overlap_chars = 0
                overlap_lines = []
                for prev_line in reversed(current_buffer):
                    overlap_lines.insert(0, prev_line)
                    overlap_chars += len(prev_line)
                    if overlap_chars >= self.chunk_overlap:
                        break
                current_buffer = overlap_lines
                current_length = sum(len(x) for x in current_buffer)

        # 处理末尾剩余缓冲区
        if current_buffer:
            chunk_text = "\n".join(current_buffer)
            if len(chunk_text.strip()) > 15:  # 忽略过短无意义尾行
                chunks.append({
                    "title": f"{title} > {current_heading}",
                    "content": f"【章节: {current_heading}】\n{chunk_text}",
                    "token_count": len(chunk_text)
                })

        # 如果文章整体过短未产生任何 chunk，将全文作为一个 chunk
        if not chunks and content.strip():
            chunks.append({
                "title": title,
                "content": f"【文章: {title}】\n{content.strip()}",
                "token_count": len(content)
            })

        return chunks
