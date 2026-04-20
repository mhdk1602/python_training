from __future__ import annotations

from rag_lab.config import Settings
from rag_lab.service import RetrievalLabService


def build_service() -> RetrievalLabService:
    return RetrievalLabService(Settings(vector_backend="memory", answer_threshold=0.35))


def test_seed_sample_corpus_indexes_multiple_sources() -> None:
    service = build_service()
    assert service.status()["source_count"] >= 4


def test_search_supports_metadata_filters() -> None:
    service = build_service()
    results = service.search("accessible first stop", filters={"park_code": "zion"}, top_k=3)
    assert results
    assert all(result.metadata.get("park_code") == "zion" for result in results)


def test_answer_warns_when_no_results_match_filters() -> None:
    service = build_service()
    answer = service.answer("glaciology satellites", filters={"park_code": "xxxx"}, top_k=3)
    assert answer.warning == "No matching chunks passed retrieval."


def test_agent_can_explain_tags() -> None:
    service = build_service()
    response = service.run_agent("Explain why this content was tagged as family-friendly.")
    assert response.mode == "tag-explanation"
    assert response.trace[0].tool == "search"
