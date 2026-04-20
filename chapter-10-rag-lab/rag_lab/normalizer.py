from __future__ import annotations

from html import unescape
import re
from typing import Any

from .schemas import ContentItem


def _clean_text(value: str) -> str:
    text = unescape(value or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


class NpsContentNormalizer:
    source_type = "nps-api"

    def to_content_item(self, record: dict[str, Any]) -> ContentItem:
        short = _clean_text(record.get("shortDescription", ""))
        long = _clean_text(record.get("longDescription", "")) or short
        topics = ", ".join(record.get("topics", []))
        title = record.get("title", "Untitled NPS Record").strip()
        body_parts = [short, long]
        if topics:
            body_parts.append(f"Topics: {topics}.")
        if record.get("duration"):
            body_parts.append(f"Estimated duration: {record['duration']}.")
        body = " ".join(part for part in body_parts if part)
        summary = short or long[:180]
        metadata = {
            "park_code": record.get("parkCode", ""),
            "park_name": record.get("parkName", ""),
            "state": record.get("state", ""),
            "duration": record.get("duration", ""),
            "pets_allowed": str(record.get("petsAllowed", "")).lower(),
            "topics": ", ".join(record.get("topics", [])),
        }
        return ContentItem(
            source_id=record.get("id", title.lower().replace(" ", "-")),
            source_type=self.source_type,
            title=title,
            body=body,
            summary=summary,
            metadata=metadata,
            source_url=record.get("url", "https://www.nps.gov"),
            updated_at=record.get("lastIndexedAt", "2026-04-20T09:00:00Z"),
        )


class MarkdownContentNormalizer:
    source_type = "markdown-note"

    def to_content_item(self, record: dict[str, Any]) -> ContentItem:
        body = _clean_text(record.get("body", ""))
        paragraphs = [part.strip() for part in body.split(". ") if part.strip()]
        summary = ". ".join(paragraphs[:2]).strip()
        return ContentItem(
            source_id=record["id"],
            source_type=self.source_type,
            title=record["title"],
            body=body,
            summary=summary,
            metadata={"origin": "local-markdown", "authorial": "true"},
            source_url=record["url"],
            updated_at=record.get("updated_at", "2026-04-20T09:00:00Z"),
        )
