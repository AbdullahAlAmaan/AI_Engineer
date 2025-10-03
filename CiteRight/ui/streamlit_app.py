import streamlit as st
import requests, os

API = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="RAG Assistant", layout="centered")
st.title("RAG Assistant (Hybrid + Rerank + Ollama)")

with st.sidebar:
    st.header("Ingest")
    ingest_dir = st.text_input("Folder path", "./data/sample_docs")
    if st.button("Ingest"):
        r = requests.post(f"{API}/ingest", json={"paths": [ingest_dir]})
        st.success(r.json())

query = st.text_input("Ask a question", placeholder="What is RAG?")
if st.button("Search") and query:
    r = requests.post(f"{API}/query", json={"query": query})
    if r.ok:
        out = r.json()
        st.subheader("Answer")
        st.write(out["answer"])
        st.subheader("Citations")
        for c in out["citations"]:
            st.code(f"{c['source']}: {c['snippet']}")
    else:
        st.error(r.text)

