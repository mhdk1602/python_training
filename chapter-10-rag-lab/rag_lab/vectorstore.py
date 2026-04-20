from __future__ import annotations

from abc import ABC, abstractmethod
import hashlib
import json
import math
from typing import Iterable

import requests

from .chunking import tags_from_metadata
from .config import Settings
from .schemas import ChunkRecord, SearchResult


def _tokenize(text: str) -> list[str]:
    return ["".join(char for char in token.lower() if char.isalnum()) for token in text.split() if token.strip()]


class Embedder(ABC):
    model_name: str

    @abstractmethod
    def embed(self, texts: Iterable[str]) -> list[list[float]]:
        raise NotImplementedError


class HashingEmbedder(Embedder):
    model_name = "hashing-embedder-v1"

    def __init__(self, dimensions: int = 192) -> None:
        self.dimensions = dimensions

    def embed(self, texts: Iterable[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            vector = [0.0] * self.dimensions
            for token in _tokenize(text):
                slot = _stable_hash(token) % self.dimensions
                sign = -1.0 if _stable_hash(f"sign:{token}") % 2 else 1.0
                vector[slot] += sign
            norm = math.sqrt(sum(value * value for value in vector)) or 1.0
            vectors.append([value / norm for value in vector])
        return vectors


class OllamaEmbedder(Embedder):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model_name = settings.ollama_embedding_model

    def embed(self, texts: Iterable[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            response = requests.post(
                f"{self.settings.ollama_base_url}/api/embed",
                json={"model": self.settings.ollama_embedding_model, "input": text},
                timeout=60,
            )
            response.raise_for_status()
            payload = response.json()
            if payload.get("embeddings"):
                vectors.append(payload["embeddings"][0])
            elif payload.get("embedding"):
                vectors.append(payload["embedding"])
            else:
                raise ValueError("Ollama embed response did not include embeddings.")
        return vectors


class VectorStore(ABC):
    backend_name: str

    def __init__(self, embedder: Embedder, collection_name: str) -> None:
        self.embedder = embedder
        self.collection_name = collection_name

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def upsert(self, chunks: list[ChunkRecord]) -> None:
        raise NotImplementedError

    @abstractmethod
    def query(self, query: str, filters: dict[str, str] | None = None, top_k: int = 5) -> list[SearchResult]:
        raise NotImplementedError


class InMemoryVectorStore(VectorStore):
    backend_name = "memory"

    def __init__(self, embedder: Embedder, collection_name: str) -> None:
        super().__init__(embedder, collection_name)
        self._rows: list[tuple[ChunkRecord, list[float]]] = []

    def reset(self) -> None:
        self._rows = []

    def upsert(self, chunks: list[ChunkRecord]) -> None:
        if not chunks:
            return
        existing = {chunk.chunk_id: (chunk, vector) for chunk, vector in self._rows}
        embeddings = self.embedder.embed(chunk.text for chunk in chunks)
        for chunk, vector in zip(chunks, embeddings):
            existing[chunk.chunk_id] = (chunk, vector)
        self._rows = list(existing.values())

    def query(self, query: str, filters: dict[str, str] | None = None, top_k: int = 5) -> list[SearchResult]:
        query_vector = self.embedder.embed([query])[0]
        scored: list[tuple[ChunkRecord, float]] = []
        for chunk, vector in self._rows:
            if not _matches_filters(chunk.metadata, filters or {}):
                continue
            score = _cosine_similarity(query_vector, vector)
            scored.append((chunk, max(score, 0.0)))

        scored.sort(key=lambda item: item[1], reverse=True)
        return [_search_result_from_chunk(chunk, score) for chunk, score in scored[:top_k]]


class ChromaVectorStore(VectorStore):
    backend_name = "chroma"

    def __init__(self, embedder: Embedder, collection_name: str, settings: Settings) -> None:
        super().__init__(embedder, collection_name)
        import chromadb

        self.client = chromadb.PersistentClient(path=str(settings.chroma_dir))
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def reset(self) -> None:
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def upsert(self, chunks: list[ChunkRecord]) -> None:
        if not chunks:
            return
        embeddings = self.embedder.embed(chunk.text for chunk in chunks)
        self.collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            embeddings=embeddings,
            metadatas=[chunk.metadata for chunk in chunks],
        )

    def query(self, query: str, filters: dict[str, str] | None = None, top_k: int = 5) -> list[SearchResult]:
        embedded_query = self.embedder.embed([query])[0]
        response = self.collection.query(
            query_embeddings=[embedded_query],
            n_results=top_k,
            where=filters or None,
        )
        results: list[SearchResult] = []
        ids = response.get("ids", [[]])[0]
        documents = response.get("documents", [[]])[0]
        metadatas = response.get("metadatas", [[]])[0]
        distances = response.get("distances", [[]])[0] if response.get("distances") else [0.0] * len(ids)

        for chunk_id, document, metadata, distance in zip(ids, documents, metadatas, distances):
            tags = tags_from_metadata(metadata.get("tags_json", "[]"))
            extra_metadata = json.loads(metadata.get("metadata_json", "{}"))
            results.append(
                SearchResult(
                    chunk_id=chunk_id,
                    score=1.0 / (1.0 + float(distance)),
                    source_id=metadata.get("source_id", ""),
                    title=metadata.get("title", "Untitled"),
                    snippet=document[:260],
                    tags=tags,
                    metadata=extra_metadata | {"source_url": metadata.get("source_url", "")},
                )
            )
        return results


def select_embedder(settings: Settings) -> Embedder:
    try:
        embedder = OllamaEmbedder(settings)
        embedder.embed(["health probe"])
        return embedder
    except Exception:
        return HashingEmbedder()


def select_vector_store(settings: Settings, embedder: Embedder) -> VectorStore:
    if settings.vector_backend == "memory":
        return InMemoryVectorStore(embedder, settings.collection_name)
    try:
        return ChromaVectorStore(embedder, settings.collection_name, settings)
    except Exception:
        return InMemoryVectorStore(embedder, settings.collection_name)


def _matches_filters(metadata: dict[str, str], filters: dict[str, str]) -> bool:
    for key, expected in filters.items():
        current = metadata.get(key)
        if current is None:
            return False
        if str(current).lower() != str(expected).lower():
            return False
    return True


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left)) or 1.0
    right_norm = math.sqrt(sum(value * value for value in right)) or 1.0
    return numerator / (left_norm * right_norm)


def _search_result_from_chunk(chunk: ChunkRecord, score: float) -> SearchResult:
    metadata_json = chunk.metadata.get("metadata_json", "{}")
    source_url = chunk.metadata.get("source_url", "")
    extra_metadata = json.loads(metadata_json)
    extra_metadata["source_url"] = source_url
    return SearchResult(
        chunk_id=chunk.chunk_id,
        score=score,
        source_id=chunk.metadata.get("source_id", chunk.parent_id),
        title=chunk.metadata.get("title", "Untitled"),
        snippet=chunk.text[:260],
        tags=list(chunk.tags),
        metadata=extra_metadata,
    )


def _stable_hash(value: str) -> int:
    return int(hashlib.sha256(value.encode("utf-8")).hexdigest(), 16)
