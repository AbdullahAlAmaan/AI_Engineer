from sentence_transformers import CrossEncoder
from typing import List

class CrossEncoderReranker:
    def __init__(self, model_name: str):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, docs: List, top_k: int = 5):
        if not docs:
            return []
        pairs = [[query, d.page_content] for d in docs]
        scores = self.model.predict(pairs).tolist()
        ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        return [d for d, s in ranked[:top_k]], [float(s) for _, s in ranked[:top_k]]

