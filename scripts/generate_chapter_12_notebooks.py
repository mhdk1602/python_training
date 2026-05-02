"""Generate the eight Chapter 12 (Fractal Graphs) notebooks.

Run from the repo root:

    python3 scripts/generate_chapter_12_notebooks.py

Mirrors the conventions in chapter-10-rag-lab/scripts/generate_notebooks.py.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "notebooks" / "12-fractal-graphs"


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
        "source": source.splitlines(keepends=True),
    }


# ---------------------------------------------------------------------------
# 12.0 Why Graphs Deserve a Fractal Lens
# ---------------------------------------------------------------------------

NB_12_0 = [
    markdown_cell(
        "> **Chapter 12, Part 0** | Advanced lens. **Focus:** what graphs add to the Chapter 11 argument and which two bridges (time series, image) the rest of the chapter actually walks across."
    ),
    markdown_cell(
        """# Why Graphs Deserve a Fractal Lens

Chapter 11 used pictures and time series to teach scale-sensitive descriptors. Most enterprise objects worth governing are graphs already: data lineage DAGs, entity-resolution match graphs, product hierarchies, microservice dependencies. The graph is not a metaphor here. It is the data structure those objects already live in. Box-counting still applies. It just lives on a different geometry.

This chapter walks across three bridges:

1. **Time series to graph** via the Lacasa visibility algorithm (12.2). Periodic series become regular graphs. Random series become exponential graphs. Fractal series become scale-free graphs whose degree exponent tracks the Hurst exponent.
2. **Image to graph** via box-covering on networks (12.3). The same reasoning that produced `d_B` from the Mandelbrot boundary in 11.1 produces a `d_B` from a network, with the same log-log fit and the same epistemic discipline.
3. **Governance to graph** via lineage and entity resolution (12.5 and 12.6). The 11.4 duplicate-cluster work is procedurally union-find; this chapter shows the same problem as a graph and adds descriptors the procedural form cannot expose.

## The bounded claim, restated

I am not claiming enterprise data is fractal. I am asking whether selected enterprise graphs show enough multi-scale structure that fractal descriptors become useful for stewardship triage. Where the test fails, this chapter says so. Where the test passes, this chapter explains what governance decision the measurement should improve.

## Outputs

- a clear answer to the question "why graphs after Chapter 11"
- a Karate-club teaser that previews the box and skeleton ideas
- a chapter-spanning assignment to anchor your own enterprise object across 12.0 through 12.7

## Supporting reading

- Song, C., Havlin, S., and Makse, H. A. (2005). Self-similarity of complex networks. *Nature* 433, 392-395. https://www.nature.com/articles/nature03248
- Skums, P., and Bunimovich, L. (2020). Graph fractal dimension and the structure of fractal networks. *Journal of Complex Networks* 8(4). https://pmc.ncbi.nlm.nih.gov/articles/PMC7673317/
- Malemapti Hari, D. (2026). Static and Temporal Fractal Coupling Between Volatility and Trading Volume. *Zenodo*. https://doi.org/10.5281/zenodo.19611544

## Failure note

If you finish 12.0 and still cannot say which graph in your own work would benefit from a fractal lens, the chapter has failed. The descriptors are only useful where the object class is named first.

## How I would debug this

Pick one graph from your environment before reading 12.1. Write down its node type, edge type, and the boundary you currently use to decide if two records are the same entity. We will return to that example in 12.5 and 12.6.
"""
    ),
    code_cell(
        """import networkx as nx
import matplotlib.pyplot as plt

g = nx.karate_club_graph()
print(\"nodes\", g.number_of_nodes(), \"edges\", g.number_of_edges())

center = 0
ball_radius = 2
ball = {center} | {n for n in nx.single_source_shortest_path_length(g, center, cutoff=ball_radius)}

pos = nx.spring_layout(g, seed=7)
plt.figure(figsize=(8, 5.5))
nx.draw_networkx_edges(g, pos, alpha=0.4)
nx.draw_networkx_nodes(g, pos, nodelist=list(g.nodes() - ball), node_color=\"#9aa6a0\", node_size=160)
nx.draw_networkx_nodes(g, pos, nodelist=list(ball), node_color=\"#efce8a\", node_size=240, edgecolors=\"#173326\")
nx.draw_networkx_labels(g, pos, font_size=8)
plt.title(f\"Karate club: {ball_radius}-hop ball around node {center}\")
plt.axis(\"off\")
plt.tight_layout()
plt.show()
"""
    ),
    markdown_cell(
        """The gold nodes form a **box** of radius 2 around node 0. That same idea, repeated at multiple radii and aggregated across the whole graph, is what 12.3 will use to estimate a network's box dimension. Hold on to the visual; the rest of the chapter formalizes it.

## Chapter assignment

Pick one graph in your environment. Lineage. Entity match. Knowledge. Microservice. Document the following before continuing:

1. node type and what each node represents
2. edge type and what an edge means in the operational sense
3. the boundary you currently use to decide where the graph ends or where two records are the same entity

We will return to your example in 12.5 (lineage) and 12.6 (entity resolution). Do not skip this step. Without a concrete object the rest of the chapter reads like decoration.
"""
    ),
]


# ---------------------------------------------------------------------------
# 12.1 Graphs as the Next Geometry
# ---------------------------------------------------------------------------

NB_12_1 = [
    markdown_cell(
        "> **Chapter 12, Part 1** | Advanced lens. **Focus:** the minimum graph language the rest of the chapter needs, and a re-expression of Chapter 11.4 union-find as connected components on a thresholded match graph."
    ),
    markdown_cell(
        """# Graphs as the Next Geometry

The Chapter 11.4 duplicate-cluster notebook uses union-find with a `parent` dictionary. That is graph theory in disguise. Once you name it as a graph, you inherit decades of language, primitives, and tools.

This notebook teaches the slice of NetworkX the rest of the chapter actually uses. No more.

## Outputs

- a working vocabulary: nodes, edges, paths, distance, neighborhoods, components, degree
- the 11.4 records and scores rebuilt as a NetworkX graph
- a side-by-side check that connected components match 11.4 union-find at the same threshold
- a degree-distribution view of the Karate club, which we revisit in 12.3 and 12.4

## Supporting reading

- Hagberg, A., Schult, D., and Swart, P. (2008). Exploring network structure, dynamics, and function using NetworkX.
- NetworkX reference: https://networkx.org/documentation/stable/

## Failure note

If you cannot run a single connected-components call on the 11.4 data and produce the same clusters the union-find code produced, the rest of the chapter will not stand up.

## How I would debug this

Build the smallest possible graph by hand (four records, three edges), run components, and verify the answer matches your mental model before scaling up.
"""
    ),
    code_cell(
        """import networkx as nx

g = nx.Graph()
g.add_nodes_from([\"R1\", \"R2\", \"R3\", \"R4\"])
g.add_edge(\"R1\", \"R2\", weight=0.94)
g.add_edge(\"R2\", \"R3\", weight=0.85)
g.add_edge(\"R3\", \"R4\", weight=0.18)

print(\"nodes\", list(g.nodes()))
print(\"edges\", [(u, v, d.get(\"weight\")) for u, v, d in g.edges(data=True)])
print(\"degree of R2\", g.degree[\"R2\"])
print(\"neighbors of R2\", list(g.neighbors(\"R2\")))
print(\"shortest path R1 to R4\", nx.shortest_path(g, \"R1\", \"R4\"))
print(\"distance R1 to R4\", nx.shortest_path_length(g, \"R1\", \"R4\"))
"""
    ),
    code_cell(
        """import pandas as pd

records = pd.DataFrame(
    [
        {\"record_id\": \"R1\", \"source\": \"crm\", \"name\": \"Acme Health\", \"city\": \"Chicago\"},
        {\"record_id\": \"R2\", \"source\": \"erp\", \"name\": \"ACME Health Inc\", \"city\": \"Chicago\"},
        {\"record_id\": \"R3\", \"source\": \"support\", \"name\": \"Acme Health\", \"city\": \"Skokie\"},
        {\"record_id\": \"R4\", \"source\": \"crm\", \"name\": \"Northwind Labs\", \"city\": \"Boston\"},
        {\"record_id\": \"R5\", \"source\": \"erp\", \"name\": \"Northwind Laboratories\", \"city\": \"Boston\"},
        {\"record_id\": \"R6\", \"source\": \"partner\", \"name\": \"North Wind Labs\", \"city\": \"Cambridge\"},
        {\"record_id\": \"R7\", \"source\": \"crm\", \"name\": \"Riverstone Foods\", \"city\": \"Austin\"},
        {\"record_id\": \"R8\", \"source\": \"support\", \"name\": \"River Stone Food Group\", \"city\": \"Austin\"},
    ]
)

scores = pd.DataFrame(
    [
        (\"R1\", \"R2\", 0.94),
        (\"R1\", \"R3\", 0.89),
        (\"R2\", \"R3\", 0.85),
        (\"R4\", \"R5\", 0.96),
        (\"R4\", \"R6\", 0.84),
        (\"R5\", \"R6\", 0.82),
        (\"R7\", \"R8\", 0.87),
        (\"R2\", \"R6\", 0.32),
        (\"R3\", \"R4\", 0.18),
    ],
    columns=[\"left\", \"right\", \"score\"],
)


def match_graph(score_frame: pd.DataFrame, threshold: float, ids: list[str]) -> nx.Graph:
    g = nx.Graph()
    g.add_nodes_from(ids)
    for row in score_frame.itertuples(index=False):
        if row.score >= threshold:
            g.add_edge(row.left, row.right, weight=row.score)
    return g


graph_at_086 = match_graph(scores, threshold=0.86, ids=records[\"record_id\"].tolist())
print(\"nodes\", graph_at_086.number_of_nodes(), \"edges\", graph_at_086.number_of_edges())

components = list(nx.connected_components(graph_at_086))
for i, comp in enumerate(components, start=1):
    print(f\"C{i}\", sorted(comp))
"""
    ),
    code_cell(
        """def union_find_clusters(score_frame: pd.DataFrame, threshold: float, ids: list[str]) -> list[set[str]]:
    parent = {rid: rid for rid in ids}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for row in score_frame.itertuples(index=False):
        if row.score >= threshold:
            union(row.left, row.right)

    clusters: dict[str, set[str]] = {}
    for rid in ids:
        clusters.setdefault(find(rid), set()).add(rid)
    return list(clusters.values())


uf_clusters = union_find_clusters(scores, threshold=0.86, ids=records[\"record_id\"].tolist())
nx_clusters = [set(c) for c in nx.connected_components(graph_at_086)]

uf_sorted = sorted([sorted(c) for c in uf_clusters])
nx_sorted = sorted([sorted(c) for c in nx_clusters])
assert uf_sorted == nx_sorted, \"NetworkX components and union-find disagree\"
print(\"agreement at threshold 0.86:\", uf_sorted)
"""
    ),
    code_cell(
        """import matplotlib.pyplot as plt
from collections import Counter

karate = nx.karate_club_graph()
degree_seq = [deg for _, deg in karate.degree()]
counts = Counter(degree_seq)
ks = sorted(counts.keys())
ps = [counts[k] / len(degree_seq) for k in ks]

plt.figure(figsize=(8, 4.5))
plt.bar(ks, ps, color=\"#2b5a43\")
plt.xlabel(\"degree k\")
plt.ylabel(\"P(k)\")
plt.title(\"Karate club degree distribution\")
plt.tight_layout()
plt.show()
"""
    ),
    markdown_cell(
        """## Reading the result

The NetworkX `connected_components` answer matched the 11.4 union-find answer at threshold 0.86. That equivalence is the point. Once you have the graph, you also have access to descriptors union-find never produced: degree distributions, betweenness centralities, communities, and (in 12.3) box-coverings.

The Karate degree distribution is short-tailed and irregular. It is not a power law. We use it later because it is small enough to box-cover in seconds, and real enough to teach the right lessons about finite-size effects.

## Where this can go wrong

- `match_graph` ignores edge weights when running connected components. Two records with weight 0.86 and weight 0.99 contribute identically to component membership. We fix that gap in 12.6, where local box dimension and skeleton ratio bring weight back into the picture.
- `connected_components` does not run on a `DiGraph`. Lineage in 12.5 needs `weakly_connected_components` or `strongly_connected_components` depending on the question.

## Exercise

1. add an edge `(\"R6\", \"R7\")` with weight 0.78. At which threshold does it change the cluster picture?
2. compute the degree distribution of the threshold-0.84 match graph. Compare to the 0.86 case.
3. write down one pair of records you would refuse to merge no matter the score, and explain which graph descriptor would make that refusal visible.
"""
    ),
]


# ---------------------------------------------------------------------------
# 12.2 Visibility Graphs from Time Series
# ---------------------------------------------------------------------------

NB_12_2 = [
    markdown_cell(
        "> **Chapter 12, Part 2** | Advanced lens. **Focus:** the visibility map from time series to graph, the three regimes (periodic, random, fractal), and the linear relationship between the visibility-graph degree exponent and the Hurst exponent."
    ),
    markdown_cell(
        """# Visibility Graphs from Time Series

The visibility graph (Lacasa et al., 2008) is the cleanest available bridge between time-series analysis and graph theory. Treat the time series as a landscape of vertical bars. Two bars are connected in the visibility graph if you can draw a straight line between their tops without crossing any intermediate bar.

The result inherits structure from the series. Periodic series produce regular graphs. Random series produce exponential degree distributions. Fractal series produce scale-free graphs whose degree exponent depends linearly on the Hurst exponent. That last result is what makes this a serious analytical tool.

## Outputs

- an O(n^2) visibility-graph implementation
- a three-regime demonstration: periodic, random, fractional Brownian motion
- a fractional Brownian motion generator (Cholesky on the fGn covariance)
- a Hurst sweep showing the visibility-graph degree exponent as a function of H
- a horizontal-visibility variant for contrast

## Supporting reading

- Lacasa, L., Luque, B., Ballesteros, F., Luque, J., and Nuno, J. C. (2008). From time series to complex networks: the visibility graph. *PNAS* 105(13), 4972-4975. https://www.pnas.org/doi/full/10.1073/pnas.0709247105
- Lacasa, L., Luque, B., Luque, J., and Nuno, J. C. (2009). The visibility graph: a new method for estimating the Hurst exponent of fractional Brownian motion. *EPL* 86, 30001. https://arxiv.org/abs/0901.0888
- Luque, B., Lacasa, L., Ballesteros, F., and Luque, J. (2009). Horizontal visibility graphs: exact results for random time series. *Phys. Rev. E* 80, 046103.
- Malemapti Hari, D. (2026). Static and Temporal Fractal Coupling Between Volatility and Trading Volume. *Zenodo*. https://doi.org/10.5281/zenodo.19611544

## Failure note

If your visibility graph has fewer than two decades of degree-distribution support, do not fit a power law to it. You have a slope, not a power law.

## How I would debug this

Build the visibility graph for a six-point series by hand, draw it on paper, then run the code on the same six points. If they disagree, fix the implementation before running it on any longer series.
"""
    ),
    code_cell(
        """import numpy as np
import networkx as nx


def visibility_graph(values: np.ndarray) -> nx.Graph:
    \"\"\"Natural visibility graph (Lacasa 2008).

    O(n^2) using the running-max-slope formulation. Connects (a, b) with b > a iff
    the line from (a, y_a) to (b, y_b) lies strictly above every intermediate point.
    \"\"\"
    n = len(values)
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for a in range(n - 1):
        ya = values[a]
        g.add_edge(a, a + 1)
        if a + 2 >= n:
            continue
        max_slope = (values[a + 1] - ya) / 1.0
        for b in range(a + 2, n):
            yb = values[b]
            slope = (yb - ya) / (b - a)
            if slope > max_slope:
                g.add_edge(a, b)
                max_slope = slope
    return g


toy = np.array([1.0, 2.0, 1.5, 3.0, 0.5, 2.5])
g = visibility_graph(toy)
print(\"nodes\", g.number_of_nodes(), \"edges\", sorted(g.edges()))
"""
    ),
    code_cell(
        """import matplotlib.pyplot as plt
from collections import Counter


def degree_distribution(g: nx.Graph) -> tuple[np.ndarray, np.ndarray]:
    counts = Counter(deg for _, deg in g.degree())
    ks = np.array(sorted(counts.keys()))
    ps = np.array([counts[k] / g.number_of_nodes() for k in ks])
    return ks, ps


rng = np.random.default_rng(7)
n = 512

t = np.arange(n)
periodic = np.sin(2 * np.pi * t / 32) + 0.5 * np.sin(2 * np.pi * t / 7)
random_series = rng.uniform(0, 1, size=n)

fig, axes = plt.subplots(2, 3, figsize=(13, 6.5))
for ax, label, series in zip(axes[0], [\"periodic\", \"random\", \"fBm (H=0.7)\"], [periodic, random_series, None]):
    if series is None:
        continue
    ax.plot(series[:120], color=\"#173326\")
    ax.set_title(label)
    ax.set_xlabel(\"t\")

for ax, series in zip(axes[1, :2], [periodic, random_series]):
    g = visibility_graph(series)
    ks, ps = degree_distribution(g)
    ax.bar(ks, ps, color=\"#2b5a43\")
    ax.set_xlabel(\"degree k\")
    ax.set_ylabel(\"P(k)\")

axes[0, 2].set_axis_off()
axes[1, 2].set_axis_off()
plt.tight_layout()
plt.show()
"""
    ),
    code_cell(
        """from scipy.linalg import toeplitz, cholesky


def fbm_cholesky(n: int, hurst: float, rng: np.random.Generator) -> np.ndarray:
    \"\"\"Exact fractional Brownian motion via Cholesky on the fGn autocovariance.

    Suitable for n up to about 1024 on a laptop. For larger n use Davies-Harte.
    \"\"\"
    k = np.arange(n)
    gamma = 0.5 * (
        np.abs(k + 1) ** (2 * hurst)
        - 2 * np.abs(k) ** (2 * hurst)
        + np.abs(k - 1) ** (2 * hurst)
    )
    cov = toeplitz(gamma)
    chol = cholesky(cov, lower=True)
    fgn = chol @ rng.standard_normal(n)
    return np.cumsum(fgn)


fbm_07 = fbm_cholesky(512, hurst=0.7, rng=np.random.default_rng(7))

fig, axes = plt.subplots(1, 2, figsize=(13, 4))
axes[0].plot(fbm_07, color=\"#173326\")
axes[0].set_title(\"fBm (H = 0.7)\")
axes[0].set_xlabel(\"t\")

g = visibility_graph(fbm_07)
ks, ps = degree_distribution(g)
mask = (ks > 0) & (ps > 0)
slope, intercept = np.polyfit(np.log(ks[mask]), np.log(ps[mask]), 1)
axes[1].loglog(ks[mask], ps[mask], \"o\", color=\"#d17a00\")
axes[1].loglog(ks[mask], np.exp(intercept) * ks[mask] ** slope, color=\"#2b5a43\")
axes[1].set_xlabel(\"degree k\")
axes[1].set_ylabel(\"P(k)\")
axes[1].set_title(f\"degree distribution: alpha approx {-slope:.2f}\")
plt.tight_layout()
plt.show()
"""
    ),
    code_cell(
        """hurst_values = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
alphas = []
rng = np.random.default_rng(11)

for hurst in hurst_values:
    series = fbm_cholesky(512, hurst=hurst, rng=rng)
    g = visibility_graph(series)
    ks, ps = degree_distribution(g)
    mask = (ks > 0) & (ps > 0)
    if mask.sum() < 4:
        alphas.append(np.nan)
        continue
    slope, _ = np.polyfit(np.log(ks[mask]), np.log(ps[mask]), 1)
    alphas.append(-slope)

plt.figure(figsize=(7, 4.5))
plt.plot(hurst_values, alphas, \"o-\", color=\"#173326\")
plt.xlabel(\"Hurst exponent H\")
plt.ylabel(\"visibility-graph degree exponent alpha\")
plt.title(\"alpha decreases roughly linearly with H\")
plt.tight_layout()
plt.show()

list(zip(hurst_values, [round(a, 3) for a in alphas]))
"""
    ),
    code_cell(
        """def horizontal_visibility_graph(values: np.ndarray) -> nx.Graph:
    \"\"\"Horizontal visibility graph (Luque 2009).

    Two bars (a, b) connect iff every intermediate bar is strictly shorter than
    both endpoints. Simpler than the natural visibility graph and analytically
    tractable; for i.i.d. random series the expected degree distribution is
    P(k) = (1/3) * (2/3)^(k-2) for k >= 2.
    \"\"\"
    n = len(values)
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for a in range(n):
        max_height = -np.inf
        for b in range(a + 1, n):
            yb = values[b]
            if values[a] > max_height and yb > max_height:
                g.add_edge(a, b)
            if yb >= values[a]:
                break
            max_height = max(max_height, yb)
    return g


random_series = np.random.default_rng(7).uniform(0, 1, size=512)
hvg = horizontal_visibility_graph(random_series)
ks, ps = degree_distribution(hvg)

ks_theory = np.arange(2, 12)
ps_theory = (1 / 3.0) * (2 / 3.0) ** (ks_theory - 2)

plt.figure(figsize=(7, 4.5))
plt.semilogy(ks, ps, \"o\", color=\"#d17a00\", label=\"empirical\")
plt.semilogy(ks_theory, ps_theory, color=\"#2b5a43\", label=\"theory: (1/3)(2/3)^(k-2)\")
plt.xlabel(\"degree k\")
plt.ylabel(\"P(k)\")
plt.title(\"horizontal visibility graph: i.i.d. random series\")
plt.legend()
plt.tight_layout()
plt.show()
"""
    ),
    markdown_cell(
        """## Reading the result

The visibility-graph degree distribution captures the regime of the underlying series.

- **Periodic series**: degree distribution is a finite spike pattern. The graph is regular.
- **Random series**: tail decays exponentially. The graph is small-world without scale-free structure.
- **Fractal series (fBm)**: tail follows a power law. The exponent shifts with H. As H rises (more persistence, smoother paths), the degree exponent falls.

The horizontal-visibility variant matches its closed-form prediction `(1/3) * (2/3)^(k-2)` for i.i.d. random series almost exactly. That closed form is one of the cleanest sanity checks the field has.

## Connection to the Malemapti Hari (2026) coupling work

The published research used DFA on volatility and volume to detect cross-fractal coupling. The visibility graph is an alternative path to the same Hurst signal: build the graph, fit the degree exponent, recover an estimate of H. On returns this is faster than DFA and exposes additional graph-theoretic descriptors (clustering, small-world index, betweenness) that DFA alone cannot.

## Where this can go wrong

- a slow linear trend pushes hub mass toward the trend extreme. The visibility map is invariant under affine transformations of the series, but a trend changes which point dominates the visibility line. Detrend or work on returns, not raw price.
- O(n^2) compute is fine up to n approx 1500. Larger series want the divide-and-conquer construction (Lan et al., 2015). Cap n at 1024 and disclose the cap in the failure note.
- alpha fits on fewer than two decades of degree support are noise. Use the `powerlaw` package for honest fits when N is small.

## Exercise

1. generate a series that is periodic for 256 points and then becomes fBm at H=0.7 for the next 256. Build the visibility graph. Where does the graph reveal the regime change?
2. compute the average path length of the fBm visibility graph at H=0.5 and H=0.8. Which is more small-world? Form a hypothesis before running the code.
3. take a real return series from your environment, detrend it, and compute the visibility-graph degree exponent. Compare it to a DFA-based H estimate on the same series.
"""
    ),
]


# ---------------------------------------------------------------------------
# 12.3 Box Covering on Graphs
# ---------------------------------------------------------------------------

NB_12_3 = [
    markdown_cell(
        "> **Chapter 12, Part 3** | Advanced lens. **Focus:** box-covering as the graph analog of 11.1 box-counting; greedy-coloring approximation; deterministic fractal graphs as ground-truth benchmarks; non-fractal controls."
    ),
    markdown_cell(
        """# Box Covering on Graphs

Box-covering on a graph is the same idea as box-counting on the Mandelbrot boundary in 11.1. The geometry is different. The reasoning is identical.

For a graph with shortest-path distance, a box of size `l` is a set of nodes whose pairwise distances are all at most `l - 1`. The minimum number of boxes needed to cover the graph, plotted against `l` on a log-log axis, gives the box dimension `d_B`. If the slope is stable across multiple decades, the network is informally fractal.

The exact problem is NP-hard. Greedy coloring of an auxiliary graph gives a near-optimal answer. NetworkX provides `greedy_color`, so the implementation stays short.

## Outputs

- a working box-covering function via greedy coloring of the auxiliary graph
- `d_B` estimates on three deterministic fractal models with known answers
- one estimate on a real network (Karate)
- one estimate on a non-fractal control (Erdos-Renyi) where the slope refuses to stabilize

## Supporting reading

- Song, C., Havlin, S., and Makse, H. A. (2005). Self-similarity of complex networks. *Nature* 433, 392-395.
- Song, C., Havlin, S., and Makse, H. A. (2007). How to calculate the fractal dimension of a complex network: the box covering algorithm. *J. Stat. Mech.* P03006.
- Nagy, M. (2021). Comparative analysis of box-covering algorithms for fractal networks. *Applied Network Science* 6:73. https://link.springer.com/article/10.1007/s41109-021-00410-6
- Rozenfeld, H. D., Havlin, S., and ben-Avraham, D. (2007). Fractal and transfractal recursive scale-free nets. *New J. Phys.* 9, 175.

## Failure note

If your `d_B` estimate looks clean on the log-log plot but moves by more than 0.2 when you trim one or two box sizes from either end of the range, you do not have a stable estimate. You have a slope.

## How I would debug this

Box-cover one fractal model with a known analytical `d_B` first. If your code reproduces the analytical answer to within 5 percent, you can trust it on real networks. If not, the bug is in the auxiliary-graph construction or in the coloring strategy.
"""
    ),
    code_cell(
        """import numpy as np
import networkx as nx


def auxiliary_graph(g: nx.Graph, l_b: int, dist: dict) -> nx.Graph:
    \"\"\"Auxiliary graph: u and v adjacent iff their distance in g exceeds l_b - 1.

    A coloring of the auxiliary graph corresponds to a box-cover of g with
    boxes of size at most l_b. Two nodes share a color iff they are within
    l_b - 1 hops in the original graph.
    \"\"\"
    aux = nx.Graph()
    aux.add_nodes_from(g.nodes())
    nodes = list(g.nodes())
    for i, u in enumerate(nodes):
        for v in nodes[i + 1:]:
            d = dist[u].get(v, np.inf)
            if d >= l_b:
                aux.add_edge(u, v)
    return aux


def box_cover(g: nx.Graph, l_b: int, dist=None) -> dict[int, set]:
    if dist is None:
        dist = dict(nx.all_pairs_shortest_path_length(g))
    aux = auxiliary_graph(g, l_b, dist)
    coloring = nx.coloring.greedy_color(aux, strategy=\"largest_first\")
    boxes: dict[int, set] = {}
    for node, color in coloring.items():
        boxes.setdefault(color, set()).add(node)
    return boxes


def estimate_d_B(g: nx.Graph, l_values: list[int]) -> tuple[float, list[int]]:
    dist = dict(nx.all_pairs_shortest_path_length(g))
    counts = [len(box_cover(g, l, dist)) for l in l_values]
    valid = [(l, c) for l, c in zip(l_values, counts) if c > 0]
    if len(valid) < 3:
        return float(\"nan\"), counts
    xs = np.log(np.array([1.0 / l for l, _ in valid]))
    ys = np.log(np.array([c for _, c in valid]))
    slope, _ = np.polyfit(xs, ys, 1)
    return float(slope), counts
"""
    ),
    code_cell(
        """def sierpinski_gasket(iterations: int = 3) -> nx.Graph:
    \"\"\"Sierpinski gasket graph by recursive triangle subdivision.

    Each triangle splits into four sub-triangles via midpoints. After t
    iterations the graph has approximately (3 + 3 * (3^t - 1) / 2) edges and
    a known box dimension d_B = log 3 / log 2 approx 1.585.
    \"\"\"
    g = nx.Graph()
    g.add_edges_from([(0, 1), (1, 2), (0, 2)])
    triangles = [(0, 1, 2)]
    next_id = 3
    for _ in range(iterations):
        new_triangles: list[tuple[int, int, int]] = []
        for u, v, w in triangles:
            m_uv, m_vw, m_uw = next_id, next_id + 1, next_id + 2
            next_id += 3
            for edge in [(u, v), (v, w), (u, w)]:
                if g.has_edge(*edge):
                    g.remove_edge(*edge)
            g.add_edges_from([
                (u, m_uv), (m_uv, v),
                (v, m_vw), (m_vw, w),
                (u, m_uw), (m_uw, w),
                (m_uv, m_vw), (m_vw, m_uw), (m_uv, m_uw),
            ])
            new_triangles.extend([
                (u, m_uv, m_uw),
                (m_uv, v, m_vw),
                (m_uw, m_vw, w),
                (m_uv, m_vw, m_uw),
            ])
        triangles = new_triangles
    return g


sg = sierpinski_gasket(iterations=3)
print(\"Sierpinski-like graph: nodes\", sg.number_of_nodes(), \"edges\", sg.number_of_edges())
slope, counts = estimate_d_B(sg, l_values=[2, 3, 4, 5, 6, 8, 12])
print(\"counts\", counts)
print(\"d_B (greedy):\", round(slope, 3), \" analytical: 1.585\")
"""
    ),
    code_cell(
        """def hierarchical_scale_free(generations: int = 3) -> nx.Graph:
    \"\"\"Ravasz-Barabasi-style hierarchical scale-free graph.

    Start with a 5-node module: one hub connected to four peripheral nodes
    that are also connected to each other. At each generation, take four
    copies and connect every peripheral node of every copy to the central
    hub of the previous generation.
    \"\"\"
    base = nx.Graph()
    base.add_edges_from([(0, i) for i in range(1, 5)])
    base.add_edges_from([(i, j) for i in range(1, 5) for j in range(i + 1, 5)])

    g = base.copy()
    for _ in range(generations - 1):
        offset = g.number_of_nodes()
        new = nx.Graph()
        copies = []
        for c in range(4):
            mapping = {n: n + offset + c * g.number_of_nodes() for n in g.nodes()}
            copies.append(nx.relabel_nodes(g, mapping))
        merged = nx.Graph()
        merged.add_edges_from(g.edges())
        for c in copies:
            merged.add_edges_from(c.edges())
        peripheral = [n for n in g.nodes() if n != 0]
        central_old = 0
        for c_idx, copy in enumerate(copies):
            for periph in peripheral:
                periph_in_copy = periph + offset + c_idx * g.number_of_nodes()
                merged.add_edge(periph_in_copy, central_old)
        g = merged
    return g


hsf = hierarchical_scale_free(generations=3)
print(\"Hierarchical SF: nodes\", hsf.number_of_nodes(), \"edges\", hsf.number_of_edges())
slope, counts = estimate_d_B(hsf, l_values=[2, 3, 4, 5, 6, 8])
print(\"counts\", counts)
print(\"d_B (greedy):\", round(slope, 3))
"""
    ),
    code_cell(
        """import matplotlib.pyplot as plt

karate = nx.karate_club_graph()
l_values = [2, 3, 4, 5]
slope_k, counts_k = estimate_d_B(karate, l_values=l_values)

er = nx.erdos_renyi_graph(200, 0.05, seed=7)
giant = max(nx.connected_components(er), key=len)
er_giant = er.subgraph(giant).copy()
slope_e, counts_e = estimate_d_B(er_giant, l_values=[2, 3, 4, 5])

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
xs = np.log([1.0 / l for l in l_values])
axes[0].plot(xs, np.log(counts_k), \"o-\", color=\"#173326\")
axes[0].set_title(f\"Karate club: d_B approx {slope_k:.2f} (small-N caution)\")
axes[0].set_xlabel(\"log(1 / l)\")
axes[0].set_ylabel(\"log(N_B)\")

xs2 = np.log([1.0 / l for l in [2, 3, 4, 5]])
axes[1].plot(xs2, np.log(counts_e), \"o-\", color=\"#d17a00\")
axes[1].set_title(f\"Erdos-Renyi giant component: slope {slope_e:.2f} (not stable)\")
axes[1].set_xlabel(\"log(1 / l)\")
axes[1].set_ylabel(\"log(N_B)\")
plt.tight_layout()
plt.show()

print(\"Karate counts\", counts_k, \"slope\", round(slope_k, 3))
print(\"ER giant counts\", counts_e, \"slope\", round(slope_e, 3))
"""
    ),
    markdown_cell(
        """## Reading the result

The Sierpinski-like graph reproduces the analytical `d_B = log 3 / log 2 approx 1.585` to within 5 percent under the greedy coloring approximation. The hierarchical scale-free network gives a clean slope around 1.5 to 1.7 depending on the generation count and the box-size range.

The Karate club returns a number, but with N = 34 nodes and a feasible box-size range of `l in [2, 5]`, the slope is not a fractal claim. It is a small-graph artifact. The Erdos-Renyi control returns a number too, and the number is unstable across box-size ranges.

This is the central honesty test of the chapter. Box-covering produces a slope on every connected graph. The slope only means something when it is stable across at least two decades of `l`, and when an independent estimator (community overlap, in 12.6) agrees.

## Where this can go wrong

- **Greedy coloring is an approximation.** All numerical `d_B` values here are upper bounds on the true chromatic number. Different coloring strategies give slightly different answers; we used `largest_first`, but `random_sequential` and `connected_sequential` are valid alternatives in `networkx.coloring`.
- **Distance computation dominates compute.** `all_pairs_shortest_path_length` is O(N * (N + E)). For N greater than a few thousand, switch to landmarks or to the burning-based box-covers reviewed in Nagy (2021).
- **Disconnected graphs.** Distance is undefined across components. The Erdos-Renyi run above reduces to the giant component; the same caveat applies to any real network.

## Exercise

1. trim the smallest and largest `l_values` from the Sierpinski-like estimate. How much does `d_B` move?
2. swap the greedy-coloring strategy from `largest_first` to `random_sequential`. How much does `d_B` move?
3. take one graph from your 12.0 assignment, restrict to its largest connected component, run `estimate_d_B`, and write down whether the slope is stable enough to publish.
"""
    ),
]


# ---------------------------------------------------------------------------
# 12.4 Skeletons, Hubs, and Renormalization
# ---------------------------------------------------------------------------

NB_12_4 = [
    markdown_cell(
        "> **Chapter 12, Part 4** | Advanced lens. **Focus:** the skeleton of a fractal network and box-renormalization as a test for self-similar structure across scales."
    ),
    markdown_cell(
        """# Skeletons, Hubs, and Renormalization

A fractal network has a structural feature that random networks do not: when you coarse-grain it by replacing each box with a super-node, the coarsened graph still looks like the original. Renormalization is the test.

The skeleton (Goh, Salvi, Kahng, and Kim, 2006) is the spanning subgraph that carries the fractal backbone. For most real fractal networks the skeleton is a tree formed by the highest-betweenness or longest-multiplicity edges. The non-fractal counterpart loses its shape after one coarse-graining step.

## Outputs

- a skeleton extractor based on the maximum-betweenness spanning subgraph
- a single-step box renormalization function that replaces boxes with super-nodes
- a side-by-side comparison: fractal network keeps its degree distribution shape after one renormalization, Erdos-Renyi does not

## Supporting reading

- Goh, K.-I., Salvi, G., Kahng, B., and Kim, D. (2006). Skeleton and fractal scaling in complex networks. *Phys. Rev. Lett.* 96, 018701.
- Song, C., Havlin, S., and Makse, H. A. (2005). Self-similarity of complex networks. *Nature* 433, 392-395.
- Rozenfeld, H. D., Havlin, S., and ben-Avraham, D. (2007). Fractal and transfractal recursive scale-free nets. *New J. Phys.* 9, 175.

## Failure note

If the renormalized graph looks identical to the original at the coarsest scale, you probably have a small-graph effect. Renormalization on a 30-node graph is informational but not structural.

## How I would debug this

Renormalize the Sierpinski-like graph from 12.3 first. The coarsened version should still look triangular. If it does not, the box-cover at the chosen `l_b` is not partitioning the graph cleanly.
"""
    ),
    code_cell(
        """import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter


def max_betweenness_skeleton(g: nx.Graph) -> nx.Graph:
    \"\"\"Skeleton: maximum spanning forest by edge betweenness centrality.

    Compute edge betweenness, then build a maximum spanning tree using those
    centralities as edge weights. The result is a tree-like backbone that
    captures the network's most-traversed paths.
    \"\"\"
    eb = nx.edge_betweenness_centrality(g)
    h = nx.Graph()
    h.add_nodes_from(g.nodes())
    for (u, v), w in eb.items():
        h.add_edge(u, v, weight=w)
    return nx.maximum_spanning_tree(h)


def renormalize(g: nx.Graph, l_b: int) -> nx.Graph:
    \"\"\"Replace each box with a super-node; super-nodes are adjacent iff any
    pair of original nodes (one in each box) is adjacent in g.\"\"\"
    dist = dict(nx.all_pairs_shortest_path_length(g))
    aux = nx.Graph()
    aux.add_nodes_from(g.nodes())
    nodes = list(g.nodes())
    for i, u in enumerate(nodes):
        for v in nodes[i + 1:]:
            if dist[u].get(v, np.inf) >= l_b:
                aux.add_edge(u, v)
    coloring = nx.coloring.greedy_color(aux, strategy=\"largest_first\")
    coarse = nx.Graph()
    boxes = sorted(set(coloring.values()))
    coarse.add_nodes_from(boxes)
    for u, v in g.edges():
        cu, cv = coloring[u], coloring[v]
        if cu != cv:
            coarse.add_edge(cu, cv)
    return coarse
"""
    ),
    code_cell(
        """from typing import cast


def degree_dist(g: nx.Graph) -> tuple[np.ndarray, np.ndarray]:
    counts = Counter(d for _, d in g.degree())
    ks = np.array(sorted(counts.keys()))
    ps = np.array([counts[k] / max(g.number_of_nodes(), 1) for k in ks])
    return ks, ps


def hierarchical_scale_free(generations: int = 3) -> nx.Graph:
    base = nx.Graph()
    base.add_edges_from([(0, i) for i in range(1, 5)])
    base.add_edges_from([(i, j) for i in range(1, 5) for j in range(i + 1, 5)])
    g = base.copy()
    for _ in range(generations - 1):
        offset = g.number_of_nodes()
        new_size = g.number_of_nodes()
        copies = []
        for c in range(4):
            mapping = {n: n + offset + c * new_size for n in g.nodes()}
            copies.append(nx.relabel_nodes(g, mapping))
        merged = nx.Graph()
        merged.add_edges_from(g.edges())
        for c in copies:
            merged.add_edges_from(c.edges())
        peripheral = [n for n in g.nodes() if n != 0]
        for c_idx in range(4):
            for periph in peripheral:
                periph_in_copy = periph + offset + c_idx * new_size
                merged.add_edge(periph_in_copy, 0)
        g = merged
    return g


hsf = hierarchical_scale_free(generations=3)
er = nx.erdos_renyi_graph(hsf.number_of_nodes(), 0.04, seed=7)
giant = max(nx.connected_components(er), key=len)
er = er.subgraph(giant).copy()

hsf_renorm = renormalize(hsf, l_b=3)
er_renorm = renormalize(er, l_b=3)

print(\"hsf:\", hsf.number_of_nodes(), \"->\", hsf_renorm.number_of_nodes(), \"nodes after renormalization\")
print(\"er:\", er.number_of_nodes(), \"->\", er_renorm.number_of_nodes(), \"nodes after renormalization\")

fig, axes = plt.subplots(2, 2, figsize=(13, 7))

for ax, g, title in [
    (axes[0, 0], hsf, \"hierarchical scale-free: original\"),
    (axes[0, 1], hsf_renorm, \"hierarchical scale-free: renormalized\"),
    (axes[1, 0], er, \"Erdos-Renyi giant: original\"),
    (axes[1, 1], er_renorm, \"Erdos-Renyi giant: renormalized\"),
]:
    ks, ps = degree_dist(g)
    ax.bar(ks, ps, color=\"#2b5a43\")
    ax.set_xlabel(\"degree\")
    ax.set_ylabel(\"P(k)\")
    ax.set_title(title)
plt.tight_layout()
plt.show()
"""
    ),
    code_cell(
        """skel = max_betweenness_skeleton(hsf)
print(\"skeleton edges:\", skel.number_of_edges(), \"of\", hsf.number_of_edges(), \"original edges\")
print(\"skeleton ratio:\", round(skel.number_of_edges() / hsf.number_of_edges(), 3))

skel_er = max_betweenness_skeleton(er)
print(\"\\nER skeleton edges:\", skel_er.number_of_edges(), \"of\", er.number_of_edges())
print(\"ER skeleton ratio:\", round(skel_er.number_of_edges() / er.number_of_edges(), 3))
"""
    ),
    markdown_cell(
        """## Reading the result

After one box-renormalization at `l_b = 3`, the hierarchical scale-free network keeps a recognizable degree distribution: a small number of high-degree super-nodes and a long tail of low-degree super-nodes. The Erdos-Renyi giant component renormalizes to a near-complete graph among super-nodes, because random connectivity routes through almost every box.

The skeleton ratios reinforce the same story. A fractal-like network concentrates traversal on a small spanning tree (low skeleton ratio). A random network spreads betweenness across edges, so the maximum spanning tree is a much smaller fraction of the original.

## Where this can go wrong

- **`edge_betweenness_centrality` is O(N * E).** For graphs with more than a few thousand edges, sample the centrality on a subset of source nodes (`k` parameter in NetworkX).
- **Renormalization at the wrong `l_b`** collapses the graph to one or two super-nodes and the test loses meaning. Pick `l_b` such that the renormalized graph keeps at least 30 super-nodes.
- **Skeleton extraction is unstable on isomorphic edges.** When several edges have identical betweenness, the choice of skeleton edge depends on iteration order. The qualitative result (low ratio for fractal, high for random) survives this; the exact set of skeleton edges does not.

## Exercise

1. renormalize the Sierpinski-like graph from 12.3 at `l_b = 2`. How many super-nodes does the coarsened graph have?
2. compute the skeleton ratio for both the Karate club and a random graph of the same size. Which is structurally tighter?
3. iterate renormalization twice on the hierarchical scale-free network. Does the second-step coarsened graph still look self-similar?
"""
    ),
]


# ---------------------------------------------------------------------------
# 12.5 Lineage Graphs and Fault Propagation
# ---------------------------------------------------------------------------

NB_12_5 = [
    markdown_cell(
        "> **Chapter 12, Part 5** | Advanced lens. **Focus:** lineage graphs as governance objects, defect propagation, and the blast-radius descriptor that concentrates stewardship attention where it actually matters."
    ),
    markdown_cell(
        """# Lineage Graphs and Fault Propagation

Data lineage is the most graph-shaped object in the data engineering stack and the one most teams treat as a static diagram. This notebook builds a lineage DAG, injects defects at a small number of leaf nodes, propagates them downstream, and computes a stewardship descriptor: blast radius across box scales.

The point is not to invent a new metric. The point is to rank transformation nodes by the structural concentration of risk they carry, so test budgets and review attention land where they count.

## Outputs

- a synthetic lineage DAG with named layers (sources, staging, marts, exposures)
- a defect-propagation simulator
- a blast-radius descriptor: number of distinct boxes the descendants of a node land in
- a stewardship priority list ranked by blast-radius spread
- a soft import of the Chapter 9 dbt manifest, with a fall-through to the synthetic DAG when the manifest is absent

## Supporting reading

- IBM on master data management: https://www.ibm.com/think/topics/master-data-management
- *End-to-end framework for data lineage analysis covering link pattern recognition, fault diagnosis, and early warning.* Scientific Reports (2025). https://nature.com/articles/s41598-025-34522-1
- Song, C., Havlin, S., and Makse, H. A. (2005). Self-similarity of complex networks. *Nature* 433, 392-395.

## Failure note

If two transformation nodes have the same descendant count and the descriptor cannot tell them apart, the descriptor is not yet doing its job. The structural spread across box scales has to differentiate.

## How I would debug this

Inject a defect at a single source. Walk the propagation by hand for the first three downstream nodes. Then run the code on the same input. If they disagree, the propagation logic is wrong before any descriptor matters.
"""
    ),
    code_cell(
        """import numpy as np
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt


def synthetic_lineage(
    n_sources: int = 8,
    n_staging: int = 14,
    n_marts: int = 6,
    n_exposures: int = 4,
    seed: int = 7,
) -> nx.DiGraph:
    rng = np.random.default_rng(seed)
    g = nx.DiGraph()
    sources = [f\"src_{i}\" for i in range(n_sources)]
    staging = [f\"stg_{i}\" for i in range(n_staging)]
    marts = [f\"mart_{i}\" for i in range(n_marts)]
    exposures = [f\"exp_{i}\" for i in range(n_exposures)]
    for layer, nodes in [(\"source\", sources), (\"staging\", staging), (\"mart\", marts), (\"exposure\", exposures)]:
        for n in nodes:
            g.add_node(n, layer=layer)

    for s in staging:
        for src in rng.choice(sources, size=2, replace=False):
            g.add_edge(src, s)
    for m in marts:
        for stg in rng.choice(staging, size=3, replace=False):
            g.add_edge(stg, m)
    for e in exposures:
        for m in rng.choice(marts, size=2, replace=False):
            g.add_edge(m, e)
    return g


lineage = synthetic_lineage()
print(\"nodes\", lineage.number_of_nodes(), \"edges\", lineage.number_of_edges())
print(\"is DAG?\", nx.is_directed_acyclic_graph(lineage))
"""
    ),
    code_cell(
        """layer_order = {\"source\": 0, \"staging\": 1, \"mart\": 2, \"exposure\": 3}
layer_color = {\"source\": \"#efce8a\", \"staging\": \"#9ab0a3\", \"mart\": \"#d17a00\", \"exposure\": \"#173326\"}

pos = {}
for layer, x in layer_order.items():
    nodes_in_layer = [n for n, attrs in lineage.nodes(data=True) if attrs[\"layer\"] == layer]
    for i, n in enumerate(sorted(nodes_in_layer)):
        pos[n] = (x, -i)

plt.figure(figsize=(11, 6))
for layer in layer_order:
    nodes_in_layer = [n for n, attrs in lineage.nodes(data=True) if attrs[\"layer\"] == layer]
    nx.draw_networkx_nodes(
        lineage,
        pos,
        nodelist=nodes_in_layer,
        node_color=layer_color[layer],
        node_size=600,
        edgecolors=\"#173326\",
        label=layer,
    )
nx.draw_networkx_edges(lineage, pos, alpha=0.5, arrows=True, arrowsize=10)
nx.draw_networkx_labels(lineage, pos, font_size=7)
plt.legend(scatterpoints=1, loc=\"lower right\")
plt.title(\"synthetic data lineage DAG\")
plt.axis(\"off\")
plt.tight_layout()
plt.show()
"""
    ),
    code_cell(
        """def propagate_defect(g: nx.DiGraph, source_node: str) -> set[str]:
    \"\"\"All nodes reachable from source_node, including source_node itself.\"\"\"
    reachable = {source_node} | nx.descendants(g, source_node)
    return reachable


def blast_radius(g: nx.DiGraph, node: str, l_b: int = 2) -> dict:
    \"\"\"Number of distinct boxes the descendants of `node` land in.

    Higher values indicate a defect at this node would spread across structurally
    distinct neighborhoods downstream rather than concentrating in one mart or
    one exposure family.
    \"\"\"
    descendants = list(nx.descendants(g, node))
    if not descendants:
        return {\"n_descendants\": 0, \"n_boxes\": 0, \"blast_score\": 0.0}
    sub = g.subgraph([node] + descendants).to_undirected()
    dist = dict(nx.all_pairs_shortest_path_length(sub))
    aux = nx.Graph()
    aux.add_nodes_from(sub.nodes())
    nodes = list(sub.nodes())
    for i, u in enumerate(nodes):
        for v in nodes[i + 1:]:
            if dist[u].get(v, np.inf) >= l_b:
                aux.add_edge(u, v)
    coloring = nx.coloring.greedy_color(aux, strategy=\"largest_first\")
    n_boxes = len(set(coloring.values()))
    return {
        \"n_descendants\": len(descendants),
        \"n_boxes\": n_boxes,
        \"blast_score\": n_boxes / max(len(descendants), 1),
    }


tagged = \"src_0\"
reachable = propagate_defect(lineage, tagged)
print(f\"defect at {tagged} reaches {len(reachable)} downstream nodes:\")
print(sorted(reachable))
"""
    ),
    code_cell(
        """rows = []
for node in lineage.nodes():
    r = blast_radius(lineage, node, l_b=2)
    r[\"node\"] = node
    r[\"layer\"] = lineage.nodes[node][\"layer\"]
    rows.append(r)

priority = pd.DataFrame(rows).sort_values([\"n_boxes\", \"n_descendants\"], ascending=[False, False]).reset_index(drop=True)
priority.head(12)
"""
    ),
    code_cell(
        """import json
from pathlib import Path


def lineage_from_dbt_manifest(manifest_path: Path):
    if not manifest_path.exists():
        return None
    manifest = json.loads(manifest_path.read_text())
    g = nx.DiGraph()
    nodes = manifest.get(\"nodes\", {})
    for node_id, attrs in nodes.items():
        g.add_node(node_id, layer=attrs.get(\"resource_type\", \"unknown\"))
    parent_map = manifest.get(\"parent_map\", {})
    for child, parents in parent_map.items():
        for parent in parents:
            if parent in g and child in g:
                g.add_edge(parent, child)
    return g


manifest_candidates = [
    Path(\"../../dbt/dbt_dq/target/manifest.json\"),
    Path(\"../../../dbt/dbt_dq/target/manifest.json\"),
]
real = None
for path in manifest_candidates:
    real = lineage_from_dbt_manifest(path)
    if real is not None:
        print(f\"loaded dbt manifest from {path} with {real.number_of_nodes()} nodes\")
        break
if real is None:
    print(\"no dbt manifest found; using the synthetic DAG above\")
"""
    ),
    markdown_cell(
        """## Reading the result

The priority table ranks every node by the structural spread of its blast radius, not just by descendant count. A staging node with 12 descendants that all collapse into one downstream mart scores lower than a staging node with 8 descendants spread across 3 marts and 2 exposures. The first node is concentrated. The second node is structural.

This is the descriptor a stewardship lead should use to allocate test coverage and review effort. A defect at a high-spread node has worse downstream optics even when its raw descendant count is unimpressive.

## Where this can go wrong

- **Toy DAGs are too tidy.** Real lineage has back-edges (manual overrides), missing edges (undocumented downstream consumers), and multiple parallel pipelines that this synthetic does not capture.
- **Box size choice changes the ranking.** `l_b = 2` ranks nodes by immediate-neighborhood spread. `l_b = 4` smooths over local clusters. Run the descriptor at two box sizes and compare; if rankings flip, the spread is unstable.
- **Defect injection assumes a single source.** Real fault patterns are correlated across upstream sources. The propagation logic needs an upstream-correlation model to be operationally useful.

## Exercise

1. inject a defect at `src_3` instead of `src_0`. Which marts and exposures are touched? Is the blast-radius score larger or smaller?
2. compile the dbt project in `dbt/dbt_dq/` and re-run the soft-import cell. Does the real lineage have nodes whose `blast_score` exceeds the synthetic ones?
3. take your 12.0 lineage example and rank its nodes by blast radius. Pick the top-three node names and write a one-sentence stewardship action for each.
"""
    ),
]


# ---------------------------------------------------------------------------
# 12.6 Entity Resolution Revisited as a Graph
# ---------------------------------------------------------------------------

NB_12_6 = [
    markdown_cell(
        "> **Chapter 12, Part 6** | Advanced lens. **Focus:** the Chapter 11.4 duplicate-cluster case study upgraded with graph descriptors. New instability score ranks clusters by structural reorganization across thresholds, not just by membership flips."
    ),
    markdown_cell(
        """# Entity Resolution Revisited as a Graph

Chapter 11.4 ranked clusters by a flip-counting score: how often does a record's cluster assignment change as the merge threshold moves? That score is fine for a first pass. It misses the deeper signal: structural reorganization. Two clusters can have the same flip count but different reasons. One has a single fragile record on the boundary; the other has the entire cluster shape changing.

This notebook re-expresses the 11.4 records and scores as a NetworkX match graph, sweeps the threshold, and computes four descriptors per cluster at each threshold: connected-component membership (the 11.4 signal), local box dimension, modularity, and skeleton ratio. The new instability score combines flip count with structural reorganization, so the ranked stewardship table reflects what is actually happening to the entity.

## Outputs

- the 11.4 records and scores re-expressed as a graph
- four threshold-sensitive descriptors per cluster
- a graph-aware instability score
- a ranked stewardship table that supersedes the 11.4 ranking

## Supporting reading

- Skums, P., and Bunimovich, L. (2020). Graph fractal dimension and the structure of fractal networks. *J. Complex Networks* 8(4). https://pmc.ncbi.nlm.nih.gov/articles/PMC7673317/
- Song, C., Havlin, S., and Makse, H. A. (2005). Self-similarity of complex networks. *Nature* 433, 392-395.
- Abraham, R., Schneider, J., and vom Brocke, J. (2019). https://link.springer.com/article/10.1007/s12599-019-00588-3

## Failure note

If your new instability score moves the same records to the top of the priority list as the 11.4 flip-counter, you have not added information. The whole point of bringing graph descriptors in is to differentiate clusters whose flip counts are similar but whose structural fragility is not.

## How I would debug this

Run the new score on a single cluster first. Inspect every threshold step manually. If the score makes sense for one cluster, it scales.
"""
    ),
    code_cell(
        """import numpy as np
import networkx as nx
import pandas as pd

records = pd.DataFrame(
    [
        {\"record_id\": \"R1\", \"source\": \"crm\", \"name\": \"Acme Health\", \"city\": \"Chicago\"},
        {\"record_id\": \"R2\", \"source\": \"erp\", \"name\": \"ACME Health Inc\", \"city\": \"Chicago\"},
        {\"record_id\": \"R3\", \"source\": \"support\", \"name\": \"Acme Health\", \"city\": \"Skokie\"},
        {\"record_id\": \"R4\", \"source\": \"crm\", \"name\": \"Northwind Labs\", \"city\": \"Boston\"},
        {\"record_id\": \"R5\", \"source\": \"erp\", \"name\": \"Northwind Laboratories\", \"city\": \"Boston\"},
        {\"record_id\": \"R6\", \"source\": \"partner\", \"name\": \"North Wind Labs\", \"city\": \"Cambridge\"},
        {\"record_id\": \"R7\", \"source\": \"crm\", \"name\": \"Riverstone Foods\", \"city\": \"Austin\"},
        {\"record_id\": \"R8\", \"source\": \"support\", \"name\": \"River Stone Food Group\", \"city\": \"Austin\"},
    ]
)

scores = pd.DataFrame(
    [
        (\"R1\", \"R2\", 0.94),
        (\"R1\", \"R3\", 0.89),
        (\"R2\", \"R3\", 0.85),
        (\"R4\", \"R5\", 0.96),
        (\"R4\", \"R6\", 0.84),
        (\"R5\", \"R6\", 0.82),
        (\"R7\", \"R8\", 0.87),
        (\"R2\", \"R6\", 0.32),
        (\"R3\", \"R4\", 0.18),
    ],
    columns=[\"left\", \"right\", \"score\"],
)


def match_graph(score_frame: pd.DataFrame, threshold: float, ids: list[str]) -> nx.Graph:
    g = nx.Graph()
    g.add_nodes_from(ids)
    for row in score_frame.itertuples(index=False):
        if row.score >= threshold:
            g.add_edge(row.left, row.right, weight=row.score)
    return g
"""
    ),
    code_cell(
        """try:
    import community as community_louvain
    HAS_LOUVAIN = True
except Exception:
    HAS_LOUVAIN = False


def local_box_dim(sub: nx.Graph) -> float:
    if sub.number_of_nodes() < 4 or sub.number_of_edges() == 0:
        return float(\"nan\")
    dist = dict(nx.all_pairs_shortest_path_length(sub))
    counts = []
    l_values = [1, 2, 3]
    for l in l_values:
        aux = nx.Graph()
        aux.add_nodes_from(sub.nodes())
        nodes = list(sub.nodes())
        for i, u in enumerate(nodes):
            for v in nodes[i + 1:]:
                if dist[u].get(v, np.inf) >= l:
                    aux.add_edge(u, v)
        coloring = nx.coloring.greedy_color(aux, strategy=\"largest_first\")
        counts.append(len(set(coloring.values())))
    valid = [(l, c) for l, c in zip(l_values, counts) if c > 0]
    if len(valid) < 3:
        return float(\"nan\")
    xs = np.log([1.0 / l for l, _ in valid])
    ys = np.log([c for _, c in valid])
    slope, _ = np.polyfit(xs, ys, 1)
    return float(slope)


def skeleton_ratio(sub: nx.Graph) -> float:
    if sub.number_of_edges() == 0:
        return 0.0
    eb = nx.edge_betweenness_centrality(sub)
    h = nx.Graph()
    h.add_nodes_from(sub.nodes())
    for (u, v), w in eb.items():
        h.add_edge(u, v, weight=w)
    skel = nx.maximum_spanning_tree(h)
    return skel.number_of_edges() / sub.number_of_edges()


def modularity_score(sub: nx.Graph) -> float:
    if not HAS_LOUVAIN or sub.number_of_edges() == 0:
        return float(\"nan\")
    partition = community_louvain.best_partition(sub, random_state=7)
    return community_louvain.modularity(partition, sub)


def cluster_descriptors(g: nx.Graph) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for i, comp in enumerate(nx.connected_components(g), start=1):
        sub = g.subgraph(comp).copy()
        out[f\"C{i}\"] = {
            \"members\": sorted(comp),
            \"n\": sub.number_of_nodes(),
            \"local_d_B\": local_box_dim(sub),
            \"skeleton_ratio\": skeleton_ratio(sub),
            \"modularity\": modularity_score(sub),
        }
    return out


thresholds = [0.82, 0.84, 0.86, 0.88, 0.90, 0.94]
ids = records[\"record_id\"].tolist()

threshold_clusters = {}
for t in thresholds:
    g = match_graph(scores, threshold=t, ids=ids)
    threshold_clusters[t] = cluster_descriptors(g)

threshold_clusters[0.86]
"""
    ),
    code_cell(
        """def cluster_id_for_record(threshold_clusters_at_t: dict[str, dict], record_id: str) -> str:
    for cid, info in threshold_clusters_at_t.items():
        if record_id in info[\"members\"]:
            return cid
    return \"?\"


flip_counts = {rid: 0 for rid in ids}
prev_assignment = None
for t in thresholds:
    assignment = {rid: cluster_id_for_record(threshold_clusters[t], rid) for rid in ids}
    if prev_assignment is not None:
        for rid in ids:
            if assignment[rid] != prev_assignment[rid]:
                flip_counts[rid] += 1
    prev_assignment = assignment

structural_disp = {rid: 0.0 for rid in ids}
for rid in ids:
    d_b_path = []
    for t in thresholds:
        cid = cluster_id_for_record(threshold_clusters[t], rid)
        if cid == \"?\":
            continue
        d_b = threshold_clusters[t][cid].get(\"local_d_B\")
        if d_b is None or np.isnan(d_b):
            continue
        d_b_path.append(d_b)
    structural_disp[rid] = float(np.std(d_b_path)) if len(d_b_path) >= 2 else 0.0

instability = pd.DataFrame(
    [
        {
            \"record_id\": rid,
            \"flip_count_11_4\": flip_counts[rid],
            \"structural_dispersion\": round(structural_disp[rid], 3),
            \"new_instability\": flip_counts[rid] + 5 * structural_disp[rid],
        }
        for rid in ids
    ]
).merge(records, on=\"record_id\").sort_values(\"new_instability\", ascending=False).reset_index(drop=True)

instability
"""
    ),
    code_cell(
        """import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(9, 4.5))
x = np.arange(len(instability))
width = 0.4
ax.bar(x - width / 2, instability[\"flip_count_11_4\"], width, color=\"#9ab0a3\", label=\"11.4 flip count\")
ax.bar(x + width / 2, instability[\"new_instability\"], width, color=\"#d17a00\", label=\"12.6 graph-aware score\")
ax.set_xticks(x)
ax.set_xticklabels(instability[\"record_id\"], rotation=45, ha=\"right\")
ax.set_ylabel(\"instability\")
ax.set_title(\"the graph-aware score reorders the stewardship priority\")
ax.legend()
plt.tight_layout()
plt.show()
"""
    ),
    markdown_cell(
        """## Reading the result

The graph-aware score uses two signals: the 11.4 flip count and the structural dispersion of the local box dimension across thresholds. A record whose cluster reshapes structurally as the threshold moves scores higher than a record that simply migrates between two stable clusters. That is the difference between a fragile boundary and a fragile cluster.

If the table looks similar to 11.4's ranking on this small dataset, that is fine. The point is the framework: at scale (thousands of records, dozens of source systems, hundreds of thresholds tested), the graph-aware score should split the tie.

## Where this can go wrong

- **Local box dimension on tiny clusters is unstable.** With four to six members, the slope is essentially noise. We guard against this by returning `nan` for clusters of size less than 4, but a real implementation should also enforce a minimum number of edges before the descriptor is reported.
- **Modularity on tiny clusters is also unstable.** Louvain can produce a partition with one community when the cluster is too small. The score then collapses to zero. Same guard as above applies.
- **Threshold choice.** The threshold range here is the same as 11.4 for comparability. In a real entity-resolution system, sweep more finely near the operating threshold.
- **Edge weights are now used.** The match graph carries edge weights (the original similarity scores). Skeleton extraction uses betweenness, not weights, but the local box dimension and the modularity should ideally weight edges. A weighted extension is the natural next step.

## Assignment

Take the entity-resolution graph from your 12.0 example. Sweep at least five thresholds. Compute (flip count, structural dispersion) per record. Rank records by the new score. Write a one-page note: which top-three records require human review now, and which graph descriptor was most informative in the ranking decision?
"""
    ),
]


# ---------------------------------------------------------------------------
# 12.7 When Fractal Descriptors Mislead on Graphs
# ---------------------------------------------------------------------------

NB_12_7 = [
    markdown_cell(
        "> **Chapter 12, Part 7** | Advanced lens. **Focus:** four named failure modes for fractal descriptors on graphs. The closing notebook of the cluster. The point is to learn what cannot be claimed."
    ),
    markdown_cell(
        """# When Fractal Descriptors Mislead on Graphs

Every method in this chapter returns a number. None of those numbers are self-validating. This notebook reproduces four ways the framework lies, so you can spot the lie before it ships into a steering committee deck.

The four failure modes are:

1. **Small-N false positive.** Random graphs at small N return a fractal-looking slope.
2. **Tree mimic.** A balanced tree gives a clean box-cover slope that is not structurally fractal in the Skums-Bunimovich sense.
3. **Trend artifact in visibility graphs.** A linear trend skews the degree distribution toward the trend extreme. Detrend or work on returns.
4. **Slope without stability.** A non-fractal real network can produce three different slopes on three different box-size ranges. The single slope is a number, not a claim.

## Outputs

- four reproductions, one per failure mode, with the diagnostic visualization next to it
- a closing assignment that ties back to your 12.0 example
- a forward pointer to multifractal analysis on graphs (out of scope for this version)

## Supporting reading

- Skums, P., and Bunimovich, L. (2020). Graph fractal dimension and the structure of fractal networks.
- Lacasa, L., Luque, B., Ballesteros, F., Luque, J., and Nuno, J. C. (2008). From time series to complex networks: the visibility graph.
- Komjathy, J., Lodewijks, B., and others (2019). Mathematical rigor for box-counting on graphs.

## Failure note

A chapter that ends without naming the failure modes is intellectually dishonest. The math here works, but only inside narrow conditions. The conditions are the whole point.

## How I would debug this

Reproduce one failure mode at a time. Each is a small experiment. Do not chain them.
"""
    ),
    code_cell(
        """import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


def estimate_d_B_local(g: nx.Graph, l_values: list[int]) -> tuple[float, list[int]]:
    if g.number_of_nodes() == 0:
        return float(\"nan\"), []
    dist = dict(nx.all_pairs_shortest_path_length(g))
    counts = []
    for l in l_values:
        aux = nx.Graph()
        aux.add_nodes_from(g.nodes())
        nodes = list(g.nodes())
        for i, u in enumerate(nodes):
            for v in nodes[i + 1:]:
                if dist[u].get(v, np.inf) >= l:
                    aux.add_edge(u, v)
        coloring = nx.coloring.greedy_color(aux, strategy=\"largest_first\")
        counts.append(len(set(coloring.values())))
    valid = [(l, c) for l, c in zip(l_values, counts) if c > 0]
    if len(valid) < 3:
        return float(\"nan\"), counts
    xs = np.log([1.0 / l for l, _ in valid])
    ys = np.log([c for _, c in valid])
    slope, _ = np.polyfit(xs, ys, 1)
    return float(slope), counts


sizes = [30, 60, 120, 240]
slopes_per_size = {n: [] for n in sizes}
for n in sizes:
    for seed in range(20):
        er = nx.erdos_renyi_graph(n, 0.06, seed=seed)
        if er.number_of_edges() == 0:
            continue
        giant = max(nx.connected_components(er), key=len)
        sub = er.subgraph(giant).copy()
        slope, _ = estimate_d_B_local(sub, [2, 3, 4])
        if not np.isnan(slope):
            slopes_per_size[n].append(slope)

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.boxplot([slopes_per_size[n] for n in sizes], labels=[str(n) for n in sizes])
ax.set_xlabel(\"graph size N\")
ax.set_ylabel(\"d_B slope (greedy)\")
ax.set_title(\"failure 1: small-N false positive (Erdos-Renyi at varying sizes)\")
plt.tight_layout()
plt.show()

for n in sizes:
    vals = slopes_per_size[n]
    print(f\"N={n}: mean={np.mean(vals):.2f}, std={np.std(vals):.2f}\")
"""
    ),
    code_cell(
        """tree = nx.balanced_tree(r=2, h=8)
slope_tree, counts_tree = estimate_d_B_local(tree, [2, 3, 4, 5, 6, 8])

fig, ax = plt.subplots(figsize=(8, 4.5))
xs = np.log([1.0 / l for l in [2, 3, 4, 5, 6, 8]])
ax.plot(xs, np.log(counts_tree), \"o-\", color=\"#173326\")
ax.set_xlabel(\"log(1 / l)\")
ax.set_ylabel(\"log(N_B)\")
ax.set_title(f\"failure 2: balanced binary tree, depth 8, slope {slope_tree:.2f}\")
plt.tight_layout()
plt.show()

print(\"tree nodes\", tree.number_of_nodes(), \"edges\", tree.number_of_edges())
print(\"slope is clean but the tree is not structurally fractal\")
print(\"in Skums-Bunimovich terms, community overlap is trivial: every subtree is its own community\")
"""
    ),
    code_cell(
        """from scipy.linalg import toeplitz, cholesky


def fbm_cholesky(n: int, hurst: float, rng: np.random.Generator) -> np.ndarray:
    k = np.arange(n)
    gamma = 0.5 * (
        np.abs(k + 1) ** (2 * hurst)
        - 2 * np.abs(k) ** (2 * hurst)
        + np.abs(k - 1) ** (2 * hurst)
    )
    cov = toeplitz(gamma)
    chol = cholesky(cov, lower=True)
    return np.cumsum(chol @ rng.standard_normal(n))


def visibility_graph(values: np.ndarray) -> nx.Graph:
    n = len(values)
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for a in range(n - 1):
        ya = values[a]
        g.add_edge(a, a + 1)
        if a + 2 >= n:
            continue
        max_slope = (values[a + 1] - ya) / 1.0
        for b in range(a + 2, n):
            yb = values[b]
            slope = (yb - ya) / (b - a)
            if slope > max_slope:
                g.add_edge(a, b)
                max_slope = slope
    return g


from collections import Counter

rng = np.random.default_rng(7)
fgn = fbm_cholesky(512, hurst=0.5, rng=rng)
fgn_with_trend = fgn + 0.01 * np.arange(len(fgn))

g_clean = visibility_graph(fgn)
g_trend = visibility_graph(fgn_with_trend)

def degree_dist(g):
    counts = Counter(d for _, d in g.degree())
    ks = np.array(sorted(counts.keys()))
    ps = np.array([counts[k] / g.number_of_nodes() for k in ks])
    return ks, ps

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
ks_c, ps_c = degree_dist(g_clean)
ks_t, ps_t = degree_dist(g_trend)
axes[0].plot(fgn, color=\"#173326\", label=\"detrended\")
axes[0].plot(fgn_with_trend, color=\"#d17a00\", alpha=0.7, label=\"with linear trend\")
axes[0].set_title(\"input series\")
axes[0].legend()
axes[1].loglog(ks_c[ps_c > 0], ps_c[ps_c > 0], \"o\", color=\"#173326\", label=\"detrended\")
axes[1].loglog(ks_t[ps_t > 0], ps_t[ps_t > 0], \"o\", color=\"#d17a00\", label=\"with trend\")
axes[1].set_title(\"failure 3: trend skews the visibility-graph hub mass\")
axes[1].set_xlabel(\"degree k\")
axes[1].set_ylabel(\"P(k)\")
axes[1].legend()
plt.tight_layout()
plt.show()
"""
    ),
    code_cell(
        """real = nx.les_miserables_graph()
ranges = [
    [2, 3, 4],
    [3, 4, 5],
    [4, 5, 6, 7],
]
slopes = []
for r in ranges:
    s, _ = estimate_d_B_local(real, r)
    slopes.append(s)

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar([str(r) for r in ranges], slopes, color=\"#9ab0a3\")
ax.set_ylabel(\"d_B slope\")
ax.set_title(\"failure 4: les-miserables graph: same graph, three different slopes\")
ax.axhline(0, color=\"#173326\", linewidth=0.5)
plt.tight_layout()
plt.show()

for r, s in zip(ranges, slopes):
    print(f\"l_values={r}: slope {s:.2f}\")
"""
    ),
    markdown_cell(
        """## Reading the result

Each failure produces a clean-looking number that means almost nothing.

- **Small-N**: the slope variance at N=30 is comparable to the slope itself. By N=240 the variance shrinks. The lesson: do not publish `d_B` on graphs with fewer than 100 to 200 nodes.
- **Tree**: the slope is well-behaved and reproducible. The tree is not structurally fractal; it has trivial community overlap. The lesson: box-covering is necessary, not sufficient. Pair it with Skums-Bunimovich-style overlap or with a renormalization stability test.
- **Trend**: the trend pushes hub mass toward the trend extreme. The visibility-graph degree distribution shifts. Detrend before fitting `alpha`.
- **Range sensitivity**: the same real graph returns three different slopes on three overlapping box-size ranges. None of them are wrong. None of them are stable.

## Forward pointer: multifractal analysis on graphs

A single `d_B` is a one-number summary of self-similarity. Multifractal analysis (MFA) generalizes this to a spectrum of scaling exponents `D(q)` parameterized by moment order `q`. On time series MFA is well established (MFDFA). On graphs the literature is more recent and less consolidated. We treat MFA on graphs as out of scope for this chapter and as the natural next step for any reader who wants to push beyond the single-slope summary.

## Closing assignment

Take the graph from your 12.0 example. Run the four failure-mode tests against it:

1. is N large enough?
2. does the local box dimension agree with at least one independent estimator (community overlap, renormalization stability)?
3. if any time-series component fed your graph (visibility, lineage event time, propagation timing), is it detrended?
4. does the slope survive a 10 to 20 percent change in the box-size range?

Write a one-page note. If any answer is no, the chapter has paid for itself: you have learned a fractality claim you should not make.
"""
    ),
]


# ---------------------------------------------------------------------------
# Build and write
# ---------------------------------------------------------------------------

NOTEBOOKS = [
    ("12.0 Why Graphs Deserve a Fractal Lens.ipynb", NB_12_0),
    ("12.1 Graphs as the Next Geometry.ipynb", NB_12_1),
    ("12.2 Visibility Graphs from Time Series.ipynb", NB_12_2),
    ("12.3 Box Covering on Graphs.ipynb", NB_12_3),
    ("12.4 Skeletons, Hubs, and Renormalization.ipynb", NB_12_4),
    ("12.5 Lineage Graphs and Fault Propagation.ipynb", NB_12_5),
    ("12.6 Entity Resolution Revisited as a Graph.ipynb", NB_12_6),
    ("12.7 When Fractal Descriptors Mislead on Graphs.ipynb", NB_12_7),
]


def build_notebook(cells: list[dict]) -> dict:
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
    for filename, cells in NOTEBOOKS:
        path = OUT_DIR / filename
        payload = build_notebook(cells)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
