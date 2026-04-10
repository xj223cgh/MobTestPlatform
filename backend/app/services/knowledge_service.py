# -*- coding: utf-8 -*-
"""知识库服务：文档上传、向量化、存储与语义检索（基于 ChromaDB）。"""
import os
import re
import uuid
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

_client = None
_collection = None


def _ensure_env():
    """确保从 backend/.env 加载环境变量。"""
    env_file = Path(__file__).resolve().parent.parent.parent / '.env'
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_file, override=True)


def _get_collection():
    """获取或初始化 ChromaDB 集合（单例），持久化目录从环境变量读取。"""
    global _client, _collection
    if _collection is not None:
        return _collection
    try:
        import chromadb
    except ImportError:
        raise RuntimeError("chromadb is not installed. Run: pip install chromadb")
    _ensure_env()
    persist_dir = os.getenv('CHROMA_PERSIST_DIR', './app/ai/knowledge/chroma_data')
    backend_dir = Path(__file__).resolve().parent.parent.parent
    persist_path = (backend_dir / persist_dir).resolve()
    persist_path.mkdir(parents=True, exist_ok=True)

    _client = chromadb.PersistentClient(path=str(persist_path))
    _collection = _client.get_or_create_collection(
        name="knowledge_base",
        metadata={"hnsw:space": "cosine"}
    )
    return _collection


def _call_embedding_api(texts: List[str]) -> List[List[float]]:
    """调用 Embedding API 将文本列表转为向量，按 32 条一批发送。"""
    import requests as _req
    _ensure_env()
    api_key = (os.getenv('AI_API_KEY') or '').strip()
    base_url = (os.getenv('AI_BASE_URL') or 'https://api.siliconflow.cn/v1').strip().rstrip('/')
    model = (os.getenv('EMBEDDING_MODEL') or 'BAAI/bge-large-zh-v1.5').strip()

    if not api_key or api_key.startswith('sk-your'):
        raise ValueError("AI_API_KEY not configured for embedding")

    url = f"{base_url}/embeddings"
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}

    all_embeddings: List[List[float]] = []
    batch_size = 32
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        resp = _req.post(url, headers=headers, json={
            'model': model, 'input': batch, 'encoding_format': 'float'
        }, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if 'error' in data:
            raise ValueError(f"Embedding API error: {data['error']}")
        all_embeddings.extend(item['embedding'] for item in data['data'])
    return all_embeddings


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """按段落将文本切分为多个片段，每段不超过 chunk_size 字符。"""
    text = (text or '').strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    paragraphs = re.split(r'\n\s*\n', text)
    chunks: List[str] = []
    current: List[str] = []
    current_len = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if current_len + len(para) > chunk_size and current:
            chunks.append('\n\n'.join(current))
            current = []
            current_len = 0
        current.append(para)
        current_len += len(para)

    if current:
        chunks.append('\n\n'.join(current))
    return chunks if chunks else [text]


def _parse_document(content: bytes, filename: str) -> str:
    """解析文档内容为纯文本，支持 .txt / .md（多编码探测）和 .docx。"""
    ext = Path(filename).suffix.lower()
    if ext in ('.txt', '.md'):
        for enc in ('utf-8', 'gbk', 'gb2312', 'latin-1'):
            try:
                return content.decode(enc)
            except (UnicodeDecodeError, LookupError):
                continue
        return content.decode('utf-8', errors='replace')
    if ext == '.docx':
        try:
            from docx import Document
            import io
            doc = Document(io.BytesIO(content))
            return '\n\n'.join(p.text for p in doc.paragraphs if p.text.strip())
        except ImportError:
            raise RuntimeError("python-docx is not installed. Run: pip install python-docx")
    raise ValueError(f"Unsupported file type: {ext}. Supported: .txt, .md, .docx")


# ---- 公共接口 ----

def upload_document(file_content: bytes, filename: str, metadata: dict = None) -> dict:
    """上传文档到知识库：解析 → 分块 → 向量化 → 存入 ChromaDB。"""
    text = _parse_document(file_content, filename)
    if not text.strip():
        raise ValueError("Document content is empty after parsing")

    doc_id = str(uuid.uuid4())
    chunks = _chunk_text(text)
    if not chunks:
        raise ValueError("No text chunks produced from document")

    embeddings = _call_embedding_api(chunks)
    collection = _get_collection()
    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {'doc_id': doc_id, 'filename': filename, 'chunk_index': i,
         'total_chunks': len(chunks), **(metadata or {})}
        for i in range(len(chunks))
    ]
    collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
    return {'doc_id': doc_id, 'filename': filename, 'total_chunks': len(chunks), 'text_length': len(text)}


def list_documents() -> List[dict]:
    """列出知识库中所有已索引的文档（按 doc_id 去重）。"""
    collection = _get_collection()
    result = collection.get(include=['metadatas'])
    seen: dict = {}
    for meta in (result.get('metadatas') or []):
        doc_id = meta.get('doc_id')
        if doc_id and doc_id not in seen:
            seen[doc_id] = {
                'doc_id': doc_id,
                'filename': meta.get('filename', ''),
                'total_chunks': meta.get('total_chunks', 0),
            }
    return list(seen.values())


def delete_document(doc_id: str) -> bool:
    """从知识库中删除指定文档及其所有向量片段。"""
    collection = _get_collection()
    result = collection.get(where={'doc_id': doc_id}, include=['metadatas'])
    ids = result.get('ids') or []
    if not ids:
        return False
    collection.delete(ids=ids)
    return True


def search(query_text: str, top_k: int = None) -> List[dict]:
    """语义检索：将查询文本向量化，在知识库中查找最相似的 top_k 个片段。"""
    _ensure_env()
    if top_k is None:
        try:
            top_k = int(os.getenv('KNOWLEDGE_TOP_K', '5'))
        except (TypeError, ValueError):
            top_k = 5

    collection = _get_collection()
    if collection.count() == 0:
        return []

    query_embedding = _call_embedding_api([query_text])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=['documents', 'metadatas', 'distances']
    )

    items = []
    for i in range(len(results['ids'][0])):
        items.append({
            'chunk_id': results['ids'][0][i],
            'text': results['documents'][0][i],
            'metadata': results['metadatas'][0][i],
            'distance': results['distances'][0][i],
        })
    return items
