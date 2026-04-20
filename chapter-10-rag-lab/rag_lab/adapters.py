from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
import json
import re
from typing import Any

import requests


class SourceAdapter(ABC):
    source_type: str

    @abstractmethod
    def fetch(self) -> list[dict[str, Any]]:
        raise NotImplementedError


class SampleJsonAdapter(SourceAdapter):
    source_type = "nps-api"

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def fetch(self) -> list[dict[str, Any]]:
        with self.file_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)


class MarkdownNoteAdapter(SourceAdapter):
    source_type = "markdown-note"

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def fetch(self) -> list[dict[str, Any]]:
        text = self.file_path.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
        title = title_match.group(1).strip() if title_match else self.file_path.stem.replace("-", " ").title()
        return [
            {
                "id": f"md-{self.file_path.stem}",
                "title": title,
                "body": text,
                "url": self.file_path.as_uri(),
                "updated_at": "2026-04-20T09:00:00Z",
            }
        ]


class NpsSourceAdapter(SourceAdapter):
    source_type = "nps-api"

    def __init__(self, api_key: str, park_code: str = "zion", resource: str = "thingstodo", limit: int = 6) -> None:
        self.api_key = api_key
        self.park_code = park_code
        self.resource = resource
        self.limit = limit
        self.base_url = "https://developer.nps.gov/api/v1"

    def fetch(self) -> list[dict[str, Any]]:
        params = {
            "api_key": self.api_key,
            "parkCode": self.park_code,
            "limit": self.limit,
        }
        response = requests.get(f"{self.base_url}/{self.resource}", params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        return payload.get("data", [])
