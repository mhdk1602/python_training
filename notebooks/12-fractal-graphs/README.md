# Chapter 12: Fractal Graphs

> Advanced lens. Reads after Chapter 11. Walks across three bridges the curriculum has been pointing at: time series → graph (visibility), image → graph (box-covering), governance → graph (lineage and entity resolution).

## What this chapter is

Chapter 11 used pictures and time series to teach scale-sensitive descriptors. Most enterprise objects worth governing are graphs already: data lineage DAGs, entity-resolution match graphs, product hierarchies, microservice dependencies. This chapter formalizes the graph language and shows when a fractal claim on a graph buys you something that ordinary summary statistics cannot.

The chapter is a cluster, not a single notebook. Read in order. The first three notebooks teach the vocabulary; the next three teach the enterprise translation; the last one is the honesty notebook that names what cannot be claimed.

## Run it

```bash
cd notebooks/12-fractal-graphs

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install jupyter

jupyter notebook
```

If `python-louvain` fails to install on Apple Silicon, the notebooks degrade gracefully (community detection becomes a no-op). If `powerlaw` fails, fits fall back to `np.polyfit` with a documented warning.

## Notebook spine

| # | Notebook | What you build |
|---|----------|----------------|
| 12.0 | Why Graphs Deserve a Fractal Lens | The framing. The three bridges named. The bounded claim that survives the rest of the chapter. |
| 12.1 | Graphs as the Next Geometry | Minimum NetworkX language. Rebuild the Chapter 11.4 union-find as connected components on a thresholded match graph. |
| 12.2 | Visibility Graphs from Time Series | Lacasa visibility algorithm. Three regimes (periodic, random, fractal). Hurst-to-degree-exponent reproduction. |
| 12.3 | Box Covering on Graphs | Greedy-coloring box covering. Estimate `d_B` on Sierpinski-like, (u,v)-flower, hierarchical scale-free, Karate club, and a non-fractal control. |
| 12.4 | Skeletons, Hubs, and Renormalization | Skeleton extraction. Two iterations of box renormalization. The fractal network keeps its shape; the random one does not. |
| 12.5 | Lineage Graphs and Fault Propagation | Synthetic data lineage DAG. Defect propagation. Blast-radius across box scales as a stewardship descriptor. |
| 12.6 | Entity Resolution Revisited as a Graph | The 11.4 records and scores re-expressed as a graph. Local box dimension, community overlap, skeleton ratio. A graph-aware instability score that supersedes the flip-counting score from 11.4. |
| 12.7 | When Fractal Descriptors Mislead on Graphs | Four named failure modes: small-N false positives, tree mimics, trend artifacts in visibility graphs, slope-without-stability claims. |

## Public studio

[mhdk1602.github.io/python_training/fractal-graphs.html](https://mhdk1602.github.io/python_training/fractal-graphs.html)

Three interactive panels: Visibility Graph Lab, Box-Covering Lab, Lineage Risk Lab. Same shell as the existing fractals studio.

## Bounded claim

I am not claiming enterprise data is fractal. I am asking whether selected enterprise graphs (lineage, entity resolution, hierarchy) show enough multi-scale structure that fractal descriptors become useful for stewardship triage. Where the test fails, the chapter says so. Where the test passes, the chapter explains what governance decision the measurement should improve.
