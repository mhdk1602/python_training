from __future__ import annotations

import json

import requests

from .config import Settings
from .retrieval import Retriever
from .schemas import AnswerResponse, Citation, SearchResult, TagResult


class AnswerService:
    def __init__(self, retriever: Retriever, settings: Settings) -> None:
        self.retriever = retriever
        self.settings = settings

    def answer(self, query: str, filters: dict[str, str] | None = None, top_k: int = 4) -> AnswerResponse:
        results = self.retriever.search(query=query, filters=filters, top_k=top_k)
        trace = [
            {"step": "retrieval", "query": query, "top_k": top_k, "hits": len(results)},
        ]

        if not results:
            return AnswerResponse(
                answer="I do not have enough grounded evidence to answer that yet.",
                citations=[],
                matched_tags=[],
                applied_filters=filters or {},
                warning="No matching chunks passed retrieval.",
                trace=trace,
            )

        if results[0].score < self.settings.answer_threshold:
            trace.append({"step": "threshold", "score": results[0].score, "threshold": self.settings.answer_threshold})
            return AnswerResponse(
                answer="I found nearby material, but it is too weak to support a clean answer.",
                citations=_build_citations(results),
                matched_tags=_collect_tags(results),
                applied_filters=filters or {},
                warning="Top retrieval score was below the grounded-answer threshold.",
                trace=trace,
            )

        answer = self._draft_answer(query, results)
        trace.append({"step": "answer", "mode": "ollama" if answer["llm_used"] else "extractive"})
        return AnswerResponse(
            answer=answer["text"],
            citations=_build_citations(results),
            matched_tags=_collect_tags(results),
            applied_filters=filters or {},
            warning=None,
            trace=trace,
        )

    def _draft_answer(self, query: str, results: list[SearchResult]) -> dict[str, object]:
        prompt = {
            "instruction": (
                "Answer the user's question using only the retrieved evidence. "
                "If the evidence is partial, say so plainly. Return a JSON object with one key named 'answer'."
            ),
            "question": query,
            "evidence": [
                {
                    "title": result.title,
                    "snippet": result.snippet,
                    "source_id": result.source_id,
                    "score": round(result.score, 4),
                }
                for result in results
            ],
        }
        try:
            response = requests.post(
                f"{self.settings.ollama_base_url}/api/generate",
                json={
                    "model": self.settings.ollama_chat_model,
                    "stream": False,
                    "format": "json",
                    "prompt": json.dumps(prompt),
                },
                timeout=60,
            )
            response.raise_for_status()
            payload = response.json()
            text = json.loads(payload.get("response", "{}")).get("answer")
            if text:
                return {"text": text, "llm_used": True}
        except Exception:
            pass

        top = results[0]
        supporting_titles = ", ".join(result.title for result in results[1:3])
        text = (
            f"{top.title} is the strongest match. {top.snippet} "
            f"I would treat {supporting_titles or top.title} as supporting context rather than independent confirmation."
        )
        return {"text": text, "llm_used": False}


def _build_citations(results: list[SearchResult]) -> list[Citation]:
    citations: list[Citation] = []
    seen: set[str] = set()
    for result in results:
        if result.source_id in seen:
            continue
        seen.add(result.source_id)
        citations.append(
            Citation(
                source_id=result.source_id,
                title=result.title,
                source_url=result.metadata.get("source_url", ""),
                quote=result.snippet,
            )
        )
    return citations


def _collect_tags(results: list[SearchResult]) -> list[TagResult]:
    merged: dict[tuple[str, str], TagResult] = {}
    for result in results:
        for tag in result.tags:
            key = (tag.tag_key, tag.value)
            if key not in merged or merged[key].confidence < tag.confidence:
                merged[key] = tag
    return list(merged.values())
