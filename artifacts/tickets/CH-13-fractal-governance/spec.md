# CH-13 Fractal Governance: Pressure Fields, AI Mediation, and the Visualization Layer

**Owner:** Dineshkumar Malemapti Hari
**Status:** Approved (proceed to plan and implementation)
**Created:** 2026-05-09
**Connects to:** Chapter 11 (Fractals and governance), Chapter 12 (Fractal graphs), Chapter 8 (LLMs), Chapter 10 (Retrieval and agents), and the candidate's PhD dissertation (UC, Spring 2026)

## Context

Chapter 11 introduced fractals as a stewardship lens. Chapter 12 generalized that lens onto graphs. The dissertation studies institutional pressures on data governance practice through qualitative case study. Chapter 13 fuses the three: it teaches institutional theory's three pressure mechanisms (coercive, mimetic, normative) as **multi-scale fields measurable with fractal-graph descriptors**, uses AI as both subject and agent in governance measurement, and renders the result as the most ambitious interactive surface in the repository.

The pedagogical claim is bounded. The chapter does not assert that every governance phenomenon is fractal, that AI mediation replaces qualitative coding, or that pressure scores from a parser are equivalent to validated psychometric instruments. The chapter teaches a usable apparatus and names the failure modes explicitly.

## S### Acceptance criteria (success looks like this)

- **S001-clean-clone-runs.** A reader who clones the repository, creates a Python 3.9+ virtualenv, and `pip install -r notebooks/13-fractal-governance/requirements.txt` can execute every notebook from 13.0 through 13.8 end-to-end on a laptop without an Anthropic API key, and notebook 13.5 degrades gracefully to a deterministic mock when no key is present.
- **S002-studio-renders.** Opening `governance-studio.html` directly in a browser (file:// or http) renders three working interactive labs without a backend: pressure field, decoupling lens, and regulation cascade. No external API calls are required for the three labs to operate.
- **S003-citation-fidelity.** Every academic claim in the notebooks and the studio is anchored to a verified citation drawn from the dissertation bibliography or from the candidate's own published work. Citations follow APA 7 with full DOI or stable URL.
- **S004-fractal-thread-continues.** Chapter 13 explicitly extends Chapters 11 and 12 by reusing visibility-graph and box-covering descriptors, applied to governance objects (incident time series, knowledge graphs, regulation cascades).
- **S005-honesty-notebook-included.** Notebook 13.8 names the failure modes of the apparatus before any reader can deploy it. The chapter is not complete without it.
- **S006-pages-integration.** The studio page is reachable from `index.html` primary nav, the existing four studio pages cross-link to it, the README is updated, and Chapter 13 appears in the curriculum arc with the same visual treatment as Chapters 10-12.
- **S007-no-co-authors.** Every commit uses the `mhdk1602 / mhdk.dinesh@gmail.com` identity with SSH signing and zero AI co-author trailers.

## F### Functional requirements

### Notebook spine (8 + a closer = 9 notebooks)

- **F001 13.0 Why Governance Needs a Fractal Lens.**
  - Frames the chapter. Names the three streams (institutional theory, fractal graphs, AI governance).
  - Defines pressure mechanisms with verified citations (DiMaggio-Powell 1983, Meyer-Rowan 1977, Scott 2008, Greenwood 2011).
  - Lists the eight notebooks and the bridges between them.
  - Sets the bounded claim. Names the audiences.

- **F002 13.1 The Multi-Scale Pressure Field.**
  - Implements a `PressureVector` dataclass with three dimensions (coercive, mimetic, normative) and a `scale` enum (field, firm, division, team, practitioner).
  - Provides `decompose_across_scales(case_text, scale_set)` returning a 3xN matrix of pressure intensities.
  - Plots the pressure field as a 3D radar / heatmap small-multiples grid.
  - Includes a worked example using a verified passage (Walsh et al. 2025 on consulting-firm governance).
  - Closes with a self-check exercise.

- **F003 13.2 Decoupling as Multi-Scale Decoherence.**
  - Formalizes Meyer-Rowan decoupling as **scale-dependent divergence between formal and operational signals**.
  - Implements `decoupling_dimension(formal_series, operational_series)` returning a scalar that quantifies how much divergence propagates across measurement scales.
  - Uses the Longpre et al. 2024 audit (70% license miscategorization) as the worked empirical example.
  - Connects back to Chapter 11.4 duplicate-cluster decoupling between match scores and steward judgment.

- **F004 13.3 The Governance Knowledge Graph.**
  - Parses an embedded set of ~30 verified citations from the dissertation bibliography into a NetworkX graph with author, paper, and concept nodes.
  - Computes degree distribution and box dimension `d_B` using Chapter 12's box-covering implementation.
  - Runs Louvain community detection and labels communities by their dominant concept.
  - Reports the bounded claim: the bibliography KG of one dissertation is too small for asymptotic claims, but the descriptors are still useful for triage.

- **F005 13.4 Visibility Graphs of Governance Time Series.**
  - Reuses the Chapter 12 visibility-graph algorithm.
  - Generates synthetic governance incident streams with three regimes: low-maturity (bursty), medium-maturity (mixed), high-maturity (smooth) and computes the visibility-graph degree exponent for each.
  - Optionally loads a public proxy series (CVE counts or GitHub Advisory time series) if a network connection is available; otherwise uses the synthetic dataset.
  - Connects to Malemapti Hari (2026) Zenodo paper for methodological provenance.

- **F006 13.5 AI as Governance Subject and Agent.**
  - **Subject side:** builds a provenance graph for an LLM training pipeline (data sources, license, training run, evaluation, deployment). Computes box dimension and identifies high-blast-radius nodes.
  - **Agent side:** uses the Anthropic Claude API to parse a free-text governance incident report into a structured `GovernanceIncident` object (involved scales, dominant pressure, suggested control). Includes graceful fallback to a deterministic mock parser when no API key is present.
  - Names hallucination risks explicitly and the validation requirements before such a parser could be used in production.
  - Cites Birkstedt et al. 2023, Mäntymäki et al. 2022, Papagiannidis et al. 2025.

- **F007 13.6 The Translation Cascade.**
  - Models a regulatory cascade: source regulation (e.g., DORA Article 9 or EU AI Act Article 10) → firm policy → engagement SOP → practitioner action.
  - Implements `translation_drift(layer_texts)` using TF-IDF similarity decay between adjacent layers.
  - Plots the cascade with drift annotations on each transition.
  - Connects to Stepanovic et al. 2025, Mahmutovic 2025, Faulconbridge et al. 2024 (hyper-muddling, the consultancy-as-translator argument).

- **F008 13.7 Capstone Lab: Build Your Own Governance Pressure Map.**
  - Walks the reader through assembling their own pressure map for an environment they describe.
  - Uses the parser from 13.5 (or its mock fallback) to convert free-text input into a pressure profile.
  - Outputs a printable summary: pressure profile, decoupling dimension, suggested next governance action, citations.

- **F009 13.8 When the Visualization Lies.**
  - Names four failure modes:
    1. Pressure scores are subjective and vary by parser prompt.
    2. Decoupling lacks ground truth without longitudinal data.
    3. Knowledge graph from one bibliography reflects the curator's reading list, not the field.
    4. AI parsers hallucinate; their outputs need validation against trained human coders.
  - Demonstrates each failure mode with a small adversarial example.
  - Pairs explicitly with notebook 12.7 of Chapter 12.

### Studio page (governance-studio.html)

- **F010 Lab 1: Multi-Scale Pressure Field.** A 3-axis (coercive, mimetic, normative) interactive radar with a scale slider that decomposes a sample governance scenario across scales. The reader can edit the scenario text and see the pressure vector recompute (using a deterministic JS heuristic, not the live LLM).
- **F011 Lab 2: The Decoupling Lens.** A side-by-side formal vs operational visualization. Drag any value on either side; the decoupling-dimension readout updates in real time. The lens illustrates Meyer-Rowan's classical claim with a clickable pre-loaded scenario set.
- **F012 Lab 3: Regulation Cascade.** An animated waterfall from regulation source through firm policy, engagement SOP, and practitioner action. Each layer has an editable label. The translation-drift score recomputes when labels change. Three pre-loaded cascades (DORA, EU AI Act, DAMA-DMBOK) seed the lab.
- **F013 Site integration.** The page is wired into `index.html` primary navigation, the curriculum arc, a new spotlight panel, and the four existing studio pages cross-link to it.

### Generator script

- **F014 scripts/generate_chapter_13_notebooks.py.** A single Python script that emits all nine notebooks deterministically, mirroring the Chapter 12 generator pattern. Notebook outputs are not embedded by the generator (papermill or jupyter execute is run separately to embed outputs).

## N### Non-functional requirements

- **N001 Python compatibility.** Notebooks run on Python 3.9+ (matching the candidate's daily environment). No Python 3.10+ syntax (no `dict | None`, no PEP 604 unions in signatures).
- **N002 Dependency surface.** Add only what is needed: `networkx`, `python-louvain`, `scikit-learn` (for TF-IDF), `scipy`, `pandas`, `numpy`, `matplotlib`, `anthropic` (optional). No heavyweight UI dependencies.
- **N003 Studio independence.** The studio page must not require a backend. All three labs are pure vanilla JS with inline math. No npm build step. No D3 or React dependencies; rendering uses native SVG with the visual idiom established in `fractal-graphs.css`.
- **N004 Citation discipline.** Every citation includes a DOI or a stable URL. Citations match the verified May 2026 audit in the dissertation bibliography.
- **N005 Voice.** Prose follows the candidate's content standards: bounded claims, named failure modes, named audiences, dissertation linkages where appropriate, no marketing language.
- **N006 Visual continuity.** Studio reuses the existing color tokens (`--sand`, `--moss`, `--mist`, `--cream`) and typography (Fraunces + Manrope). It does not introduce a new design system.

## E### Edge cases

- **E001 Anthropic key missing.** Notebook 13.5 detects missing `ANTHROPIC_API_KEY` and switches to a deterministic mock parser. The notebook reports clearly which path it took.
- **E002 Network blocked.** Notebook 13.4 detects HTTP failure when fetching public CVE data and falls back to the synthetic dataset, reporting the substitution.
- **E003 Reader edits scenario in studio with empty text.** All three studio labs handle empty input by showing a neutral state and a prompt: "type a scenario or load a preset."
- **E004 Knowledge graph small-N.** Notebook 13.3 reports its own confidence interval on `d_B` and explicitly states that ~30 papers is too few for asymptotic claims.
- **E005 Visibility graph degenerate input.** Notebook 13.4 handles constant series (all incidents identical) by returning an explicit "degenerate" status rather than a misleading slope.

## C### Components

- **C001 PressureVector / Scale.** Dataclass + enum in 13.1, reused by 13.2, 13.5, 13.7.
- **C002 BoxCover.** Reused from Chapter 12. Imported in 13.3.
- **C003 VisibilityGraph.** Reused from Chapter 12. Imported in 13.4.
- **C004 GovernanceParser.** New in 13.5. Two implementations: `LLMParser` (Anthropic-backed) and `MockParser` (deterministic regex+keyword heuristic).
- **C005 TranslationCascade.** New in 13.6. TF-IDF based.
- **C006 GovernanceStudio (studio JS).** Three lab modules in `site-assets/governance-studio.js`, each self-contained, sharing the reveal-on-scroll observer pattern from `fractal-graphs.js`.

## A### APIs and data shapes

- **A001 PressureVector.** `{coercive: float, mimetic: float, normative: float, scale: Scale, evidence: list[str]}` where each pressure is in [0, 1].
- **A002 GovernanceIncident.** `{summary: str, scales: list[Scale], dominant_pressure: str, suggested_control: str, confidence: float, citations: list[str]}`.
- **A003 CascadeLayer.** `{name: str, text: str, drift_to_next: float | None}`.
- **A004 Anthropic call shape (13.5).** `client.messages.create(model="claude-3-haiku", max_tokens=512, messages=[...])`. Wrapped in try/except so missing key or rate limit triggers `MockParser`.

## M### Data models

- **M001 Bibliography seed.** A list of ~30 verified citations from the dissertation bibliography embedded directly in 13.3 as Python literals. Includes author, year, title, venue, DOI, three concept tags. The seed is curated to span the four pressure communities (regulatory, methodological, AI governance, classical institutional theory).
- **M002 Synthetic incident streams.** Three 256-point series for low/medium/high maturity governance, each with documented generative parameters (mean inter-arrival, severity distribution, autocorrelation).
- **M003 Cascade preset library.** Three pre-loaded cascades for DORA, EU AI Act, and DAMA-DMBOK. Each layer is two to three sentences. Each preset cites its source.

## V### Validation rules

- **V001 d_B stability.** Box dimension reported only when the log-log slope is stable across at least four scales (R^2 > 0.9). Otherwise notebook reports "no scaling regime."
- **V002 Drift bounds.** Translation drift bounded to [0, 1]. Drift > 0.6 is flagged as suspicious; flag is shown in studio Lab 3.
- **V003 Pressure normalization.** Each pressure component clipped to [0, 1] and the L1 norm of the vector is annotated alongside the radar plot.
- **V004 Anthropic safety.** All Anthropic calls use a strict system prompt that constrains output to the `GovernanceIncident` shape; output is JSON-validated before display, falling back to mock if validation fails.

## U### Unit / I### Integration test ideas (lightweight)

- **U001** PressureVector clipping math.
- **U002** decoupling_dimension reproducibility on a fixed seed.
- **U003** translation_drift adjacency identity (drift(x, x) = 0).
- **I001** Notebooks 13.0 through 13.8 execute end-to-end with deterministic seeds.
- **I002** Studio labs render in a headless browser without console errors.

(For this iteration, tests are realized as embedded notebook assertions and a manual smoke pass, mirroring Chapter 12.)

## D### Dependencies

- Chapter 12 box-covering and visibility-graph code (copied or imported).
- Chapter 8 Anthropic patterns (env var loading, prompt template style).
- The dissertation bibliography (test2.md) for citation accuracy. Not embedded; ~30 citations curated into 13.3 directly.
- python-louvain (community detection), scikit-learn (TF-IDF for cascade drift).

## R### Risks

- **R001 LLM brittleness.** Notebook 13.5 with a real key may produce non-deterministic outputs; mitigated by structured-output prompt and JSON validation. Mock fallback ensures CI / smoke tests are deterministic.
- **R002 Studio scope creep.** Three labs is the cap. A fourth lab is tempting but pushes complexity past the time budget.
- **R003 Citation drift.** New papers appear monthly. Mitigated by anchoring citations to the May 2026 audited bibliography and including a TODO at the end of 13.3 to refresh quarterly.
- **R004 Visualization performance.** SVG with 30 nodes + 60 edges is fine. If the KG grows past ~100 nodes, performance degrades and a canvas-based fallback would be needed. Out of scope for this chapter.

## Q### Open questions resolved

- **Q001** Should the studio call the live Anthropic API from JS? **Resolved: no.** The studio uses deterministic JS heuristics. The live API lives in notebook 13.5 only, where the reader controls the API key.
- **Q002** Should the bibliography KG be loaded from `test2.md` at runtime? **Resolved: no.** The KG is seeded with curated literals so the chapter is self-contained and the dissertation bibliography stays out of the public repo.
- **Q003** Should this chapter be Chapter 12.5 or Chapter 13? **Resolved: Chapter 13.** Chapter 12 was already shipped; Chapter 13 is the next-numbered slot.
- **Q004** Should the studio host four labs or three? **Resolved: three.** The fourth (LLM translator) lives in notebook 13.7 instead.
