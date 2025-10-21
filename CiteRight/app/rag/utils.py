from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.config import settings

splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", ".", " "]
)

def chunk_text(text: str):
    return splitter.split_text(text)


def diversify_sources(docs, max_per_source: int = 2):
    """
    Diversify documents by limiting how many come from each source
    
    Args:
        docs: List of documents with metadata
        max_per_source: Maximum documents per source origin (default: 2)
        
    Returns:
        Diversified list of documents
    """
    diversified = []
    source_counts = {}
    
    for doc in docs:
        meta = getattr(doc, 'metadata', {}) or {}
        origin = meta.get('origin', 'Unknown')
        
        # Check if we've reached the limit for this source
        if source_counts.get(origin, 0) >= max_per_source:
            continue  # Skip this document
        
        diversified.append(doc)
        source_counts[origin] = source_counts.get(origin, 0) + 1
    
    return diversified


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


def format_citations(docs, max_per_source: int = 2):
    """
    Format citations for CiteRight-Multiverse with structured metadata
    Limits the number of citations from each source for diversity
    
    Args:
        docs: List of documents to cite
        max_per_source: Maximum citations per source origin (default: 2)
    """
    cites = []
    source_counts = {}  # Track citations per origin
    
    for d in docs:
        meta = getattr(d, 'metadata', {}) or {}
        
        # Extract metadata fields
        source = meta.get("source", "unknown")
        origin = meta.get("origin", "Unknown")
        license_info = meta.get("license", "Unknown")
        url = meta.get("url", "")
        
        # Check if we've reached the limit for this source
        if source_counts.get(origin, 0) >= max_per_source:
            continue  # Skip this citation
        
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
        
        # Increment count for this origin
        source_counts[origin] = source_counts.get(origin, 0) + 1
    
    return cites

