from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # LLM Settings
    llm_base_url: str = "http://host.docker.internal:1234/v1"
    llm_model: str = "qwen3.5-2b"
    llm_temperature: float = 0.4

    # Embeddings
    embedding_model: str = "BAAI/bge-m3"  # GPU model
    embedding_device: str = "cuda"
    cpu_embedding_model: str = "intfloat/multilingual-e5-small"  # Smaller, fast, Japanese support
    vector_size: int = 1024  # Will be auto-detected during ingest

    # Vector DB
    qdrant_url: Optional[str] = "http://qdrant:6333"
    qdrant_path: Optional[str] = None
    collection_name: str = "tech_reports"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8769

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
