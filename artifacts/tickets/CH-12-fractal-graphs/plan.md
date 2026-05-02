# Chapter 12 — Fractal Graphs: Plan

> **Ticket:** CH-12-fractal-graphs
> **Author:** mhdk1602
> **Date:** 2026-05-01
> **Status:** Plan (planning stage of the 4-stage loop)
> **Spec:** `./spec.md`

This document translates the spec into ordered work items. P### are implementation steps. W### are file changes. K### are testing checkpoints. X### are commit points. Q-defaults from the spec are taken as decided (see "Decisions locked" below).

---

## Decisions locked (from spec Q001–Q005)

- **D1 (Q001):** Keep both 11.4 (union-find primer) and 12.6 (graph upgrade). 11.4 stays untouched.
- **D2 (Q002):** Ship Karate club graph (NetworkX built-in) and a synthetic lineage subgraph. No external downloads at notebook runtime.
- **D3 (Q003):** Build all three studio panels: Visibility Graph Lab, Box-Covering Lab, Lineage Risk Lab.
- **D4 (Q004):** Multifractal analysis out of scope for v1. Forward pointer in 12.7.
- **D5 (Q005):** Cite Malemapti Hari (2026, Zenodo) in 12.2 cell 1. Algorithm is self-contained.

---

## P — Implementation steps

| ID | Step | Implements (spec IDs) | Files touched |
|---|---|---|---|
| **P001** | Add chapter-local dependencies. Create `notebooks/12-fractal-graphs/requirements.txt` with `networkx>=3.2`, `python-louvain>=0.16`, `powerlaw>=1.5`, `scipy`, `pandas`, `numpy`, `matplotlib`. Document in chapter folder README. | D002, N005 | W001 |
| **P002** | Create the notebook generator script at `scripts/generate_chapter_12_notebooks.py`. Mirror the conventions in `chapter-10-rag-lab/scripts/generate_notebooks.py`. | N002, S007 | W002 |
| **P003** | Author 12.0 (preface) cells: blockquote header, framing markdown, one teaser code cell rendering Karate club with NetworkX, closing assignment. | F001, S001, C001 | W003 |
| **P004** | Author 12.1 (graphs primer) cells: minimum graph language, rebuild 11.4 records and scores as a NetworkX graph, connected-components walk-through, degree histogram on Karate club. | F001, C002 | W003 |
| **P005** | Author 12.2 (visibility graph) cells: O(n²) visibility kernel, three-regime demonstration (sin, uniform random, fBm at H ∈ {0.3, 0.5, 0.7}), Hurst-vs-α reproduction figure. Cell 1 cites Malemapti Hari (2026). | F002, F003, F004, C003 | W003 |
| **P006** | Author 12.3 (box covering on graphs) cells: auxiliary-graph builder, greedy-coloring `box_cover`, `estimate_d_B`, three reference networks (Sierpinski-like, (u,v)-flower, hierarchical SHM), one real network (Karate), one non-fractal control (Erdős-Rényi). | F005, F006, C004 | W003 |
| **P007** | Author 12.4 (skeleton + renormalization) cells: skeleton extractor (max-betweenness spanning), renormalize one fractal and one non-fractal, side-by-side coarse-grained adjacency. | F007, C005 | W003 |
| **P008** | Author 12.5 (lineage and propagation) cells: synthetic DAG builder, defect propagation, blast-radius descriptor, dbt manifest soft-import. | F009, C006 | W003 |
| **P009** | Author 12.6 (entity resolution upgrade) cells: rebuild 11.4 records as graph, sweep thresholds, compute four cluster descriptors per threshold, new instability score, ranked stewardship table. | F010, C007 | W003 |
| **P010** | Author 12.7 (epistemic guardrails) cells: four worked failure modes (small-N, tree mimic, trend artifact, slope-without-stability) with closing assignment that ties back to 12.0. | F011, E001–E007, C008 | W003 |
| **P011** | Run the generator. Execute every notebook end-to-end against the chapter requirements file. Fix any runtime errors. | N003, N004, S007 | W003 |
| **P012** | Build `fractal-graphs.html`. Mirror `fractals-governance.html` shell, navigation, hero, sections. Wire IDs that JS will hook into. | F012, S005, C009 | W004 |
| **P013** | Build `site-assets/fractal-graphs.css`. Reuse the design tokens (`--cream`, `--moss`, `--sand`, `--shadow`) from `fractals.css`. Add three lab-specific layouts. | S005, C010 | W005 |
| **P014** | Build `site-assets/fractal-graphs.js`. Three labs: visibility, box-covering, lineage. Vanilla JS, no bundler. Reuse the `[data-reveal]` intersection observer pattern from `fractals.js`. | F012, C010 | W006 |
| **P015** | Wire Chapter 12 into `index.html`: add nav link, add chapter-river card for 12, add a spotlight section. | S005 | W007 |
| **P016** | Update `README.md`: add Chapter 12 to "Repository Shape", "Tracks at a Glance", "If You Like To Learn By...", "Learning Roadmap", and the syllabus header link list. Update the directory listing in "Repository Structure". | S005 | W008 |
| **P017** | Update `.cursor/rules/research-entity.mdc` to add `notebooks/12-fractal-graphs/`. | N008 | W009 |
| **P018** | Cross-link studio pages: add a Fractal Graphs link to the nav of `fractals-governance.html` and `embeddings-bridge.html` and `ranking-lab.html`. | S005 | W010 |
| **P019** | Smoke checks: all eight notebooks execute end-to-end; the studio page loads without console errors; HTML validates; nav links resolve. | K001–K003 | W003, W004 |
| **P020** | Commit and push in five logical chunks (X001–X005). | — | — |

---

## W — File changes

| ID | Path | Type | Notes |
|---|---|---|---|
| **W001** | `notebooks/12-fractal-graphs/requirements.txt` | new | Chapter-local deps. |
| **W002** | `scripts/generate_chapter_12_notebooks.py` | new | Notebook generator. |
| **W003** | `notebooks/12-fractal-graphs/12.0–12.7 *.ipynb` | new (8 files) | Generated by W002. |
| **W004** | `fractal-graphs.html` | new | Studio page. |
| **W005** | `site-assets/fractal-graphs.css` | new | Studio styles. |
| **W006** | `site-assets/fractal-graphs.js` | new | Studio scripts. |
| **W007** | `index.html` | edit | Nav link, chapter-river card, spotlight section. |
| **W008** | `README.md` | edit | Roadmap, tracks, repository shape, syllabus header. |
| **W009** | `.cursor/rules/research-entity.mdc` | edit | Add chapter 12 path. |
| **W010** | `fractals-governance.html`, `embeddings-bridge.html`, `ranking-lab.html` | edit | Cross-link nav. |
| **W011** | `notebooks/12-fractal-graphs/README.md` | new | Run guide for the chapter. |

---

## K — Testing checkpoints

- **K001 — Notebook execution.** All eight notebooks run end-to-end with a fresh venv that has only the packages from W001. Run via `jupyter nbconvert --to notebook --execute --inplace` for each notebook. Any cell that produces a non-deterministic seed must use `np.random.default_rng(7)`.
- **K002 — Studio page sanity.** Open `fractal-graphs.html` locally with a static server; confirm the three labs load, the visibility graph reacts to series-edits, the box-covering animation cycles, and the lineage panel responds to clicks. No console errors.
- **K003 — Cross-page links.** Every nav link, README link, and studio cross-link resolves on disk and through GitHub Pages routing.
- **K004 — Lint posture.** No new linter errors in HTML or JS. README markdown renders cleanly on GitHub.
- **K005 — Citation correctness.** Every reference in the spec source-of-truth list appears at least once in a notebook cell 1, exactly as written.

---

## X — Commit points

| ID | Scope | Files | Suggested message |
|---|---|---|---|
| **X001** | Spec + plan + chapter requirements | W001, `artifacts/tickets/CH-12-fractal-graphs/spec.md`, `artifacts/tickets/CH-12-fractal-graphs/plan.md` | `Add Chapter 12 spec, plan, and chapter requirements` |
| **X002** | Notebook generator + 8 notebooks + chapter README | W002, W003, W011 | `Add Chapter 12 fractal graphs notebook spine` |
| **X003** | Studio page (HTML + CSS + JS) | W004, W005, W006 | `Add Fractal Graphs studio page with three interactive labs` |
| **X004** | Site wiring (index, README, research-entity rule) | W007, W008, W009 | `Wire Chapter 12 into site index and README` |
| **X005** | Cross-link existing studio pages | W010 | `Cross-link Fractal Graphs studio across existing pages` |

After X005: `git push origin main`.

---

## Risks during execution

- **Re001 — `python-louvain` install friction on Apple Silicon.** Fallback: notebooks must guard the import with `try/except ImportError` and degrade to a stub partition (single community) when the package is absent. The chapter does not require Louvain to read.
- **Re002 — `powerlaw` dependency tree.** `powerlaw` pulls in `mpmath`. If this fails, fallback is the `np.polyfit` slope with a documented goodness-of-fit warning.
- **Re003 — fBm generator.** `numpy` does not ship a fractional Brownian motion generator. We implement Hosking's method or use the Davies-Harte algorithm in a small helper inside 12.2. No new dependencies.
- **Re004 — Karate club rendering.** NetworkX 3.x removed `nx.info()`. Use `g.number_of_nodes()` and `g.number_of_edges()` directly.
- **Re005 — Visibility graph compute time.** O(n²) is acceptable up to n ≈ 1500. Notebooks cap n at 1024 and document the cap.

---

## Acceptance gate (handoff to implementation)

- All P### steps above have an owner (mhdk1602) and a sequence.
- All W### file changes are listed.
- All K### checkpoints have a runnable command.
- All X### commit messages are short, factual, and free of co-author trailers.
