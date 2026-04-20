from __future__ import annotations

from .schemas import SearchResult
from .vectorstore import VectorStore


class Retriever:
    def __init__(self, vector_store: VectorStore) -> None:
        self.vector_store = vector_store

    def search(self, query: str, filters: dict[str, str] | None = None, top_k: int = 5) -> list[SearchResult]:
        return self.vector_store.query(query=query, filters=filters, top_k=top_k)
