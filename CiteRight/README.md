# CiteRight 🎯

A multi-source RAG (Retrieval-Augmented Generation) system that provides accurate, well-cited answers from **Wikipedia, StackExchange, arXiv, and Wikidata**—or exclusively from your uploaded PDFs.

## ✨ Key Features

- **Multi-Source Intelligence**: Pull from 4 authoritative sources (Wikipedia, StackExchange, arXiv, Wikidata)
- **PDF-Only Mode**: Search exclusively in your uploaded documents with zero external contamination
- **Citation Diversity**: Maximum 2 citations per source for balanced, multi-perspective answers
- **Fresh Data**: No caching - every query fetches current, relevant content
- **Quality Evaluation**: Optional metrics (faithfulness, accuracy, precision) with transparency traces
- **100% Local & Private**: Runs entirely on your machine using Ollama - no external API calls
- **Hybrid Retrieval**: FAISS (semantic) + BM25 (keyword) + Cross-Encoder reranking

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Ollama ([Install](https://ollama.ai))

### Installation

**1. Install Ollama and pull the model:**
```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the LLM model
ollama pull wizardlm2:latest

# Start Ollama
ollama serve
```

**2. Set up the project:**
```bash
# Clone the repository
git clone <your-repo-url>
cd CiteRight

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**3. Start the application:**

Open **3 terminal windows**:

**Terminal 1** - Ollama (if not already running):
```bash
ollama serve
```

**Terminal 2** - API Backend:
```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 3** - Streamlit UI:
```bash
source venv/bin/activate
streamlit run ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

**4. Open your browser:**
- **UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## 📖 How to Use

### Basic Query with External Sources

1. Open http://localhost:8501
2. Type your question (e.g., "What is quantum mechanics?")
3. Select sources (Wikipedia, StackExchange, arXiv, Wikidata)
4. Adjust "Max items per source" (default: 3)
5. Click **🔍 Search**

### PDF-Only Mode (Your Documents)

1. **Upload PDF**: Click "Upload PDF" in sidebar → Choose file → Upload
2. **Enable PDF-only**: Check "Search in uploaded PDFs only"
3. **Ask question**: Type your question about the PDF content
4. **Search**: Click **🔍 Search** - results will come ONLY from your PDF

### Enable Quality Evaluation (Optional)

- Check "Enable Query Evaluation" to get:
  - **Faithfulness Score**: How grounded the answer is (0-1)
  - **Citation Accuracy**: Correctness of attributions
  - **Precision@k**: Relevance of retrieved content
  - **Transparency Trace**: Sentence-level source mapping

## 🎯 Example Use Cases

### Research & Fact-Checking
```
Query: "What are the key principles of quantum mechanics?"
Sources: Wikipedia + arXiv
Result: Scholarly answer with academic citations
```

### Technical Q&A
```
Query: "How does FAISS indexing work?"
Sources: StackExchange + Wikipedia
Result: Practical explanation with community insights
```

### Private Document Analysis
```
Upload: Your resume/report/paper
PDF-Only Mode: Enabled
Query: "What are the key technical skills mentioned?"
Result: Answer ONLY from your document - no hallucinations
```

## ⚙️ Configuration

Edit `env.example` (or create `.env`):

```env
# Models
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
OLLAMA_MODEL=wizardlm2:latest
OLLAMA_HOST=http://localhost:11434

# Retrieval Settings
RETRIEVE_K=20          # Initial candidates
RERANK_TOP_K=5         # After reranking
CONTEXT_TOP_K=4        # Used in prompt

# Chunking
CHUNK_SIZE=900
CHUNK_OVERLAP=180
```

## 📊 Data Sources

| Source | Content | License | Max Citations per Query |
|--------|---------|---------|------------------------|
| **Wikipedia** | Encyclopedia articles | CC BY-SA 3.0 | 2 |
| **StackExchange** | Q&A discussions | CC BY-SA 4.0 | 2 |
| **arXiv** | Research papers | CC BY 4.0 | 2 |
| **Wikidata** | Structured data | CC0 1.0 | 2 |
| **User PDFs** | Your documents | User Provided | Unlimited |

*Citation diversity ensures balanced, multi-perspective answers*

## 🏗️ Architecture

```
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│  Source Selection       │
│  (Wiki/Stack/arXiv/     │
│   Wikidata/PDF-only)    │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Dynamic Ingestion      │
│  (Fresh content fetch)  │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Hybrid Retrieval       │
│  (FAISS + BM25)         │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Reranking              │
│  (Cross-Encoder)        │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Source Diversification │
│  (Max 2 per source)     │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Generation             │
│  (Ollama LLM)           │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Optional Evaluation    │
│  (Quality Metrics)      │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Cited Answer           │
└─────────────────────────┘
```

## 🛠️ Project Structure

```
CiteRight/
├── app/
│   ├── main.py                    # FastAPI backend
│   ├── models.py                  # Pydantic models
│   ├── config.py                  # Settings
│   └── rag/
│       ├── multiverse_ingester.py # Multi-source orchestrator
│       ├── wikipedia_ingester.py  # Wikipedia API
│       ├── stackexchange_ingester.py # StackExchange API
│       ├── arxiv_ingester.py      # arXiv API
│       ├── wikidata_ingester.py   # Wikidata API
│       ├── pdf_processor.py       # PDF handling
│       ├── retriever.py           # Hybrid search (FAISS + BM25)
│       ├── reranker.py            # Cross-encoder
│       ├── generator.py           # Ollama LLM
│       ├── evaluator.py           # Quality metrics
│       └── utils.py               # Helper functions
├── ui/
│   └── streamlit_app.py           # Web interface
├── .cursor/
│   └── prompts.json               # System prompts
├── requirements.txt               # Dependencies
├── EVALUATOR.md                   # Evaluation system docs
└── README.md                      # This file
```

## 🔍 API Endpoints

### Query with Source Selection
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "sources": ["wikipedia", "stackexchange"],
    "max_per_source": 3,
    "enable_evaluation": false,
    "pdf_only": false
  }'
```

### Query PDF-Only Mode
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key skills?",
    "pdf_only": true
  }'
```

### Upload PDF
```bash
curl -X POST "http://localhost:8000/upload-pdf" \
  -F "file=@/path/to/document.pdf"
```

## 🐛 Troubleshooting

### Ollama not found
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### Model not found
```bash
# Pull the model
ollama pull wizardlm2:latest

# List available models
ollama list
```

### Port already in use
```bash
# Use different ports
uvicorn app.main:app --port 8001
streamlit run ui/streamlit_app.py --server.port 8502
```

### Slow responses
- Disable evaluation (faster)
- Reduce `max_per_source` (fewer API calls)
- Use smaller Ollama model: `ollama pull llama3.2:1b`

### PDF not being searched
1. Make sure PDF is uploaded first (check sidebar)
2. Enable "Search in uploaded PDFs only" checkbox
3. The system will filter to ONLY User Upload sources

## 📝 Requirements

- **Python**: 3.9+
- **Ollama**: Latest version
- **RAM**: 8GB minimum (16GB recommended for wizardlm2)
- **Storage**: 5GB for model + embeddings

## 🔐 Privacy & Security

✅ **100% Local Processing**
- All LLM inference on your machine
- No data sent to external LLM APIs
- Source content fetched from public APIs only

✅ **PDF Privacy**
- Uploaded PDFs stay local
- Never sent to external services
- Cleared with vectorstore unless in PDF-only mode

## 🎓 Advanced Features

### Citation Diversity
- Automatically limits to 2 citations per source
- Ensures balanced, multi-perspective answers
- Prevents single-source dominance

### Selective Re-ask
- Detects low-confidence answers
- Automatically refines with stricter citations
- No user intervention needed

### Quality Evaluation
- LLM-based answer auditing
- Grounding verification
- Cross-source synthesis
- Adaptive tone adjustment

## 🤝 Contributing

This project demonstrates:
- Multi-source RAG architecture
- Hybrid retrieval systems
- Citation diversity mechanisms
- Quality evaluation frameworks
- Local LLM integration

## 📄 License

MIT License - Feel free to use for your own projects!

## 🙏 Acknowledgments

Built with:
- [Ollama](https://ollama.ai) - Local LLM runtime
- [LangChain](https://langchain.com) - RAG framework
- [FAISS](https://faiss.ai) - Vector search
- [Sentence Transformers](https://www.sbert.net) - Embeddings
- [FastAPI](https://fastapi.tiangolo.com) - Backend API
- [Streamlit](https://streamlit.io) - Web UI

---

**Made with ❤️ for accurate, well-cited AI responses**
