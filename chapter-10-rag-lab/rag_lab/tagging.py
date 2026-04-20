from __future__ import annotations

import json
from typing import Iterable

import requests

from .config import Settings
from .schemas import ContentItem, TagResult


TAG_ONTOLOGY: dict[str, dict[str, object]] = {
    "family-friendly": {
        "type": "boolean",
        "description": "Suitable for visitors with children or first-time planners.",
        "keywords": ["family", "children", "all ages", "gentler", "approachable", "first-time"],
    },
    "accessible": {
        "type": "boolean",
        "description": "Signals step-free or low-friction access.",
        "keywords": ["accessible", "paved", "wheelchair", "gentle terrain", "low-friction"],
    },
    "ranger-led": {
        "type": "boolean",
        "description": "Includes a ranger, guide, or formal interpretive program.",
        "keywords": ["ranger", "guided", "program", "interpretive"],
    },
    "trip-length": {
        "type": "enum",
        "description": "How much of the day the content appears to consume.",
        "values": {
            "short": ["45 minutes", "1 hour", "short walk", "low-friction"],
            "half-day": ["1.5 hours", "2 hours", "half-day"],
            "full-day": ["full day", "all day"],
        },
    },
    "logistics": {
        "type": "boolean",
        "description": "Mentions operational constraints such as shuttles, permits, or reservations.",
        "keywords": ["shuttle", "permit", "reservation", "timing", "arrival time"],
    },
}


class RuleBasedTagger:
    def tag(self, content: ContentItem) -> list[TagResult]:
        haystack = f"{content.title} {content.body} {' '.join(str(value) for value in content.metadata.values())}".lower()
        tags: list[TagResult] = []

        for tag_key, config in TAG_ONTOLOGY.items():
            tag_type = config["type"]
            if tag_type == "boolean":
                for keyword in config["keywords"]:
                    if keyword in haystack:
                        tags.append(
                            TagResult(
                                tag_key=tag_key,
                                value="true",
                                confidence=0.82,
                                method="rule",
                                evidence=f"Matched keyword '{keyword}' in content text.",
                            )
                        )
                        break
            else:
                for label, keywords in config["values"].items():
                    for keyword in keywords:
                        if keyword in haystack:
                            tags.append(
                                TagResult(
                                    tag_key=tag_key,
                                    value=label,
                                    confidence=0.74,
                                    method="rule",
                                    evidence=f"Assigned '{label}' after matching '{keyword}'.",
                                )
                            )
                            break
                    else:
                        continue
                    break

        return tags


class ModelAssistedTagger:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def tag(self, content: ContentItem) -> list[TagResult]:
        prompt = {
            "instruction": (
                "Read the content and return a JSON object with a top-level 'tags' array. "
                "Each tag entry must include tag_key, value, confidence, method, and evidence. "
                "Only use the provided ontology."
            ),
            "ontology": TAG_ONTOLOGY,
            "content": {
                "title": content.title,
                "summary": content.summary,
                "body": content.body[:1600],
            },
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
            model_text = payload.get("response", "{}")
            parsed = json.loads(model_text)
            return [TagResult(**tag, method="model") for tag in parsed.get("tags", [])]
        except Exception:
            return []


class CombinedTagger:
    def __init__(self, settings: Settings) -> None:
        self.rule_tagger = RuleBasedTagger()
        self.model_tagger = ModelAssistedTagger(settings)
        self.settings = settings

    def tag(self, content: ContentItem) -> list[TagResult]:
        merged: dict[tuple[str, str], TagResult] = {}
        for tag in self.rule_tagger.tag(content):
            merged[(tag.tag_key, tag.value)] = tag

        if self.settings.model_assisted_tagging:
            for tag in self.model_tagger.tag(content):
                key = (tag.tag_key, tag.value)
                if key not in merged or merged[key].confidence < tag.confidence:
                    merged[key] = tag

        return list(merged.values())


def matched_tag_keys(tags: Iterable[TagResult]) -> list[str]:
    return sorted({tag.tag_key for tag in tags})
