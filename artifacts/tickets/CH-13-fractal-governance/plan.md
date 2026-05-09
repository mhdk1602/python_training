# CH-13 Fractal Governance: Plan

**Spec:** [spec.md](spec.md)
**Owner:** Dineshkumar Malemapti Hari
**Status:** Approved (proceed)
**Created:** 2026-05-09

This plan is test-driven and broken into small steps. Each P### implements a slice of one or more F###/C###/M### IDs, each W### records the file change, each K### gates progress with a test or smoke check, and each X### marks a logical commit.

## P001 Scaffold the chapter directory and dependencies

- **Implements:** N002, F014.
- **Files written:**
  - W001 `notebooks/13-fractal-governance/requirements.txt` (chapter-local pinned dependencies).
  - W002 `notebooks/13-fractal-governance/README.md` (chapter overview).
- **K001:** `pip install -r requirements.txt` succeeds in a fresh venv.

## P002 Author the generator script

- **Implements:** F014.
- **Files written:**
  - W003 `scripts/generate_chapter_13_notebooks.py` with helper cell builders and stubs for all nine notebook contents.
- **K002:** `python scripts/generate_chapter_13_notebooks.py` runs without error and emits nine `.ipynb` files (empty execution counts, no outputs yet).

## P003 Write notebook 13.0 (framing) into the generator

- **Implements:** F001, S004.
- **Files updated:**
  - W004 `scripts/generate_chapter_13_notebooks.py` (NB_13_0 content).
- **K003:** Notebook executes top-to-bottom in <10 seconds with no errors.
- **X001 commit:** `Add Chapter 13 spec, plan, and chapter scaffolding`

## P004 Write notebook 13.1 (multi-scale pressure field) into the generator

- **Implements:** F002, C001, A001, V003.
- **Files updated:**
  - W005 `scripts/generate_chapter_13_notebooks.py` (NB_13_1).
- **K004:** PressureVector clipping passes assertion. Radar plot renders. Worked example with Walsh et al. 2025 produces a sensible decomposition.

## P005 Write notebook 13.2 (decoupling) into the generator

- **Implements:** F003, U002.
- **Files updated:**
  - W006 `scripts/generate_chapter_13_notebooks.py` (NB_13_2).
- **K005:** decoupling_dimension monotonicity assertion holds (more divergence → higher score).

## P006 Write notebook 13.3 (governance KG) into the generator

- **Implements:** F004, M001, V001, C002.
- **Files updated:**
  - W007 `scripts/generate_chapter_13_notebooks.py` (NB_13_3 with embedded bibliography seed).
- **K006:** NetworkX graph constructs without error, Louvain runs, box-covering returns a valid `d_B` or an explicit "no scaling regime" message.

## P007 Write notebook 13.4 (visibility graphs of governance time series)

- **Implements:** F005, C003, S004, E005.
- **Files updated:**
  - W008 `scripts/generate_chapter_13_notebooks.py` (NB_13_4).
- **K007:** Three regimes render distinct degree-distribution shapes. Degenerate-input check returns "degenerate" rather than a slope.

## P008 Write notebook 13.5 (AI as subject and agent)

- **Implements:** F006, C004, A002, A004, V004, E001, R001.
- **Files updated:**
  - W009 `scripts/generate_chapter_13_notebooks.py` (NB_13_5 with LLMParser + MockParser).
- **K008:** Notebook executes both with and without `ANTHROPIC_API_KEY`. JSON validator catches malformed parser output and falls back to mock.

## P009 Write notebook 13.6 (translation cascade)

- **Implements:** F007, C005, A003, V002.
- **Files updated:**
  - W010 `scripts/generate_chapter_13_notebooks.py` (NB_13_6 with three preset cascades).
- **K009:** Drift values lie in [0, 1]; drift > 0.6 is flagged.

## P010 Write notebook 13.7 (capstone)

- **Implements:** F008, S001.
- **Files updated:**
  - W011 `scripts/generate_chapter_13_notebooks.py` (NB_13_7).
- **K010:** Capstone runs end-to-end with the mock parser and produces a printable summary.

## P011 Write notebook 13.8 (when the visualization lies)

- **Implements:** F009, S005, R001-R004.
- **Files updated:**
  - W012 `scripts/generate_chapter_13_notebooks.py` (NB_13_8).
- **K011:** Each of the four failure modes is demonstrated with a concrete adversarial example.
- **X002 commit:** `Add Chapter 13 fractal governance notebook spine`

## P012 Build studio HTML

- **Implements:** F010, F011, F012, S002, N006.
- **Files written:**
  - W013 `governance-studio.html`.
- **K012:** Page loads in browser, all three lab containers render placeholders.

## P013 Build studio CSS

- **Implements:** N006.
- **Files written:**
  - W014 `site-assets/governance-studio.css` (reuses tokens from `fractal-graphs.css` palette).
- **K013:** Visual regression check by eye against existing studio pages: no token drift.

## P014 Build studio JS (three labs)

- **Implements:** F010, F011, F012, C006, V002, V003.
- **Files written:**
  - W015 `site-assets/governance-studio.js`.
- **K014:** Reload `governance-studio.html`, edit a scenario, drag a value, swap a cascade preset; readouts update without console errors.
- **X003 commit:** `Add Fractal Governance studio page with three interactive labs`

## P015 Wire Chapter 13 into the site

- **Implements:** F013, S006.
- **Files updated:**
  - W016 `index.html` (nav link, curriculum-arc card, spotlight panel, metrics).
  - W017 `README.md` (curriculum, repository structure, learning roadmap, syllabus).
  - W018 `fractal-graphs.html`, `fractals-governance.html`, `embeddings-bridge.html`, `ranking-lab.html` (cross-link nav).
- **K015:** Open each modified page; confirm the new link is present and navigates correctly.
- **X004 commit:** `Wire Chapter 13 into site index, README, and existing studio pages`

## P016 Smoke test the chapter

- **Implements:** S001, I001.
- **Steps:**
  - Create `.venv-ch13`, `pip install -r notebooks/13-fractal-governance/requirements.txt`.
  - Execute notebooks via `jupyter nbconvert --to notebook --execute --inplace` for each.
  - Confirm 13.5 mock path activates (no key set).
  - Confirm git status clean except for output cells.
- **K016:** All nine notebooks execute and embed outputs without error.

## P017 Commit and push

- **Implements:** S007.
- **Steps:**
  - Verify `git config user.name` is `mhdk1602` and `user.email` is `mhdk.dinesh@gmail.com`.
  - Confirm SSH signing config.
  - Confirm no AI co-author trailers in `git log`.
  - `git push origin main`.
- **X005 commit:** `Embed executed Chapter 13 notebook outputs`

## Final validation (S### sweep)

- S001 to S007 verified manually and via the smoke pass before push.

## References

- Spec: [spec.md](spec.md)
- Chapter 12 reference: `notebooks/12-fractal-graphs/`, `fractal-graphs.html`, `scripts/generate_chapter_12_notebooks.py`
- Research plan: `non-git-files/governance-ai-fractals-research-plan.md` (out of repo)
- Chapter 12 research plan: `non-git-files/fractal-graphs-research-plan.md` (out of repo)
- Candidate's published work: Malemapti Hari, D. (2026). *Static and Temporal Fractal Coupling Between Volatility and Trading Volume*. Zenodo. https://doi.org/10.5281/zenodo.19611544
