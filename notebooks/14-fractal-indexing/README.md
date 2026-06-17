# Chapter 14: Fractal Indexing (Hilbert, Z-order, and the Hidden Math of Modern Storage)

**Audience:** practitioners and curious engineers who want to understand the math underneath the indexes they already use. **Prerequisites:** comfort with NumPy, basic SQL, and a willingness to read a log-log plot. The HNSW notebook (14.4) assumes you have heard of approximate nearest neighbors but does not assume you have implemented one.

## What this chapter argues

Three things are true at once and rarely connected.

1. Production data systems already ship fractal indexes. Apache Iceberg added Hilbert curve clustering in 2025 (PR #5824). Delta Lake's Liquid Clustering (3.0) uses Hilbert curves and reports up to 10× query acceleration with 90% data-skipping improvement. DuckDB ships `ST_Hilbert`. Uber's H3 and Google's S2 are both hierarchical fractal subdivisions of the sphere. HNSW, the dominant vector index, is a hierarchical small-world graph.
2. The theoretical apparatus is older than the production systems and largely forgotten. Faloutsos and Kamel (1994) used fractal dimension to estimate range-query selectivity on R-trees with relative error below 5% on real data, versus 40-100% under uniformity assumptions. Korn, Pagel, and Faloutsos (2001) named the "self-similarity blessing": real high-dimensional data has effective fractal dimension much smaller than the ambient dimension. Modern OLAP optimizers ignore this.
3. HNSW (Malkov and Yashunin, 2018) is structurally a small-world / scale-free network. The hierarchical layer assignment with exponentially decaying probability is exactly the scale-separation pattern that produces fractal network structure. Vector databases ship HNSW as a black box.

This chapter builds the apparatus from first principles, shows it running in production engines, and names the failure modes. The interactive surface visualizes the curves and the index search itself, because the locality intuition is impossible to convey in text.

The bounded claim. The chapter does not assert that fractal indexes are universally faster. It asserts that for skewed multi-dimensional OLAP, persistent-correlated time-series, low-intrinsic-dimension embedding spaces, and high-cardinality spatial selectivity, the fractal apparatus produces measurable engineering wins that the default-histograms approach cannot match. The companion research plan at `non-git-files/fractal-indexing-research-plan.md` (out of the public repo) outlines the validation program that turns the apparatus into a peer-reviewed engineering contribution.

## Notebook spine

| Notebook | Title | Purpose |
|---|---|---|
| 14.0 | Why Indexes Are Already Fractal | Frames the chapter, three production examples, history paragraph, bounded claim. |
| 14.1 | Space-Filling Curves: Z-order, Hilbert, and Locality | Pure-NumPy Z-order and Hilbert curves, locality measure, side-by-side visualization. |
| 14.2 | Hilbert R-tree: Bulk-Loading by Fractal Order | Reproduces Kamel-Faloutsos (1994) on synthetic 10,000-point data; reports node utilization. |
| 14.3 | Fractal Dimension as a Selectivity Oracle | Grassberger-Procaccia D2 estimator; reproduces Faloutsos-Kamel (1994) selectivity formula on geospatial data. |
| 14.4 | HNSW as a Hierarchical Small-World Index | Tiny pure-Python HNSW (50 nodes, 3 layers); visualizes layer assignment and search descent. |
| 14.5 | Liquid Clustering at Home: Z-order vs Hilbert on Parquet | DuckDB benchmark with `ST_Hilbert` on real geospatial data; honest numbers. |
| 14.6 | Adaptive Chunking by Hurst Exponent | fGn streams at H=0.3, 0.5, 0.8; Hurst-driven chunk boundaries; explicit bridge to the Zenodo paper. |
| 14.7 | Capstone: Build Your Own Fractal Index for Your Workload | Decision tree from workload shape to index family; reproducible benchmark harness. |
| 14.8 | When the Speedup Is a Lie | Names four failure modes; pairs with notebooks 12.7 and 13.8. |

## How to run

```bash
cd notebooks/14-fractal-indexing
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

Notebooks regenerate from the generator script:

```bash
python scripts/generate_chapter_14_notebooks.py
```

Outputs are embedded after execution. The execution path used during development was:

```bash
for nb in notebooks/14-fractal-indexing/14.*.ipynb; do
  jupyter nbconvert --to notebook --execute --inplace --allow-errors "$nb"
done
```

## How this fits the public site

The interactive surface lives at `indexing-studio.html` (top-level) and reuses the visual idiom of `governance-studio.html`. The studio implements three labs:

- **Curve Trace Animator.** Watch a Hilbert or Z-order curve trace through a 32×32 grid; drag a query rectangle to see which tiles must be fetched.
- **Index Race Track.** Bulk-load 5,000 random points; toggle between naive scan, Z-order, Hilbert, and R-tree; see pages-fetched and ms-elapsed update in real time.
- **HNSW Climber.** Visualize a tiny HNSW; pick a query; watch the search descend layer by layer; slider for `M` rebuilds the graph.

The studio is vanilla JS so it works directly from `file://` without a backend.

## Citation

Cite this chapter as part of the repository:

> Malemapti Hari, D. (2026). *Data Engineering with Python: Project-First Training Repository, Chapter 14: Fractal Indexing*. https://github.com/mhdk1602/python_training

The methodological provenance for the Hurst-exponent work in notebook 14.6 runs through:

> Malemapti Hari, D. (2026). *Static and Temporal Fractal Coupling Between Volatility and Trading Volume*. Zenodo. https://doi.org/10.5281/zenodo.19611544

The classical fractal-indexing apparatus this chapter reimplements is anchored in:

> Kamel, I., and Faloutsos, C. (1994). Hilbert R-tree: An improved R-tree using fractals. *VLDB '94*, 500-509.

> Faloutsos, C., and Kamel, I. (1994). Beyond uniformity and independence: Analysis of R-trees using the concept of fractal dimension. *PODS '94*, 4-13.

> Malkov, Y. A., and Yashunin, D. A. (2018). Efficient and robust approximate nearest neighbor search using hierarchical navigable small world graphs. *IEEE TPAMI*. arXiv:1603.09320.
