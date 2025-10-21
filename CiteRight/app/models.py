from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class IngestRequest(BaseModel):
    paths: List[str]

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = None
    sources: Optional[List[str]] = None
    max_per_source: Optional[int] = 5

class QueryResponse(BaseModel):
    answer: str
    citations: list
    used_reask: bool
    timings_ms: dict

class MultiverseIngestRequest(BaseModel):
    query: Optional[str] = None
    sources: Optional[List[str]] = None
    max_per_source: Optional[int] = 5
    specific_content: Optional[Dict[str, Any]] = None
