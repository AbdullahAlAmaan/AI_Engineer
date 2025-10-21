import streamlit as st
import requests, os

API = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="CiteRight-Multiverse", layout="centered")
st.title("CiteRight")

# Initialize session state for source selection
if 'sources_selected' not in st.session_state:
    st.session_state.sources_selected = {
        'wikipedia': True,
        'stackexchange': True, 
        'arxiv': True,
        'wikidata': True
    }

# Sidebar for PDF upload only
with st.sidebar:
    st.subheader("Upload PDF")
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

# Main query interface

query = st.text_input("Ask a question", placeholder="What is quantum mechanics?")

# PDF-only mode toggle (at the top)
pdf_only = st.checkbox("Search in uploaded PDFs only", value=False)

if not pdf_only:
    # Source selection for query (only show when NOT in PDF-only mode)
    st.subheader(" Sources")
    col1, col2 = st.columns(2)
    with col1:
        query_wikipedia = st.checkbox("Wikipedia", value=st.session_state.sources_selected['wikipedia'], key="query_wiki")
        query_stackexchange = st.checkbox("StackExchange", value=st.session_state.sources_selected['stackexchange'], key="query_stack")
    with col2:
        query_arxiv = st.checkbox("arXiv", value=st.session_state.sources_selected['arxiv'], key="query_arxiv")
        query_wikidata = st.checkbox("Wikidata", value=st.session_state.sources_selected['wikidata'], key="query_wikidata")

    query_max_per_source = st.slider("Max items per source", 1, 10, 3, key="query_max")
else:
    # Set defaults when in PDF-only mode
    query_wikipedia = False
    query_stackexchange = False
    query_arxiv = False
    query_wikidata = False
    query_max_per_source = 0

# Evaluation toggle
enable_evaluation = st.checkbox("Enable Query Evaluation (slower)", value=False)

if st.button("🔍 Search") and query:
    # Save current selections to session state
    st.session_state.sources_selected = {
        'wikipedia': query_wikipedia,
        'stackexchange': query_stackexchange,
        'arxiv': query_arxiv,
        'wikidata': query_wikidata
    }
    
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
            "sources": selected_sources if not pdf_only else [],
            "max_per_source": query_max_per_source,
            "enable_evaluation": enable_evaluation,
            "pdf_only": pdf_only
        }
        r = requests.post(f"{API}/query", json=payload)
        if r.ok:
            out = r.json()
            
            st.subheader("📝 Answer")
            st.write(out["answer"])
            
            # Display evaluation metrics if available
            if out.get("evaluation") and not out["evaluation"].get("evaluation_failed"):
                eval_data = out["evaluation"]
                st.info("**Quality Metrics**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Faithfulness", f"{eval_data.get('faithfulness_score', 0):.2f}")
                with col2:
                    st.metric("Citation Accuracy", f"{eval_data.get('citation_accuracy', 0):.2f}")
                with col3:
                    st.metric("Precision@k", f"{eval_data.get('precision_at_k', 0):.2f}")
                
                
            st.subheader("Sources")
            for i, c in enumerate(out["citations"]):
                with st.expander(f"Source {i+1}: {c.get('formatted_source', c.get('source', 'Unknown'))}"):
                    st.write(f"**Origin:** {c.get('origin', 'Unknown')}")
                    st.write(f"**License:** {c.get('license', 'Unknown')}")
                    if c.get('url'):
                        st.write(f"**URL:** {c['url']}")
                    st.write(f"**Snippet:** {c['snippet']}")
        else:
            st.error(f"❌ Query failed: {r.text}")



