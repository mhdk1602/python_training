from __future__ import annotations

from pathlib import Path

from .adapters import MarkdownNoteAdapter, NpsSourceAdapter, SampleJsonAdapter
from .agent import BoundedAgent
from .answering import AnswerService
from .chunking import chunk_content_item
from .config import Settings, settings
from .normalizer import MarkdownContentNormalizer, NpsContentNormalizer
from .retrieval import Retriever
from .schemas import AgentResponse, AnswerResponse, ContentItem, SearchResult
from .tagging import CombinedTagger
from .vectorstore import select_embedder, select_vector_store


class RetrievalLabService:
    def __init__(self, app_settings: Settings | None = None) -> None:
        self.settings = app_settings or settings
        self.embedder = select_embedder(self.settings)
        self.vector_store = select_vector_store(self.settings, self.embedder)
        self.retriever = Retriever(self.vector_store)
        self.answer_service = AnswerService(self.retriever, self.settings)
        self.contents: dict[str, ContentItem] = {}
        self.agent = BoundedAgent(self.answer_service, self.retriever, self)
        self.tagger = CombinedTagger(self.settings)
        self.seed_sample_corpus()

    def seed_sample_corpus(self) -> dict[str, object]:
        nps_items = self._normalize_nps_records(
            SampleJsonAdapter(self.settings.data_dir / "nps_things_to_do.json").fetch()
        )
        markdown_items = self._normalize_markdown_records(
            MarkdownNoteAdapter(self.settings.data_dir / "field_notes.md").fetch()
        )
        all_items = nps_items + markdown_items
        self._index_items(all_items)
        return self.status() | {"indexed_sources": len(all_items)}

    def refresh_live_nps(self, park_code: str, resource: str, limit: int) -> dict[str, object]:
        if not self.settings.nps_api_key:
            raise ValueError("NPS_API_KEY is not set.")
        records = NpsSourceAdapter(
            api_key=self.settings.nps_api_key,
            park_code=park_code,
            resource=resource,
            limit=limit,
        ).fetch()
        items = self._normalize_nps_records(records)
        self._index_items(items, replace=False)
        return self.status() | {"indexed_sources": len(items), "park_code": park_code}

    def search(self, query: str, filters: dict[str, str] | None = None, top_k: int = 5) -> list[SearchResult]:
        return self.retriever.search(query=query, filters=filters, top_k=top_k)

    def answer(self, query: str, filters: dict[str, str] | None = None, top_k: int = 4) -> AnswerResponse:
        return self.answer_service.answer(query=query, filters=filters, top_k=top_k)

    def run_agent(self, query: str, filters: dict[str, str] | None = None) -> AgentResponse:
        return self.agent.run(query=query, filters=filters)

    def inspect_source(self, source_id: str) -> dict[str, object]:
        item = self.contents[source_id]
        return {
            "source_id": item.source_id,
            "title": item.title,
            "summary": item.summary,
            "body": item.body,
            "metadata": item.metadata,
            "tags": [tag.model_dump() for tag in item.tags],
            "source_url": item.source_url,
        }

    def explain_tags(self, source_id: str) -> dict[str, object]:
        item = self.contents[source_id]
        return {
            "source_id": source_id,
            "title": item.title,
            "tags": [tag.model_dump() for tag in item.tags],
        }

    def list_sources(self) -> list[dict[str, object]]:
        return [
            {
                "source_id": item.source_id,
                "title": item.title,
                "summary": item.summary,
                "body": item.body,
                "source_type": item.source_type,
                "tags": [tag.model_dump() for tag in item.tags],
                "metadata": item.metadata,
                "source_url": item.source_url,
            }
            for item in self.contents.values()
        ]

    def status(self) -> dict[str, object]:
        return {
            "backend": self.vector_store.backend_name,
            "embedding_model": self.embedder.model_name,
            "source_count": len(self.contents),
        }

    def _normalize_nps_records(self, records: list[dict[str, object]]) -> list[ContentItem]:
        normalizer = NpsContentNormalizer()
        return [self._tag_item(normalizer.to_content_item(record)) for record in records]

    def _normalize_markdown_records(self, records: list[dict[str, object]]) -> list[ContentItem]:
        normalizer = MarkdownContentNormalizer()
        return [self._tag_item(normalizer.to_content_item(record)) for record in records]

    def _tag_item(self, item: ContentItem) -> ContentItem:
        item.tags = self.tagger.tag(item)
        return item

    def _index_items(self, items: list[ContentItem], replace: bool = True) -> None:
        if replace:
            self.vector_store.reset()
            self.contents = {}
        chunks = []
        for item in items:
            self.contents[item.source_id] = item
            chunks.extend(
                chunk_content_item(
                    item,
                    collection=self.settings.collection_name,
                    embedding_model=self.embedder.model_name,
                )
            )
        self.vector_store.upsert(chunks)
