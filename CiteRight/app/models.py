from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class IngestRequest(BaseModel):
    paths: List[str]

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = None
    sources: Optional[List[str]] = None
    max_per_source: Optional[int] = 5
    enable_evaluation: Optional[bool] = False
    pdf_only: Optional[bool] = False  # Only search uploaded PDFs

class QueryResponse(BaseModel):
    answer: str
    citations: list
    used_reask: bool
    timings_ms: dict
    evaluation: Optional[Dict[str, Any]] = None

class MultiverseIngestRequest(BaseModel):
    query: Optional[str] = None
    sources: Optional[List[str]] = None
    max_per_source: Optional[int] = 5
    specific_content: Optional[Dict[str, Any]] = None
