"""Generate the nine Chapter 15 (Orchestration as Asset Graphs) notebooks.

Run from the repo root:

    python3 scripts/generate_chapter_15_notebooks.py

Mirrors the Chapter 12-14 generators. Notebooks are written without outputs;
embed outputs separately via:

    for nb in notebooks/15-orchestration/15.*.ipynb; do
      jupyter nbconvert --to notebook --execute --inplace --allow-errors "$nb"
    done
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "notebooks" / "15-orchestration"


def markdown_cell(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }


def code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.strip("\n").splitlines(keepends=True),
    }


def write_notebook(filename: str, cells: list) -> None:
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.10"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path = OUT_DIR / filename
    path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)} ({len(cells)} cells)")


# ---------------------------------------------------------------------------
# The orchestrator core, consolidated. Notebooks 15.4+ paste this one cell so
# they stand alone. Notebooks 15.1-15.3 build the same thing incrementally.
# No triple-quoted strings inside, so the generator's own strings stay intact.
# ---------------------------------------------------------------------------

CORE = r"""# The tiny orchestrator we build across 15.1-15.3, collected into one cell.
from collections import deque
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class Asset:
    name: str
    deps: list
    compute: Callable
    partitioned: bool = False


class AssetGraph:
    def __init__(self):
        self.assets = {}

    def add(self, asset):
        self.assets[asset.name] = asset
        return self

    def _downstream(self):
        down = {n: [] for n in self.assets}
        for n, a in self.assets.items():
            for d in a.deps:
                if d in down:
                    down[d].append(n)
        return down

    def topological_order(self):
        indeg = {n: 0 for n in self.assets}
        for n, a in self.assets.items():
            for d in a.deps:
                if d in indeg:
                    indeg[n] += 1
        down = self._downstream()
        q = deque(sorted(n for n, k in indeg.items() if k == 0))
        order = []
        while q:
            n = q.popleft()
            order.append(n)
            for m in sorted(down[n]):
                indeg[m] -= 1
                if indeg[m] == 0:
                    q.append(m)
        if len(order) != len(self.assets):
            stuck = sorted(n for n in self.assets if n not in order)
            raise ValueError("cycle detected among assets: " + ", ".join(stuck))
        return order

    def _needed(self, targets):
        need = set()
        stack = list(targets)
        while stack:
            n = stack.pop()
            if n in need or n not in self.assets:   # ignore refs outside the graph
                continue
            need.add(n)
            stack.extend(self.assets[n].deps)
        return need

    def materialize(self, targets=None, log=None, partition=None, verbose=True):
        order = self.topological_order()
        if targets is not None:
            need = self._needed(targets)
            order = [n for n in order if n in need]
        results = {}
        for n in order:
            tag = " [" + str(partition) + "]" if partition is not None else ""
            if log is not None and log.is_materialized(n, partition):
                results[n] = log.value(n, partition)
                if verbose:
                    print("  skip   " + n + tag + " (already materialized)")
                continue
            inputs = {d: results.get(d) for d in self.assets[n].deps}
            value = self.assets[n].compute(inputs)
            results[n] = value
            if log is not None:
                log.record(n, partition, value)
            if verbose:
                print("  build  " + n + tag)
        return results


class MaterializationLog:
    def __init__(self):
        self.store = {}

    def is_materialized(self, name, partition=None):
        return (name, partition) in self.store

    def record(self, name, partition=None, value=None):
        self.store[(name, partition)] = value

    def value(self, name, partition=None):
        return self.store[(name, partition)]


def backfill(graph, target, partitions, log, verbose=True):
    report = {"materialized": [], "skipped": []}
    order = [n for n in graph.topological_order() if n in graph._needed([target])]
    for p in partitions:
        for n in order:
            if log.is_materialized(n, p):
                report["skipped"].append((n, p))
                continue
            inputs = {d: (log.value(d, p) if log.is_materialized(d, p) else None)
                      for d in graph.assets[n].deps}
            log.record(n, p, graph.assets[n].compute(inputs))
            report["materialized"].append((n, p))
    return report


def blast_radius(graph, failed):
    down = graph._downstream()
    seen, stack = set(), list(down[failed])
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        stack.extend(down[n])
    return seen


@dataclass
class RetryPolicy:
    max_attempts: int = 1


def materialize_with_failures(graph, failing=None, retry=None, verbose=True):
    failing = failing or {}
    retry = retry or RetryPolicy()
    order = graph.topological_order()
    status, results, attempts_used = {}, {}, {}
    for n in order:
        if any(status.get(d) in ("failed", "skipped") for d in graph.assets[n].deps):
            status[n] = "skipped"
            if verbose:
                print("  skip    " + n + " (upstream failed)")
            continue
        attempts, ok = 0, False
        while attempts < retry.max_attempts:
            attempts += 1
            if attempts <= failing.get(n, 0):
                if verbose:
                    print("  retry   " + n + " attempt " + str(attempts) + " failed")
                continue
            ok = True
            break
        attempts_used[n] = attempts
        if ok:
            inputs = {d: results.get(d) for d in graph.assets[n].deps}
            results[n] = graph.assets[n].compute(inputs)
            status[n] = "materialized"
            if verbose:
                print("  build   " + n + " (attempt " + str(attempts) + ")")
        else:
            status[n] = "failed"
            if verbose:
                print("  FAIL    " + n + " (exhausted " + str(retry.max_attempts) + " attempts)")
    return status, results, attempts_used


print("orchestrator core ready:", len([Asset, AssetGraph, MaterializationLog,
      backfill, blast_radius, RetryPolicy, materialize_with_failures]), "building blocks")
"""


# ===========================================================================
# 15.0 From Cron to Asset Graphs
# ===========================================================================

NB_0 = [
    markdown_cell(
        "> **Chapter 15, Part 0** | Engineering lens. **Focus:** why cron-plus-scripts fails in four predictable ways, and why the fix is to model a pipeline as a graph of assets rather than a sequence of tasks."
    ),
    markdown_cell(
        """# From Cron to Asset Graphs

The repo has pipelines but no scheduler. Chapter 9 ships a dbt project, Chapter 10 builds a retrieval service, and the trading platform moves market data through Flask and Postgres. None of it answers the question every team hits in month two: what runs, in what order, when an upstream changes, and what happens when step four fails at 2am.

The default answer is cron plus a pile of scripts. It breaks in four predictable ways.

1. **No dependency awareness.** `0 2 * * *  python build_marts.py` runs at 2am whether or not the 1am ingest succeeded. The marts get built on yesterday's data and nobody notices for a week.
2. **No partial recovery.** One bad partition means rerun the whole pipeline from the top, because the scripts have no idea which days are already done.
3. **No lineage.** Ask "what feeds the executive dashboard" and the only honest answer is "read all forty scripts."
4. **No idempotency.** Rerun the ingest and you double-count, because the script appends instead of replacing.

Modern orchestrators (Dagster, Airflow, Prefect, Temporal) exist to fix exactly these four failures. This chapter teaches the idea the way the rest of the repo teaches its hard topics: build the apparatus from first principles in pure Python, connect it to real code in this repo, then map it onto the production tool.

## The shift: tasks to assets

The older mental model is **tasks**: a task is a thing you run. Airflow's original DAG is a graph of tasks. The newer mental model, the one Dagster is built on, is **assets**: an asset is a thing that exists, defined by what it depends on and how to compute it. You do not "run a task"; you "materialize an asset", which means producing the current version of it from its upstreams.

The asset framing is the one I use in this chapter because it reuses a vocabulary the repo already built. In Chapter 12 a lineage graph was a DAG of data objects with a structural blast radius. An asset graph is the same DAG, made executable. Materialize it in topological order and you have orchestration."""
    ),
    code_cell(
        """# An asset, at its smallest: a name, the upstreams it needs, and how to compute it.
from dataclasses import dataclass
from typing import Callable


@dataclass
class Asset:
    name: str
    deps: list          # names of upstream assets
    compute: Callable   # compute(inputs: dict) -> value, inputs keyed by dep name


# A four-asset pipeline: raw events -> a staged table -> daily marts -> a report.
raw = Asset("raw_events", [], lambda i: list(range(100)))
staged = Asset("stg_events", ["raw_events"], lambda i: [x for x in i["raw_events"] if x % 2 == 0])
marts = Asset("daily_marts", ["stg_events"], lambda i: {"rows": len(i["stg_events"])})
report = Asset("report", ["daily_marts"], lambda i: f"report: {i['daily_marts']['rows']} rows")

for a in (raw, staged, marts, report):
    deps = ", ".join(a.deps) if a.deps else "(none)"
    print(f"{a.name:14s} <- {deps}")"""
    ),
    markdown_cell(
        """That print is already a lineage listing, the thing cron could never give you. Each asset names its upstreams, so the dependency structure lives in the data, not in forty scripts and one engineer's memory.

What it does not yet do is run anything in the right order, skip work already done, recover from a failure, or stay safe under a rerun. Those are the next four notebooks.

## The bounded claim

I am not arguing you should write your own orchestrator, that Dagster is the only right choice, or that asset-oriented beats task-oriented orchestration for every workload. The claim is narrower: orchestration is best understood as ordered, idempotent, observable materialization of an asset graph, and about 150 lines of pure Python make every core concept concrete and runnable on a laptop.

## The chapter spine

| Notebook | What it builds |
|---|---|
| 15.0 (this one) | The four failures of cron; the asset abstraction; the bounded claim. |
| 15.1 | `Asset` and `AssetGraph`; topological materialization; cycle detection. |
| 15.2 | Partitions and idempotent backfills. |
| 15.3 | Sensors on a simulated clock and freshness policies. |
| 15.4 | The repo's real dbt project, parsed into an asset graph. |
| 15.5 | Failure, retries, and the Chapter 12 blast radius. |
| 15.6 | Every concept mapped to the real Dagster API. |
| 15.7 | Capstone: the trading platform's data, orchestrated. |
| 15.8 | When the schedule lies: four failure modes. |

## Three audiences

- **The engineer with a cron pile** who has felt all four failures and wants the mental model that fixes them. By the end of 15.2 you will have idempotent backfills in under a hundred lines.
- **The dbt user** who runs `dbt build` by hand and wonders what a scheduler adds. By the end of 15.4 your own dbt models will be an asset graph.
- **The platform engineer** evaluating Dagster. By the end of 15.6 you will see exactly which of your toy concepts each Dagster primitive replaces, and by 15.8 where it still bites."""
    ),
]


# ===========================================================================
# 15.1 A Tiny Asset Graph From Scratch
# ===========================================================================

NB_1 = [
    markdown_cell(
        "> **Chapter 15, Part 1** | Engineering lens. **Focus:** build `AssetGraph`, materialize it in dependency order, and make a cycle fail loudly."
    ),
    markdown_cell(
        """# A Tiny Asset Graph From Scratch

An orchestrator's first job is to run things in the right order. "Right order" means: never materialize an asset before all of its upstreams are materialized. That is a topological sort of the dependency DAG, and it is the whole of this notebook.

We build three things:

1. `AssetGraph`, a container of assets.
2. `topological_order()`, which returns a safe run order or raises if the graph has a cycle.
3. `materialize()`, which runs the assets in that order and threads each asset's outputs into its downstreams."""
    ),
    code_cell(
        """from collections import deque
from dataclasses import dataclass
from typing import Callable


@dataclass
class Asset:
    name: str
    deps: list
    compute: Callable


class AssetGraph:
    def __init__(self):
        self.assets = {}

    def add(self, asset):
        self.assets[asset.name] = asset
        return self

    def _downstream(self):
        down = {n: [] for n in self.assets}
        for n, a in self.assets.items():
            for d in a.deps:
                if d in down:
                    down[d].append(n)
        return down

    def topological_order(self):
        # Kahn's algorithm. Start from assets with no upstreams, peel inward.
        indeg = {n: 0 for n in self.assets}
        for n, a in self.assets.items():
            for d in a.deps:
                if d in indeg:
                    indeg[n] += 1
        down = self._downstream()
        q = deque(sorted(n for n, k in indeg.items() if k == 0))
        order = []
        while q:
            n = q.popleft()
            order.append(n)
            for m in sorted(down[n]):
                indeg[m] -= 1
                if indeg[m] == 0:
                    q.append(m)
        if len(order) != len(self.assets):
            stuck = sorted(n for n in self.assets if n not in order)
            raise ValueError("cycle detected among assets: " + ", ".join(stuck))
        return order

    def materialize(self, verbose=True):
        results = {}
        for n in self.topological_order():
            inputs = {d: results.get(d) for d in self.assets[n].deps}
            results[n] = self.assets[n].compute(inputs)
            if verbose:
                print("  build  " + n)
        return results


print("AssetGraph defined")"""
    ),
    markdown_cell(
        "Build the same four-asset pipeline from 15.0, but now wired into a graph that knows how to run it. The marts asset depends on staging, which depends on raw; the report sits at the bottom."
    ),
    code_cell(
        """g = AssetGraph()
g.add(Asset("raw_events", [], lambda i: list(range(100))))
g.add(Asset("stg_events", ["raw_events"], lambda i: [x for x in i["raw_events"] if x % 2 == 0]))
g.add(Asset("daily_marts", ["stg_events"], lambda i: {"rows": len(i["stg_events"])}))
g.add(Asset("report", ["daily_marts"], lambda i: f"{i['daily_marts']['rows']} rows kept"))

order = g.topological_order()
print("run order:", " -> ".join(order))
print()
results = g.materialize()
print()
print("report says:", results["report"])"""
    ),
    markdown_cell(
        """## Validation V001: an asset never runs before its upstreams

The run order is only correct if every asset appears after all of its dependencies. We assert it rather than eyeball it."""
    ),
    code_cell(
        """position = {name: i for i, name in enumerate(order)}
for name, asset in g.assets.items():
    for dep in asset.deps:
        assert position[dep] < position[name], f"{dep} ran after {name}"
print("V001 holds: every asset runs after its upstreams")"""
    ),
    markdown_cell(
        """## Validation V002: a cycle must fail loudly

The worst orchestrator failure is the silent one. If two assets depend on each other, there is no safe order, and the scheduler must say so instead of looping forever or picking an arbitrary order. We add a back-edge and confirm the error names the assets involved."""
    ),
    code_cell(
        """bad = AssetGraph()
bad.add(Asset("a", ["c"], lambda i: 1))
bad.add(Asset("b", ["a"], lambda i: 2))
bad.add(Asset("c", ["b"], lambda i: 3))   # c <- b <- a <- c is a cycle

try:
    bad.topological_order()
except ValueError as err:
    print("rejected as expected:", err)"""
    ),
    markdown_cell(
        "## See the graph\n\nA picture makes the dependency structure obvious. NetworkX draws the DAG; the left-to-right layering is exactly the materialization order."
    ),
    code_cell(
        """import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()
for n, a in g.assets.items():
    G.add_node(n)
    for d in a.deps:
        G.add_edge(d, n)

layer = {n: i for i, n in enumerate(order)}
pos = {n: (layer[n], -0.0) for n in G.nodes}
# spread nodes vertically a touch so labels do not collide
for i, n in enumerate(order):
    pos[n] = (i, (i % 2) * 0.4 - 0.2)

fig, ax = plt.subplots(figsize=(9, 2.6))
nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#7c5cff", width=2,
                       arrowsize=18, node_size=2600)
nx.draw_networkx_nodes(G, pos, ax=ax, node_color="#0a0f1e",
                       edgecolors="#62e6ff", linewidths=2, node_size=2600)
nx.draw_networkx_labels(G, pos, ax=ax, font_color="#e9edfb", font_size=9)
ax.set_title("asset graph, drawn in materialization order", color="#333", fontsize=11)
ax.axis("off")
plt.tight_layout()
plt.show()"""
    ),
    markdown_cell(
        "That is orchestration in one notebook: a graph, a safe order, and a run. Everything from here adds the properties a real scheduler needs. Next: partitions and backfills, so a rerun does not redo work that is already done."
    ),
]


# ===========================================================================
# 15.2 Partitions and Backfills
# ===========================================================================

NB_2 = [
    markdown_cell(
        "> **Chapter 15, Part 2** | Engineering lens. **Focus:** partition assets by date, record what is materialized, and make backfills idempotent so a rerun is a no-op."
    ),
    markdown_cell(
        """# Partitions and Backfills

Real pipelines do not materialize one giant table; they materialize one slice per day (or per hour, per region, per tenant). Each slice is a **partition**. The two properties that matter:

- **Backfill**: materialize a range of past partitions that are missing.
- **Idempotency**: materializing a partition that already exists does nothing. Rerun the backfill and it is a no-op.

Cron has neither. It reran everything, every time, and double-counted. We fix both with a materialization log: a record of which (asset, partition) pairs already exist."""
    ),
    code_cell(CORE),
    markdown_cell(
        """The log is the whole trick. `materialize` checks it before computing an asset, and skips anything already recorded. Build a partitioned pipeline and materialize a single day."""
    ),
    code_cell(
        """g = AssetGraph()
g.add(Asset("ingest", [], lambda i: 1, partitioned=True))
g.add(Asset("clean", ["ingest"], lambda i: 1, partitioned=True))
g.add(Asset("rollup", ["clean"], lambda i: 1, partitioned=True))

log = MaterializationLog()
print("materialize 2026-06-01:")
g.materialize(log=log, partition="2026-06-01")"""
    ),
    markdown_cell(
        "## Validation V003: idempotency\n\nMaterialize the same day again. Every asset should skip, because the log already has it. No compute runs, nothing double-counts."
    ),
    code_cell(
        """print("re-materialize the same day:")
g.materialize(log=log, partition="2026-06-01")"""
    ),
    markdown_cell(
        "## Backfill a week, then rerun it\n\n`backfill` walks a list of partitions and materializes only what is missing. Backfill a full week; every (asset, day) is new. Then backfill an overlapping range and watch most of it skip."
    ),
    code_cell(
        """week = [f"2026-06-0{d}" for d in range(1, 8)]   # 01..07
log2 = MaterializationLog()

report = backfill(g, "rollup", week, log2, verbose=False)
print(f"first backfill of {len(week)} days:")
print(f"  materialized: {len(report['materialized'])} (asset, day) pairs")
print(f"  skipped:      {len(report['skipped'])}")

# Now backfill days 05..10. Days 05-07 already exist; only 08-10 are new.
again = backfill(g, "rollup", [f"2026-06-0{d}" if d < 10 else "2026-06-10"
                               for d in range(5, 11)], log2, verbose=False)
print()
print("overlapping backfill of days 05..10:")
print(f"  materialized: {len(again['materialized'])} (the 3 genuinely new days x 3 assets)")
print(f"  skipped:      {len(again['skipped'])} (already done)")"""
    ),
    markdown_cell(
        "## The backfill heatmap\n\nA partition grid makes the state legible: assets down the side, days across the top, filled where materialized. This is the same view the studio's Lab 2 animates, and the same view Dagster shows in its asset catalog."
    ),
    code_cell(
        """import numpy as np
import matplotlib.pyplot as plt

assets = g.topological_order()
days = [f"2026-06-{d:02d}" for d in range(1, 11)]
grid = np.zeros((len(assets), len(days)))
for (name, part) in log2.store:
    if name in assets and part in days:
        grid[assets.index(name), days.index(part)] = 1

fig, ax = plt.subplots(figsize=(9, 2.4))
ax.imshow(grid, aspect="auto", cmap="BuPu", vmin=0, vmax=1)
ax.set_xticks(range(len(days)))
ax.set_xticklabels([d[-2:] for d in days])
ax.set_yticks(range(len(assets)))
ax.set_yticklabels(assets)
ax.set_xlabel("day of June 2026")
ax.set_title("materialized partitions (filled = done)", fontsize=11)
for spine in ax.spines.values():
    spine.set_visible(False)
plt.tight_layout()
plt.show()

print("days 08-10 were filled by the second backfill; 01-07 by the first.")"""
    ),
    markdown_cell(
        "Idempotent backfills are the single property that turns a fragile cron pile into something you can rerun without fear. Next: sensors, so the pipeline reacts to the world instead of waiting for a clock."
    ),
]


# ===========================================================================
# 15.3 Sensors and Freshness
# ===========================================================================

NB_3 = [
    markdown_cell(
        "> **Chapter 15, Part 3** | Engineering lens. **Focus:** trigger work when a condition becomes true (a sensor), and flag an asset as stale when it falls behind a freshness target."
    ),
    markdown_cell(
        """# Sensors and Freshness

A schedule says "run at 2am". A **sensor** says "run when the file lands". Sensors are how a pipeline reacts to the world instead of guessing when the world will be ready. A **freshness policy** is the other half: it tells you when an asset has fallen too far behind to trust.

Both need a notion of time. To keep the notebook deterministic and offline, we drive a simulated clock instead of `time.time()`. Nothing here sleeps; we just advance a counter and watch the sensor and the freshness check react."""
    ),
    code_cell(
        """from dataclasses import dataclass, field
from typing import Callable


class Clock:
    def __init__(self, t=0):
        self.t = t

    def tick(self, n=1):
        self.t += n
        return self.t


@dataclass
class Sensor:
    name: str
    condition: Callable   # condition(clock) -> bool
    on_fire: Callable     # on_fire(clock) -> None
    last_fired: object = None

    def poll(self, clock):
        if self.condition(clock):
            self.on_fire(clock)
            self.last_fired = clock.t
            return True
        return False


print("Sensor and Clock defined")"""
    ),
    markdown_cell(
        "A worked sensor: a file lands at tick 3 and again at tick 7. The sensor polls every tick and fires only when an unprocessed file is present. This is the polling loop every orchestrator runs under the hood."
    ),
    code_cell(
        """clock = Clock()
arrivals = {3, 7}          # ticks at which a new file appears
processed = set()
runs = []


def file_waiting(clk):
    return clk.t in arrivals and clk.t not in processed


def process_file(clk):
    processed.add(clk.t)
    runs.append(clk.t)


sensor = Sensor("new_file", file_waiting, process_file)

for _ in range(10):
    t = clock.t
    fired = sensor.poll(clock)
    print(f"  t={t}: " + ("FIRED -> materialized partition" if fired else "idle"))
    clock.tick()

print()
print("sensor fired at ticks:", runs)"""
    ),
    markdown_cell(
        """## Freshness: when is an asset too old?

A freshness policy sets a maximum age. If the newest materialization of an asset is older than that, the asset is **stale** and anything reading it is on thin ice. This is how a platform turns "the dashboard looks wrong" into an alert that fires before anyone opens the dashboard."""
    ),
    code_cell(
        """@dataclass
class FreshnessPolicy:
    max_age: int   # in clock ticks

    def is_stale(self, last_materialized, now):
        if last_materialized is None:
            return True
        return (now - last_materialized) > self.max_age


policy = FreshnessPolicy(max_age=4)
last = max(runs)            # asset last built at the sensor's final firing
print(f"asset last materialized at t={last}, policy allows age <= {policy.max_age}")
print()
for now in (last + 2, last + 4, last + 6):
    state = "STALE" if policy.is_stale(last, now) else "fresh"
    print(f"  at t={now} (age {now - last}): {state}")"""
    ),
    markdown_cell(
        "Sensors and freshness are the reactive half of orchestration. A scheduler that only runs on a clock is blind to whether its inputs actually arrived. Next: point the orchestrator at the repo's own dbt project and let it discover the graph for itself."
    ),
]


# ===========================================================================
# 15.4 Wrapping the Repo's dbt Project as Assets
# ===========================================================================

NB_4 = [
    markdown_cell(
        "> **Chapter 15, Part 4** | Engineering lens. **Focus:** parse the repo's real dbt models into an asset graph automatically, the same way Dagster's dbt integration does."
    ),
    markdown_cell(
        """# Wrapping the Repo's dbt Project as Assets

Chapter 9 of this repo ships a dbt project at `dbt/dbt_dq`. Its models reference each other with `ref('model_name')`. Those `ref()` calls *are* the dependency edges, which means we can build an asset graph from the SQL without running dbt at all. This is exactly what Dagster's `dagster-dbt` integration does: it reads the dbt manifest and turns each model into a software-defined asset.

We do the lightweight version: a regex over the `.sql` files. If the dbt directory is not present (someone copied just this folder), we fall back to embedded sample SQL with the same shape, so the notebook always runs."""
    ),
    code_cell(CORE),
    code_cell(
        """import re
from pathlib import Path

# Walk up from the notebook to find dbt/dbt_dq/models. Fall back to embedded SQL.
here = Path.cwd()
models_dir = None
for base in [here, *here.parents]:
    candidate = base / "dbt" / "dbt_dq" / "models"
    if candidate.exists():
        models_dir = candidate
        break

sources = {}
if models_dir is not None:
    for sql in sorted(models_dir.glob("*.sql")):
        sources[sql.stem] = sql.read_text(encoding="utf-8")
    print(f"read {len(sources)} dbt models from {models_dir}")
else:
    # Fallback: the same shape as the repo's models.
    sources = {
        "calendar": "select 1 as date_key",
        "stg_nyc_taxi": "select * from {{ ref('nyc_taxi_data') }}",
        "nyc_taxi_data": "select 1 as trip_id",
        "nyc_taxi_transform": ("select t.*, c.date_key "
                               "from {{ ref('stg_nyc_taxi') }} t "
                               "cross join {{ ref('calendar') }} c"),
    }
    print("dbt project not found; using embedded sample SQL")

print("models:", ", ".join(sorted(sources)))"""
    ),
    markdown_cell(
        "## From `ref()` calls to edges\n\nA dbt `ref('x')` inside model `y` means `y` depends on `x`. One regex extracts every edge. The result is a real dependency graph for the repo's own data-quality models."
    ),
    code_cell(
        """REF = re.compile(r"ref\\(\\s*['\\\"]([A-Za-z0-9_]+)['\\\"]\\s*\\)")

dbt_graph = AssetGraph()
for model, sql in sources.items():
    deps = list(dict.fromkeys(REF.findall(sql)))      # dedupe, preserve order
    dbt_graph.add(Asset(model, deps, (lambda i: {"ok": True})))

# Some refs point at seeds (taxi_zone_lookup) that are not model files.
# Add them as source assets so the graph is complete and safe to traverse.
known = set(dbt_graph.assets)
for model in list(dbt_graph.assets):
    for dep in dbt_graph.assets[model].deps:
        if dep not in known:
            dbt_graph.add(Asset(dep, [], (lambda i: {"seed": True})))
            known.add(dep)

for model in sorted(dbt_graph.assets):
    deps = dbt_graph.assets[model].deps
    print(f"{model:22s} <- {', '.join(deps) if deps else '(source)'}")

print()
print("safe build order:", " -> ".join(dbt_graph.topological_order()))"""
    ),
    markdown_cell(
        "Materializing this graph is `dbt build` in dependency order, minus the warehouse. Each asset's compute would run the model's SQL; here it just returns a marker so the notebook stays offline."
    ),
    code_cell(
        """print("materialize the dbt asset graph (offline stand-in for `dbt build`):")
dbt_graph.materialize()"""
    ),
    markdown_cell(
        """## Draw the dbt lineage\n\nThis is the Chapter 12 lineage graph, except every node is a dbt model the repo actually ships, and the edges came from parsing SQL. Orchestration and lineage are the same DAG seen from two angles: lineage asks "what feeds what", orchestration asks "in what order do I build it"."""
    ),
    code_cell(
        """import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()
for n, a in dbt_graph.assets.items():
    G.add_node(n)
    for d in a.deps:
        if d in dbt_graph.assets:
            G.add_edge(d, n)

order = dbt_graph.topological_order()
pos = {n: (order.index(n), (order.index(n) % 2) * 0.5 - 0.25) for n in G.nodes}

fig, ax = plt.subplots(figsize=(10, 3))
nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#7c5cff", width=2, arrowsize=16, node_size=3000)
nx.draw_networkx_nodes(G, pos, ax=ax, node_color="#0a0f1e", edgecolors="#ff9d2e",
                       linewidths=2, node_size=3000)
nx.draw_networkx_labels(G, pos, ax=ax, font_color="#e9edfb", font_size=8)
ax.set_title("dbt models as an asset graph (parsed from ref() calls)", fontsize=11)
ax.axis("off")
plt.tight_layout()
plt.show()"""
    ),
    markdown_cell(
        """In production you would not regex the SQL; you would read `target/manifest.json` after `dbt parse`, which gives you the exact compiled DAG plus column-level lineage. The one-liner for that path:

```bash
dbt ls --output json   # or: dbt parse && read target/manifest.json
```

The principle is identical. dbt already knows its graph; an orchestrator's job is to read that graph and materialize it on a schedule, with partitions, sensors, and retries layered on. Next: what happens when one of these models fails."""
    ),
]


# ===========================================================================
# 15.5 Failure, Retries, and Blast Radius
# ===========================================================================

NB_5 = [
    markdown_cell(
        "> **Chapter 15, Part 5** | Engineering lens. **Focus:** when an asset fails, skip its descendants rather than build them on missing inputs; retry transient failures; and quantify the damage with the Chapter 12 blast radius."
    ),
    markdown_cell(
        """# Failure, Retries, and Blast Radius

Everything so far assumed the happy path. Real orchestration is mostly about the unhappy path. Three questions:

1. When `clean` fails, what happens to `rollup` downstream? It must be **skipped**, not built on a missing input. Building on missing data is how a failed run silently produces a wrong dashboard.
2. Some failures are transient (a network blip). A **retry policy** gives an asset N attempts before it is declared failed.
3. When an asset fails, how much breaks? That is its **blast radius**, the set of downstream descendants, the exact descriptor Chapter 12 built for lineage risk."""
    ),
    code_cell(CORE),
    markdown_cell(
        "## Skip-on-failure\n\nBuild a diamond: `ingest` feeds both `clean_a` and `clean_b`, which both feed `join`, which feeds `report`. Force `clean_a` to fail every attempt. Watch `join` and `report` get skipped, while `clean_b` still builds (it does not depend on the failure)."
    ),
    code_cell(
        """g = AssetGraph()
g.add(Asset("ingest", [], lambda i: 1))
g.add(Asset("clean_a", ["ingest"], lambda i: 1))
g.add(Asset("clean_b", ["ingest"], lambda i: 1))
g.add(Asset("join", ["clean_a", "clean_b"], lambda i: 1))
g.add(Asset("report", ["join"], lambda i: 1))

status, _, _ = materialize_with_failures(g, failing={"clean_a": 99})
print()
print("final status:")
for n, s in status.items():
    print(f"  {n:9s} {s}")"""
    ),
    markdown_cell(
        "## Validation V004: nothing downstream of a failure is materialized\n\nThe guarantee is that no asset is ever built on a failed or missing input. We assert it on the run above."
    ),
    code_cell(
        """skipped = {n for n, s in status.items() if s == "skipped"}
materialized = {n for n, s in status.items() if s == "materialized"}
assert "join" in skipped and "report" in skipped, "downstream of failure must skip"
assert "clean_b" in materialized, "siblings of a failure still build"
print("V004 holds: join and report skipped, clean_b still built")"""
    ),
    markdown_cell(
        "## Retries turn a transient failure into a success\n\nNow let `clean_a` fail only twice, then succeed. A retry policy of three attempts absorbs it; the whole graph completes."
    ),
    code_cell(
        """status2, _, attempts = materialize_with_failures(
    g, failing={"clean_a": 2}, retry=RetryPolicy(max_attempts=3))
print()
print(f"clean_a took {attempts['clean_a']} attempts; final status of report:", status2["report"])"""
    ),
    markdown_cell(
        "## Validation V005: blast radius equals downstream descendants\n\nThe blast radius of a failed asset is everything reachable from it in the DAG. We compute it with our own traversal and cross-check against NetworkX's `descendants`."
    ),
    code_cell(
        """import networkx as nx

G = nx.DiGraph()
for n, a in g.assets.items():
    for d in a.deps:
        G.add_edge(d, n)

for failed in ("ingest", "clean_a", "report"):
    ours = blast_radius(g, failed)
    theirs = nx.descendants(G, failed)
    assert ours == theirs, f"mismatch for {failed}"
    print(f"  fail {failed:9s} -> blast radius {len(ours)}: {sorted(ours) or '(none, it is a leaf)'}")

print()
print("V005 holds: blast radius equals graph descendants")"""
    ),
    markdown_cell(
        "Blast radius is the number that should decide your on-call priority. A failure in `ingest` breaks everything; a failure in `report` breaks nothing downstream. Chapter 12 ranked stewardship by exactly this descriptor. Orchestration is where it earns its keep. Next: map all of this onto Dagster."
    ),
]


# ===========================================================================
# 15.6 From Our Toy to Dagster
# ===========================================================================

NB_6 = [
    markdown_cell(
        "> **Chapter 15, Part 6** | Engineering lens. **Focus:** every concept we built has a one-to-one Dagster primitive. This notebook is the Rosetta stone. The Dagster code is illustration, not executed."
    ),
    markdown_cell(
        """# From Our Toy to Dagster

We built an orchestrator in about 150 lines. Dagster is that idea, hardened for production: a web UI, a database of run history, a daemon for schedules and sensors, retries, partitions, freshness, and integrations. The concepts map one to one. This notebook is the translation table.

**The Dagster code below is illustrative and is not executed in this notebook.** Running it needs `pip install dagster dagster-webserver` and a `dagster dev` process. The point is to recognize each primitive as something you already built."""
    ),
    markdown_cell(
        """## Assets

Our toy:

```python
g.add(Asset("stg_events", ["raw_events"], compute_stg))
```

Dagster:

```python
from dagster import asset

@asset
def raw_events() -> list:
    return list(range(100))

@asset
def stg_events(raw_events: list) -> list:        # the parameter name IS the dependency
    return [x for x in raw_events if x % 2 == 0]
```

Dagster reads the dependency from the function signature. Our `deps=["raw_events"]` is the same edge, written by hand. The `@asset` decorator registers the function the way `g.add(...)` registered ours."""
    ),
    markdown_cell(
        """## Partitions and backfills

Our toy:

```python
backfill(g, "rollup", week, log)          # log skips what is already done
```

Dagster:

```python
from dagster import asset, DailyPartitionsDefinition

daily = DailyPartitionsDefinition(start_date="2026-06-01")

@asset(partitions_def=daily)
def rollup(context):
    day = context.partition_key
    ...
```

Dagster's backfills are launched from the UI or `dagster job backfill`, and its storage is the materialization log we hand-built. Re-running a materialized partition is a no-op for the same reason ours was: the system already recorded it."""
    ),
    markdown_cell(
        """## Sensors and freshness

Our toy:

```python
Sensor("new_file", file_waiting, process_file).poll(clock)
FreshnessPolicy(max_age=4).is_stale(last, now)
```

Dagster:

```python
from dagster import sensor, RunRequest, FreshnessPolicy, asset

@sensor(target=rollup)
def new_file_sensor(context):
    if file_has_landed():
        yield RunRequest(partition_key=today())

@asset(legacy_freshness_policy=FreshnessPolicy(maximum_lag_minutes=240))
def rollup(): ...
```

Same two ideas: a polled condition that yields work, and a max-age that marks an asset stale. Dagster's daemon runs the poll loop we ran by hand with `for _ in range(10)`."""
    ),
    markdown_cell(
        """## Retries and the run graph

Our toy:

```python
materialize_with_failures(g, retry=RetryPolicy(max_attempts=3))
```

Dagster:

```python
from dagster import asset, RetryPolicy, Backoff

@asset(retry_policy=RetryPolicy(max_retries=3, delay=2, backoff=Backoff.EXPONENTIAL))
def clean_a(): ...
```

Skip-on-failure is automatic in Dagster: if an upstream asset fails, downstream assets in the same run are not materialized, exactly as our `status == "skipped"` branch enforced."""
    ),
    markdown_cell(
        """## Wiring it together

Dagster collects assets, schedules, and sensors into a `Definitions` object, which is the deployable unit:

```python
from dagster import Definitions

defs = Definitions(
    assets=[raw_events, stg_events, rollup, clean_a],
    sensors=[new_file_sensor],
)
```

That object is our `AssetGraph` plus the reactive pieces, registered for a long-running daemon instead of a single `materialize()` call.

## Why Dagster here, and not Airflow or Prefect

Airflow is task-first: you author a DAG of operators, and data assets are implicit. It is the incumbent, with the largest operator ecosystem, and it is the right answer when you have hundreds of existing Airflow DAGs. Prefect is Python-function-first with a light touch and excellent dynamic-workflow ergonomics, strong when your control flow is irregular. Dagster is asset-first, which is why this chapter uses it: the asset graph is the same object as the lineage graph from Chapter 12, so the mental model carries straight through. None of the three is wrong. The asset framing is simply the one that made this chapter's pure-Python core the shortest path to the idea.

Next: put the whole apparatus to work on the repo's own trading platform."""
    ),
]


# ===========================================================================
# 15.7 Capstone: Orchestrate the Trading Platform's Data
# ===========================================================================

NB_7 = [
    markdown_cell(
        "> **Chapter 15, Part 7** | Engineering lens. **Capstone.** Build a real asset graph for the repo's trading platform, partition it by trading day, run it, and backfill a week."
    ),
    markdown_cell(
        """# Capstone: Orchestrate the Trading Platform's Data

The trading platform (Applied System A) moves market data into portfolio views and an "Ask Warren" analysis surface. Today that flow is implicit, spread across the Flask API and the Streamlit app. Here we make it an explicit asset graph:

```
market_data -> price_history -> positions -> daily_pnl -> warren_context
```

Each asset is partitioned by trading day. We generate synthetic OHLC bars (no network), materialize one day, then backfill a trading week. The compute functions are real pandas, so this is a working pipeline, just with a synthetic source standing in for yfinance."""
    ),
    code_cell(CORE),
    code_cell(
        """import numpy as np
import pandas as pd

TICKERS = ["AAPL", "MSFT", "NVDA", "AMZN"]
rng = np.random.default_rng(15)


def gen_market_data(inputs, day=None):
    # synthetic OHLC bars for the day, one row per ticker
    base = rng.uniform(80, 400, size=len(TICKERS))
    spread = rng.uniform(1, 6, size=len(TICKERS))
    return pd.DataFrame({
        "ticker": TICKERS,
        "open": base,
        "high": base + spread,
        "low": base - spread,
        "close": base + rng.uniform(-2, 2, size=len(TICKERS)),
        "day": day,
    })


def price_history(inputs, day=None):
    md = inputs["market_data"]
    return md[["ticker", "close", "day"]].copy()


def positions(inputs, day=None):
    # a fixed book of shares per ticker
    shares = {"AAPL": 50, "MSFT": 30, "NVDA": 20, "AMZN": 10}
    ph = inputs["price_history"]
    out = ph.copy()
    out["shares"] = out["ticker"].map(shares)
    out["market_value"] = out["close"] * out["shares"]
    return out


def daily_pnl(inputs, day=None):
    pos = inputs["positions"]
    return pd.DataFrame({"day": [day], "portfolio_value": [pos["market_value"].sum()]})


def warren_context(inputs, day=None):
    pnl = inputs["daily_pnl"]
    val = pnl["portfolio_value"].iloc[0]
    return f"On {day} the portfolio was worth ${val:,.0f}."


print("compute functions ready for", len(TICKERS), "tickers")"""
    ),
    markdown_cell(
        "The asset graph closes over the partition day so each compute knows which day it is building. We materialize a single trading day end to end and read off the Ask Warren context the graph produced."
    ),
    code_cell(
        """def build_graph(day):
    g = AssetGraph()
    g.add(Asset("market_data", [], lambda i: gen_market_data(i, day), partitioned=True))
    g.add(Asset("price_history", ["market_data"], lambda i: price_history(i, day), partitioned=True))
    g.add(Asset("positions", ["price_history"], lambda i: positions(i, day), partitioned=True))
    g.add(Asset("daily_pnl", ["positions"], lambda i: daily_pnl(i, day), partitioned=True))
    g.add(Asset("warren_context", ["daily_pnl"], lambda i: warren_context(i, day), partitioned=True))
    return g


day = "2026-06-08"
g = build_graph(day)
print("run order:", " -> ".join(g.topological_order()))
print()
results = g.materialize(verbose=True)
print()
print("Ask Warren context:", results["warren_context"])"""
    ),
    markdown_cell(
        "## Backfill the trading week\n\nMonday to Friday. Each day rebuilds the graph for that partition (the source closes over the day) and materializes it. We collect the daily portfolio value the pipeline computed and plot the week."
    ),
    code_cell(
        """import matplotlib.pyplot as plt

trading_week = ["2026-06-08", "2026-06-09", "2026-06-10", "2026-06-11", "2026-06-12"]
values = []
for d in trading_week:
    res = build_graph(d).materialize(verbose=False)
    values.append(res["daily_pnl"]["portfolio_value"].iloc[0])
    print(res["warren_context"])

fig, ax = plt.subplots(figsize=(8, 3))
ax.plot([d[-2:] for d in trading_week], values, marker="o", color="#7c5cff", linewidth=2)
ax.fill_between([d[-2:] for d in trading_week], values, alpha=0.12, color="#7c5cff")
ax.set_title("portfolio value across the trading week (synthetic)", fontsize=11)
ax.set_xlabel("trading day (June 2026)")
ax.set_ylabel("portfolio value ($)")
ax.grid(alpha=0.2)
plt.tight_layout()
plt.show()"""
    ),
    markdown_cell(
        "That is the trading platform as an orchestrated asset graph: partitioned by day, materialized in dependency order, backfillable across a week, and ending in the exact context string the Ask Warren surface consumes. Swap the synthetic source for yfinance and the same graph runs against live data. Last notebook: the failure modes, because none of this is free."
    ),
]


# ===========================================================================
# 15.8 When the Schedule Lies
# ===========================================================================

NB_8 = [
    markdown_cell(
        "> **Chapter 15, Part 8** | The honesty closer. **Focus:** four ways an orchestrated pipeline reports success while being wrong. Pairs with 12.7, 13.8, and 14.8."
    ),
    markdown_cell(
        """# When the Schedule Lies

Every advanced chapter in this repo ends by naming its own failure modes, because an apparatus that cannot fail cannot inform. Orchestration's failures are worse than cron's in one specific way: a scheduler with a green dashboard is more trusted, so when it lies, it lies with authority.

Four failure modes, each demonstrated."""
    ),
    code_cell(CORE),
    markdown_cell(
        """## 1. Silent partial failure

An asset "completes" but produces empty output. The run is green. Downstream builds on nothing and reports zero, which looks like a quiet day rather than a broken pipeline. The fix is a data-quality assertion inside the asset, not a status check outside it."""
    ),
    code_cell(
        """g = AssetGraph()
g.add(Asset("ingest", [], lambda i: []))                     # returns EMPTY, but does not raise
g.add(Asset("rollup", ["ingest"], lambda i: {"rows": len(i["ingest"])}))

res = g.materialize(verbose=False)
print("run status: SUCCESS (every asset returned without error)")
print("rollup output:", res["rollup"], "<- zero rows, and nothing flagged it")
print()
# The fix: assert inside the asset.
def ingest_checked(i):
    data = []
    if len(data) == 0:
        raise ValueError("ingest produced 0 rows; failing loudly instead of passing empty downstream")
    return data

try:
    AssetGraph().add(Asset("ingest", [], ingest_checked)).materialize(verbose=False)
except ValueError as e:
    print("with an in-asset check:", e)"""
    ),
    markdown_cell(
        """## 2. Sensor storms

A sensor whose condition is always true fires on every poll. Instead of one run per file, you get a run per tick, and the executor drowns. The fix is a cursor: the sensor must remember what it already handled."""
    ),
    code_cell(
        """class Clock:
    def __init__(self): self.t = 0
    def tick(self): self.t += 1


# Broken: condition ignores whether work was already done.
clock = Clock()
storm = 0
for _ in range(10):
    if True:                      # always fires
        storm += 1
    clock.tick()
print(f"broken sensor: {storm} runs launched in 10 ticks (a storm)")

# Fixed: a cursor remembers the last handled tick.
clock = Clock()
handled_until = -1
fixed_runs = 0
arrivals = {3, 7}
for _ in range(10):
    if clock.t in arrivals and clock.t > handled_until:
        fixed_runs += 1
        handled_until = clock.t
    clock.tick()
print(f"fixed sensor:  {fixed_runs} runs (one per genuine arrival)")"""
    ),
    markdown_cell(
        """## 3. Backfill thundering herd

Backfilling a year of daily partitions at once launches 365 simultaneous materializations. The warehouse that handles one day comfortably falls over under 365. The fix is a concurrency limit: backfill in bounded waves."""
    ),
    code_cell(
        """def backfill_waves(partitions, max_concurrent):
    waves = [partitions[i:i + max_concurrent] for i in range(0, len(partitions), max_concurrent)]
    return waves


year = [f"day_{i:03d}" for i in range(365)]
naive = len(year)
waves = backfill_waves(year, max_concurrent=10)
print(f"naive backfill: {naive} partitions launched at once (thundering herd)")
print(f"bounded backfill: {len(waves)} waves of <= 10, peak concurrency 10")
print("peak warehouse load drops by", f"{naive // 10}x")"""
    ),
    markdown_cell(
        """## 4. Retry masking a data bug

Retries are for transient failures. Point them at a deterministic data bug and they just burn compute, then fail anyway, while delaying the alert by however long the retries took. A retry policy should distinguish retriable errors (timeouts) from terminal ones (a schema violation)."""
    ),
    code_cell(
        """attempts = {"count": 0}


def deterministic_bug(i):
    attempts["count"] += 1
    raise ValueError("column 'price' is null")     # same failure every time, not transient


g = AssetGraph().add(Asset("bad", [], deterministic_bug))
status, _, used = materialize_with_failures(g, failing={"bad": 99},
                                            retry=RetryPolicy(max_attempts=5), verbose=False)
print(f"retried {5} times, still failed; wasted {5 - 1} extra runs on a non-transient bug")
print()
print("the fix: classify errors")
print("  retriable  -> timeout, connection reset, 503    -> retry")
print("  terminal   -> null constraint, schema mismatch  -> fail fast, alert now")"""
    ),
    markdown_cell(
        """## The through-line

All four failures share a shape: the orchestrator reported success on a metric that was not the thing you cared about. Green status is not green data. The same lesson closed Chapter 12 (descriptors oversold), Chapter 13 (governance signals gamed), and Chapter 14 (benchmark speedups that vanish in production).

An orchestrator is leverage. It runs your pipeline reliably, on a schedule, with recovery. It will also run a wrong pipeline reliably, on a schedule, with recovery. The instrumentation that catches the four failures above (in-asset data checks, sensor cursors, concurrency caps, error classification) is not optional polish. It is the part that makes the leverage safe.

That is Chapter 15. You built an orchestrator, pointed it at the repo's own dbt project and trading platform, mapped it to Dagster, and learned where it bites. Chapter 16 on the roadmap takes the next step: data contracts and change capture, which move quality enforcement to the producer boundary where governance actually has leverage."""
    ),
]


# ---------------------------------------------------------------------------

NOTEBOOKS = {
    "15.0 From Cron to Asset Graphs.ipynb": NB_0,
    "15.1 A Tiny Asset Graph From Scratch.ipynb": NB_1,
    "15.2 Partitions and Backfills.ipynb": NB_2,
    "15.3 Sensors and Freshness.ipynb": NB_3,
    "15.4 Wrapping the dbt Project as Assets.ipynb": NB_4,
    "15.5 Failure, Retries, and Blast Radius.ipynb": NB_5,
    "15.6 From Our Toy to Dagster.ipynb": NB_6,
    "15.7 Capstone Orchestrate the Trading Platform.ipynb": NB_7,
    "15.8 When the Schedule Lies.ipynb": NB_8,
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for filename, cells in NOTEBOOKS.items():
        write_notebook(filename, cells)
    print(f"\ngenerated {len(NOTEBOOKS)} notebooks in {OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
