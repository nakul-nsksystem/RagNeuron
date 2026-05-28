#!/bin/bash
set -e

# Detect GPU
if command -v nvidia-smi &> /dev/null && nvidia-smi -L &> /dev/null; then
    GPU_AVAILABLE=true
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
else
    GPU_AVAILABLE=false
fi

# Get mode from args or prompt
MODE="${1:-}"

if [ -z "$MODE" ]; then
    if [ "$GPU_AVAILABLE" = true ]; then
        echo "GPU detected: $GPU_NAME"
        echo "Choose deployment mode:"
        echo "  1) Local ingestion (GPU) + Docker Qdrant + Local API"
        echo "  2) Full Docker stack (no GPU)"
        read -p "Select [1]: " MODE
        MODE="${MODE:-1}"
    else
        echo "No GPU detected. Using Docker mode."
        MODE=2
    fi
fi

stopContainers() {
    echo "Stopping containers..."
    docker compose down 2>/dev/null || true
}

startQdrant() {
    echo "Starting Qdrant..."
    docker compose up -d qdrant
    sleep 3
}

case $MODE in
    1)
        echo "=== Mode: Local ingestion + Docker Qdrant + Local API ==="
        stopContainers
        startQdrant

        echo "Ingesting data (local GPU)..."
        uv run python -m src.ingest

        echo "Starting API..."
        uv run uvicorn src.main:app --host 0.0.0.0 --port 8769
        ;;

    2)
        echo "=== Mode: Full Docker Stack ==="
        stopContainers
        docker compose up -d

        echo ""
        echo "To ingest data:"
        echo "  docker exec rag-neuron-api uv run python -m src.ingest"
        ;;

    ingest)
        echo "=== Running ingestion only ==="
        startQdrant
        uv run python -m src.ingest
        ;;

    api)
        echo "=== Starting API only ==="
        uv run uvicorn src.main:app --host 0.0.0.0 --port 8769
        ;;

    *)
        echo "Usage: $0 [1|2|ingest|api]"
        echo "  1    - Local ingestion + Docker Qdrant + Local API (with GPU)"
        echo "  2    - Full Docker stack (no GPU)"
        echo "  ingest - Run ingestion only"
        echo "  api   - Run API only"
        ;;
esac
