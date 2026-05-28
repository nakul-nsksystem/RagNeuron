# RagNeuron

A RAG (Retrieval Augmented Generation) system for searching technical support reports. Ask questions in plain language and get answers from past repair cases.

**No ML/AI background needed!** This guide walks you through every step.

---

## What Does This Do?

You have a database of past repair records (in any language, like Japanese). Instead of manually searching through them, you can ask questions like:

- "My cutting machine shows servo error, what should I do?"
- "The laser head is not responding"
- "X軸が動かない" (X-axis not moving)

RagNeuron finds the most similar past cases and uses AI to give you a helpful answer.

---

## Prerequisites

Before starting, you need 3 things:

### 1. Python (already on most computers)

Check if you have it:
```bash
python --version
```

If not, download from [python.org](https://www.python.org/downloads/)

### 2. Docker (for the vector database)

**Windows:**
1. Download Docker Desktop from [docker.com](https://www.docker.com/get-started/)
2. Install it
3. Start Docker Desktop

**macOS:**
```bash
brew install --cask docker
```

**Linux (Ubuntu):**
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
```

Verify Docker is running:
```bash
docker --version
```

### 3. LM Studio (for AI answers)

Download from [lmstudio.ai](https://lmstudio.ai/)

1. Download and install LM Studio
2. Open LM Studio
3. Download a model (recommended: Qwen3.5-2B or similar)
4. Click "Start Server" (usually at port 1234)

---

## Installation

### Step 1: Get the Code

**Option A: Download ZIP**
1. Go to the GitHub repo
2. Click the green "Code" button
3. Click "Download ZIP"
4. Extract to a folder

**Option B: Using Git**
```bash
git clone https://github.com/nakul-nsksystem/RagNeuron.git
cd RagNeuron
```

### Step 2: Install uv

uv is a fast Python package manager.

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or use pip:
```bash
pip install uv
```

### Step 3: Install Python Dependencies

```bash
cd RagNeuron
uv sync
```

This automatically creates a virtual environment and installs all packages.

---

## Quick Start (One Command)

After installing everything, run:

```bash
# Linux/macOS
./run.sh

# Windows
run.bat
```

The script will:
1. Detect if you have a GPU
2. Ask which mode you want
3. Start everything for you

---

## Manual Setup (If You Prefer)

### Start Qdrant (Vector Database)

```bash
docker compose up -d qdrant
```

Wait 3 seconds for it to start.

### Add Your Data

Place your JSON data file as `data/tech_reports_rag.json`

Format should be:
```json
[
  {
    "text": "Problem description",
    "metadata": {
      "report_id": 1,
      "work_symptom": "Problem",
      "work_detail": "Solution",
      "device": "Device name",
      "error_code": "ERROR123"
    }
  }
]
```

### Ingest Your Data

```bash
uv run python -m src.ingest
```

This takes 1-10 minutes depending on data size and your hardware.

### Start the API

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8769
```

### Open in Browser

- API: http://localhost:8769
- Docs (try queries here): http://localhost:8769/docs
- Qdrant Dashboard: http://localhost:6333

---

## Usage Examples

### Test with Curl

```bash
curl -X POST http://localhost:8769/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "カット機 動かない", "top_k": 5}'
```

### Using the Docs Interface

1. Open http://localhost:8769/docs in your browser
2. Click on `/POST /rag/query`
3. Click "Try it out"
4. Enter your question and top_k value
5. Click "Execute"

### Example Questions

In English:
- "Cutting machine not responding"
- "Laser head error"
- "Servo motor failure"

In Japanese:
- "カット機が動かない"
- "激光头不工作"
- "X軸エラー"

---

## Deployment Modes

### Mode 1: Hybrid (Recommended for development)

- **Ingestion**: Runs on your computer (GPU if available)
- **Database**: Qdrant in Docker
- **API**: Runs locally

Best if you have an NVIDIA GPU.

```bash
./run.sh 1   # Linux/macOS
run.bat 1     # Windows
```

### Mode 2: Full Docker (Recommended for deployment)

Everything runs in Docker containers.

```bash
./run.sh 2   # Linux/macOS
run.bat 2     # Windows
```

---

## Configuration

Copy the example file and edit:

```bash
cp .env.example .env
```

Settings:

| Setting | Description | Default |
|---------|-------------|---------|
| `LLM_BASE_URL` | LM Studio address | http://localhost:1234/v1 |
| `LLM_MODEL` | Model name in LM Studio | qwen3.5-2b |
| `EMBEDDING_DEVICE` | "cuda" for GPU, "cpu" for CPU | cuda |
| `QDRANT_URL` | Qdrant address | http://localhost:6333 |
| `API_PORT` | API port | 8769 |

---

## Embedding Models

The system automatically selects the best model for your hardware:

| Hardware | Model | Dimensions | Speed |
|----------|-------|------------|-------|
| NVIDIA GPU | BAAI/bge-m3 | 1024 | Fast |
| CPU only | intfloat/multilingual-e5-small | 384 | Faster |

If you have a GPU, it uses BGE-M3 for better quality. If not, it switches to a smaller, faster model that still handles Japanese well.

---

## Troubleshooting

### "docker: command not found"

Docker is not installed. Follow the [Prerequisites](#prerequisites) section above.

### "LM Studio connection error"

1. Make sure LM Studio is running
2. Click "Start Server" in LM Studio
3. Check that the URL in `.env` matches (default: http://localhost:1234)

### "No relevant information found"

- Try different keywords
- Make sure you've run ingestion (`uv run python -m src.ingest`)
- Check that your data is in `data/tech_reports_rag.json`

### Qdrant errors

Reset the vector database:
```bash
rm -rf vectors/qdrant-data
uv run python -m src.ingest
```

### Out of memory

If running on CPU and memory is low:
1. Reduce batch size in `src/ingest.py`
2. Or add more RAM

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/rag/query` | POST | Ask a question (uses AI) |
| `/rag/search` | POST | Search only (no AI) |
| `/rag/ingest` | POST | Re-ingest your data |
| `/health` | GET | Check if running |
| `/` | GET | API info |

---

## Project Structure

```
RagNeuron/
├── src/
│   ├── config.py        # Settings
│   ├── ingest.py        # Import data
│   ├── rag.py          # Search logic
│   └── main.py         # API server
├── scripts/
│   └── prepare_data.py  # Data preparation
├── data/               # Your data goes here
├── vectors/            # Vector database
├── docker-compose.yml  # Docker services
├── Dockerfile         # Docker image
├── run.sh             # Linux/macOS launcher
├── run.bat            # Windows launcher
└── pyproject.toml     # Python packages
```

---

## Tech Stack

- **Embeddings**: BAAI/bge-m3 or multilingual-e5-small
- **Vector Database**: Qdrant
- **LLM**: Local via LM Studio (or OpenAI)
- **API**: FastAPI
- **Package Manager**: uv

---

## License

MIT - Do whatever you want with it.

---

## Support

Open an issue on GitHub if you need help.
