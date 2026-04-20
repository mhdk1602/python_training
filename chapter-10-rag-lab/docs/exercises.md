# Exercise Pack

These exercises are meant to change the system, not just restate it.

## Exercise 1: Add a third source adapter

Create a `JsonFileAdapter` for a learner-chosen dataset. Keep the `ContentItem` contract unchanged. The retriever should work without modification.

## Exercise 2: Extend the ontology

Add one enum-style tag and one boolean tag. Record both the confidence score and the evidence string. Then inspect two false positives and explain whether the failure lives in the rules or the source text.

## Exercise 3: Evaluate chunking

Run the same query across two chunk sizes. Compare citation quality, answer specificity, and duplicate retrieval. Write down which failure mode appeared first.

## Exercise 4: Harden weak-evidence behavior

Change the answer threshold so the service refuses to answer sooner. Then compare the user experience in the demo UI. A system that declines cleanly is often more useful than one that improvises.

## Exercise 5: Swap the backend

Keep the application interfaces intact and replace the in-memory store with Chroma or Qdrant. The public request and response shapes should not change.
