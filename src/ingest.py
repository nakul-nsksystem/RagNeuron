import json
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from tqdm import tqdm

from src.config import settings


def load_data():
    data_file = "data/tech_reports_rag.json"
    with open(data_file, "r", encoding="utf-8") as f:
        return json.load(f)


def chunk_data(data):
    print("Chunking data...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = []
    for record in tqdm(data, desc="Processing records"):
        text = record["text"]
        metadata = record["metadata"]

        if len(text.strip()) == 0:
            continue

        record_chunks = text_splitter.split_text(text)

        for i, chunk in enumerate(record_chunks):
            chunks.append({"text": chunk, "chunk_index": i, "metadata": metadata})

    print(f"Created {len(chunks)} chunks from {len(data)} records")
    return chunks


def create_embeddings():
    if settings.embedding_device == "cuda":
        model = settings.embedding_model
        vector_size = 1024
    else:
        model = settings.cpu_embedding_model
        vector_size = 384  # multilingual-e5-small is 384 dimensions

    print(f"Loading embedding model: {model} (device: {settings.embedding_device})")
    embeddings = HuggingFaceEmbeddings(
        model_name=model,
        model_kwargs={"device": settings.embedding_device},
        encode_kwargs={"normalize_embeddings": True},
    )
    return embeddings, vector_size


def store_in_qdrant(chunks, embeddings, vector_size):
    print("Connecting to Qdrant...")

    if settings.qdrant_url:
        qdrant_client = QdrantClient(url=settings.qdrant_url)
    else:
        qdrant_client = QdrantClient(path=settings.qdrant_path or "./vectors/qdrant")

    collection_name = settings.collection_name

    try:
        qdrant_client.delete_collection(collection_name=collection_name)
        print(f"Deleted existing collection: {collection_name}")
    except:
        pass

    print(f"Creating collection with vector size {vector_size}...")
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

    print("Generating embeddings and storing...")

    batch_size = 100
    for i in tqdm(range(0, len(chunks), batch_size), desc="Embedding batches"):
        batch = chunks[i : i + batch_size]
        texts = [chunk["text"] for chunk in batch]

        vectors = embeddings.embed_documents(texts)

        points = []
        for j, (chunk, vector) in enumerate(zip(batch, vectors)):
            point_id = i + j
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector.tolist() if hasattr(vector, "tolist") else vector,
                    payload={
                        "text": chunk["text"],
                        "chunk_index": chunk["chunk_index"],
                        "report_id": chunk["metadata"].get("report_id"),
                        "report_cd": chunk["metadata"].get("report_cd"),
                        "work_symptom": chunk["metadata"].get("work_symptom"),
                        "work_detail": chunk["metadata"].get("work_detail"),
                        "device": chunk["metadata"].get("device"),
                        "error_code": chunk["metadata"].get("error_code"),
                        "total_fee": chunk["metadata"].get("total_fee"),
                    },
                )
            )

        qdrant_client.upsert(collection_name=collection_name, points=points)

    print(f"Successfully stored {len(chunks)} chunks in Qdrant")


def ingest():
    print("=" * 50)
    print("Starting RAG ingestion process")
    print("=" * 50)

    data = load_data()
    chunks = chunk_data(data)
    embeddings, vector_size = create_embeddings()
    store_in_qdrant(chunks, embeddings, vector_size)

    print("=" * 50)
    print("Ingestion complete!")
    print("=" * 50)


if __name__ == "__main__":
    ingest()
