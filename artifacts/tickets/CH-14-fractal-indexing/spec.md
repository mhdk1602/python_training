# CH-14 Fractal Indexing: Hilbert, Z-order, and the Hidden Math of Modern Storage

**Owner:** Dineshkumar Malemapti Hari
**Status:** Draft (proceed to plan and implementation pending user go-ahead)
**Created:** 2026-05-12
**Connects to:** Chapters 11-13 (the fractal trilogy), Chapter 8 (LLMs / vector embeddings), Chapter 10 (retrieval), the candidate's PhD dissertation (UC, Spring 2026), and the [Zenodo coupling paper](https://doi.org/10.5281/zenodo.19611544)
**Companion:** [non-git-files/fractal-indexing-research-plan.md](../../../../non-git-files/fractal-indexing-research-plan.md)

## Context

Chapters 11-13 used fractals as a research lens. Chapter 14 reframes the same mathematics as an engineering tool. Most modern data systems already ship fractal indexes (Iceberg's Hilbert curve, Delta Lake's Liquid Clustering, DuckDB's `ST_Hilbert`, H3, S2, HNSW), and most engineers who use them have never seen the curve traced through a grid. The teaching gap is real and the production payoff is real: 10× query acceleration in Liquid Clustering, 28% savings over R*-trees from Hilbert R-trees, 44% compression improvement from Hilbert-ordered GeoParquet.

This chapter teaches the apparatus from first principles, then shows it running in production engines, then names the failure modes. The interactive surface visualizes the curves and the index search itself, because the locality intuition is impossible to convey in text.

The bounded claim. The chapter does not assert that fractal indexes are universally faster. It asserts that for skewed multi-dimensional OLAP, persistent-correlated time-series, low-intrinsic-dimension embedding spaces, and high-cardinality spatial selectivity, the fractal apparatus produces measurable engineering wins that the default-histograms approach cannot match.

## S### Acceptance criteria

- **S001-clean-clone-runs.** A reader who clones the repo, creates a Python 3.9+ venv, and `pip install -r notebooks/14-fractal-indexing/requirements.txt` can execute every notebook from 14.0 through 14.8 end-to-end on a laptop with no external services beyond optional DuckDB.
- **S002-studio-renders.** Opening `indexing-studio.html` directly in a browser renders three working interactive labs without a backend.
- **S003-citation-fidelity.** Every empirical claim is anchored to a verified citation. Numerical claims about Liquid Clustering, Hilbert R-trees, and HNSW cite the original sources or release notes verbatim.
- **S004-fractal-thread-continues.** Chapter 14 explicitly extends Chapters 11-13 by reusing fractal-dimension and Hurst-exponent concepts, applied here to engineering problems instead of governance or research analytics.
- **S005-honesty-notebook-included.** Notebook 14.8 names the failure modes explicitly. The chapter is not complete without it.
- **S006-pages-integration.** The studio page is reachable from `index.html` primary nav, the four existing studio pages cross-link to it, the README is updated, and Chapter 14 appears in the curriculum arc with the same visual treatment as Chapters 10-13.
- **S007-no-co-authors.** Every commit uses the `mhdk1602 / mhdk.dinesh@gmail.com` identity with SSH signing and zero AI co-author trailers.
- **S008-benchmark-honest.** Notebook 14.5 (DuckDB Z-order vs Hilbert benchmark) reports both the wins and the losses; benchmarks must run on the reader's machine and produce numbers, not just describe them.

## F### Functional requirements

### Notebook spine (8 + a closer = 9 notebooks)

- **F001 14.0 Why Indexes Are Already Fractal.**
  - Frames the chapter. Names the three production fractal indexes most engineers use without recognizing them: Z-order, Hilbert, HNSW.
  - Reproduces a one-paragraph history: Hilbert (1891), Lebesgue (1904), Faloutsos lab (1990s-2000s), modern revival (2020s).
  - Sets the bounded claim and names the audiences.

- **F002 14.1 Space-Filling Curves: Z-order, Hilbert, and Locality.**
  - Build Z-order (Morton) and Hilbert curves in pure NumPy on a 16×16 and 64×64 grid.
  - Compute the locality measure: average path distance for points within Euclidean distance `r`.
  - Show that Hilbert preserves locality 30-40% better than Z-order on average.
  - Includes a worked visualization of both curves overlaid on a 32×32 grid.

- **F003 14.2 Hilbert R-tree: Bulk-Loading by Fractal Order.**
  - Reproduce Kamel-Faloutsos (1994) Hilbert R-tree bulk loading on a synthetic 10,000-point dataset.
  - Compare against naive R-tree and Hilbert-bulk-loaded R-tree; report node utilization (Hilbert-loaded ≈100%, naive ≈70%) and bounding-box area savings.
  - Use `rtree` Python package for the comparison baseline.

- **F004 14.3 Fractal Dimension as a Selectivity Oracle.**
  - Implement correlation dimension D2 estimator (Grassberger-Procaccia, 1983).
  - Reproduce the Faloutsos-Kamel (1994) selectivity prediction formula on a real dataset (NYC taxi pickup coordinates, sampled).
  - Compare predicted vs actual range-query selectivity; report relative error.
  - Compare against PostgreSQL `EXPLAIN ANALYZE` selectivity estimates if available; otherwise against a naive uniform-distribution estimator.

- **F005 14.4 HNSW as a Hierarchical Small-World Index.**
  - Build a tiny HNSW (50 nodes, 3 layers) in pure Python with NumPy.
  - Visualize layer assignment and search descent for a sample query.
  - Report degree distribution per layer; show the scale-separation that produces logarithmic complexity.
  - Connect explicitly to Watts-Strogatz small-world theory and Song-Havlin-Makse fractal-network framework.

- **F006 14.5 Liquid Clustering at Home: Z-order vs Hilbert on Parquet.**
  - Use DuckDB to bulk-load a real geospatial dataset (NYC taxi pickup or OSM building footprints).
  - Order three copies: row-major, Z-order, Hilbert.
  - Run a battery of bounding-box queries; report I/O (pages read), wall-clock latency, and Parquet file sizes.
  - Honest reporting: include workloads where the win is small and workloads where Hilbert wins big.

- **F007 14.6 Adaptive Chunking by Hurst Exponent.**
  - Reuse the candidate's Zenodo paper Hurst estimator (DFA-based).
  - Generate fGn streams at H=0.3, 0.5, 0.8.
  - Compare fixed-interval chunking versus Hurst-driven chunk-boundary placement on a range-query workload.
  - Connect explicitly to Paper 0 (Zenodo) and the H2 hypothesis in the research plan.

- **F008 14.7 Capstone: Build Your Own Fractal Index for Your Workload.**
  - Walk the reader through choosing the right index for a workload they describe (geospatial, embedding, time-series, or relational).
  - Decision tree: workload shape → recommended index family → tuning hyperparameters.
  - Output: a printable workload-to-index recommendation card and a reproducible benchmark harness.

- **F009 14.8 When the Speedup Is a Lie.**
  - Names the failure modes:
    1. Skewed updates make Hilbert order go stale faster than Z-order.
    2. Selectivity estimators based on training-time fractal dimension fail when the data drifts.
    3. HNSW recall collapses when the embedding manifold has high local intrinsic dimension.
    4. Benchmark cache effects can produce 5-10× phantom speedups that vanish in production.
  - Demonstrates each with an adversarial example.
  - Pairs explicitly with notebooks 12.7 and 13.8 (the prior failure-mode closers).

### Studio page (indexing-studio.html)

- **F010 Lab 1: Curve Trace Animator.** A 32×32 grid where the reader watches a Hilbert or Z-order curve trace through, square by square, with adjustable speed. A draggable query rectangle highlights which "tiles" must be fetched; counts pages read for each curve type and a row-major baseline. The locality intuition becomes visceral when the reader watches Hilbert keep returning to nearby cells while Z-order jumps across the grid.

- **F011 Lab 2: Index Race Track.** Bulk-load 5,000 random points (with optional skew slider). Toggle index types (naive scan, Z-order, Hilbert, R-tree). The query box position is controlled by drag. A bar chart shows pages-fetched and ms-elapsed for each index, updated in real time. The reader can see one method beating another by a factor of 10×.

- **F012 Lab 3: HNSW Climber.** Visualize a tiny HNSW (50-100 nodes, 3 layers). The reader picks a query point. The search descends layer by layer with animated arrows; visited dots turn yellow. A side panel shows the visit count per layer to demonstrate logarithmic complexity. A slider for `M` (graph degree) lets the reader rebuild and observe how recall and visit-count change.

- **F013 Site integration.** The page is wired into `index.html` primary navigation, the curriculum arc gets a fourth featured card, a new spotlight panel describes the chapter, and the four existing studio pages cross-link to it.

### Generator script

- **F014 scripts/generate_chapter_14_notebooks.py.** A single Python script emits all nine notebooks deterministically, mirroring the Chapter 12 and Chapter 13 generators.

## N### Non-functional requirements

- **N001 Python 3.9+ compatibility.** No PEP 604 union syntax in signatures.
- **N002 Dependency surface.** `numpy`, `pandas`, `scipy`, `matplotlib`, `networkx`, `rtree`, `duckdb`, `pyarrow`. All available via pip; no native build dependencies beyond what `rtree` and `duckdb` already require.
- **N003 Studio independence.** Pure vanilla JS, no backend, no npm. Reuses the design tokens from `governance-studio.css`.
- **N004 Citation discipline.** All claims about Liquid Clustering, HNSW, and Hilbert R-trees include the source. Numerical claims (10× speedup, 28% savings, 44% compression) are attributed verbatim to the original release notes or papers.
- **N005 Voice.** Bounded claims, named failure modes, named audiences, dissertation linkages where appropriate. No marketing language.
- **N006 Visual continuity.** Studio reuses the existing color tokens and typography (Fraunces + Manrope). It does not introduce a new design system.
- **N007 Benchmark honesty.** Notebooks that report numbers must produce them on the reader's machine, not pre-baked. The reader sees their own results.

## E### Edge cases

- **E001 DuckDB not installed.** Notebook 14.5 detects the missing dependency, falls back to a pure-Python Parquet emulation that demonstrates the qualitative result, and prints clearly what the reader is missing.
- **E002 Network blocked.** Notebook 14.5 detects HTTP failure when fetching real geospatial data and falls back to a synthetic dataset.
- **E003 R-tree library missing.** Notebook 14.2 detects missing `rtree` and falls back to a pure-Python R-tree implementation (slower; explicitly slower).
- **E004 Reader edits sliders to extreme values in studio.** All three labs handle degenerate inputs (zero points, query box outside the grid, M=0) by showing a neutral state and a prompt.
- **E005 HNSW with M=2.** Notebook 14.4 and Lab 3 handle the degenerate small-M case by reporting "graph too sparse for ANN; recall collapses."

## C### Components

- **C001 SpaceFillingCurve.** Z-order and Hilbert curve generators in `lib/curves.py`-style helper section. Reused across 14.1, 14.2, 14.5, and Lab 1.
- **C002 CorrelationDimension.** Grassberger-Procaccia D2 estimator. Used in 14.3 and 14.6.
- **C003 HilbertRTreeBulkLoader.** Bulk-load helper that orders entries by Hilbert value before R-tree insertion. Used in 14.2.
- **C004 TinyHNSW.** Pure-Python HNSW for pedagogical visualization. Used in 14.4 and Lab 3.
- **C005 BenchmarkHarness.** Shared timing utility used in 14.5 and 14.6.
- **C006 IndexingStudio.** Three lab modules in `site-assets/indexing-studio.js`.

## A### APIs and data shapes

- **A001 Curve API.** `hilbert_d_to_xy(d, n)`, `hilbert_xy_to_d(x, y, n)`, `zorder_xy_to_d(x, y)`, `zorder_d_to_xy(d)`. n is power of 2.
- **A002 Selectivity prediction (Faloutsos-Kamel 1994).** `predicted_selectivity(D2, query_radius, dataset_size)` returns expected fraction of points returned.
- **A003 HNSW API.** `TinyHNSW(M=16, ef_construction=100, ml=1/np.log(2))` with `add(vector)` and `search(query, k=10)`.

## M### Data models

- **M001 NYC taxi sample.** ~50,000 pickup coordinates from the public 2024 yellow-cab dataset (downsampled and bbox-clipped to Manhattan for tractability and reproducibility).
- **M002 OSM building footprints.** Optional alternative to taxi data; ~10,000 polygon centroids.
- **M003 Synthetic skew dataset.** `make_zipfian_2d(n, alpha)` for the skew slider in Lab 2.
- **M004 fGn time series.** Three pre-generated 4096-point series at H=0.3, 0.5, 0.8 for 14.6.

## V### Validation rules

- **V001 Curve invertibility.** `hilbert_xy_to_d(*hilbert_d_to_xy(d, n), n) == d` for all d in range. Same for Z-order. Asserted in 14.1.
- **V002 Locality bound.** Average curve-distance for Euclidean-r-neighbours must be lower for Hilbert than for Z-order. Asserted in 14.1.
- **V003 D2 stability.** Correlation dimension must be reported only when the log-log slope is stable across at least 4 scales (R² > 0.9).
- **V004 HNSW recall floor.** Lab 3 reports recall@10 alongside latency; if recall < 0.5, flag as misconfigured.
- **V005 Benchmark variance.** All benchmark results in 14.5 and 14.6 are run 5 times; mean and standard deviation are reported.

## D### Dependencies

- Chapter 12 box-covering and visibility-graph code (referenced, not duplicated).
- Chapter 13 governance-studio CSS palette (reused).
- Zenodo paper Hurst estimator (reimplemented inline in 14.6).

## R### Risks

- **R001 DuckDB version drift.** `ST_Hilbert` requires a recent DuckDB version. Pinned in requirements.txt with a fallback path.
- **R002 NYC taxi dataset URL drift.** TLC has changed dataset URLs in the past. Cached snapshot or instructions to reproduce.
- **R003 Benchmark unreproducibility.** Wall-clock results vary by machine. Mitigated by reporting relative ratios alongside absolute numbers.
- **R004 Studio canvas performance.** A 32×32 grid with animation is fine; 256×256 would not be. Capped at 64×64 maximum.

## Q### Open questions to resolve before build

- **Q001** Should the chapter ship a real Iceberg integration as a stretch lab, or stay on DuckDB for portability? *Default proposal: stay on DuckDB; note Iceberg integration as a follow-up exercise.*
- **Q002** Should the studio include a fourth lab on H3 hexagonal indexing? *Default proposal: no; three labs is the cap from prior chapters. H3 gets a paragraph in 14.5.*
- **Q003** Should notebook 14.3 attempt the live PostgreSQL `EXPLAIN ANALYZE` comparison, or stay synthetic? *Default proposal: synthetic, with a clearly marked extension exercise for readers who have a Postgres instance.*
- **Q004** Should notebook 14.6 use the `lindel` DuckDB extension, or stay in pure Python? *Default proposal: pure Python first, with a final cell that demonstrates the same result via lindel for readers who want the production path.*
