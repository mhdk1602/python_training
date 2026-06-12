# Contributing

Thanks for considering a contribution. This repo is a cumulative curriculum, so changes are judged on whether they keep the spine teachable, not just whether the code runs.

## Ways to contribute

- **Fix an error in a notebook.** Open a PR with the corrected cell and a one-line note on what was wrong.
- **Add exercises.** Each notebook closes with "Try It Yourself" tasks. New exercises should be solvable with only the material covered up to that point in the spine.
- **Propose a chapter.** Check the [roadmap](README.md#roadmap-chapters-on-the-bench) first. Open an issue with the chapter number in the title and a sketch of the notebook sequence.
- **Improve a studio.** The interactive pages under `site-assets/` are vanilla JS and CSS. Keep them dependency-free.

## Content standards

The full standards live in [`.cursor/rules/research-entity.mdc`](.cursor/rules/research-entity.mdc). The short version:

1. State what the reader will learn in the first cell.
2. Build from concept to working example to challenge, in that order.
3. All code must execute given the documented prerequisites. Chapter-local dependencies go in the chapter's `requirements.txt`.
4. Tie abstractions to one of the applied systems or a concrete engineering scenario.
5. Advanced chapters (11+) must name their own failure modes. Descriptors that cannot fail cannot inform.

## Workflow

1. Fork and branch from `main` (`feature/your-topic`).
2. Keep notebook names in the `{Chapter}.{Section} {Topic Name}.ipynb` convention.
3. Strip bulky outputs before committing unless the rendered output is the point (plots in the fractal chapters, for example).
4. Open a PR describing what changed and which chapter it touches.

## Site changes

The GitHub Pages site is plain HTML/CSS/JS served from the repo root. To preview locally:

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

No build step, no framework. Keep it that way.
