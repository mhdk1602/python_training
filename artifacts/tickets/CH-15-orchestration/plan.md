# CH-15 Orchestration as Asset Graphs — Implementation Plan

**Spec:** [spec.md](./spec.md)
**Style anchors:** Chapter 13 plan, Chapter 14 plan
**Identity:** Dinesh Hari / mhdk.dinesh@gmail.com (no AI co-authors; push via `github.com-personal` SSH remote)

## Risk-adjusted autonomy

Guided. The agent edits files freely and runs read-only commands without confirmation. File deletion outside the chapter folder and any force push require user confirmation. Because the session directive was explicit ("execute what's next", "go crazy", with prior pushes approved this session), the agent commits and pushes to `origin/main` after every checkpoint passes and the studio render is verified by screenshot.

## Commit and merge strategy

Four logical commits, a slightly tightened version of the five used for Chapters 12-14 (the citation-audit commit folds into scaffolding because this chapter has fewer external numerical claims):

- **X001 Scaffolding.** spec, plan, requirements.txt, README, .gitignore note.
- **X002 Generator + notebooks.** generate_chapter_15_notebooks.py and all 9 executed notebooks with embedded outputs.
- **X003 Studio.** orchestration-studio.html, site-assets/orchestration-studio.css, site-assets/orchestration-studio.js.
- **X004 Site integration.** index.html (curriculum, gallery, counters), README updates, six cross-link nav updates to existing studio pages.

All four commit on `main` directly, matching the workflow used for Chapters 12-14.

## P### Implementation steps

### Phase 1: Scaffolding

- **P001 Land spec and plan.** Both files in `artifacts/tickets/CH-15-orchestration/`. Confirm identity, no co-author trailers. **Refs:** S008.
- **P002 Create chapter folder** `notebooks/15-orchestration/`. **Refs:** F001-F008.
- **P003 Write requirements.txt.** numpy, networkx, matplotlib, pandas, jupyter; pinned to recent stable. **Refs:** N002.
- **P004 Write Chapter 15 README.md.** Mirrors the 12-14 READMEs: audience, prerequisites, bounded claim, notebook-spine table, how to run, how it fits the site, citation. **Refs:** S004, N004.
- **K001 Phase 1 checkpoint.** Scaffolding files exist; identity check passes.
- **X001 Commit.** "Add Chapter 15 orchestration scaffolding (spec, plan, requirements, README)."

### Phase 2: Generator and notebooks

- **P005 Write `scripts/generate_chapter_15_notebooks.py`.** Same `markdown_cell`/`code_cell` helpers and notebook envelope as the 12-14 generators. **Refs:** F013.
- **P006 Implement 15.0** (From Cron to Asset Graphs): the four failures, the asset abstraction, the bounded claim. **Refs:** F001.
- **P007 Implement 15.1** (A Tiny Asset Graph From Scratch): `Asset`, `AssetGraph`, topological materialize, cycle detection, NetworkX viz. **Refs:** F002, V001, V002, A001, A002, C001, C002.
- **P008 Implement 15.2** (Partitions and Backfills): partition keys, `MaterializationLog`, `backfill`, idempotent rerun. **Refs:** F003, V003, A003, C003.
- **P009 Implement 15.3** (Sensors and Freshness): polling `Sensor` on a simulated clock, `FreshnessPolicy`, staleness detection. **Refs:** F003b, C004.
- **P010 Implement 15.4** (Wrapping the dbt Project): parse `dbt/dbt_dq/models/*.sql` ref() edges, build and materialize the graph, embedded fallback. **Refs:** F004, M002, E001, C006.
- **P011 Implement 15.5** (Failure, Retries, Blast Radius): failure injection, skip-on-failure, `RetryPolicy`, `blast_radius`. **Refs:** F005, V004, V005, A004, C005.
- **P012 Implement 15.6** (From Our Toy to Dagster): concept-by-concept mapping to `@asset`, partitions, sensors, freshness, retry, `Definitions`; Airflow/Prefect paragraph; Dagster code labelled illustrative. **Refs:** F006, S006.
- **P013 Implement 15.7** (Capstone: Orchestrate the Trading Platform): market_data → price_history → positions → daily_pnl → warren_context, partitioned by trading day, run + backfill. **Refs:** F007, M003, M004.
- **P014 Implement 15.8** (When the Schedule Lies): four failure modes with adversarial demos. **Refs:** F008, S005, E006.
- **P015 Run generator.** Emits nine notebooks in `notebooks/15-orchestration/`.
- **P016 Smoke test env.** Create venv, install requirements, `python -c "import numpy, networkx, matplotlib, pandas"`.
- **P017 Execute notebooks 15.0-15.8** via `jupyter nbconvert --execute --to notebook --inplace`. Embeds outputs.
- **K002 Phase 2 checkpoint.** All nine notebooks execute without error and embed outputs; validation rules V001-V005 pass; `scripts/validate_notebooks.py` is clean.
- **X002 Commit.** "Add Chapter 15 notebook generator and nine executed notebooks (tiny asset-graph orchestrator, partitions, backfills, sensors, dbt graph, blast radius, Dagster bridge, capstone, failure modes)."

### Phase 3: Studio

- **P018 Write `orchestration-studio.html`.** Mirrors `indexing-studio.html`: header, hero with two signal cards, three lab sections, notebook-path section, footer. Cross-links present. **Refs:** F009-F011, S002, S007.
- **P019 Write `site-assets/orchestration-studio.css`.** Reuses night-sky tokens; adds run-state colors (idle, running, materialized, stale, failed, skipped) and DAG/grid layout styles. **Refs:** N003, N005.
- **P020 Write `site-assets/orchestration-studio.js`.** Lab 1 materializer wave, Lab 2 backfill grid, Lab 3 blast radius. Reveal observer. **Refs:** F009-F011, E005.
- **P021 Verify render.** Serve locally, screenshot the studio in a headless browser, confirm three labs draw and animate, no console errors.
- **K003 Phase 3 checkpoint.** Studio renders; three labs interactive; no broken local links.
- **X003 Commit.** "Add Chapter 15 orchestration studio (asset-graph materializer, backfill grid, blast-radius explorer)."

### Phase 4: Site integration

- **P022 Update `index.html`.** Curriculum card 15, studio gallery card with an SVG preview, bumped counters (notebooks, chapters, studios). **Refs:** F012, S007.
- **P023 Cross-link existing studios.** Add an Orchestration nav link to `embeddings-bridge.html`, `ranking-lab.html`, `fractals-governance.html`, `fractal-graphs.html`, `governance-studio.html`, `indexing-studio.html`. **Refs:** F012.
- **P024 Update root README.md.** Mark Chapter 15 in the roadmap as shipped with the studio live, bump notebook/studio counts, add to Repository Shape and Tracks, add a Quick Start option, add the chapter to the structure listing. **Refs:** S007.
- **P025 Run CI scripts locally.** `python3 scripts/validate_notebooks.py` and `python3 scripts/check_site_links.py` both exit 0.
- **K004 Phase 4 checkpoint.** Counters consistent, all local links resolve, both CI scripts clean.
- **X004 Commit + push.** "Wire Chapter 15 into the site (index, README, cross-links across six studio pages)." Push to `origin/main`; confirm Actions CI green.

## W### File changes

| ID | Path | Action |
|---|---|---|
| W001 | `artifacts/tickets/CH-15-orchestration/spec.md` | Created |
| W002 | `artifacts/tickets/CH-15-orchestration/plan.md` | Created |
| W003 | `notebooks/15-orchestration/requirements.txt` | Created |
| W004 | `notebooks/15-orchestration/README.md` | Created |
| W005 | `scripts/generate_chapter_15_notebooks.py` | Created |
| W006-W014 | `notebooks/15-orchestration/15.0 … 15.8 *.ipynb` | Generated + executed |
| W015 | `orchestration-studio.html` | Created |
| W016 | `site-assets/orchestration-studio.css` | Created |
| W017 | `site-assets/orchestration-studio.js` | Created |
| W018 | `index.html` | Modified |
| W019-W024 | six existing `*studio*.html` / studio pages | Modified (nav cross-link) |
| W025 | `README.md` | Modified |

## K### Checkpoints summary

- **K001** Scaffolding lands; identity verified.
- **K002** Nine notebooks execute with outputs; V001-V005 pass; validator clean.
- **K003** Studio renders all three labs; screenshot verified; links resolve.
- **K004** Counters consistent; both CI scripts clean; Actions CI green after push.

## Anti-patterns to avoid

- **Z001 Becoming a Dagster tutorial.** The toy orchestrator is the spine. Dagster is one notebook (15.6), shown not run.
- **Z002 Pre-baked results.** Idempotency, skip-on-failure, and backfill no-ops must be demonstrated by rerunning real cells, not described.
- **Z003 Hiding the failure modes.** Notebook 15.8 is mandatory.
- **Z004 Design-system drift.** The studio reuses the night-sky tokens. New colors are limited to run states.
- **Z005 Vendor lock-in language.** Teach the apparatus, not one vendor's branding. The Dagster mapping is illustrative, with an Airflow/Prefect comparison paragraph.

## Open decisions (defaults from spec; override before P005)

- **Q001** Dagster as the production analogue. Default: yes.
- **Q002** 15.4 parses SQL structure only, no live dbt run. Default: yes.
- **Q003** Three labs, sensors covered in the notebooks not a fourth lab. Default: yes.
- **Q004** Generator script, not hand-authored notebooks. Default: yes.
