# Chapter 15: Orchestration as Asset Graphs (From Cron to Idempotent Materialization)

**Audience:** data engineers who have a pile of scripts on a cron schedule and have started to feel the pain. **Prerequisites:** comfort with Python functions and dictionaries, a little NetworkX, and a willingness to think about a pipeline as a graph rather than a sequence. No prior orchestrator experience assumed.

## What this chapter argues

The curriculum has pipelines but no scheduler. Chapter 9 ships a dbt project, Chapter 10 builds a retrieval service, and the trading platform moves market data through Flask and Postgres. Nothing so far answers the question every team hits in month two: what runs, in what order, when an upstream changes, and what happens when step four fails at 2am.

Cron plus a pile of scripts is the default answer, and it breaks in four predictable ways:

1. **No dependency awareness.** Script B runs on its own schedule whether or not script A succeeded.
2. **No partial recovery.** One bad day means rerun everything from the top.
3. **No lineage.** Nobody can say what feeds what without reading every script.
4. **No idempotency.** Rerunning double-counts.

Modern orchestrators (Dagster, Airflow, Prefect, Temporal) exist to fix exactly these four failures. This chapter teaches the idea the way the rest of the repo teaches its hard topics: build a tiny orchestrator from first principles in pure Python, connect it to real code already in this repo, then map it onto the production tool.

The production analogue is Dagster, because its software-defined-asset model frames orchestration as the materialization of a dependency graph of assets. That framing is the correct one, and it reuses the lineage vocabulary Chapter 12 already built.

**The bounded claim.** I am not arguing you should write your own orchestrator, that Dagster is the only right choice, or that asset-oriented beats task-oriented orchestration for every workload. The claim is narrower: orchestration is best understood as ordered, idempotent, observable materialization of an asset graph, and about 150 lines of pure Python make every core concept concrete and runnable on a laptop. Where the apparatus and the production tools fail, notebook 15.8 says so.

## Notebook spine

| Notebook | Title | Purpose |
|---|---|---|
| 15.0 | From Cron to Asset Graphs | Frames the chapter: the four failures of cron, the asset abstraction, the bounded claim. |
| 15.1 | A Tiny Asset Graph From Scratch | `Asset` and `AssetGraph` in pure Python; topological materialization; cycle detection; NetworkX visualization. |
| 15.2 | Partitions and Backfills | Partition keys, a materialization log, idempotent backfills that skip work already done. |
| 15.3 | Sensors and Freshness | A polling sensor on a simulated clock and a freshness policy that detects staleness. |
| 15.4 | Wrapping the Repo's dbt Project as Assets | Parse the real `dbt/dbt_dq` models for `ref()` edges and orchestrate them; bridges to Chapter 12 lineage. |
| 15.5 | Failure, Retries, and Blast Radius | Skip-on-failure, a retry policy, and the blast-radius descriptor from Chapter 12. |
| 15.6 | From Our Toy to Dagster | Every toy concept mapped to the real Dagster API; Airflow and Prefect compared in a paragraph. |
| 15.7 | Capstone: Orchestrate the Trading Platform's Data | An asset graph for the repo's own data flow, partitioned by trading day. |
| 15.8 | When the Schedule Lies | Four failure modes named and demonstrated; pairs with 12.7, 13.8, 14.8. |

## How to run

```bash
cd notebooks/15-orchestration
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

Notebooks regenerate from the generator script:

```bash
python scripts/generate_chapter_15_notebooks.py
```

Outputs are embedded after execution. The execution path used during development was:

```bash
for nb in notebooks/15-orchestration/15.*.ipynb; do
  jupyter nbconvert --to notebook --execute --inplace --allow-errors "$nb"
done
```

Every notebook runs offline in seconds. There is no scheduler daemon to install and no warehouse to connect to. Notebook 15.4 reads the repo's dbt models if it can find them and falls back to embedded sample SQL otherwise.

## How this fits the public site

The interactive surface lives at `orchestration-studio.html` (top level) and reuses the night-sky idiom of `indexing-studio.html`. The studio implements three labs:

- **Asset Graph Materializer.** Click Materialize and watch a topological wave sweep the DAG; a node cannot start before its upstreams finish.
- **Backfill and Partitions.** Select a date range, backfill the missing partition cells in dependency order, then watch a second backfill no-op.
- **Failure Blast Radius.** Fail a node and watch its downstream descendants get skipped; a panel reports the blast radius.

The studio is vanilla JS, so it works directly from `file://` with no backend.

## Citation

Cite this chapter as part of the repository:

> Malemapti Hari, D. (2026). *Data Engineering with Python: Project-First Training Repository, Chapter 15: Orchestration as Asset Graphs*. https://github.com/mhdk1602/python_training

The asset-graph framing and the blast-radius descriptor connect to:

> Chapter 12 of this repository (Fractal Graphs): lineage as a graph and structural blast-radius ranking.

The production tool the chapter maps onto:

> Dagster: software-defined assets. https://dagster.io
