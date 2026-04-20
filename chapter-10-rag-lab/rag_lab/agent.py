from __future__ import annotations

from typing import TYPE_CHECKING

from .answering import AnswerService
from .retrieval import Retriever
from .schemas import AgentResponse, AgentStep

if TYPE_CHECKING:
    from .service import RetrievalLabService


class BoundedAgent:
    def __init__(self, answer_service: AnswerService, retriever: Retriever, service: "RetrievalLabService") -> None:
        self.answer_service = answer_service
        self.retriever = retriever
        self.service = service

    def run(self, query: str, filters: dict[str, str] | None = None) -> AgentResponse:
        lower = query.lower()
        trace: list[AgentStep] = []
        results = self.retriever.search(query, filters=filters, top_k=3)
        trace.append(
            AgentStep(
                tool="search",
                input_summary=query,
                output_summary=f"Retrieved {len(results)} candidate chunks.",
            )
        )

        if "tag" in lower and ("why" in lower or "explain" in lower):
            if not results:
                return AgentResponse(mode="tag-explanation", tag_explanation={"message": "No matching content."}, trace=trace)
            explanation = self.service.explain_tags(results[0].source_id)
            trace.append(
                AgentStep(
                    tool="explain_tags",
                    input_summary=results[0].source_id,
                    output_summary=f"Explained {len(explanation.get('tags', []))} tags.",
                )
            )
            return AgentResponse(mode="tag-explanation", tag_explanation=explanation, trace=trace)

        if "inspect" in lower or "show source" in lower or "citation" in lower:
            if not results:
                return AgentResponse(mode="source-inspection", source_preview={"message": "No matching source."}, trace=trace)
            preview = self.service.inspect_source(results[0].source_id)
            trace.append(
                AgentStep(
                    tool="inspect_source",
                    input_summary=results[0].source_id,
                    output_summary=f"Loaded source '{preview.get('title', 'unknown')}'.",
                )
            )
            return AgentResponse(mode="source-inspection", source_preview=preview, trace=trace)

        answer = self.answer_service.answer(query, filters=filters, top_k=4)
        trace.append(
            AgentStep(
                tool="answer",
                input_summary=query,
                output_summary=answer.warning or "Delivered grounded answer with citations.",
            )
        )
        return AgentResponse(mode="answer", answer_response=answer, trace=trace)
