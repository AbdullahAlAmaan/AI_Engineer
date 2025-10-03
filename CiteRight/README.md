# RAG Assistant (Hybrid + Reranker + Ollama)

A production-ready RAG (Retrieval-Augmented Generation) assistant with hybrid retrieval, reranking, and selective re-ask capabilities using local Ollama models.

## Features

- **Hybrid Retrieval**: Combines FAISS (dense) + BM25 (sparse) search
- **Cross-Encoder Reranking**: Improves relevance with sentence-transformers
- **Selective Re-ask**: Automatically refines answers when confidence is low
- **Local LLM**: Uses Ollama with wizardlm2:latest model
- **Caching**: SQLite-based query caching for performance
- **FastAPI Backend**: RESTful API with comprehensive logging
- **Streamlit UI**: Simple web interface for testing
- **Docker Support**: Complete containerization with docker-compose

## Quickstart

### Prerequisites

1. **Install Ollama** and pull the wizardlm2 model:
   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull the model
   ollama pull wizardlm2:latest
   ```

2. **Start Ollama service**:
   ```bash
   ollama serve
   ```

### Option 1: Docker Compose (Recommended)

1. **Start everything**:
   ```bash
   docker compose up --build
   ```

2. **Access the application**:
   - API: http://localhost:8000
   - UI: http://localhost:8501

### Option 2: Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the API**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **Start the UI** (in another terminal):
   ```bash
   streamlit run ui/streamlit_app.py
   ```

## Usage

1. **Ingest Documents**:
   - Place your text files (.txt, .md) in `data/sample_docs/`
   - Use the UI sidebar to ingest documents
   - Or call the API directly: `POST /ingest` with `{"paths": ["./data/sample_docs"]}`

2. **Ask Questions**:
   - Use the Streamlit UI to ask questions
   - Or call the API directly: `POST /query` with `{"query": "your question"}`

## Configuration

Copy `env.example` to `.env` and modify settings:

```env
# Model Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2
OLLAMA_MODEL=wizardlm2:latest
OLLAMA_HOST=http://localhost:11434

# Retrieval Settings
RETRIEVE_K=20          # Number of initial candidates
RERANK_TOP_K=5         # Top documents after reranking
CONTEXT_TOP_K=4        # Documents used in context

# Quality Thresholds
MIN_RERANK_SCORE=0.4   # Minimum rerank score for confidence
MIN_CITATION_COVERAGE=0.6  # Minimum citation coverage
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │───▶│   FastAPI API    │───▶│   Ollama LLM    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Hybrid Retriever│
                       │  (FAISS + BM25)  │
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Cross-Encoder    │
                       │ Reranker         │
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Selective Re-ask │
                       │ (Quality Check)  │
                       └──────────────────┘
```

## API Endpoints

- `POST /ingest` - Ingest documents from specified paths
- `POST /query` - Query the RAG system
- `GET /docs` - API documentation (Swagger UI)

## Performance Features

- **Caching**: SQLite-based query caching reduces redundant LLM calls
- **Metrics**: JSON logging with latency tracking for monitoring
- **Selective Re-ask**: Only refines answers when confidence is low
- **Hybrid Search**: Combines semantic and keyword search for better recall

## Development

### Project Structure
```
CiteRight/
├── app/
│   ├── main.py                    # FastAPI service
│   ├── config.py                  # Settings
│   ├── deps.py                    # Shared singletons
│   ├── models.py                  # Pydantic models
│   ├── logging_utils.py           # JSON logging
│   └── rag/
│       ├── ingest.py              # Document ingestion
│       ├── retriever.py           # Hybrid retrieval
│       ├── reranker.py            # Cross-encoder reranking
│       ├── generator.py           # Ollama LLM wrapper
│       ├── caching.py             # SQLite cache
│       ├── selective_reask.py     # Quality control
│       └── utils.py               # Helper functions
├── ui/
│   └── streamlit_app.py           # Web UI
├── data/
│   └── sample_docs/               # Document storage
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## Troubleshooting

1. **Ollama Connection Issues**: Ensure Ollama is running on port 11434
2. **Model Not Found**: Run `ollama pull wizardlm2:latest`
3. **Memory Issues**: Reduce `RETRIEVE_K` and `CONTEXT_TOP_K` in config
4. **Slow Performance**: Enable caching and reduce chunk sizes

## License

MIT License - feel free to use this project for your own RAG applications!

