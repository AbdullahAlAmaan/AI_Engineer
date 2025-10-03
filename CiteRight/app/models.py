from pydantic import BaseModel
from typing import List, Optional

class IngestRequest(BaseModel):
    paths: List[str]

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = None

class QueryResponse(BaseModel):
    answer: str
    citations: list
    used_reask: bool
    timings_ms: dict
