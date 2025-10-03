from langchain_community.vectorstores import FAISS
from rank_bm25 import BM25Okapi
from typing import List, Tuple
import numpy as np
from app.deps import vectorstore, embeddings
from app.config import settings

_bm25 = None
_bm25_docs = []
_bm25_paths = []


def _ensure_bm25():
    global _bm25
    if _bm25 is not None:
        return _bm25
    # Build BM25 corpus from FAISS docstore to keep things in sync
    vs = vectorstore()
    store = vs.docstore._dict  # {id: Document}
    texts = []
    paths = []
    for _id, doc in store.items():
        texts.append(doc.page_content)
        paths.append(doc.metadata.get("source", "unknown"))
    tokenized = [t.lower().split() for t in texts]
    bm25 = BM25Okapi(tokenized)
    global _bm25_docs, _bm25_paths
    _bm25_docs, _bm25_paths, _bm25 = texts, paths, bm25
    return _bm25


def hybrid_search(query: str, k: int) -> List:
    """Combine FAISS (dense) + BM25 (sparse), then dedupe and score-union."""
    vs = vectorstore()

    # Dense candidates
    dense_docs = vs.similarity_search(query, k=k)

    # Sparse candidates
    bm25 = _ensure_bm25()
    scores = bm25.get_scores(query.lower().split())
    top_idx = np.argsort(scores)[::-1][:k]
    sparse_docs = []
    for i in top_idx:
        from langchain.docstore.document import Document
        sparse_docs.append(Document(page_content=_bm25_docs[i], metadata={"source": _bm25_paths[i], "bm25": float(scores[i])}))

    # Merge by simple max-score heuristic (dense has implicit cosine sim via FAISS ordering)
    merged = []
    seen = set()
    for d in dense_docs + sparse_docs:
        key = (d.metadata.get("source", ""), d.page_content[:80])
        if key in seen:
            continue
        seen.add(key)
        merged.append(d)

    return merged[:k]

