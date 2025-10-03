from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import settings

splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", ".", " "]
)

def chunk_text(text: str):
    return splitter.split_text(text)


def build_context(docs, max_chunks: int):
    chunks = [d.page_content if hasattr(d, 'page_content') else d for d in docs][:max_chunks]
    return "\n---\n".join(chunks)


def format_citations(docs):
    cites = []
    for d in docs:
        meta = getattr(d, 'metadata', {}) or {}
        cites.append({
            "source": meta.get("source") or meta.get("path") or "unknown",
            "snippet": (getattr(d, 'page_content', str(d))[:200] + "…") if getattr(d, 'page_content', None) else ""
        })
    return cites

