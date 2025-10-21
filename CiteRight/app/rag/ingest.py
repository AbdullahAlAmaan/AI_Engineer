from pathlib import Path
from typing import Iterable
from app.rag.utils import chunk_text
from app.config import settings
from app.deps import vectorstore, embeddings


def _read_file(p: Path) -> str:
    suf = p.suffix.lower()
    if suf in {".txt", ".md"}:
        return p.read_text(encoding="utf-8", errors="ignore")
    # Simple PDF fallback via pypdf if you add it; here we keep text-only for portability
    raise ValueError(f"Unsupported file type: {p}")


def ingest_paths(paths: Iterable[str]):
    vs = vectorstore()
    texts = []
    metas = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            for f in p.rglob("*.txt"):
                txt = _read_file(f)
                for ch in chunk_text(txt):
                    texts.append(ch)
                    # Enhanced metadata for CiteRight-Multiverse
                    metas.append({
                        "source": f.name,
                        "origin": "Local Document",
                        "license": "Unknown",
                        "url": "",
                        "path": str(f)
                    })
        else:
            txt = _read_file(p)
            for ch in chunk_text(txt):
                texts.append(ch)
                # Enhanced metadata for CiteRight-Multiverse
                metas.append({
                    "source": p.name,
                    "origin": "Local Document", 
                    "license": "Unknown",
                    "url": "",
                    "path": str(p)
                })

    if texts:
        vs.add_texts(texts=texts, metadatas=metas)
        vs.save_local(settings.VECTOR_INDEX_PATH)
    return {"chunks_added": len(texts)}

