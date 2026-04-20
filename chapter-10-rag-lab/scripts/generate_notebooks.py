from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "notebooks" / "10-retrieval-systems-and-agents"
PACKAGE_PATH = "../../chapter-10-rag-lab"


def markdown_cell(source: str) -> dict[str, object]:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code_cell(source: str) -> dict[str, object]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


NOTEBOOKS = [
    {
        "name": "10.1 System Frame.ipynb",
        "cells": [
            markdown_cell(
                "> **Chapter 10, Part 1** | Continues from Chapter 8. **Focus:** system contracts, evidence flow, and why retrieval pipelines fail before the model even speaks."
            ),
            markdown_cell(
                """# From Raw Content to Answer

This chapter defines the system boundary.

Most RAG tutorials start with a vector store because embeddings are visually seductive. I would start elsewhere. Before retrieval, I want to know what a content unit is, which fields are stable enough to filter later, and which evidence must survive all the way into the answer payload.

## Outputs

- a working `ContentItem` contract
- an architecture map for ingestion, tagging, indexing, retrieval, and answer synthesis
- a small glossary that keeps the rest of the capstone precise

## Supporting reading

- corpus design and chunk boundary discipline
- NPS API authentication and rate-limit etiquette
- why metadata filters often matter more than semantic similarity

## Failure note

If you cannot print one raw record, one normalized record, and one chunk side by side, you are debugging in the dark.

## How I would debug this

Start with one record and one question. I want to see the full path from source payload to retrieved snippet before I touch prompts.
"""
            ),
            code_cell(
                f"""from pathlib import Path
import sys

sys.path.append("{PACKAGE_PATH}")

from rag_lab.schemas import ContentItem, TagResult

example = ContentItem(
    source_id="demo-1",
    source_type="json",
    title="Accessible Canyon Walk",
    body="A paved route with low grade and high interpretive value.",
    summary="A paved route suitable for first-time visitors.",
    tags=[
        TagResult(
            tag_key="accessible",
            value="true",
            confidence=0.91,
            method="rule",
            evidence="Matched 'paved route'.",
        )
    ],
    metadata={{"state": "UT", "park_code": "zion"}},
    source_url="https://example.org/demo-1",
    updated_at="2026-04-20T09:00:00Z",
)

example
"""
            ),
            markdown_cell(
                """## Glossary

- **content item**: the normalized record the rest of the pipeline can trust
- **tag result**: a label plus confidence, method, and evidence
- **chunk record**: the retrieval unit, derived from a content item
- **search result**: the chunk plus ranking signal and citation context
- **grounded answer**: an answer that can point back to retrieved evidence
"""
            ),
        ],
    },
    {
        "name": "10.2 Source Adapters and Ingestion.ipynb",
        "cells": [
            markdown_cell(
                "> **Chapter 10, Part 2** | **Focus:** source adapters, ingestion contracts, and the discipline of dataset-agnostic pipelines."
            ),
            markdown_cell(
                """# Source Adapters and Ingestion

This chapter is about one interface: `SourceAdapter.fetch()`.

If I can swap the input source without rewriting retrieval, the system is portable. If I cannot, the app is a demo stitched to one dataset.

## Outputs

- `NpsSourceAdapter` for the public API
- `MarkdownNoteAdapter` for local authored material
- idempotent sample ingestion through the lab service

## Reading pack

- pagination and partial fetches
- duplicate handling
- source freshness and update timestamps
- practical rate-limit etiquette

## Failure note

Ingestion bugs usually look like retrieval bugs later. Missing identifiers and unstable URLs are the usual culprits.
"""
            ),
            code_cell(
                f"""import sys
sys.path.append("{PACKAGE_PATH}")

from pathlib import Path
from rag_lab.adapters import SampleJsonAdapter, MarkdownNoteAdapter

nps_records = SampleJsonAdapter(Path("{PACKAGE_PATH}") / "data" / "nps_things_to_do.json").fetch()
note_records = MarkdownNoteAdapter(Path("{PACKAGE_PATH}") / "data" / "field_notes.md").fetch()

len(nps_records), len(note_records), nps_records[0]["title"], note_records[0]["title"]
"""
            ),
            code_cell(
                f"""import sys
sys.path.append("{PACKAGE_PATH}")

from rag_lab.service import RetrievalLabService

lab = RetrievalLabService()
lab.status(), lab.list_sources()[:2]
"""
            ),
            markdown_cell(
                """## Exercise

Add a third adapter for a local JSON export from your own work. Keep the public retrieval interface unchanged.
"""
            ),
        ],
    },
    {
        "name": "10.3 Content Normalization and Tagging.ipynb",
        "cells": [
            markdown_cell(
                "> **Chapter 10, Part 3** | **Focus:** normalization, tag ontology design, and why provenance matters."
            ),
            markdown_cell(
                """# Content Normalization and Tagging

Normalization is where raw records stop being accidental schemas.

I want learners to feel the difference between a record that happens to contain text and a content item that the rest of the system can reason about. Tagging sits right on top of that boundary. The right ontology is small, inspectable, and tied to downstream questions.

## Outputs

- `Normalizer.to_content_item()`
- rule-based tags for transparent first-pass labeling
- model-assisted tags as an optional second pass

## Reading pack

- booleans versus enums
- label drift and review loops
- confidence scores that actually mean something

## Failure note

Tags without evidence strings become impossible to audit once the corpus grows.
"""
            ),
            code_cell(
                f"""import sys
sys.path.append("{PACKAGE_PATH}")

from pathlib import Path
from rag_lab.adapters import SampleJsonAdapter
from rag_lab.normalizer import NpsContentNormalizer
from rag_lab.tagging import CombinedTagger
from rag_lab.config import Settings

records = SampleJsonAdapter(Path("{PACKAGE_PATH}") / "data" / "nps_things_to_do.json").fetch()
normalizer = NpsContentNormalizer()
tagger = CombinedTagger(Settings(vector_backend="memory"))

item = normalizer.to_content_item(records[0])
item.tags = tagger.tag(item)
item.model_dump()
"""
            ),
            markdown_cell(
                """## How I would debug this

Print one false positive tag and ask a narrower question: was the mistake in the source text, the rule list, or the ontology itself?
"""
            ),
        ],
    },
    {
        "name": "10.4 Embeddings and the Local Vector Store.ipynb",
        "cells": [
            markdown_cell(
                "> **Chapter 10, Part 4** | **Focus:** chunking, embeddings, persistence, and metadata-aware retrieval."
            ),
            markdown_cell(
                """# Embeddings and the Local Vector Store

Chunking is not a preprocessing footnote. It is the retrieval problem wearing a different name.

This chapter uses a local-first default: hashing embeddings if nothing else is available, Ollama embeddings when the runtime is present, and Chroma persistence when the environment supports it. That keeps the lab finishable on a personal machine while preserving production-minded interfaces.

## Outputs

- chunk records with stable parent IDs
- Chroma persistence when available
- metadata filters that survive the index boundary

## Reading pack

- chunk size versus answer precision
- overlap tradeoffs
- why collection lifecycle matters during iteration
"""
            ),
            code_cell(
                f"""import sys
sys.path.append("{PACKAGE_PATH}")

from rag_lab.service import RetrievalLabService
from rag_lab.chunking import chunk_content_item

lab = RetrievalLabService()
source = lab.inspect_source("nps-zion-riverside")
item = lab.contents["nps-zion-riverside"]
chunks = chunk_content_item(item, collection="chapter10", embedding_model=lab.embedder.model_name)

len(chunks), chunks[0].model_dump()
"""
            ),
            code_cell(
                f"""import sys
sys.path.append("{PACKAGE_PATH}")

from rag_lab.service import RetrievalLabService

lab = RetrievalLabService()
results = lab.search("accessible first stop in Zion", filters={{"park_code": "zion"}}, top_k=3)
[result.model_dump() for result in results]
"""
            ),
            markdown_cell(
                """## Failure note

If filters are bolted on after indexing, you usually end up with brittle application-side filtering and misleading similarity scores.
"""
            ),
        ],
    },
    {
        "name": "10.5 Retrieval and Grounded Answers.ipynb",
        "cells": [
            markdown_cell(
                "> **Chapter 10, Part 5** | **Focus:** search quality, citation flow, and grounded answer behavior."
            ),
            markdown_cell(
                """# Retrieval and Grounded Answers

The answer layer should behave like a careful analyst. It should say what it knows, cite what it used, and refuse to overstate weak evidence.

## Outputs

- `Retriever.search(query, filters)`
- `AnswerService.answer(...)`
- answer warnings for low-confidence retrieval

## Reading pack

- retrieval metrics beyond vibes
- citation formatting in product surfaces
- common hallucination patterns in lightly grounded systems
"""
            ),
            code_cell(
                f"""import sys
sys.path.append("{PACKAGE_PATH}")

from rag_lab.service import RetrievalLabService

lab = RetrievalLabService()
answer = lab.answer("What is a good accessible first stop in Zion?", filters={{"park_code": "zion"}})
answer.model_dump()
"""
            ),
            code_cell(
                f"""import sys
sys.path.append("{PACKAGE_PATH}")

from rag_lab.service import RetrievalLabService

lab = RetrievalLabService()
weak = lab.answer("Which source covers glaciology satellites in Montana?", filters={{"park_code": "zion"}})
weak.model_dump()
"""
            ),
            markdown_cell(
                """## How I would debug this

When a grounded answer looks wrong, I check the ranking before I inspect the prose. Retrieval usually tells you whether the answer layer ever had a chance.
"""
            ),
        ],
    },
    {
        "name": "10.6 Agentic Q&A.ipynb",
        "cells": [
            markdown_cell(
                "> **Chapter 10, Part 6** | **Focus:** bounded agents, tool routing, and when not to overcomplicate retrieval."
            ),
            markdown_cell(
                """# Agentic Q&A

An agent is justified only when the user benefits from tool choice, not when the engineer wants a more dramatic architecture diagram.

The bounded agent in this capstone has three tools:

- search for candidate evidence
- inspect a source
- explain tag assignments

That is enough to show why agents can help without giving them permission to improvise over every failure.
"""
            ),
            code_cell(
                f"""import sys
sys.path.append("{PACKAGE_PATH}")

from rag_lab.service import RetrievalLabService

lab = RetrievalLabService()
agent_answer = lab.run_agent("Explain why this content was tagged as family-friendly in Zion.")
agent_answer.model_dump()
"""
            ),
            code_cell(
                f"""import sys
sys.path.append("{PACKAGE_PATH}")

from rag_lab.service import RetrievalLabService

lab = RetrievalLabService()
inspect = lab.run_agent("Inspect the source about the evening ranger program.")
inspect.model_dump()
"""
            ),
            markdown_cell(
                """## Failure note

If the search tool is weak, the agent just becomes a persuasive narrator for bad retrieval.
"""
            ),
        ],
    },
    {
        "name": "10.7 Demo UI and Evaluation.ipynb",
        "cells": [
            markdown_cell(
                "> **Chapter 10, Part 7** | **Focus:** UI honesty, retrieval traces, and evaluating whether the system deserves trust."
            ),
            markdown_cell(
                """# Demo UI and Evaluation

The frontend is not decoration in this chapter. It is part of the epistemic contract.

If the user cannot see the winning snippets, the applied filters, and the reasoning trace, the interface is asking for trust it did not earn.

## Outputs

- a dedicated Next.js route
- filter chips, citation drawer, tag inspector, and retrieval trace
- an evaluation checklist for answer quality and evidence quality
"""
            ),
            code_cell(
                f"""import sys
sys.path.append("{PACKAGE_PATH}")

from rag_lab.service import RetrievalLabService

lab = RetrievalLabService()
ui_payload = {{
    "search": [result.model_dump() for result in lab.search("family-friendly short stop", filters={{"state": "UT"}})],
    "answer": lab.answer("What should a first-time visitor start with in Zion?", filters={{"park_code": "zion"}}).model_dump(),
}}

ui_payload
"""
            ),
            markdown_cell(
                """## Evaluation checklist

- Did the answer cite the right sources?
- Did a metadata filter narrow the field correctly?
- Could a learner explain why the top chunk won?
- Did the system decline cleanly when evidence was weak?

## Exercise

Take one attractive but misleading UI choice from the route and remove it. This chapter cares more about auditability than polish for its own sake.
"""
            ),
        ],
    },
]


def build_notebook(cells: list[dict[str, object]]) -> dict[str, object]:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.11.0",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for notebook in NOTEBOOKS:
        path = OUT_DIR / notebook["name"]
        payload = build_notebook(notebook["cells"])
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
