# CiteRight-Multiverse 🌌

A production-ready multi-source RAG (Retrieval-Augmented Generation) assistant that pulls content from Wikipedia, Wikidata, StackExchange, and arXiv for comprehensive factual synthesis.

## Features

- **Multi-Source Ingestion**: Automatically pulls content from Wikipedia, StackExchange, arXiv, and Wikidata
- **Hybrid Retrieval**: Combines FAISS (dense) + BM25 (sparse) search
- **Cross-Encoder Reranking**: Improves relevance with sentence-transformers
- **Selective Re-ask**: Automatically refines answers when confidence is low
- **Local LLM**: Uses Ollama with wizardlm2:latest model
- **Structured Citations**: Proper attribution with source, origin, license, and URL metadata
- **Caching**: SQLite-based query caching for performance
- **FastAPI Backend**: RESTful API with comprehensive logging
- **Streamlit UI**: Enhanced web interface with multi-source controls
- **Docker Support**: Complete containerization with docker-compose

## Data Sources

| Source | Content Type | License | API |
|--------|-------------|---------|-----|
| **Wikipedia** | Encyclopedia articles | CC BY-SA 3.0 | wikipedia library |
| **StackExchange** | Q&A content | CC BY-SA 4.0 | StackAPI |
| **arXiv** | Research papers | CC BY 4.0 | arxiv library |
| **Wikidata** | Structured data | CC0 1.0 | Wikidata API |

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

### Multi-Source Ingestion

1. **Query-Based Ingestion**:
   ```bash
   curl -X POST "http://localhost:8000/ingest-multiverse" \
        -H "Content-Type: application/json" \
        -d '{
          "query": "quantum mechanics",
          "sources": ["wikipedia", "stackexchange", "arxiv", "wikidata"],
          "max_per_source": 5
        }'
   ```

2. **Specific Content Ingestion**:
   ```bash
   curl -X POST "http://localhost:8000/ingest-multiverse" \
        -H "Content-Type: application/json" \
        -d '{
          "specific_content": {
            "wikipedia_titles": ["Quantum mechanics", "Albert Einstein"],
            "arxiv_ids": ["2304.01234", "2305.05678"],
            "wikidata_ids": ["Q937", "Q42"]
          }
        }'
   ```

### Querying

1. **Ask Questions**:
   ```bash
   curl -X POST "http://localhost:8000/query" \
        -H "Content-Type: application/json" \
        -d '{"query": "What is quantum mechanics and how does it differ from classical mechanics?"}'
   ```

2. **Use the Streamlit UI**:
   - Navigate to http://localhost:8501
   - Use the sidebar to ingest from multiple sources
   - Ask questions in the main interface

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
                       │  Multi-Source    │
                       │  Ingestion       │
                       │  (Wikipedia,     │
                       │   StackExchange,  │
                       │   arXiv,         │
                       │   Wikidata)      │
                       └──────────────────┘
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

- `POST /ingest` - Ingest documents from local paths
- `POST /ingest-multiverse` - Ingest from multiple online sources
- `POST /query` - Query the RAG system
- `GET /docs` - API documentation (Swagger UI)

## Testing

Run the comprehensive test suite:

```bash
python test_multiverse.py
```

This will test:
- API connectivity
- Individual source ingestion (Wikipedia, StackExchange, arXiv, Wikidata)
- Multi-source ingestion
- Query processing with proper citations

## Performance Features

- **Caching**: SQLite-based query caching reduces redundant LLM calls
- **Metrics**: JSON logging with latency tracking for monitoring
- **Selective Re-ask**: Only refines answers when confidence is low
- **Hybrid Search**: Combines semantic and keyword search for better recall
- **Rate Limiting**: Built-in throttling for external APIs
- **Error Handling**: Graceful degradation when sources are unavailable

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
│       ├── ingest.py              # Local document ingestion
│       ├── multiverse_ingester.py # Multi-source ingestion
│       ├── wikipedia_ingester.py  # Wikipedia API client
│       ├── stackexchange_ingester.py # StackExchange API client
│       ├── arxiv_ingester.py      # arXiv API client
│       ├── wikidata_ingester.py   # Wikidata API client
│       ├── retriever.py           # Hybrid retrieval
│       ├── reranker.py            # Cross-encoder reranking
│       ├── generator.py           # Ollama LLM wrapper
│       ├── caching.py             # SQLite cache
│       ├── selective_reask.py     # Quality control
│       └── utils.py               # Helper functions
├── ui/
│   └── streamlit_app.py           # Enhanced web UI
├── .cursor/
│   └── prompts.json               # CiteRight-Multiverse prompt
├── data/
│   └── sample_docs/               # Document storage
├── requirements.txt
├── docker-compose.yml
├── test_multiverse.py             # Comprehensive test suite
└── README.md
```

## Troubleshooting

1. **Ollama Connection Issues**: Ensure Ollama is running on port 11434
2. **Model Not Found**: Run `ollama pull wizardlm2:latest`
3. **API Rate Limits**: Some sources may have rate limits; the system includes throttling
4. **Memory Issues**: Reduce `RETRIEVE_K` and `CONTEXT_TOP_K` in config
5. **Network Issues**: Check internet connection for external API access
6. **Import Errors**: Run `pip install -r requirements.txt` to install all dependencies

## License

MIT License - feel free to use this project for your own multi-source RAG applications!

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests to enhance the multi-source capabilities.

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

