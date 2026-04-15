"""文档分块工具：用于 Map-Reduce 分段生成测试用例时的需求文档拆分。"""
import re
from typing import List


def extract_summary(text: str, max_length: int = 300) -> str:
    """提取文档摘要：标题结构 + 开头段落，供分段生成时作为全局上下文。"""
    lines = text.strip().splitlines()
    headings = []
    first_para: List[str] = []
    collecting_para = True

    for line in lines:
        stripped = line.strip()
        if re.match(r'^#{1,4}\s+', stripped):
            headings.append(stripped.lstrip('#').strip())
        elif collecting_para:
            if stripped:
                first_para.append(stripped)
            elif first_para:
                collecting_para = False

    parts = []
    if headings:
        parts.append('文档结构：' + '；'.join(headings[:10]))
    if first_para:
        parts.append('开头摘要：' + ''.join(first_para[:3])[:200])
    summary = '\n'.join(parts)
    return summary[:max_length] if summary else text[:max_length]


def split_document(text: str, max_chunk_size: int = 2000, overlap: int = 200) -> List[str]:
    """将文档按标题拆分为语义段落，超长段落再按字数二次拆分，相邻段落保留 overlap 字符重叠。"""
    text = (text or '').strip()
    if not text:
        return []
    if len(text) <= max_chunk_size:
        return [text]

    sections = _split_by_headings(text)

    raw_chunks: List[str] = []
    for section in sections:
        if len(section) <= max_chunk_size:
            raw_chunks.append(section)
        else:
            raw_chunks.extend(_split_by_size(section, max_chunk_size))

    if overlap > 0 and len(raw_chunks) > 1:
        overlapped = [raw_chunks[0]]
        for i in range(1, len(raw_chunks)):
            prev_tail = raw_chunks[i - 1][-overlap:]
            overlapped.append(prev_tail + '\n…\n' + raw_chunks[i])
        return overlapped

    return raw_chunks


def _split_by_headings(text: str) -> List[str]:
    """按 Markdown 标题（# ~ ###）拆分文档为多个段落。"""
    parts = re.split(r'(?=^#{1,3}\s+)', text, flags=re.MULTILINE)
    return [p.strip() for p in parts if p.strip()]


def _split_by_size(text: str, max_size: int) -> List[str]:
    """按段落累积字数拆分超长文本，确保每块不超过 max_size。"""
    paragraphs = re.split(r'\n\s*\n', text)
    chunks: List[str] = []
    current: List[str] = []
    current_len = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if current_len + len(para) > max_size and current:
            chunks.append('\n\n'.join(current))
            current = []
            current_len = 0
        current.append(para)
        current_len += len(para)

    if current:
        chunks.append('\n\n'.join(current))
    return chunks if chunks else [text]
