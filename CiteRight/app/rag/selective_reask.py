from typing import List
from app.config import settings


def should_reask(rerank_scores: List[float], used_context_chunks: int, answer_text: str) -> bool:
    if not rerank_scores:
        return True
    # Confidence proxy: average of top rerank scores + presence of citation tokens
    avg_score = sum(rerank_scores) / len(rerank_scores)
    has_citation_marker = "[" in answer_text and "]" in answer_text
    coverage_ok = used_context_chunks >= max(1, int(settings.CONTEXT_TOP_K * settings.MIN_CITATION_COVERAGE))
    if avg_score < settings.MIN_RERANK_SCORE or (not has_citation_marker) or (not coverage_ok):
        return True
    return False

