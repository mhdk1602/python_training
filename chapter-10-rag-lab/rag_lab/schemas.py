from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TagResult(BaseModel):
    tag_key: str
    value: str
    confidence: float = Field(ge=0.0, le=1.0)
    method: str
    evidence: str


class ContentItem(BaseModel):
    source_id: str
    source_type: str
    title: str
    body: str
    summary: str
    tags: list[TagResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    source_url: str
    updated_at: str


class ChunkRecord(BaseModel):
    chunk_id: str
    parent_id: str
    text: str
    tags: list[TagResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    embedding_model: str
    collection: str


class SearchResult(BaseModel):
    chunk_id: str
    score: float
    source_id: str
    title: str
    snippet: str
    tags: list[TagResult] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Citation(BaseModel):
    source_id: str
    title: str
    source_url: str
    quote: str


class AnswerResponse(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    matched_tags: list[TagResult] = Field(default_factory=list)
    applied_filters: dict[str, Any] = Field(default_factory=dict)
    warning: str | None = None
    trace: list[dict[str, Any]] = Field(default_factory=list)


class AgentStep(BaseModel):
    tool: str
    input_summary: str
    output_summary: str


class AgentResponse(BaseModel):
    mode: str
    answer_response: AnswerResponse | None = None
    source_preview: dict[str, Any] | None = None
    tag_explanation: dict[str, Any] | None = None
    trace: list[AgentStep] = Field(default_factory=list)


class SearchRequest(BaseModel):
    query: str
    filters: dict[str, Any] = Field(default_factory=dict)
    top_k: int = Field(default=5, ge=1, le=12)


class AnswerRequest(BaseModel):
    query: str
    filters: dict[str, Any] = Field(default_factory=dict)
    top_k: int = Field(default=4, ge=1, le=10)


class AgentRequest(BaseModel):
    query: str
    filters: dict[str, Any] = Field(default_factory=dict)


class LiveNpsRequest(BaseModel):
    park_code: str = Field(default="zion", min_length=4, max_length=4)
    resource: str = Field(default="thingstodo")
    limit: int = Field(default=6, ge=1, le=20)
