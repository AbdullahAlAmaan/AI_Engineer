# CiteRight 🎯

A multi-source RAG (Retrieval-Augmented Generation) assistant that pulls content from **Wikipedia, StackExchange, arXiv, and Wikidata** for accurate, well-cited answers.

## ✨ Key Features

- **Multi-Source Intelligence**: Pulls from 4 authoritative sources
- **Fresh Data Every Time**: No stale cached results
- **Citation Diversity**: Maximum 2 citations per source for balanced answers
- **Quality Evaluation**: Optional metrics (faithfulness, accuracy, precision)
- **PDF Upload**: Add your own documents
- **Local & Private**: Everything runs on your machine with Ollama

## 🚀 Quick Start (3 Steps)

### Step 1: Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the model
ollama pull wizardlm2:latest
```

### Step 2: Install Dependencies

```bash
# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### Step 3: Start the Application

**Terminal 1** - Start Ollama:
```bash
ollama serve
```

**Terminal 2** - Start the API:
```bash
source venv/bin/activate  # If using venv
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 3** - Start the UI:
```bash
source venv/bin/activate  # If using venv
streamlit run ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

### Step 4: Open Your Browser

- **UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## 📚 How to Use

### Basic Query

1. Open http://localhost:8501
2. Type your question (e.g., "What is machine learning?")
3. Select sources (Wikipedia, StackExchange, arXiv, Wikidata)
4. Adjust "Max items per source" (default: 3)
5. Click **Search** 🔍

### Enable Quality Evaluation (Optional)

- Check ☑️ "Enable Query Evaluation" 
- Takes longer but shows:
  - **Faithfulness Score**: How grounded the answer is
  - **Citation Accuracy**: Correctness of attributions
  - **Precision@k**: Relevance of retrieved content

### Upload Your Own PDFs

1. Click **"Upload PDF"** in the sidebar
2. Choose your PDF file
3. Click **"Upload PDF"** button
4. Your document is now searchable!

## 🎯 Example Queries

```
"What is quantum mechanics?"
"Explain lemmatization in NLP"
"How does machine learning work?"
"What are the key differences between Python and JavaScript?"
```

## 🔧 Configuration

Edit `.env` or `env.example` to customize:

```env
# Models
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
OLLAMA_MODEL=wizardlm2:latest

# Retrieval Settings
RETRIEVE_K=20          # Initial candidates
RERANK_TOP_K=5         # After reranking
CONTEXT_TOP_K=4        # Used in prompt
```

## 📊 Data Sources

| Source | Content | License | Max per Query |
|--------|---------|---------|---------------|
| **Wikipedia** | Encyclopedia | CC BY-SA 3.0 | 2 citations |
| **StackExchange** | Q&A | CC BY-SA 4.0 | 2 citations |
| **arXiv** | Research Papers | CC BY 4.0 | 2 citations |
| **Wikidata** | Structured Data | CC0 1.0 | 2 citations |

*Note: Citation diversity ensures balanced, multi-perspective answers*

## 🏗️ Architecture

```
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│  Multi-Source Ingestion │
│  (Wikipedia, Stack,     │
│   arXiv, Wikidata)      │
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
│       ├── multiverse_ingester.py # Multi-source ingestion
│       ├── wikipedia_ingester.py  # Wikipedia API
│       ├── stackexchange_ingester.py # Stack API
│       ├── arxiv_ingester.py      # arXiv API
│       ├── wikidata_ingester.py   # Wikidata API
│       ├── pdf_processor.py       # PDF handling
│       ├── retriever.py           # Hybrid search
│       ├── reranker.py            # Cross-encoder
│       ├── generator.py           # Ollama LLM
│       ├── evaluator.py           # Quality metrics
│       └── utils.py               # Helper functions
├── ui/
│   └── streamlit_app.py           # Web interface
├── .cursor/
│   └── prompts.json               # System prompts
├── requirements.txt               # Dependencies
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
    "enable_evaluation": false
  }'
```

### Upload PDF
```bash
curl -X POST "http://localhost:8000/upload-pdf" \
  -F "file=@/path/to/your/document.pdf"
```

## ⚙️ Advanced Features

### 1. Citation Diversity
- Automatically limits to **2 citations per source**
- Ensures multi-perspective answers
- Prevents single-source dominance

### 2. Quality Evaluation
Enable to get:
- **Faithfulness Score**: 0-1 scale of answer grounding
- **Citation Accuracy**: Correctness of attributions  
- **Precision@k**: Relevance of retrieved chunks
- **Transparency Trace**: Sentence-level source mapping

### 3. Selective Re-ask
- Automatically refines low-confidence answers
- Stricter citation requirements on second pass
- Improves answer quality

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
- Use a smaller Ollama model: `ollama pull llama3.2:1b`

## 📝 Requirements

- **Python**: 3.9+
- **Ollama**: Latest version
- **RAM**: 8GB minimum (16GB recommended for wizardlm2)
- **Storage**: 5GB for model + embeddings

## 🔐 Privacy

✅ **100% Local Processing**
- All LLM inference happens on your machine
- No data sent to external LLM APIs
- Source content fetched from public APIs only

## 📄 License

MIT License - Feel free to use for your own projects!

## 🤝 Contributing

Issues and pull requests welcome! This project demonstrates:
- Multi-source RAG architecture
- Hybrid retrieval systems
- Citation diversity mechanisms
- Quality evaluation frameworks
- Local LLM integration

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
