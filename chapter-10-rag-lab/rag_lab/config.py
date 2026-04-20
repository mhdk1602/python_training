from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(slots=True)
class Settings:
    app_name: str = "Chapter 10 Retrieval Lab"
    base_dir: Path = Path(__file__).resolve().parents[1]
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_embedding_model: str = os.getenv("RAG_LAB_EMBED_MODEL", "nomic-embed-text")
    ollama_chat_model: str = os.getenv("RAG_LAB_CHAT_MODEL", "llama3.1:8b-instruct")
    nps_api_key: str | None = os.getenv("NPS_API_KEY")
    vector_backend: str = os.getenv("RAG_LAB_VECTOR_BACKEND", "chroma")
    chroma_dir_name: str = os.getenv("RAG_LAB_CHROMA_DIR", ".chroma")
    model_assisted_tagging: bool = os.getenv("RAG_LAB_MODEL_TAGS", "false").lower() == "true"
    answer_threshold: float = float(os.getenv("RAG_LAB_ANSWER_THRESHOLD", "0.18"))
    collection_name: str = os.getenv("RAG_LAB_COLLECTION", "chapter10")

    @property
    def data_dir(self) -> Path:
        return self.base_dir / "data"

    @property
    def chroma_dir(self) -> Path:
        return self.base_dir / self.chroma_dir_name


settings = Settings()
