from __future__ import annotations

import json
import re

from .schemas import ChunkRecord, ContentItem, TagResult


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def chunk_content_item(
    content: ContentItem,
    collection: str,
    embedding_model: str,
    chunk_size: int = 85,
    overlap: int = 18,
) -> list[ChunkRecord]:
    words = content.body.split()
    if not words:
        return []

    chunks: list[ChunkRecord] = []
    start = 0
    index = 0
    while start < len(words):
        window = words[start : start + chunk_size]
        text = " ".join(window)
        flat_metadata = {
            "source_id": content.source_id,
            "source_type": content.source_type,
            "title": content.title,
            "source_url": content.source_url,
            "summary": content.summary,
            "updated_at": content.updated_at,
            "metadata_json": json.dumps(content.metadata, sort_keys=True),
            "tags_json": json.dumps([tag.model_dump() for tag in content.tags], sort_keys=True),
        }
        for key, value in content.metadata.items():
            if value is not None:
                flat_metadata[_slug(key)] = str(value)
        for tag in content.tags:
            flat_metadata[f"tag_{_slug(tag.tag_key)}"] = tag.value

        chunks.append(
            ChunkRecord(
                chunk_id=f"{content.source_id}::chunk-{index}",
                parent_id=content.source_id,
                text=text,
                tags=list(content.tags),
                metadata=flat_metadata,
                embedding_model=embedding_model,
                collection=collection,
            )
        )
        if start + chunk_size >= len(words):
            break
        start += chunk_size - overlap
        index += 1
    return chunks


def tags_from_metadata(tags_json: str) -> list[TagResult]:
    if not tags_json:
        return []
    return [TagResult(**tag) for tag in json.loads(tags_json)]
