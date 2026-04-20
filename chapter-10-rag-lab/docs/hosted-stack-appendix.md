# Hosted Stack Appendix

The default lab path is local-first because learners should be able to finish the build without committing to paid infrastructure. The interface boundaries are still production-minded.

## Hosted substitutions

| Local default | Hosted substitute | Reason |
|---|---|---|
| Ollama embeddings | OpenAI or Voyage embeddings | Better retrieval quality and easier deployment |
| Chroma local persistence | Qdrant Cloud or Pinecone | Operational durability and managed indexing |
| In-process FastAPI | FastAPI behind a container platform | Scales cleanly once the contracts stabilize |

## What should stay unchanged

- `ContentItem`, `ChunkRecord`, `SearchResult`, and `AnswerResponse`
- Retrieval filters and citation behavior
- The distinction between retrieval, answer synthesis, and agent tooling

If learners can swap the infrastructure without rewriting the application semantics, the curriculum has done its job.
