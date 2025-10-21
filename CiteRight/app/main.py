from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from app.models import IngestRequest, QueryRequest, QueryResponse, MultiverseIngestRequest
from app.rag.ingest import ingest_paths
from app.rag.multiverse_ingester import ingest_multiverse_content, ingest_specific_multiverse_content
from app.rag.pdf_processor import process_uploaded_pdf
from app.rag.retriever import hybrid_search
from app.rag.reranker import CrossEncoderReranker
from app.rag.generator import generate_with_ollama
from app.rag.selective_reask import should_reask
from app.rag.utils import build_context, format_citations, chunk_text, diversify_sources
from app.rag.evaluator import evaluate_answer
from app.logging_utils import timer, log_json
from app.deps import reranker, cache, vectorstore
from app.config import settings

app = FastAPI(title="CiteRight")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/ingest")
def ingest(req: IngestRequest):
    with timer("ingest"):
        res = ingest_paths(req.paths)
        vectorstore().save_local(settings.VECTOR_INDEX_PATH)
        return res

@app.post("/ingest-multiverse")
def ingest_multiverse(req: MultiverseIngestRequest):
    with timer("ingest_multiverse"):
        # Clear cache and vectorstore before new ingestion to avoid stale data
        cache().clear_all()
        
        # Clear existing vectorstore to start fresh
        from app.deps import embeddings
        from langchain_community.vectorstores import FAISS
        vs = FAISS.from_texts([""], embeddings())
        vs.save_local(settings.VECTOR_INDEX_PATH)
        
        if req.specific_content:
            res = ingest_specific_multiverse_content(**req.specific_content)
        else:
            # Log the sources being used for debugging
            log_json({"metric": "ingest_sources", "sources": req.sources, "query": req.query})
            res = ingest_multiverse_content(
                query=req.query,
                sources=req.sources,
                max_per_source=req.max_per_source
            )
        return res

@app.post("/clear-data")
def clear_data():
    """Clear all cached data and vectorstore"""
    with timer("clear_data"):
        try:
            # Clear cache
            cache().clear_all()
            
            # Clear vectorstore by creating a new empty one
            from app.deps import embeddings
            from langchain_community.vectorstores import FAISS
            vs = FAISS.from_texts([""], embeddings())
            vs.save_local(settings.VECTOR_INDEX_PATH)
            
            return {"message": "All data cleared successfully"}
        except Exception as e:
            return {"error": str(e)}

@app.post("/upload-pdf")
def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF file"""
    with timer("upload_pdf"):
        try:
            # Validate file type
            if not file.filename.lower().endswith('.pdf'):
                return {"error": "Only PDF files are supported"}
            
            # Read file content
            pdf_content = file.file.read()
            
            # Process PDF
            pdf_documents = process_uploaded_pdf(pdf_content, file.filename)
            
            if not pdf_documents:
                return {"error": "Failed to extract text from PDF"}
            
            # Process and chunk the content
            processed_chunks = []
            for doc in pdf_documents:
                chunks = chunk_text(doc['content'])
                for i, chunk in enumerate(chunks):
                    metadata = {
                        "source": doc.get('source', file.filename),
                        "origin": doc.get('origin', 'User Upload'),
                        "license": doc.get('license', 'User Provided'),
                        "url": doc.get('url', ''),
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "title": doc.get('title', file.filename),
                        "summary": doc.get('summary', ''),
                        **doc.get('metadata', {})
                    }
                    processed_chunks.append({
                        "content": chunk,
                        "metadata": metadata
                    })
            
            # Add to vectorstore
            if processed_chunks:
                vs = vectorstore()
                texts = [chunk['content'] for chunk in processed_chunks]
                metas = [chunk['metadata'] for chunk in processed_chunks]
                
                vs.add_texts(texts=texts, metadatas=metas)
                vs.save_local(settings.VECTOR_INDEX_PATH)
            
            return {
                "message": f"Successfully processed PDF: {file.filename}",
                "chunks_added": len(processed_chunks),
                "filename": file.filename,
                "page_count": pdf_documents[0].get('metadata', {}).get('page_count', 0)
            }
            
        except Exception as e:
            return {"error": f"Failed to process PDF: {str(e)}"}

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    q = req.query.strip()

    # Always clear cache and vectorstore for fresh results
    cache().clear_all()
    
    # Clear existing vectorstore to start fresh
    from app.deps import embeddings
    from langchain_community.vectorstores import FAISS
    vs = FAISS.from_texts([""], embeddings())
    vs.save_local(settings.VECTOR_INDEX_PATH)

    # If sources are specified, ingest content from those sources first
    if req.sources:
        log_json({"metric": "query_sources", "sources": req.sources, "query": q})
        ingest_multiverse_content(
            query=q,
            sources=req.sources,
            max_per_source=req.max_per_source
        )

    timings = {}

    # Retrieval
    with timer("retrieve"):
        candidates = hybrid_search(q, k=req.top_k or settings.RETRIEVE_K)

    # Rerank
    with timer("rerank"):
        top_docs, scores = reranker().rerank(q, candidates, top_k=settings.RERANK_TOP_K)
    
    # Diversify sources to ensure balanced representation
    top_docs = diversify_sources(top_docs, max_per_source=2)

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

    # Optional evaluation layer
    evaluation = None
    if req.enable_evaluation:
        with timer("evaluate"):
            evaluation = evaluate_answer(q, context, answer)
            # Use evaluated answer if available
            if evaluation and not evaluation.get("evaluation_failed"):
                answer = evaluation.get("final_answer", answer)

    log_json({"metric": "query", "used_reask": used_reask, "evaluation_enabled": req.enable_evaluation})
    return QueryResponse(answer=answer, citations=cites, used_reask=used_reask, timings_ms=timings, evaluation=evaluation)

