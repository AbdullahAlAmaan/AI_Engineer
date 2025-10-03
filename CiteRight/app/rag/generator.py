import requests
from app.config import settings

PROMPT = (
    "You are a careful enterprise assistant. Answer ONLY using the provided context. "
    "Cite sources inline like [source]. If context is insufficient, say you don't know.\n\n"
    "Context:\n{context}\n\nQuestion: {query}\nAnswer:"
)


def generate_with_ollama(query: str, context: str) -> str:
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": PROMPT.format(context=context, query=query),
        "stream": False,
        "options": {"temperature": 0.2}
    }
    r = requests.post(f"{settings.OLLAMA_HOST}/api/generate", json=payload, timeout=120)
    r.raise_for_status()
    return r.json().get("response", "")

