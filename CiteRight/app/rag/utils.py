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
    """Build structured context with metadata for CiteRight-Multiverse"""
    chunks = []
    for i, d in enumerate(docs[:max_chunks]):
        if hasattr(d, 'page_content'):
            content = d.page_content
            meta = getattr(d, 'metadata', {}) or {}
        else:
            content = str(d)
            meta = {}
        
        # Extract metadata fields
        source = meta.get("source", "unknown")
        origin = meta.get("origin", "Unknown")
        license_info = meta.get("license", "Unknown")
        url = meta.get("url", "")
        
        # Format chunk with metadata header
        chunk_header = f"({origin} — \"{source}\", {license_info})"
        if url:
            chunk_header += f" [{url}]"
        
        formatted_chunk = f"{chunk_header}\n{content}"
        chunks.append(formatted_chunk)
    
    return "\n\n---\n\n".join(chunks)


def format_citations(docs):
    """Format citations for CiteRight-Multiverse with structured metadata"""
    cites = []
    for d in docs:
        meta = getattr(d, 'metadata', {}) or {}
        
        # Extract metadata fields
        source = meta.get("source", "unknown")
        origin = meta.get("origin", "Unknown")
        license_info = meta.get("license", "Unknown")
        url = meta.get("url", "")
        
        # Get content snippet
        content = getattr(d, 'page_content', str(d))
        snippet = (content[:200] + "…") if content else ""
        
        cites.append({
            "source": source,
            "origin": origin,
            "license": license_info,
            "url": url,
            "snippet": snippet,
            "formatted_source": f"{origin} — \"{source}\" ({license_info})"
        })
    return cites

