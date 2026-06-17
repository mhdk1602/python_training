# Chapter 12 - Fractal Graphs: From Time Series to Networks to Lineage

> **Ticket:** CH-12-fractal-graphs
> **Author:** mhdk1602
> **Date:** 2026-05-01
> **Status:** Spec (design stage of the 4-stage loop)
> **Predecessors:** Chapter 11 (Fractals, Pattern Recognition, Governance), Chapter 9.3 (MDM and Governance), Chapter 7 (Embeddings), and the Hurst-coupling research repo `mhdk1602/fractal-pv-coupling`.

---

## TL;DR (answer-first)

1. **The answer is a Chapter 12 cluster titled `Fractal Graphs`** that formalizes graph theory inside the curriculum and shows two bridges the existing chapters have been pointing at all along: the **visibility graph** (time series → graph) and **box-covering on graphs** (image box-counting → graph dimension).
2. **Next step:** approve this spec, then move to `plan.md` (P###/W###/K###/X###) so notebook authoring can start. Target shipping `12.0–12.4` first as the conceptual backbone, then `12.5–12.7` as the enterprise translation, then `12.8` as the public studio page.
3. **Why this is the right path:**
   - `notebooks/11/11.3` already cites Song-Havlin-Makse (2005), Skums-Bunimovich (2020), and Fronczak et al. (2024). The Chapter 11 supporting reading list is a Chapter 12 syllabus that has not been written yet.
   - The string `networkx` does not appear in any committed notebook. Graph theory is conspicuously absent for a curriculum that already has lineage graphs, entity-resolution graphs, and dbt DAGs scattered across other chapters.
   - The author's own `fractal-pv-coupling` paper (Malemapti Hari, 2026) studies Hurst-style fractal coupling on time series. The visibility graph reframes that exact research as graph-theoretic and lets the chapter inherit a published, citable provenance instead of starting from a toy example.

---

## Ask behind the ask

| Layer | What it actually asks for |
|---|---|
| Stated ask | A chapter that intuitively links fractals and graphs. |
| Deeper ask | Extend the Chapter 11 thread without breaking its bounded-claim style; make graph theory a first-class teaching object; give the published fractal-coupling research a curriculum home. |
| Implication | Chapter 12 is a cluster (notebooks plus a studio page), not a one-off notebook. Without the cluster, two production bridges in the repo (entity resolution, lineage) keep relying on procedural code that hides the graph underneath. |
| Recommendation | Ship the cluster. Treat `12.6` as the canonical follow-up to `11.4` so the duplicate-cluster case study graduates from union-find to graph fractal descriptors. |

---

## S: Success criteria

- **S001: Read by a self-taught engineer.** A reader who has done Chapters 0–9 and Chapter 11 should be able to finish Chapter 12 without reaching for a graph-theory textbook. The chapter teaches the graph language it needs.
- **S002: Bounded claims.** The chapter must keep the Chapter 11 epistemic discipline. No notebook should suggest "enterprise data is fractal." Every fractal claim about a graph must be tested against scale stability, finite-size effects, and at least one independent estimator.
- **S003: Two bridges land.** Visibility graph (time series → graph) and box-covering (image → graph) both produce a working measurement on real or realistic data, not only on toy fractal models.
- **S004: Enterprise translation works without metaphor.** Lineage and entity-resolution sections produce decisions a steward could act on, not lyrical analogies.
- **S005: Studio page parity.** `fractal-graphs.html` matches the visual and interactive register of `fractals-governance.html` and `embeddings-bridge.html`. Same shell, same Manrope/Fraunces type, same eyebrow-section idiom.
- **S006: Reuse over re-derivation.** The chapter pulls from existing repo material (Chapter 11.4 records, dbt manifest in `dbt/dbt_dq/`, Chapter 7 embedding chunks) before inventing new toy data.
- **S007: Failure-aware.** Every notebook closes with at least one explicit failure mode and one stewardship implication, matching the Chapter 11 voice.

---

## F: Functional requirements

- **F001: NetworkX foundation.** Teach the minimum graph language the rest of the chapter needs: nodes, edges, paths, distance, neighborhoods, connected components, and degree distribution. Connect this to Chapter 11.4's union-find by re-expressing it as connected components on a thresholded match graph.
- **F002: Visibility graph algorithm.** Implement the Lacasa-Luque-Ballesteros-Luque-Nuño (2008) visibility criterion in NumPy + NetworkX. Show the three-regime result: periodic series → regular graph, random → exponential degree distribution, fractal → power-law degree distribution.
- **F003: Hurst-to-degree-exponent mapping.** Reproduce the Lacasa-Luque (2009) result that the visibility-graph degree exponent of fBm tracks the Hurst exponent H linearly. Use the author's own fractal-pv-coupling DFA estimator (or a stripped reimplementation) on a real return series for the demonstration.
- **F004: Horizontal visibility variant.** Add the horizontal visibility graph (Luque et al., 2009) as a contrast: simpler, analytically tractable, gives a clean separator between random and chaotic series.
- **F005: Graph box-covering.** Implement greedy-coloring box-covering on the auxiliary graph using `networkx.greedy_color`. Validate against three reference networks with known dimension: deterministic Sierpinski graph, (u,v)-flower, and a Song-Havlin-Makse hierarchical scale-free model.
- **F006: Box-covering on real networks.** Run the same estimator on a real or realistic network (Karate, Les Mis co-appearance, or a sampled subgraph from `dbt/dbt_dq/` lineage) and inspect whether the log–log slope is stable across the feasible box-size range.
- **F007: Skeleton extraction and renormalization.** Build the Goh-Salvi-Kahng-Kim (2006) skeleton (the spanning tree of high-betweenness edges or maximum-spanning by edge multiplicity) and run two iterations of box renormalization to show how a fractal network coarse-grains to a self-similar sub-graph.
- **F008: Graph fractal dimension via communities.** Implement the Skums-Bunimovich (2020) framing: estimate fractality from the overlap pattern between densely connected communities. Use Louvain or Leiden community detection and quantify pairwise overlap. Compare the community-overlap dimension to the box-covering dimension on the same graph.
- **F009: Lineage as a fractal-aware governance object.** Build a synthetic data lineage DAG (sources → staging → marts → exposures), inject defects at leaf nodes, propagate downstream, and compute a "blast radius across box scales" risk descriptor. Optionally parse `dbt/dbt_dq/target/manifest.json` if it exists to use the real lineage from Chapter 9.
- **F010: Entity resolution upgrade.** Re-express Chapter 11.4's records and pairwise scores as a NetworkX graph. At each threshold, compute (a) connected components (the existing membership signature), (b) local box dimension per cluster, (c) community overlap per cluster, (d) skeleton ratio per cluster. Define the new instability score as the dispersion of these graph descriptors across thresholds, not just membership flips.
- **F011: Epistemic guardrails.** A dedicated notebook on when fractal-on-graph claims fail: small-N effects, treelike structures with clean box-covers but no real fractality, trend-induced visibility-graph artifacts, slope-without-stability claims.
- **F012: Studio page.** `fractal-graphs.html` with three interactive panels: Visibility Graph Lab, Box-Covering Lab, Lineage Risk Lab. Mirror the existing `fractals-governance.html` shell, navigation, and design tokens.

---

## N: Non-functional requirements

- **N001: Voice.** Match the Chapter 11 register. Bounded claims. "I am not claiming X. I am asking whether Y." No grandiose vocabulary, no em-dash overuse, no triplet rule-of-three reflex.
- **N002: Notebook cell-shape contract.** Every notebook follows the existing template: header blockquote, title, "## Outputs", "## Supporting reading", "## Failure note", "## How I would debug this", code, "## Reading the result", "## Where this can go wrong", "## Exercise" or "## Assignment".
- **N003: Local-first.** Everything runs on a laptop without GPU or paid APIs. Box-covering is NP-hard so we cap problem sizes and disclose the cap.
- **N004: Determinism.** All stochastic notebooks seed `numpy.random.default_rng(7)` (existing convention from 11.2) so results are reproducible across runs and CI.
- **N005: Dependency restraint.** Add `networkx` and `python-louvain` (or `leidenalg` if a wheel is available) to `requirements.txt`. Do not add `igraph`, `graph-tool`, or anything that needs system-level compilation.
- **N006: Studio page weight.** No bundler, no React. Hand-written HTML + CSS + vanilla JS, matching the four existing studio pages. Total page weight under 200 KB excluding fonts.
- **N007: Citation discipline.** Every notebook lists its supporting reading in cell 1. Studio page links to the same canonical reference list. No citation appears without being read by the author.
- **N008: Backwards compatibility.** Chapter 12 must not modify Chapter 11 contracts. The renamed concept "graph coverings" already mentioned in 11.1 stays as a forward reference; Chapter 12 supplies the formal definition.

---

## E: Edge cases and failure modes

- **E001: Tiny graphs return any slope.** A graph with N < 50 nodes will fit a "fractal dimension" by accident. Notebooks must filter for N ≥ a threshold before publishing a slope, and the `12.7` notebook demonstrates the false positive directly.
- **E002: Trees fool box-covering.** A pure tree has a clean N_B(l_B) ∝ l_B^{-d_B} relationship without satisfying the Skums-Bunimovich community-overlap criterion. Treat box-covering as necessary not sufficient.
- **E003: Trend in time series.** A linear trend skews the visibility graph degree distribution toward high-degree hubs at the trend extremes. The visibility notebook must detrend or work on returns, not on raw price.
- **E004: Disconnected components.** Box-covering distance is undefined across disconnected components. The notebook must run per-component and either aggregate carefully or flag the largest component.
- **E005: Threshold flips that do not move the graph.** The duplicate-cluster upgrade must distinguish threshold changes that flip a record's component from threshold changes that only re-weight an edge. The new instability score should weight component changes more heavily.
- **E006: Greedy coloring is not optimal.** All numerical d_B values are approximations. Notebooks must report `d_B ≈` not `d_B =` and mention the NP-hardness in the same cell as the result.
- **E007: Power-law fits hallucinate.** Fitting `log P(k) = -α log k + c` on a short tail will return an α that means nothing. Use the Clauset-Shalizi-Newman maximum-likelihood approach or at minimum require a multi-decade tail before publishing α.

---

## C: Components (notebook spine)

| ID | File | Title | Aim |
|---|---|---|---|
| C001 | `notebooks/12-fractal-graphs/12.0 Why Graphs Deserve a Fractal Lens.ipynb` | Preface | Pyramid-style answer to the question "why graphs after Chapter 11", set bounded claim, list the three bridges (time series → graph, image → graph, governance → graph). |
| C002 | `notebooks/12-fractal-graphs/12.1 Graphs as the Next Geometry.ipynb` | NetworkX primer | Minimum graph language; rebuild Chapter 11.4 union-find as connected components; visualize the entity-match graph. |
| C003 | `notebooks/12-fractal-graphs/12.2 Visibility Graphs from Time Series.ipynb` | Time-series → graph bridge | Lacasa visibility algorithm; three regimes (periodic, random, fractal); Hurst-to-degree-exponent reproduction on a real return series. |
| C004 | `notebooks/12-fractal-graphs/12.3 Box Covering on Graphs.ipynb` | Image → graph bridge | Greedy-coloring box-covering on Sierpinski graph, (u,v)-flower, hierarchical SHM, and one real network; fit d_B on log–log; compare to known analytical values. |
| C005 | `notebooks/12-fractal-graphs/12.4 Skeletons, Hubs, and Renormalization.ipynb` | Coarse-graining iteration | Skeleton extraction; box renormalization; show the self-similar sub-graph at level 2 of a fractal network and the absence of one in a non-fractal network. |
| C006 | `notebooks/12-fractal-graphs/12.5 Lineage Graphs and Fault Propagation.ipynb` | Enterprise translation A | Synthetic and (if available) dbt-manifest-based lineage; inject defect, propagate, compute blast radius across box scales; produce a stewardship priority list. |
| C007 | `notebooks/12-fractal-graphs/12.6 Entity Resolution Revisited as a Graph.ipynb` | Enterprise translation B | Upgrade the 11.4 case study with graph descriptors; new instability score uses local box dimension, community overlap, and skeleton ratio. |
| C008 | `notebooks/12-fractal-graphs/12.7 When Fractal Descriptors Mislead on Graphs.ipynb` | Epistemic guardrails | The honesty notebook; reproduce four named failure modes; close the chapter with what cannot be claimed. |
| C009 | `fractal-graphs.html` (root) | Studio page | Three interactive panels (Visibility Graph Lab, Box-Covering Lab, Lineage Risk Lab). |
| C010 | `site-assets/fractal-graphs.css` and `site-assets/fractal-graphs.js` | Studio assets | Mirror of `fractals.css`/`fractals.js` design tokens. |

---

## M: Data models

- **M001: Time series record.** `{timestamp: datetime, value: float}` minimum; the visibility notebook works on a `numpy.ndarray` of values plus an implicit integer index.
- **M002: Graph object.** Standard NetworkX `Graph` for undirected (entity resolution, visibility), `DiGraph` for lineage.
- **M003: Box-cover record.** `{box_size: int, n_boxes: int, members: list[set[node_id]]}` per estimation step.
- **M004: Fractality summary.** `{graph_id: str, n_nodes: int, n_edges: int, d_B: float, d_B_r2: float, alpha_visibility: Optional[float], skeleton_ratio: float, modularity: float, community_overlap_score: float, fractal_claim: Literal["plausible","not_supported","insufficient_data"]}`.
- **M005: Lineage node.** `{node_id: str, layer: Literal["source","staging","mart","exposure"], owner: str, defect_state: bool}`.
- **M006: Stewardship record.** Reuse Chapter 11.4 `records`, `scores` schema verbatim. Add `cluster_id_at_threshold: dict[float, str]`, `local_box_dim_at_threshold: dict[float, float]`, `community_overlap_at_threshold: dict[float, float]`.

---

## D: Dependencies

- **D001: Existing.** `numpy`, `pandas`, `matplotlib`, `scipy`, `jupyter`. All already required by the repo.
- **D002: Add.** `networkx>=3.2` (graph operations and `greedy_color`), `python-louvain` or `leidenalg` (community detection), `powerlaw` (Clauset-Shalizi-Newman fits, optional but recommended for F003 and F011-E007).
- **D003: Optional.** `dbt-core` parsed `manifest.json` if Chapter 9's dbt project has been compiled. The 12.5 notebook should soft-import and fall back to the synthetic lineage if the manifest is absent.
- **D004: Studio page.** No new dependencies. Reuse the existing static-site idiom.

---

## R: Risks

- **R001: Box-covering compute.** Real networks at N ≈ 10⁴ already strain greedy coloring on a laptop. Mitigation: cap N at 2000 in published notebooks; cache pairwise distances; document the cap in the failure note.
- **R002: Power-law overclaiming.** Visibility-graph degree distributions tempt over-confident α fits. Mitigation: F011-E007; use `powerlaw` package and report goodness-of-fit p-values where possible.
- **R003: Studio-page maintenance.** Each new HTML page widens the surface area of the GitHub Pages site. Mitigation: factor a shared CSS partial into `site-assets/` so design tokens move once.
- **R004: Reader fatigue.** Chapter 12 is the third "advanced lens" notebook cluster after 10 and 11. Mitigation: 12.0 is short, answer-first, and explicitly tells readers which two notebooks to read if they only have one hour (12.2 and 12.6).
- **R005: Citation freshness.** Fractal-network research has moved since 2005; the chapter must include at least one 2024–2025 citation (Fronczak et al., or the Nature Sci-Reports lineage GNN paper).

---

## Q: Open questions

- **Q001** Should Chapter 12 absorb a renamed Chapter 11.4 (so the duplicate-cluster work lives in 12.6 only), or keep 11.4 as the procedural primer and 12.6 as the graph-aware sequel? Default proposal: keep both. 11.4 remains the union-find introduction; 12.6 adds the graph descriptors.
- **Q002** Do we ship a real-network demonstration inside the repo, or link out? Default proposal: ship the Karate club graph (NetworkX built-in) and one sampled lineage subgraph. No external downloads in CI.
- **Q003** Is the visibility-graph studio panel worth the build cost? It is the most novel of the three panels. Default proposal: ship it; reuse the SVG drag idiom from `embeddings-bridge.html`.
- **Q004** Should the chapter include multifractal analysis (MFDFA on graphs / multifractal scaling of node-strength)? Default proposal: out of scope for v1; mention as a forward pointer in 12.7.
- **Q005** How do we cross-promote the `fractal-pv-coupling` paper without making the curriculum dependent on a private preprint? Default proposal: cite the public Zenodo DOI in 12.2 and treat the algorithm reimplementation as self-contained.

---

## Citations (chapter source-of-truth list)

These are the references each notebook will quote. Each appears in cell 1 of the notebook that uses it, matching the Chapter 11.x style.

- **[1]** Lacasa, L., Luque, B., Ballesteros, F., Luque, J., & Nuño, J. C. (2008). *From time series to complex networks: the visibility graph.* PNAS 105(13), 4972–4975. https://www.pnas.org/doi/full/10.1073/pnas.0709247105
- **[2]** Lacasa, L., Luque, B., Luque, J., & Nuño, J. C. (2009). *The visibility graph: a new method for estimating the Hurst exponent of fractional Brownian motion.* EPL 86, 30001. https://arxiv.org/abs/0901.0888
- **[3]** Luque, B., Lacasa, L., Ballesteros, F., & Luque, J. (2009). *Horizontal visibility graphs: exact results for random time series.* Phys. Rev. E 80, 046103.
- **[4]** Song, C., Havlin, S., & Makse, H. A. (2005). *Self-similarity of complex networks.* Nature 433, 392–395. https://www.nature.com/articles/nature03248
- **[5]** Song, C., Havlin, S., & Makse, H. A. (2007). *How to calculate the fractal dimension of a complex network: the box covering algorithm.* J. Stat. Mech. P03006.
- **[6]** Goh, K.-I., Salvi, G., Kahng, B., & Kim, D. (2006). *Skeleton and fractal scaling in complex networks.* Phys. Rev. Lett. 96, 018701.
- **[7]** Rozenfeld, H. D., Havlin, S., & ben-Avraham, D. (2007). *Fractal and transfractal recursive scale-free nets.* New J. Phys. 9, 175.
- **[8]** Skums, P., & Bunimovich, L. (2020). *Graph fractal dimension and the structure of fractal networks.* Journal of Complex Networks 8(4). https://pmc.ncbi.nlm.nih.gov/articles/PMC7673317/
- **[9]** Nagy, M. (2021). *Comparative analysis of box-covering algorithms for fractal networks.* Applied Network Science 6:73. https://link.springer.com/article/10.1007/s41109-021-00410-6
- **[10]** Fronczak, P., Fronczak, A., & Bujok, M. (2024). *Fractal complex networks.* Scientific Reports. https://www.nature.com/articles/s41598-024-59765-2
- **[11]** *End-to-end framework for data lineage analysis covering link pattern recognition, fault diagnosis, and early warning.* Scientific Reports (2025). https://nature.com/articles/s41598-025-34522-1
- **[12]** Malemapti Hari, D. (2026). *Static and Temporal Fractal Coupling Between Volatility and Trading Volume.* Zenodo. https://doi.org/10.5281/zenodo.19611544
- **[13]** Lopes, R., & Betrouni, N. (2009). *Fractal and multifractal analysis: A review.* Medical Image Analysis 13, 634–649. https://pubmed.ncbi.nlm.nih.gov/19535282/ (carry-over from 11.1 and 11.2)
- **[14]** Hagberg, A., Schult, D., & Swart, P. (2008). *Exploring network structure, dynamics, and function using NetworkX.* (NetworkX reference for the implementation chapter.)

---

## Appendix A: Notebook cell-by-cell sketches

The cell-level sketches below are not the final cells. They are the seeding plan that `plan.md` will translate into P###/W###/K###/X### with concrete tests. The voice and headings already match the Chapter 11.x contract.

### 12.0: Why Graphs Deserve a Fractal Lens (preface)

Cell 0 (blockquote header):
```
> **Chapter 12, Part 0** | Advanced lens. **Focus:** what graphs add to the Chapter 11 argument and which two bridges (time series, image) the rest of the chapter actually walks across.
```

Cell 1 (markdown title and frame):

- The answer first: Chapter 11 worked on pictures and time series. Real enterprise objects (lineage, entity resolution, hierarchies, microservice dependencies) are graphs. The graph is not a metaphor; it is the data structure those objects already live in. Box-counting still applies, just on a different geometry.
- Set the bounded claim explicitly. Quote 11.3: "I am not claiming that enterprise data is fractal in the literal mathematical sense." The same discipline applies to graphs.
- One paragraph: the three bridges this chapter walks across: time series → graph (12.2), image → graph (12.3), governance → graph (12.5–12.6).
- Outputs section. Failure note. "How I would debug this."

Cell 2 (code, optional): a one-cell teaser. Render Karate-club graph with NetworkX, color nodes by community, and overlay the box-cover at l_B = 3. Just to set the visual register.

Cell 3 (markdown): assignment. "Pick one graph in your enterprise (lineage, dependency, entity match, knowledge). Write down its node type, edge type, and the boundary you currently use to decide if two records are the same entity. We will return to your example in 12.5 and 12.6."

### 12.1: Graphs as the Next Geometry

Outputs:
- a NetworkX primer that does not condescend
- the Chapter 11.4 entity-match graph rebuilt and visualized
- a degree distribution on a small real network

Code skeleton:

```python
import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

records = pd.DataFrame([...])  # reuse 11.4 records
scores = pd.DataFrame([...])    # reuse 11.4 scores

def match_graph(scores: pd.DataFrame, threshold: float) -> nx.Graph:
    g = nx.Graph()
    for _, row in scores.iterrows():
        if row["score"] >= threshold:
            g.add_edge(row["left"], row["right"], weight=row["score"])
    return g

g = match_graph(scores, threshold=0.86)
print(nx.info(g) if hasattr(nx, "info") else (g.number_of_nodes(), g.number_of_edges()))

components = list(nx.connected_components(g))
```

Reading: connect this back to the 11.4 union-find. "What we wrote as parent[] pointers is the same set of components NetworkX builds for free."

Where this can go wrong: edge weights are not yet used. Connected components ignores them. We will fix this when local box dimension enters the picture in 12.6.

### 12.2: Visibility Graphs from Time Series

Outputs:
- a NumPy implementation of the Lacasa visibility criterion
- the three-regime demonstration (periodic, random, fractal)
- Hurst-to-degree-exponent reproduction on at least one real return series

Code skeleton (visibility kernel):

```python
def visibility_graph(values: np.ndarray) -> nx.Graph:
    n = len(values)
    g = nx.Graph()
    g.add_nodes_from(range(n))
    for a in range(n):
        ya = values[a]
        for b in range(a + 1, n):
            yb = values[b]
            if b == a + 1:
                g.add_edge(a, b)
                continue
            slope = (yb - ya) / (b - a)
            visible = True
            for c in range(a + 1, b):
                yc_line = ya + slope * (c - a)
                if values[c] >= yc_line:
                    visible = False
                    break
            if visible:
                g.add_edge(a, b)
    return g
```

(Performance note: the O(n^3) version above is fine for n up to a few thousand. For larger series, switch to the divide-and-conquer construction from Lan et al. 2015.)

Three-regime cell:
- periodic series → regular graph; degree distribution is a finite spike pattern
- uniform random → exponential degree-distribution tail
- fractional Brownian motion at H ∈ {0.3, 0.5, 0.7} → power-law degree distribution; fit α; show α(H) is roughly linear

Real-data cell: pull SPY daily returns via `yfinance` (already a project dependency), build the visibility graph for a 4000-day window, fit α, compare to a DFA Hurst estimate on the same window. Cite [12] (the author's own paper) for the DFA reference.

Failure note: "If you fit α on a degree distribution with fewer than two decades of support, you have a slope, not a power law."

### 12.3: Box Covering on Graphs

Outputs:
- a working greedy-coloring box-covering function
- d_B estimates on three reference networks with known answers
- one d_B estimate on a non-fractal network (Erdős-Rényi) where the slope refuses to stabilize

Code skeleton:

```python
import networkx as nx

def auxiliary_graph(g: nx.Graph, l_b: int) -> nx.Graph:
    aux = nx.Graph()
    aux.add_nodes_from(g.nodes())
    dist = dict(nx.all_pairs_shortest_path_length(g))
    for u in g.nodes():
        for v in g.nodes():
            if u < v and dist[u].get(v, float("inf")) > l_b - 1:
                aux.add_edge(u, v)
    return aux

def box_cover(g: nx.Graph, l_b: int) -> dict:
    aux = auxiliary_graph(g, l_b)
    coloring = nx.coloring.greedy_color(aux, strategy="largest_first")
    boxes = {}
    for node, color in coloring.items():
        boxes.setdefault(color, set()).add(node)
    return boxes

def estimate_d_B(g: nx.Graph, box_sizes: list[int]) -> tuple[float, float, list[int]]:
    counts = [len(box_cover(g, l)) for l in box_sizes]
    valid = [(np.log(1.0 / l), np.log(c)) for l, c in zip(box_sizes, counts) if c > 0]
    xs, ys = zip(*valid)
    slope, intercept = np.polyfit(xs, ys, 1)
    return slope, intercept, counts
```

Reference networks:
- **Sierpinski-like graph** (recursively constructed; analytical d_B = log 3 / log 2 ≈ 1.585)
- **(u,v)-flower with u=v=2** (analytical d_B exists per Rozenfeld et al.)
- **Erdős-Rényi G(500, p=0.02)** (small-world; box count decays exponentially, not as a power law)

Reading: "If your graph passes the slope test on log–log but fails the stability test across feasible box-size ranges, what you have is small-world plus finite size, not fractality."

### 12.4: Skeletons, Hubs, and Renormalization

Outputs:
- a skeleton extractor (max-spanning by edge betweenness)
- two iterations of box renormalization on a fractal network
- a side-by-side: SHM hierarchical model retains structural shape after coarse-graining; Erdős-Rényi does not

Code skeleton (renormalization):

```python
def renormalize(g: nx.Graph, l_b: int) -> nx.Graph:
    boxes = box_cover(g, l_b)
    box_of = {n: bid for bid, members in boxes.items() for n in members}
    coarse = nx.Graph()
    coarse.add_nodes_from(boxes.keys())
    for u, v in g.edges():
        if box_of[u] != box_of[v]:
            coarse.add_edge(box_of[u], box_of[v])
    return coarse
```

Cell on Goh-Salvi-Kahng-Kim skeleton: extract max-betweenness spanning subgraph; show the skeleton recovers the recursive backbone.

### 12.5: Lineage Graphs and Fault Propagation

Outputs:
- a synthetic lineage DAG with named layers (sources → staging → marts → exposures)
- a defect-propagation simulator
- a "blast radius across box scales" risk descriptor that ranks transformation nodes for stewardship attention

Code skeleton (lineage construction):

```python
def synthetic_lineage(n_sources=8, n_staging=14, n_marts=6, n_exposures=4, seed=7) -> nx.DiGraph:
    rng = np.random.default_rng(seed)
    g = nx.DiGraph()
    sources = [f"src_{i}" for i in range(n_sources)]
    staging = [f"stg_{i}" for i in range(n_staging)]
    marts = [f"mart_{i}" for i in range(n_marts)]
    exposures = [f"exp_{i}" for i in range(n_exposures)]
    g.add_nodes_from(sources, layer="source")
    g.add_nodes_from(staging, layer="staging")
    g.add_nodes_from(marts, layer="mart")
    g.add_nodes_from(exposures, layer="exposure")
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
```

Defect propagation: BFS from a tagged source; mark every reachable downstream node as touched.

Risk descriptor: for each node, count the number of distinct boxes (at fixed l_B) its descendants land in; the higher the count, the wider the blast radius across the structural scale. Plot a stewardship priority list.

dbt fallback (soft import):

```python
import json, pathlib
manifest_path = pathlib.Path("../../dbt/dbt_dq/target/manifest.json")
if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text())
    real_lineage = build_lineage_from_manifest(manifest)
else:
    real_lineage = synthetic_lineage()
```

### 12.6: Entity Resolution Revisited as a Graph

Outputs:
- the 11.4 records and scores re-expressed as a NetworkX graph
- four threshold-sensitive descriptors per cluster (component membership, local box dimension, community overlap, skeleton ratio)
- a graph-aware instability score that supersedes 11.4's flip-counting score

Code skeleton (cluster-level estimators):

```python
def cluster_descriptors(g: nx.Graph) -> dict:
    components = list(nx.connected_components(g))
    out = {}
    for i, comp in enumerate(components):
        sub = g.subgraph(comp).copy()
        if sub.number_of_nodes() < 4:
            out[f"C{i+1}"] = {"d_B_local": None, "skeleton_ratio": None, "modularity": None, "n": sub.number_of_nodes()}
            continue
        d_B, _, _ = estimate_d_B(sub, [1, 2, 3])
        skeleton = max_spanning_skeleton(sub)
        ratio = skeleton.number_of_edges() / sub.number_of_edges()
        comm = community_louvain.best_partition(sub) if HAS_LOUVAIN else None
        modularity = community_louvain.modularity(comm, sub) if comm else None
        out[f"C{i+1}"] = {
            "d_B_local": d_B,
            "skeleton_ratio": ratio,
            "modularity": modularity,
            "n": sub.number_of_nodes(),
        }
    return out
```

New instability score: standard deviation of `d_B_local` across thresholds, plus weighted membership-flip count from 11.4. Stewardship triage flag fires when either component flips occur or `std(d_B_local) > σ_threshold`.

Reading: the 11.4 page asked "did membership change?" The 12.6 upgrade asks "did the cluster reorganize structurally?" That is the better question. Membership change is a downstream symptom of structural reorganization.

### 12.7: When Fractal Descriptors Mislead on Graphs

Four worked failure modes, one per section:

1. **Small-N false positive.** Generate 30 Erdős-Rényi graphs with N ∈ {30, 60, 120}. Fit d_B on each. Show the slope is unstable below a critical N.
2. **Tree mimic.** Take a balanced binary tree of depth 8. Show the box-cover slope looks fractal but the Skums-Bunimovich community-overlap measure flatlines.
3. **Trend artifact in visibility.** Add a slow linear drift to an fGn series. Show the visibility-graph degree distribution shifts toward a hub at the trend extreme. Detrend and watch the artifact disappear.
4. **Slope without stability.** Take a real non-fractal network. Fit d_B on three different box-size ranges. Show three different slopes. Refuse to publish a fractality claim.

Closing assignment: "Pick the graph from your 12.0 assignment. Run two independent fractality estimators (box-covering slope and Skums-Bunimovich community overlap). Write a one-page note: do they agree? If yes, what governance decision should follow? If no, why is one estimator more trustworthy on your object?"

---

## Appendix B: Studio page mockup (`fractal-graphs.html`)

Visual idiom: same shell, navigation, hero block, and section cadence as `fractals-governance.html`. Three interactive panels.

### Hero
- Eyebrow: `ADVANCED NOTEBOOK CLUSTER`
- Headline: `Fractal graphs and the structure of enterprise networks.`
- Lead: "Chapter 11 used pictures and time series. The same scale-sensitive descriptors live on graphs, where most enterprise objects already are. This page shows the three bridges the notebook spine walks across."
- Two signal cards on the rail:
  - "Why visibility graphs": "A time series is a graph in disguise. The visibility map exposes the structure."
  - "Why box-covering": "Box-counting on a graph is the same idea as Chapter 11.1, on a different geometry."

### Panel 1: Visibility Graph Lab
- Left: a small SVG canvas where the user can sketch a series with the mouse, or pick a preset (sine, random, fBm with H slider, real returns).
- Right: the visibility graph rendered live, plus a degree-distribution panel with a fitted α and (when relevant) the matching DFA Hurst estimate on the same sketch.
- The point: see periodic → regular, random → exponential, fractal → power-law happen in real time.

### Panel 2: Box-Covering Lab
- Top: graph picker (Sierpinski, (u,v)-flower, Erdős-Rényi, hierarchical SHM, Karate club, "your edgelist").
- Middle: animation that lights up boxes at each l_B from 1 upward; counts update; log-log plot fits a slope live.
- Bottom: stability indicator. Green when slope is stable across at least three decades of l_B; amber otherwise; red when the slope is not statistically distinguishable from the random reference.

### Panel 3: Lineage Risk Lab
- Left: small interactive DAG (sources → staging → marts → exposures). Click any node to inject a defect.
- Right: heatmap of blast radius across box scales; stewardship priority table updates live.
- A second toggle: "real dbt manifest" if the studio finds a compiled manifest in the repo, otherwise the synthetic DAG.

### Footer
- Notebook path closing panel mirrors `fractals-governance.html`. Buttons: Open 12.2, Open 12.3, Open 12.6, Back to home.

---

## Acceptance gate (handoff to plan.md)

Before plan.md begins, this spec must satisfy:
- All S001–S007 are testable.
- Every F### maps to at least one C### notebook and at least one citation in the source-of-truth list.
- All R### risks have a named mitigation.
- Q001–Q005 either resolved or explicitly carried into plan.md as decisions for the planning step.

The next document in the loop is `artifacts/tickets/CH-12-fractal-graphs/plan.md`, which translates this spec into P### implementation steps (cell authoring order), W### file changes, K### testing checkpoints, and X### commit points.
