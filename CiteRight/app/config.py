from pydantic import BaseModel
import os

class Settings(BaseModel):
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    RERANKER_MODEL: str = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "wizardlm2:latest")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    VECTOR_INDEX_PATH: str = os.getenv("VECTOR_INDEX_PATH", "./data/index/faiss")
    BM25_INDEX_PATH: str = os.getenv("BM25_INDEX_PATH", "./data/index/bm25.pkl")
    CACHE_DB_PATH: str = os.getenv("CACHE_DB_PATH", "./data/cache.sqlite")

    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 900))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 180))

    RETRIEVE_K: int = int(os.getenv("RETRIEVE_K", 20))
    RERANK_TOP_K: int = int(os.getenv("RERANK_TOP_K", 5))
    CONTEXT_TOP_K: int = int(os.getenv("CONTEXT_TOP_K", 4))

    MIN_RERANK_SCORE: float = float(os.getenv("MIN_RERANK_SCORE", 0.4))
    MIN_CITATION_COVERAGE: float = float(os.getenv("MIN_CITATION_COVERAGE", 0.6))
    MAX_CONTEXT_TOKENS: int = int(os.getenv("MAX_CONTEXT_TOKENS", 3200))

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))

settings = Settings()

