# RagNeuron

RAG (Retrieval Augmented Generation) system for technical support reports. Supports Japanese language.

## Features

- Semantic search over technical support records
- LLM-powered answers from local LM Studio
- Auto-selects embedding model based on hardware:
  - **GPU**: BAAI/bge-m3 (1024 dims, best quality)
  - **CPU**: intfloat/multilingual-e5-small (384 dims, fast, Japanese optimized)
- Docker support for Qdrant vector database

## Requirements

- Python 3.10+
- Docker (for Qdrant)
- LM Studio (for LLM)
- NVIDIA GPU (optional, for faster embeddings)

## Quick Start

### 1. Clone and Install

```bash
cd RagNeuron
uv sync
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your settings
```

Default `.env`:
```bash
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL=qwen3.5-2b
EMBEDDING_DEVICE=cuda   # cuda for GPU, cpu for CPU-only
QDRANT_URL=http://localhost:6333
```

### 3. Launch

**Linux/macOS:**
```bash
./run.sh        # Interactive mode (auto-detects GPU)
./run.sh 1      # Local ingestion + Docker Qdrant + Local API
./run.sh 2      # Full Docker stack
```

**Windows:**
```batch
run.bat         # Interactive mode
run.bat 1       # Local ingestion + Docker Qdrant + Local API
run.bat 2       # Full Docker stack
```

### 4. Use

```bash
curl -X POST http://localhost:8769/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "カット機 動かない", "top_k": 5}'
```

## Deployment Modes

| Mode | Ingestion | API | Best For |
|------|----------|-----|---------|
| 1 - Hybrid | Local GPU/CPU | Local | Development, GPU users |
| 2 - Docker | Docker (CPU) | Docker | CPU-only, deployment |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/rag/query` | POST | Query RAG system with LLM |
| `/rag/search` | POST | Pure vector search (no LLM) |
| `/rag/ingest` | POST | Re-ingest all data |
| `/health` | GET | Health check |

## Embedding Models

Automatically selected based on `EMBEDDING_DEVICE`:

| Device | Model | Dims | Speed |
|--------|-------|------|-------|
| cuda | BAAI/bge-m3 | 1024 | Fast |
| cpu | intfloat/multilingual-e5-small | 384 | Faster |

## Project Structure

```
RagNeuron/
├── src/
│   ├── config.py      # Configuration
│   ├── ingest.py      # Data ingestion
│   ├── rag.py         # RAG logic
│   └── main.py        # FastAPI app
├── scripts/
│   └── prepare_data.py
├── data/              # Place your data here
├── vectors/           # Vector DB storage
├── docker-compose.yml
├── Dockerfile
├── run.sh            # Linux/macOS launcher
├── run.bat           # Windows launcher
└── pyproject.toml
```

## Tech Stack

- **Embeddings**: BAAI/bge-m3 (GPU) / multilingual-e5-small (CPU)
- **Vector DB**: Qdrant
- **LLM**: Local via LM Studio
- **Framework**: FastAPI + LangChain
- **Package Manager**: uv
