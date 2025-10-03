from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from app.models import IngestRequest, QueryRequest, QueryResponse
from app.rag.ingest import ingest_paths
from app.rag.retriever import hybrid_search
from app.rag.reranker import CrossEncoderReranker
from app.rag.generator import generate_with_ollama
from app.rag.selective_reask import should_reask
from app.rag.utils import build_context, format_citations
from app.logging_utils import timer, log_json
from app.deps import reranker, cache, vectorstore
from app.config import settings

app = FastAPI(title="RAG Assistant")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/ingest")
def ingest(req: IngestRequest):
    with timer("ingest"):
        res = ingest_paths(req.paths)
        vectorstore().save_local(settings.VECTOR_INDEX_PATH)
        return res

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    q = req.query.strip()

    # Cache hit
    cached = cache().get(q)
    if cached:
        answer, citations = cached
        return QueryResponse(answer=answer, citations=citations, used_reask=False, timings_ms={"cache": 0})

    timings = {}

    # Retrieval
    with timer("retrieve"):
        candidates = hybrid_search(q, k=req.top_k or settings.RETRIEVE_K)

    # Rerank
    with timer("rerank"):
        top_docs, scores = reranker().rerank(q, candidates, top_k=settings.RERANK_TOP_K)

    # Context build
    context = build_context(top_docs, settings.CONTEXT_TOP_K)

    # Generate
    with timer("generate"):
        answer = generate_with_ollama(q, context)

    # Decide re-ask
    used_reask = False
    if should_reask(scores, used_context_chunks=len(top_docs), answer_text=answer):
        used_reask = True
        # Simple refinement: append instruction to be stricter + use different top-k slice
        alt_context = build_context(top_docs, max(1, settings.CONTEXT_TOP_K - 1))
        answer = generate_with_ollama(q + " (be strictly extractive; cite)", alt_context)

    cites = format_citations(top_docs)
    cache().set(q, answer, cites)

    log_json({"metric": "query", "used_reask": used_reask})
    return QueryResponse(answer=answer, citations=cites, used_reask=used_reask, timings_ms=timings)

