from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from rag_lab.service import RetrievalLabService
from rag_lab.schemas import AgentRequest, AnswerRequest, LiveNpsRequest, SearchRequest


service = RetrievalLabService()
app = FastAPI(title="Chapter 10 Retrieval Lab", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, object]:
    return {"ok": True} | service.status()


@app.get("/sources")
def list_sources() -> dict[str, object]:
    return {"sources": service.list_sources()}


@app.post("/demo/bootstrap")
def bootstrap() -> dict[str, object]:
    return service.seed_sample_corpus()


@app.post("/sources/nps-refresh")
def refresh_live_nps(request: LiveNpsRequest) -> dict[str, object]:
    try:
        return service.refresh_live_nps(
            park_code=request.park_code,
            resource=request.resource,
            limit=request.limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/search")
def search(request: SearchRequest) -> dict[str, object]:
    return {"results": [result.model_dump() for result in service.search(request.query, request.filters, request.top_k)]}


@app.post("/answer")
def answer(request: AnswerRequest) -> dict[str, object]:
    return service.answer(request.query, request.filters, request.top_k).model_dump()


@app.post("/agent")
def agent(request: AgentRequest) -> dict[str, object]:
    return service.run_agent(request.query, request.filters).model_dump()


@app.get("/sources/{source_id}")
def inspect_source(source_id: str) -> dict[str, object]:
    try:
        return service.inspect_source(source_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown source_id '{source_id}'.") from exc
