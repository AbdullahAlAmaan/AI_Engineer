import streamlit as st
import requests, os

API = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="CiteRight-Multiverse", layout="centered")
st.title("CiteRight")

# Sidebar for ingestion
with st.sidebar:
    st.header("📚 Data Ingestion")
    
    # PDF upload
    st.subheader("📄 Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        if st.button("📤 Upload PDF"):
            with st.spinner("Processing PDF..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                r = requests.post(f"{API}/upload-pdf", files=files)
                if r.ok:
                    result = r.json()
                    st.success(f"✅ Uploaded: {result['filename']}")
                    st.info(f"📄 {result['page_count']} pages, {result['chunks_added']} chunks")
                else:
                    st.error(f"❌ Upload failed: {r.text}")
    
    st.divider()
    
    # Multi-source ingestion
    st.subheader("Multi-Source Ingestion")
    
    # Query-based ingestion
    multiverse_query = st.text_input("Search query", placeholder="quantum mechanics")
    
    col1, col2 = st.columns(2)
    with col1:
        wikipedia_enabled = st.checkbox("Wikipedia", value=True)
        stackexchange_enabled = st.checkbox("StackExchange", value=True)
    with col2:
        arxiv_enabled = st.checkbox("arXiv", value=True)
        wikidata_enabled = st.checkbox("Wikidata", value=True)
    
    max_per_source = st.slider("Max items per source", 1, 10, 5)
    
    if st.button("Ingest from Sources") and multiverse_query:
        sources = []
        if wikipedia_enabled:
            sources.append("wikipedia")
        if stackexchange_enabled:
            sources.append("stackexchange")
        if arxiv_enabled:
            sources.append("arxiv")
        if wikidata_enabled:
            sources.append("wikidata")
        
        if sources:
            with st.spinner("Ingesting from multiple sources..."):
                payload = {
                    "query": multiverse_query,
                    "sources": sources,
                    "max_per_source": max_per_source
                }
                r = requests.post(f"{API}/ingest-multiverse", json=payload)
                if r.ok:
                    result = r.json()
                    st.success(f"✅ Ingested {result['total_chunks']} chunks")
                    st.json(result['source_stats'])
                else:
                    st.error(f"❌ Failed: {r.text}")
        else:
            st.warning("Please select at least one source")
    
    st.divider()
    
    # Specific content ingestion
    st.subheader("Specific Content")
    
    with st.expander("Add specific content"):
        wikipedia_titles = st.text_area("Wikipedia titles (one per line)", 
                                     placeholder="Quantum mechanics\nAlbert Einstein")
        stackexchange_ids = st.text_area("StackExchange question IDs (one per line)", 
                                       placeholder="12345\n67890")
        arxiv_ids = st.text_area("arXiv paper IDs (one per line)", 
                               placeholder="2304.01234\n2305.05678")
        wikidata_ids = st.text_area("Wikidata entity IDs (one per line)", 
                                 placeholder="Q937\nQ42")
        
        if st.button("Add Specific Content"):
            specific_content = {}
            
            if wikipedia_titles.strip():
                specific_content['wikipedia_titles'] = [t.strip() for t in wikipedia_titles.split('\n') if t.strip()]
            if stackexchange_ids.strip():
                specific_content['stackexchange_questions'] = [int(id.strip()) for id in stackexchange_ids.split('\n') if id.strip().isdigit()]
            if arxiv_ids.strip():
                specific_content['arxiv_ids'] = [id.strip() for id in arxiv_ids.split('\n') if id.strip()]
            if wikidata_ids.strip():
                specific_content['wikidata_ids'] = [id.strip() for id in wikidata_ids.split('\n') if id.strip()]
            
            if specific_content:
                with st.spinner("Adding specific content..."):
                    payload = {"specific_content": specific_content}
                    r = requests.post(f"{API}/ingest-multiverse", json=payload)
                    if r.ok:
                        result = r.json()
                        st.success(f"✅ Added {result['total_chunks']} chunks")
                        st.json(result['source_stats'])
                    else:
                        st.error(f"❌ Failed: {r.text}")
            else:
                st.warning("Please provide at least one content ID")

# Main query interface
st.header("🔍 Ask CiteRight-Multiverse")

query = st.text_input("Ask a question", placeholder="What is lemmatization? How does it work?")

# Source selection for query
st.subheader("📚 Select Sources for Query")
col1, col2 = st.columns(2)
with col1:
    query_wikipedia = st.checkbox("Wikipedia", value=True, key="query_wiki")
    query_stackexchange = st.checkbox("StackExchange", value=True, key="query_stack")
with col2:
    query_arxiv = st.checkbox("arXiv", value=True, key="query_arxiv")
    query_wikidata = st.checkbox("Wikidata", value=True, key="query_wikidata")

query_max_per_source = st.slider("Max items per source", 1, 10, 3, key="query_max")

if st.button("🔍 Search") and query:
    # Prepare selected sources
    selected_sources = []
    if query_wikipedia:
        selected_sources.append("wikipedia")
    if query_stackexchange:
        selected_sources.append("stackexchange")
    if query_arxiv:
        selected_sources.append("arxiv")
    if query_wikidata:
        selected_sources.append("wikidata")
    
    with st.spinner("Thinking..."):
        payload = {
            "query": query,
            "sources": selected_sources,
            "max_per_source": query_max_per_source
        }
        r = requests.post(f"{API}/query", json=payload)
        if r.ok:
            out = r.json()
            
            st.subheader("📝 Answer")
            st.write(out["answer"])
            
            if out.get("used_reask"):
                st.info("🔄 This answer was refined using selective re-ask for better quality.")
            
            st.subheader("📚 Sources")
            for i, c in enumerate(out["citations"]):
                with st.expander(f"Source {i+1}: {c.get('formatted_source', c.get('source', 'Unknown'))}"):
                    st.write(f"**Origin:** {c.get('origin', 'Unknown')}")
                    st.write(f"**License:** {c.get('license', 'Unknown')}")
                    if c.get('url'):
                        st.write(f"**URL:** {c['url']}")
                    st.write(f"**Snippet:** {c['snippet']}")
        else:
            st.error(f"❌ Query failed: {r.text}")

# Information section
with st.expander("ℹ️ About CiteRight-Multiverse"):
    st.markdown("""
    **CiteRight-Multiverse** is a local retrieval-augmented assistant that pulls content from multiple authoritative sources:
    
    - **Wikipedia**: Encyclopedia articles (CC BY-SA 3.0)
    - **StackExchange**: Q&A content (CC BY-SA 4.0)  
    - **arXiv**: Research papers (CC BY 4.0)
    - **Wikidata**: Structured data (CC0 1.0)
    
    The system uses hybrid retrieval (FAISS + BM25), cross-encoder reranking, and selective re-ask for high-quality, well-cited responses.
    
    All processing happens locally with Ollama models - your data stays private!
    """)

