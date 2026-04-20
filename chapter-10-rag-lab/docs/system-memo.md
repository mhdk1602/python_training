# System Memo

This lab starts with one claim: retrieval systems fail at the interfaces, not the embeddings.

If a learner cannot answer three questions, the implementation usually drifts fast.

1. What exactly is a content unit?
2. Which fields are stable enough to filter on later?
3. What evidence should survive the trip from source record to answer payload?

`ContentItem` is the answer to the first question. It is the contract between ingestion and everything downstream. The schema is intentionally plain. Each item has a source identifier, a source type, a readable title, the core body text, a terse summary, the applied tags, a metadata bag, the original source URL, and an update timestamp.

The second question is where many toy RAG examples break down. If metadata is an afterthought, learners end up with a vector store that can retrieve semantically similar text but cannot answer operational questions such as "show me ranger-led content in Utah" or "filter to beginner material." This capstone keeps metadata explicit from the first normalization pass.

The third question matters because grounded answers need evidence, not just context stuffing. Every chunk keeps a parent identifier, stable metadata, and enough source detail to build a citation later. That design keeps the answer layer honest. It also makes the UI auditable: learners can inspect which chunk won, why it won, and what tags shaped the result.

## Failure notes

- A beautiful embedding model cannot rescue weak chunk boundaries.
- Labels without provenance are hard to debug and harder to trust.
- Agents amplify interface mistakes. If retrieval is unstable, the agent just hides the instability behind more fluent prose.

## How I would debug this

- Inspect one raw record, one normalized content item, and one chunk side by side before touching prompts.
- Query the vector store directly with and without filters to see whether the store or the answer layer is dropping signal.
- Check the top false positives before tuning the model path. Rule-based tags often reveal the real schema mistake faster than another prompt revision.
