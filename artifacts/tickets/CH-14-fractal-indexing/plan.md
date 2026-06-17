# CH-14 Fractal Indexing - Implementation Plan

**Spec:** [spec.md](./spec.md)
**Research plan:** [non-git-files/fractal-indexing-research-plan.md](../../../../non-git-files/fractal-indexing-research-plan.md)
**Style anchors:** Chapter 12 plan, Chapter 13 plan
**Identity:** mhdk1602 / mhdk.dinesh@gmail.com (SSH-signed, no AI co-authors)

## Risk-adjusted autonomy

Guided. The agent edits files freely and runs read-only commands without confirmation. Destructive commands (force push, branch deletion, file deletion outside the chapter folder) require user confirmation. The agent does not push to `origin/main` until all checkpoints pass and the user has reviewed at least one studio render and one notebook.

## Commit and merge strategy

Five logical commits, mirroring Chapters 12 and 13:

- **X001 Scaffolding.** spec, plan, requirements.txt, README, .gitignore.
- **X002 Generator + notebooks.** generate_chapter_14_notebooks.py and all 9 notebooks with embedded outputs.
- **X003 Studio.** indexing-studio.html, site-assets/indexing-studio.css, site-assets/indexing-studio.js.
- **X004 Site integration.** index.html nav and curriculum updates, README updates, four cross-link updates to existing studio pages.
- **X005 Citation + research linkage.** CITATION.cff confirmation, research-plan reference inside Chapter 14 README, dissertation citation correctness audit.

All five commit on `main` directly. No feature branch (matches the workflow used for Chapters 12 and 13).

## P### Implementation steps

### Phase 1: Scaffolding

- **P001 Verify spec and plan land cleanly.** Read both files; confirm no typos in citations, no AI co-author trailers anywhere in the repo metadata, identity is correct.
  - **References:** S007.

- **P002 Create chapter folder.** `notebooks/14-fractal-indexing/`.
  - **References:** F001-F009.

- **P003 Write requirements.txt.** numpy, pandas, scipy, matplotlib, networkx, rtree, duckdb, pyarrow, jupyter. Pin to recent stable.
  - **References:** N002.

- **P004 Write Chapter 14 README.md.** Mirrors the Chapter 12 and 13 READMEs: purpose, audience, prerequisites, notebook spine table, how to run, citation, dissertation linkage.
  - **References:** S004, N005.

- **P005 Update root .gitignore.** Add `.venv-ch14/` and `notebooks/14-fractal-indexing/.venv/`.
  - **References:** None new; matches Chapter 12/13 pattern.

- **K001 Phase 1 checkpoint.** All scaffolding files exist and pass markdown lint. Identity check passes.

- **X001 Commit.** "Add Chapter 14 fractal indexing scaffolding (spec, plan, requirements, README, gitignore)."

### Phase 2: Generator and notebooks

- **P006 Write `scripts/generate_chapter_14_notebooks.py`.** Mirror the Chapter 12 and 13 generator scripts. Helpers: `markdown_cell`, `code_cell`, deterministic notebook UUIDs.
  - **References:** F014.

- **P007 Implement notebook 14.0 content (Why Indexes Are Already Fractal).** Framing, three production examples, history paragraph, bounded claim.
  - **References:** F001.

- **P008 Implement notebook 14.1 content (Space-Filling Curves).** Pure-NumPy Z-order and Hilbert curves, locality measure, side-by-side visualization on 32×32 grid.
  - **References:** F002, V001, V002, A001.

- **P009 Implement notebook 14.2 content (Hilbert R-tree bulk loading).** Reproduce Kamel-Faloutsos 1994 on 10,000 synthetic points; report node utilization and bounding box savings.
  - **References:** F003.

- **P010 Implement notebook 14.3 content (Fractal-dimension selectivity oracle).** Grassberger-Procaccia D2 estimator, Faloutsos-Kamel selectivity formula, NYC taxi sample comparison, relative-error reporting.
  - **References:** F004, V003, A002, M001.

- **P011 Implement notebook 14.4 content (HNSW as hierarchical small-world index).** Tiny pure-Python HNSW, layer assignment visualization, search descent, scale-separation plot.
  - **References:** F005, A003, V004.

- **P012 Implement notebook 14.5 content (Liquid Clustering at Home: DuckDB Z-order vs Hilbert).** DuckDB benchmark with `ST_Hilbert`, three orderings, real geospatial data, honest reporting.
  - **References:** F006, M001, M002, V005, E001, E002, S008.

- **P013 Implement notebook 14.6 content (Adaptive chunking by Hurst exponent).** fGn streams at H=0.3, 0.5, 0.8; Hurst-driven chunk boundaries; comparison vs fixed-interval; explicit Zenodo paper linkage.
  - **References:** F007, M004.

- **P014 Implement notebook 14.7 content (Capstone: workload-to-index decision).** Decision tree, recommendation card, reproducible benchmark harness.
  - **References:** F008.

- **P015 Implement notebook 14.8 content (When the Speedup Is a Lie).** Four named failure modes with adversarial examples.
  - **References:** F009, S005.

- **P016 Run generator script.** Produces nine notebook files in `notebooks/14-fractal-indexing/`.

- **P017 Smoke test environment.** Create `.venv-ch14`, `pip install -r requirements.txt`, `python -c "import numpy, scipy, networkx, rtree, duckdb, pyarrow"`.

- **P018 Execute notebooks 14.0 through 14.8.** Use `jupyter nbconvert --execute --to notebook --inplace` for each. Embeds outputs.

- **K002 Phase 2 checkpoint.** All nine notebooks executed without error and contain embedded outputs. Validation rules V001-V005 pass.

- **X002 Commit.** "Add Chapter 14 notebook generator and nine executed notebooks (Hilbert, Z-order, R-tree, HNSW, DuckDB benchmark, Hurst chunking, capstone, failure modes)."

### Phase 3: Studio

- **P019 Write `indexing-studio.html`.** Mirrors the structure of `governance-studio.html`: hero, three lab sections, citation footer. All cross-links present.
  - **References:** F010-F012, S002, S006.

- **P020 Write `site-assets/indexing-studio.css`.** Reuses existing color tokens; adds curve-canvas, race-track-bar-chart, and HNSW-graph-overlay styles.
  - **References:** N003, N006.

- **P021 Write `site-assets/indexing-studio.js`.**
  - **Lab 1 module.** Hilbert and Z-order grid drawing, animated trace, draggable query rectangle, page-fetch counter.
  - **Lab 2 module.** Bulk-load on click, four index types, draggable query box, real-time bar chart of pages and ms.
  - **Lab 3 module.** Tiny HNSW (50-100 nodes, 3 layers), animated search descent, M slider, recall display.
  - **References:** F010-F012, E004, E005.

- **P022 HTML lint.** Open `indexing-studio.html` in a browser; ReadLints check; visual sanity in a real browser via the user's review.

- **K003 Phase 3 checkpoint.** Studio renders, three labs interactive, no console errors, no broken links.

- **X003 Commit.** "Add Chapter 14 indexing studio (curve animator, index race track, HNSW climber)."

### Phase 4: Site integration

- **P023 Update `index.html`.** Primary nav link to `indexing-studio.html`, fourth featured curriculum card, new spotlight panel for Chapter 14, bumped notebook and studio counters.
  - **References:** F013, S006.

- **P024 Cross-link existing studio pages.** Add a primary-nav link to `indexing-studio.html` from `fractals-governance.html`, `embeddings-bridge.html`, `ranking-lab.html`, `fractal-graphs.html`, and `governance-studio.html`.
  - **References:** F013.

- **P025 Update root README.md.** Bump notebook count, bump studio count, add Chapter 14 to Repository Shape and Tracks At A Glance, add a "Chapter 14: Fractal Indexing" section under Learning Roadmap, update Repository Structure with `14-fractal-indexing/` and `indexing-studio.html`, add Quick Start "Option H: Fractal Indexing Studio".
  - **References:** S006.

- **K004 Phase 4 checkpoint.** All site links working, four counters updated consistently, ReadLints clean on all touched HTML.

- **X004 Commit.** "Wire Chapter 14 into site (index, README, cross-links across five existing studio pages)."

### Phase 5: Citation and research linkage

- **P026 Add research-plan link inside Chapter 14 README.** Single sentence pointing to `non-git-files/fractal-indexing-research-plan.md`.

- **P027 Confirm CITATION.cff still uses Malemapti Hari, D.** No edit expected; just verify.
  - **References:** S003, prior chapter precedent.

- **P028 Audit dissertation citation usage.** Spot-check that any citation of Malemapti Hari (2026, Zenodo) in Chapter 14 notebooks uses correct format.
  - **References:** S003.

- **K005 Phase 5 checkpoint.** Citation discipline holds across the chapter.

- **X005 Commit.** "Add research-plan reference and confirm citation discipline for Chapter 14."

## W### File changes

| ID | Path | Action | Notes |
|---|---|---|---|
| W001 | `artifacts/tickets/CH-14-fractal-indexing/spec.md` | Created | This spec |
| W002 | `artifacts/tickets/CH-14-fractal-indexing/plan.md` | Created | This plan |
| W003 | `notebooks/14-fractal-indexing/requirements.txt` | Created | Chapter dependencies |
| W004 | `notebooks/14-fractal-indexing/README.md` | Created | Chapter README |
| W005 | `.gitignore` | Modified | Add `.venv-ch14/` |
| W006 | `scripts/generate_chapter_14_notebooks.py` | Created | Notebook generator |
| W007 | `notebooks/14-fractal-indexing/14.0 Why Indexes Are Already Fractal.ipynb` | Generated | Framing |
| W008 | `notebooks/14-fractal-indexing/14.1 Space-Filling Curves.ipynb` | Generated | Z-order, Hilbert |
| W009 | `notebooks/14-fractal-indexing/14.2 Hilbert R-tree Bulk Loading.ipynb` | Generated | Kamel-Faloutsos 1994 |
| W010 | `notebooks/14-fractal-indexing/14.3 Fractal Dimension as a Selectivity Oracle.ipynb` | Generated | Faloutsos-Kamel 1994 selectivity |
| W011 | `notebooks/14-fractal-indexing/14.4 HNSW as a Hierarchical Small-World Index.ipynb` | Generated | Pure-Python HNSW |
| W012 | `notebooks/14-fractal-indexing/14.5 Liquid Clustering at Home.ipynb` | Generated | DuckDB Z-order vs Hilbert |
| W013 | `notebooks/14-fractal-indexing/14.6 Adaptive Chunking by Hurst Exponent.ipynb` | Generated | Connects to Zenodo paper |
| W014 | `notebooks/14-fractal-indexing/14.7 Capstone Build Your Own Fractal Index.ipynb` | Generated | Decision tree + harness |
| W015 | `notebooks/14-fractal-indexing/14.8 When the Speedup Is a Lie.ipynb` | Generated | Failure modes |
| W016 | `indexing-studio.html` | Created | Studio page |
| W017 | `site-assets/indexing-studio.css` | Created | Studio styles |
| W018 | `site-assets/indexing-studio.js` | Created | Three labs |
| W019 | `index.html` | Modified | Nav, curriculum card, spotlight, counters |
| W020 | `fractals-governance.html` | Modified | Add nav link to Indexing studio |
| W021 | `embeddings-bridge.html` | Modified | Add nav link to Indexing studio |
| W022 | `ranking-lab.html` | Modified | Add nav link to Indexing studio |
| W023 | `fractal-graphs.html` | Modified | Add nav link to Indexing studio |
| W024 | `governance-studio.html` | Modified | Add nav link to Indexing studio |
| W025 | `README.md` | Modified | Counters, table rows, new section, Quick Start, structure |

## K### Checkpoints summary

- **K001** Scaffolding lints clean, identity verified.
- **K002** All nine notebooks execute end-to-end with outputs embedded; validation rules V001-V005 pass.
- **K003** Studio renders all three labs without console errors; visual review by user.
- **K004** Site integration: counters consistent, all links working, lints clean on HTML.
- **K005** Citation discipline holds; CITATION.cff verified.

## Time estimate (transparent and inflated per leadership rule 7)

- **Phase 1 (scaffolding):** 0.5 hours.
- **Phase 2 (generator + 9 notebooks + execution + smoke test):** 4-6 hours. Notebooks 14.2 (R-tree), 14.4 (HNSW), and 14.5 (DuckDB benchmark) carry the most implementation risk.
- **Phase 3 (studio with three labs):** 4-5 hours. Lab 1 (curve animator) is the longest because the animation must be smooth and the locality counter must be accurate.
- **Phase 4 (site integration):** 1 hour.
- **Phase 5 (citation audit):** 0.5 hours.

Total: 10-13 hours of focused work. With realistic context switching and benchmark debugging on Phase 2, plan for two working sessions.

## Anti-patterns to avoid

- **Z001 Pre-baked benchmarks.** Notebook 14.5 must produce numbers on the reader's machine, not display screenshots of pre-computed results.
- **Z002 Marketing the result.** "Fractal indexes are revolutionary" is forbidden. The bounded claim is the only claim.
- **Z003 Hiding the failure modes.** Notebook 14.8 is mandatory. The chapter ships without it only if the user explicitly removes the requirement.
- **Z004 Cross-chapter drift.** The studio shares design tokens with Chapters 11-13. Do not reinvent the palette.
- **Z005 Vendor-specific lock-in.** The chapter teaches the apparatus, not Snowflake or Databricks specifics. DuckDB is used because it runs on the reader's laptop.

## Open decisions (default proposals from spec)

- **Q001** DuckDB only, not Iceberg integration in this chapter. Default: yes.
- **Q002** Three labs (no H3 fourth lab). Default: yes.
- **Q003** Notebook 14.3 stays synthetic; PostgreSQL comparison is a follow-up exercise. Default: yes.
- **Q004** Notebook 14.6 in pure Python with a final-cell `lindel` extension demonstration. Default: yes.

If the user disagrees with any of Q001-Q004, override before P006.
