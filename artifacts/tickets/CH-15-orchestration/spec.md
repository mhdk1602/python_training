# CH-15 Orchestration as Asset Graphs: From Cron to Idempotent Materialization

**Owner:** Dineshkumar Malemapti Hari
**Status:** Draft (proceed to plan and implementation)
**Created:** 2026-06-14
**Connects to:** Chapter 9 (data quality, the existing `dbt/dbt_dq` project), Chapter 12 (lineage as a graph, blast-radius descriptors), the trading platform (Applied System A), and the roadmap entry in the root README ("Chapter 15: Orchestration as Asset Graphs").
**Roadmap line:** the first of the four production-infrastructure chapters proposed in the README roadmap (15 orchestration, 16 contracts and CDC, 17 lakehouse internals, 18 governance telemetry).

## Context

The curriculum has pipelines but no scheduler. Chapter 9 ships a dbt project, Chapter 10 builds a retrieval service, and the trading platform moves market data through Flask and Postgres, but nothing in the repo answers the question every data team hits in month two: what runs, in what order, when an upstream changes, and what happens when step four fails at 2am.

The default answer most teams reach for is cron plus a pile of scripts. That answer breaks in four predictable ways: it has no dependency awareness (script B runs whether or not script A succeeded), no partial recovery (one bad day means rerun everything), no lineage (nobody can say what feeds what), and no idempotency (rerunning double-counts). Modern orchestrators (Dagster, Airflow, Prefect, Temporal) exist to fix exactly these four failures.

This chapter teaches orchestration the way the rest of the repo teaches its hard topics: build the apparatus from first principles in pure Python, connect it to something real (the repo's own dbt project and the trading platform), then map it onto the production tool. The chosen production analogue is Dagster, because its software-defined-asset model treats orchestration as the materialization of a dependency graph of assets, which is the conceptually correct framing and the one that reuses the lineage vocabulary Chapter 12 already built.

**The bounded claim.** The chapter does not argue that you should write your own orchestrator, that Dagster is the only correct choice, or that asset-oriented orchestration beats task-oriented orchestration for every workload. It argues a narrower thing: orchestration is best understood as ordered, idempotent, observable materialization of an asset graph, and a 150-line pure-Python orchestrator is enough to make every core concept (topological execution, partitions, backfills, sensors, freshness, retries, blast radius) concrete and runnable on a laptop. Where the apparatus and the production tools fail, notebook 15.8 says so explicitly.

## S### Acceptance criteria

- **S001-clean-clone-runs.** A reader who clones the repo, creates a Python 3.10+ venv, and `pip install -r notebooks/15-orchestration/requirements.txt` can execute every notebook from 15.0 through 15.8 end-to-end on a laptop with no external services and no scheduler daemon.
- **S002-studio-renders.** Opening `orchestration-studio.html` directly from `file://` renders three working interactive labs with no backend.
- **S003-pure-python-spine.** The orchestrator that carries the chapter is built from the standard library plus NumPy/NetworkX/Matplotlib for analysis and drawing only. No Dagster, Airflow, or Prefect import is required to run any notebook.
- **S004-repo-tie-in.** Notebook 15.4 builds an asset graph from the repo's real `dbt/dbt_dq` models by parsing their `ref()` calls, and notebook 15.7 orchestrates the trading platform's own data flow. The chapter connects to code already in the repo, not a toy in isolation.
- **S005-honesty-notebook-included.** Notebook 15.8 names the failure modes explicitly. The chapter is not complete without it. It pairs with 12.7, 13.8, and 14.8.
- **S006-dagster-bridge-honest.** Notebook 15.6 maps every toy concept to the real Dagster API. Dagster code is shown as clearly-labelled illustration that requires `pip install dagster`; it is not executed, and the notebook says so.
- **S007-pages-integration.** The studio is reachable from `index.html` (curriculum card, studio gallery card, counters), the six existing studio pages cross-link to it, and the README reflects Chapter 15 with the same treatment as Chapters 10-14.
- **S008-identity.** Every commit uses the `Dinesh Hari / mhdk.dinesh@gmail.com` identity with zero AI co-author trailers. Push uses the `github.com-personal` SSH remote.
- **S009-ci-green.** The repository CI (notebook validation, site-link check, rag-lab tests) stays green after the chapter lands. The new notebooks are well-formed; the new studio's local links resolve.

## F### Functional requirements

### Notebook spine (8 + a closer = 9 notebooks)

- **F001 15.0 From Cron to Asset Graphs.** Frames the chapter. Names the four failures of cron-plus-scripts (no dependency awareness, no partial recovery, no lineage, no idempotency). Introduces the asset abstraction: a thing that gets materialized, defined by its upstream dependencies and a compute function. Sets the bounded claim.
- **F002 15.1 A Tiny Asset Graph From Scratch.** Build `Asset` and `AssetGraph` in pure Python. Topological materialization in dependency order, passing upstream results downstream. Cycle detection raises a clear error. Visualize a four-asset graph (raw → staged → marts → report) with NetworkX. Asserts that an asset never runs before its upstreams.
- **F003 15.2 Partitions and Backfills.** Add partition keys (dates) and a `MaterializationLog`. A partitioned asset materializes once per partition. `backfill(asset, partitions)` runs only the missing partitions and no-ops on the ones already recorded (idempotency). Show a seven-day backfill, then a rerun that does nothing.
- **F003b 15.3 Sensors and Freshness.** A `Sensor` polls a condition (a new file landing) on a simulated clock and triggers materialization. A `FreshnessPolicy` marks an asset stale when its newest materialization is older than a threshold. Simulate time advancing; show staleness detected and resolved.
- **F004 15.4 Wrapping the Repo's dbt Project as Assets.** Parse the real `dbt/dbt_dq/models/*.sql` files for `ref()` calls, build an asset graph automatically (one node per dbt model), and materialize it in the correct order. Falls back to embedded sample SQL if the dbt directory is not found. Reuses the Chapter 12 lineage vocabulary explicitly.
- **F005 15.5 Failure, Retries, and Blast Radius.** Inject a failure in one asset. Show that downstream descendants are skipped, not run on missing inputs. Add a `RetryPolicy` (N attempts with backoff). Compute the blast radius of a failed asset as its set of downstream descendants, reusing the Chapter 12 blast-radius framing directly.
- **F006 15.6 From Our Toy to Dagster.** Map every concept built so far to Dagster's real API: `@asset`, asset dependencies, `PartitionsDefinition`, `@sensor`, `FreshnessPolicy`, `RetryPolicy`, `Definitions`. Side-by-side cells: our toy code on the left idea, the Dagster equivalent on the right. Dagster code is illustration only, clearly marked, not executed.
- **F007 15.7 Capstone: Orchestrate the Trading Platform's Data.** Build an asset graph for the repo's own data flow: market-data ingest → price history → portfolio positions → daily analytics → the Ask Warren context payload. Use the toy orchestrator with synthetic data. Produce a materialization plan, run it, and show a partitioned backfill over a trading week.
- **F008 15.8 When the Schedule Lies.** Names four failure modes with adversarial demonstrations:
  1. Silent partial failure: a partition produces empty output but the run reports success because the asset "completed".
  2. Sensor storms: a misconfigured sensor fires every poll and saturates the executor.
  3. Backfill thundering herd: backfilling a year of daily partitions at once saturates the warehouse.
  4. Retry masking a data bug: automatic retries turn a deterministic data-quality failure into wasted compute and a delayed alert.
  Pairs explicitly with 12.7, 13.8, and 14.8.

### Studio page (orchestration-studio.html)

- **F009 Lab 1: Asset Graph Materializer.** An interactive DAG (the trading-platform asset graph). The reader clicks Materialize and watches a topological wave sweep through: each node turns from idle to running to materialized in strict dependency order, with a visible delay per node. A node cannot start before all its upstreams are materialized. Reset re-arms the graph. Speed slider. The intuition: orchestration is ordered materialization.
- **F010 Lab 2: Backfill and Partitions.** A grid of partitions (assets on the vertical axis, dates on the horizontal). Cells are materialized (filled) or missing (empty). The reader selects a date range and clicks Backfill; only the missing cells fill, in dependency order, top to bottom per date. A second Backfill no-ops, demonstrating idempotency. A counter shows partitions materialized this run versus skipped.
- **F011 Lab 3: Failure Blast Radius.** The same DAG. The reader clicks a node to fail it. The failed node turns red, its downstream descendants turn grey (skipped), and a side panel reports the blast radius (count and names of skipped assets). A retry toggle shows N attempts before the failure propagates. This ties directly to 15.5 and the Chapter 12 blast-radius descriptor.
- **F012 Site integration.** Wired into `index.html` (curriculum card 15, studio gallery card, bumped counters), a new entry in the studio gallery, and a cross-link in the primary nav of the six existing studio pages.

### Generator script

- **F013 scripts/generate_chapter_15_notebooks.py.** A single deterministic Python script emits all nine notebooks, mirroring the Chapter 12-14 generators, with the same `markdown_cell` / `code_cell` helpers and notebook envelope.

## N### Non-functional requirements

- **N001 Python 3.10+ compatibility.** Type hints kept simple; no syntax newer than 3.10.
- **N002 Dependency surface.** `numpy`, `networkx`, `matplotlib`, `pandas`, `jupyter`. All pure-pip, no native build steps, no daemon.
- **N003 Studio independence.** Vanilla JS, no backend, no npm. Reuses the night-sky design tokens from `indexing-studio.css`.
- **N004 Voice.** Bounded claims, named failure modes, named audiences. No marketing language. First person where natural.
- **N005 Visual continuity.** The studio reuses the existing color tokens (`--bg #04060d`, Syne + Manrope) and adds only run-state colors (idle, running, materialized, stale, failed, skipped). It does not introduce a new design system.
- **N006 Runs offline and fast.** Every notebook executes in under ~15 seconds total on a laptop. No network calls.
- **N007 Idempotency is demonstrated, not asserted.** Wherever the chapter claims a rerun is safe, a cell reruns it and shows the no-op.

## E### Edge cases

- **E001 dbt directory missing.** Notebook 15.4 detects the absent `dbt/dbt_dq/models` directory and falls back to embedded sample SQL with the same `ref()` structure, printing what the reader is missing.
- **E002 Cyclic graph.** `AssetGraph.topological_order()` detects a cycle and raises a clear `ValueError` naming the assets in the cycle. Asserted in 15.1.
- **E003 Backfill over an already-complete range.** `backfill` on a fully-materialized range produces zero new materializations and says so. Asserted in 15.2.
- **E004 Failure with no downstream.** Blast radius of a leaf asset is the empty set. Handled in 15.5 and Lab 3.
- **E005 Studio degenerate input.** Lab 2 with an empty date range and Lab 3 failing a leaf node both show a neutral state with a prompt rather than an error.
- **E006 Retry exhaustion.** A retry policy that exhausts all attempts marks the asset failed and propagates; the chapter does not silently swallow it.

## C### Components

- **C001 Asset.** Dataclass: name, deps (list of upstream names), compute (callable on a dict of upstream values), optional partitioned flag. Reused across 15.1-15.8.
- **C002 AssetGraph.** Holds assets, computes topological order (Kahn's algorithm with cycle detection), materializes a target set with all upstreams.
- **C003 MaterializationLog.** Records (asset, partition) pairs; answers `is_materialized`. Drives idempotency in 15.2 and backfills.
- **C004 Sensor / FreshnessPolicy.** Polling trigger on a simulated clock and a staleness check. Used in 15.3.
- **C005 RetryPolicy / run_with_retries.** N attempts with backoff; surfaces exhaustion. Used in 15.5 and 15.8.
- **C006 dbt ref parser.** Regex over `.sql` files extracting `ref('model')` edges. Used in 15.4.
- **C007 OrchestrationStudio.** Three lab modules in `site-assets/orchestration-studio.js`.

## A### APIs and data shapes

- **A001 Asset API.** `Asset(name, deps, compute, partitioned=False)`; `compute(inputs: dict) -> value`, where `inputs` is keyed by upstream asset name.
- **A002 Graph API.** `AssetGraph().add(asset)`, `.topological_order() -> list[str]`, `.materialize(targets=None, log=None, partition=None) -> dict`.
- **A003 Backfill API.** `backfill(graph, target, partitions: list, log) -> dict` reporting materialized vs skipped per partition.
- **A004 Blast radius API.** `blast_radius(graph, failed: str) -> set[str]` returns downstream descendants.

## M### Data models

- **M001 Toy asset graph.** Four to six named assets forming a small DAG (raw_events → stg_events → daily_marts → report), used throughout 15.1-15.3.
- **M002 dbt model graph.** Parsed from `dbt/dbt_dq/models/*.sql`: `nyc_taxi_data`, `stg_nyc_taxi`, `nyc_taxi_transform`, `calendar`. Fallback: embedded equivalents.
- **M003 Trading-platform graph.** market_data → price_history → positions → daily_pnl → warren_context, partitioned by trading day, used in 15.7.
- **M004 Synthetic market frame.** A small pandas DataFrame of synthetic OHLC bars for a handful of tickers across a trading week, generated deterministically.

## V### Validation rules

- **V001 Topological correctness.** For every materialized asset, all its upstreams appear earlier in the run order. Asserted in 15.1.
- **V002 Cycle rejection.** A graph with a back-edge raises `ValueError` naming the cycle. Asserted in 15.1.
- **V003 Idempotency.** Re-materializing a recorded (asset, partition) is a no-op; the second backfill over a complete range reports zero new work. Asserted in 15.2.
- **V004 Skip-on-failure.** When an upstream fails, its downstream descendants are recorded as skipped, never materialized on missing inputs. Asserted in 15.5.
- **V005 Blast-radius equals descendants.** `blast_radius(g, x)` equals the set of nodes reachable from `x` in the DAG. Asserted in 15.5 against a NetworkX descendants computation.

## D### Dependencies

- Chapter 12 lineage and blast-radius framing (referenced and reused conceptually, not duplicated).
- The repo's `dbt/dbt_dq` project (read in 15.4).
- The trading-platform data shapes (modelled synthetically in 15.7).
- The night-sky studio palette from `indexing-studio.css` (reused).

## R### Risks

- **R001 Notebook execution path fragility.** 15.4 reads files relative to the repo root. Mitigated by walking up from the notebook directory to find `dbt/dbt_dq`, with an embedded fallback (E001).
- **R002 Dagster API drift.** 15.6 shows Dagster code that is not executed. Mitigated by labelling it as illustrative and pinning the described API to the stable software-defined-asset surface, not bleeding-edge features.
- **R003 Studio animation performance.** A DAG with animated state transitions is light (under 20 nodes). No risk at this scale; capped well below any performance concern.
- **R004 Scope creep into a real scheduler.** The chapter must resist becoming a Dagster tutorial. The toy orchestrator is the spine; Dagster is one notebook. Enforced by Z-rules in the plan.

## Q### Open questions (default proposals; override before P006)

- **Q001** Production analogue: Dagster, Airflow, or Prefect? *Default: Dagster, because the software-defined-asset model matches the asset-graph framing and reuses Chapter 12's lineage vocabulary. Airflow and Prefect get a one-paragraph comparison in 15.6.*
- **Q002** Should 15.4 require a live dbt run? *Default: no. Parse the SQL for structure only; running dbt needs a warehouse and breaks S001. A final cell points readers to `dbt ls --output json` for the production path.*
- **Q003** Should the studio include a fourth lab on sensors/freshness? *Default: no. Three labs is the cap from prior chapters. Sensors get full treatment in notebook 15.3.*
- **Q004** Should the chapter ship a generator script like 12-14, or hand-authored notebooks? *Default: generator, for consistency and reproducibility with the rest of the repo.*
