from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from app.config import settings
from app.rag.reranker import CrossEncoderReranker
from app.rag.caching import SqliteCache
from pathlib import Path
import os

_embeddings = None
_vectorstore = None
_reranker = None
_cache = None


def embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
    return _embeddings


def vectorstore():
    global _vectorstore
    if _vectorstore is None:
        Path(settings.VECTOR_INDEX_PATH).parent.mkdir(parents=True, exist_ok=True)
        if os.path.isdir(settings.VECTOR_INDEX_PATH):
            _vectorstore = FAISS.load_local(settings.VECTOR_INDEX_PATH, embeddings(), allow_dangerous_deserialization=True)
        else:
            _vectorstore = FAISS.from_texts([""], embeddings())  # empty placeholder
    return _vectorstore


def reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoderReranker(settings.RERANKER_MODEL)
    return _reranker


def cache():
    global _cache
    if _cache is None:
        Path(settings.CACHE_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        _cache = SqliteCache(settings.CACHE_DB_PATH)
    return _cache

