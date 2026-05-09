"""Generate the nine Chapter 13 (Fractal Governance) notebooks.

Run from the repo root:

    python3 scripts/generate_chapter_13_notebooks.py

Mirrors the Chapter 12 generator. The notebooks are written without execution counts
or outputs; embed outputs separately via:

    for nb in notebooks/13-fractal-governance/13.*.ipynb; do
      jupyter nbconvert --to notebook --execute --inplace --allow-errors "$nb"
    done
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "notebooks" / "13-fractal-governance"


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
# 13.0 Why Governance Needs a Fractal Lens
# ---------------------------------------------------------------------------

NB_13_0 = [
    markdown_cell(
        "> **Chapter 13, Part 0** | Advanced lens. **Focus:** the three streams (institutional theory, fractal-graph descriptors, AI governance) and why a single chapter braids them."
    ),
    markdown_cell(
        """# Why Governance Needs a Fractal Lens

Three research streams converge on data governance practice without ever meeting in published literature.

1. **Institutional theory** describes pressure dynamics qualitatively. Coercive, mimetic, and normative isomorphic mechanisms shape how organizations adopt practices (DiMaggio and Powell, 1983; Meyer and Rowan, 1977; Scott, 2008; Greenwood et al., 2011).
2. **Network science and fractal graph theory** give us multi-scale graph descriptors. Box-covering on graphs (Song et al., 2005), graph fractal dimension (Skums and Bunimovich, 2020), and visibility graphs of time series (Lacasa et al., 2008) make scale-sensitivity measurable.
3. **AI governance** is the new pressure environment that intensifies all three classical isomorphic mechanisms. AI governance is fragmented and gaps between external frameworks and operational implementation are well-documented (Birkstedt et al., 2023; Mäntymäki et al., 2022; Papagiannidis et al., 2025).

Each stream is mature on its own. The intersection is empty in the published literature. Chapter 13 of this repository builds an apparatus that lives at the intersection. The chapter teaches the apparatus and names the failure modes. The companion research plan describes the validation program required to push the apparatus from prototype to peer-reviewed methodological contribution.

## Bounded claim

This chapter does not argue that every governance phenomenon is fractal. It does not argue that AI parsers replace qualitative coding by trained human analysts. It does not argue that pressure scores generated from a heuristic are equivalent to validated psychometric instruments. The chapter argues a narrower thing: that fractal-graph descriptors operationalize the multi-scale structure that institutional theory predicts but rarely measures, that AI is usefully both subject and agent in governance measurement, and that an interactive surface lets practitioners see their own pressure environment in a way text alone cannot. Where the apparatus fails, notebook 13.8 says so explicitly.

## The chapter spine

| Notebook | What it builds |
|---|---|
| 13.0 (this one) | The framing and the bounded claim. |
| 13.1 | A `PressureVector` and `Scale` model; pressure decomposition across five scales. |
| 13.2 | Decoupling as scale-dependent divergence; a `decoupling_dimension` measure. |
| 13.3 | A NetworkX governance knowledge graph with box-covering and Louvain community detection. |
| 13.4 | Visibility graphs of governance incident time series across maturity levels. |
| 13.5 | AI as governance subject (provenance graph) and agent (Anthropic-backed parser with mock fallback). |
| 13.6 | A regulation-to-action translation cascade with TF-IDF drift. |
| 13.7 | A capstone lab that combines 13.1 through 13.6 into one printable diagnostic. |
| 13.8 | The four failure modes; the honesty closer. |

## Three audiences

- **The practitioner** wants a usable apparatus for diagnosing pressure conflicts and decoupling on artifacts they describe in their own words. The capstone (13.7) is for them.
- **The researcher** wants a reproducible methods reference. The provenance graph (13.5) and the translation cascade (13.6) are for them.
- **The student** wants the theory grounded in code. The pressure-field decomposition (13.1) and the decoupling lens (13.2) are for them.

## Where this connects to earlier chapters

Chapter 11 introduced fractal descriptors as a stewardship lens. Chapter 12 generalized that lens onto graphs. Chapter 13 specializes the lens onto governance objects: pressure fields, knowledge graphs, regulation cascades, and AI provenance. The `box_cover` and `visibility_graph` functions are imported from Chapter 12 essentially unchanged. The new components are the pressure model, the decoupling-dimension measure, the AI parser with mock fallback, and the translation-cascade drift.

## Supporting reading

- DiMaggio, P. J., and Powell, W. W. (1983). The iron cage revisited. *American Sociological Review, 48*(2), 147-160.
- Meyer, J. W., and Rowan, B. (1977). Institutionalized organizations. *American Journal of Sociology, 83*(2), 340-363.
- Scott, W. R. (2008). *Institutions and organizations* (3rd ed.). SAGE.
- Greenwood, R. et al. (2011). Institutional complexity and organizational responses. *Academy of Management Annals, 5*(1), 317-371.
- Song, C., Havlin, S., and Makse, H. A. (2005). Self-similarity of complex networks. *Nature, 433*, 392-395.
- Lacasa, L. et al. (2008). From time series to complex networks. *PNAS, 105*(13), 4972-4975.
- Birkstedt, T. et al. (2023). AI governance: Themes, knowledge gaps and future agendas. *Internet Research, 33*(7), 133-167.
- Mäntymäki, M. et al. (2022). Defining organizational AI governance. *AI and Ethics, 2*(4), 603-609.
- Papagiannidis, E. et al. (2025). Responsible AI governance. *J. Strategic Information Systems, 34*(2), Article 101885.
- Malemapti Hari, D. (2026). *Static and Temporal Fractal Coupling Between Volatility and Trading Volume*. Zenodo. https://doi.org/10.5281/zenodo.19611544

## Failure note

If you finish 13.0 and still cannot say which governance question in your own work would benefit from a multi-scale measurement, the chapter has failed. The apparatus is only useful where the question is named first. Pick one before reading 13.1 and we will return to it in 13.7.
"""
    ),
    code_cell(
        """# A small teaser. Three pressure mechanisms; five scales; one tiny visualization.
# Full implementation lives in 13.1.
import numpy as np
import matplotlib.pyplot as plt

scales = ['field', 'firm', 'division', 'team', 'practitioner']
mechanisms = ['coercive', 'mimetic', 'normative']

# Hand-coded teaser values for a hypothetical financial-services consulting firm
# subject to DORA, peer benchmarking, and a strong professional code.
pressure = np.array([
    [0.95, 0.40, 0.55, 0.30, 0.20],   # coercive (regulation strongest at firm/field scale)
    [0.30, 0.70, 0.65, 0.55, 0.35],   # mimetic (peer benchmarking strongest at firm/division)
    [0.45, 0.55, 0.60, 0.75, 0.85],   # normative (professional norms strongest at practitioner)
])

fig, ax = plt.subplots(figsize=(8.6, 3.8))
im = ax.imshow(pressure, aspect='auto', cmap='YlOrBr', vmin=0, vmax=1)
ax.set_xticks(range(len(scales)))
ax.set_xticklabels(scales)
ax.set_yticks(range(len(mechanisms)))
ax.set_yticklabels(mechanisms)
for i in range(pressure.shape[0]):
    for j in range(pressure.shape[1]):
        ax.text(j, i, f'{pressure[i, j]:.2f}', ha='center', va='center',
                color='black' if pressure[i, j] < 0.6 else 'white', fontsize=9)
ax.set_title('Teaser: pressure intensity by mechanism and scale\\n(financial-services consulting firm; hand-coded for illustration)')
fig.colorbar(im, ax=ax, label='intensity')
plt.tight_layout()
plt.show()

print()
print('Read 13.1 to learn the PressureVector and Scale types that produce a matrix like this.')
print('Read 13.2 to learn how decoupling shows up as scale-dependent divergence.')
"""
    ),
    markdown_cell(
        """## How I would debug this

Pick one governance object from your environment before reading 13.1. Examples: a model risk policy, an MDM stewardship workflow, an incident response runbook, an AI usage standard. Write down the object's name, its declared owner, and the scale at which it nominally lives. We will return to that example in 13.7. If it stays abstract, the chapter will feel abstract; if it stays concrete, the apparatus will earn its place.
"""
    ),
]


# ---------------------------------------------------------------------------
# 13.1 The Multi-Scale Pressure Field
# ---------------------------------------------------------------------------

NB_13_1 = [
    markdown_cell(
        "> **Chapter 13, Part 1** | Continues from [13.0 Why Governance Needs a Fractal Lens](13.0%20Why%20Governance%20Needs%20a%20Fractal%20Lens.ipynb). **Focus:** types and a concrete decomposition."
    ),
    markdown_cell(
        """# The Multi-Scale Pressure Field

Institutional theory names three pressure mechanisms (DiMaggio and Powell, 1983).

- **Coercive** pressure comes from regulation, contractual mandate, and explicit power asymmetry. DORA, the EU AI Act, BCBS 239, SOC 2 audits, and client master service agreements are all coercive sources.
- **Mimetic** pressure comes from imitation under uncertainty. Firms copy peers when no clearly correct answer exists. Adopting a competitor's data fabric architecture because they did is mimetic.
- **Normative** pressure comes from professional standards and shared training. CDMP certifications, professional ethics codes, and university curricula transmit normative pressure.

The mechanisms are usually treated qualitatively. This notebook treats them quantitatively, by introducing a `PressureVector` type that lives at one scale and a `decompose_across_scales` operation that produces a 3xN matrix of intensities. The math is light. The discipline is in the labeling.

## Why scales matter

Institutional pressures look different at different scales. A regulation operates strongly at the firm scale (the firm is the legal entity bound by the regulation) but weakly at the practitioner scale (the practitioner is bound by their professional code, not directly by DORA). A peer mimetic pressure operates strongly at the firm-and-division scale (where benchmarking happens) but weakly at the field and practitioner scales. A normative pressure from a professional code operates strongly at the practitioner scale and weakly at the field scale.

If we measure pressure at only one scale, we collapse this multi-scale structure into a single number and lose the diagnostic that institutional theory was designed to deliver. The fractal-graph apparatus from Chapter 12 generalizes naturally: a pressure field is a multi-scale object whose structure is more interesting than any single-scale summary.
"""
    ),
    code_cell(
        """from dataclasses import dataclass, field
from enum import Enum
from typing import List
import numpy as np
import matplotlib.pyplot as plt


class Scale(str, Enum):
    FIELD = 'field'
    FIRM = 'firm'
    DIVISION = 'division'
    TEAM = 'team'
    PRACTITIONER = 'practitioner'


SCALE_ORDER = [Scale.FIELD, Scale.FIRM, Scale.DIVISION, Scale.TEAM, Scale.PRACTITIONER]


@dataclass
class PressureVector:
    coercive: float
    mimetic: float
    normative: float
    scale: Scale
    evidence: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        # V003: pressures clipped to [0, 1].
        self.coercive = float(np.clip(self.coercive, 0.0, 1.0))
        self.mimetic = float(np.clip(self.mimetic, 0.0, 1.0))
        self.normative = float(np.clip(self.normative, 0.0, 1.0))

    def as_array(self) -> np.ndarray:
        return np.array([self.coercive, self.mimetic, self.normative])

    def l1(self) -> float:
        return float(self.coercive + self.mimetic + self.normative)

    def dominant(self) -> str:
        names = ['coercive', 'mimetic', 'normative']
        return names[int(np.argmax(self.as_array()))]


# Self-check.
example = PressureVector(coercive=1.4, mimetic=0.3, normative=-0.1, scale=Scale.FIRM,
                         evidence=['MSA fairness clause', 'competitor benchmark study'])
assert example.coercive == 1.0, 'V003 clipping failed (upper)'
assert example.normative == 0.0, 'V003 clipping failed (lower)'
print(f'PressureVector at {example.scale.value}: {example.as_array()} (dominant={example.dominant()}, L1={example.l1():.2f})')
"""
    ),
    markdown_cell(
        """## A worked example

The example here is a financial-services consulting firm subject to all three pressure mechanisms simultaneously: coercive pressure from regulation (DORA, EU AI Act, BCBS 239), mimetic pressure from peer firms (consulting industry benchmarks), and normative pressure from professional bodies (DAMA, ISACA, CDMP credentials). Walsh et al. (2025) and Volz et al. (2025) document exactly this kind of layered pressure environment for knowledge-intensive firms.

The intensities below are illustrative; in research use, they would be derived from the dissertation's hand-coded interview transcripts or from a validated parser (see notebook 13.5). Here, they make the apparatus concrete enough to manipulate.
"""
    ),
    code_cell(
        """def decompose_across_scales(case_name: str, decomposition: dict) -> List[PressureVector]:
    \"\"\"Materialize a pressure field as a list of PressureVectors, one per scale.

    `decomposition` is a dict keyed by Scale where each value is a dict with
    keys 'coercive', 'mimetic', 'normative', and optional 'evidence'.
    \"\"\"
    out = []
    for scale in SCALE_ORDER:
        d = decomposition.get(scale, {})
        out.append(PressureVector(
            coercive=d.get('coercive', 0.0),
            mimetic=d.get('mimetic', 0.0),
            normative=d.get('normative', 0.0),
            scale=scale,
            evidence=d.get('evidence', []),
        ))
    return out


# Decomposition for a financial-services consulting firm.
FS_FIRM = decompose_across_scales(
    'Financial-services consulting firm: data and AI governance',
    decomposition={
        Scale.FIELD:        {'coercive': 0.95, 'mimetic': 0.30, 'normative': 0.45,
                             'evidence': ['DORA Article 9', 'EU AI Act Article 10', 'BCBS 239']},
        Scale.FIRM:         {'coercive': 0.40, 'mimetic': 0.70, 'normative': 0.55,
                             'evidence': ['Big-3 data-fabric benchmarking', 'firm-level ISO 42001 program']},
        Scale.DIVISION:     {'coercive': 0.55, 'mimetic': 0.65, 'normative': 0.60,
                             'evidence': ['MSA-imposed audit logs', 'sister-division platform mimicry']},
        Scale.TEAM:         {'coercive': 0.30, 'mimetic': 0.55, 'normative': 0.75,
                             'evidence': ['internal SOPs', 'peer code review norms']},
        Scale.PRACTITIONER: {'coercive': 0.20, 'mimetic': 0.35, 'normative': 0.85,
                             'evidence': ['CDMP certification', 'tacit professional ethic']},
    },
)
matrix = np.stack([v.as_array() for v in FS_FIRM], axis=1)
print('Decomposed pressure matrix (3 mechanisms x 5 scales):')
print(np.round(matrix, 2))
"""
    ),
    code_cell(
        """def render_pressure_field(field_, title='Pressure field across scales'):
    matrix = np.stack([v.as_array() for v in field_], axis=1)
    scales = [v.scale.value for v in field_]
    mechanisms = ['coercive', 'mimetic', 'normative']

    fig, axes = plt.subplots(1, 2, figsize=(13.6, 4.0), gridspec_kw={'width_ratios': [1.5, 1]})

    ax = axes[0]
    im = ax.imshow(matrix, aspect='auto', cmap='YlOrBr', vmin=0, vmax=1)
    ax.set_xticks(range(len(scales)))
    ax.set_xticklabels(scales)
    ax.set_yticks(range(len(mechanisms)))
    ax.set_yticklabels(mechanisms)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f'{matrix[i, j]:.2f}', ha='center', va='center',
                    color='black' if matrix[i, j] < 0.6 else 'white', fontsize=9)
    ax.set_title(title)
    fig.colorbar(im, ax=ax, label='intensity')

    # Right pane: per-scale L1 norm and dominant-mechanism colour code.
    ax2 = axes[1]
    l1s = [v.l1() for v in field_]
    colors = []
    for v in field_:
        if v.dominant() == 'coercive':
            colors.append('#c46b6b')
        elif v.dominant() == 'mimetic':
            colors.append('#6e8db4')
        else:
            colors.append('#2b5a43')
    ax2.barh(range(len(field_)), l1s, color=colors)
    ax2.set_yticks(range(len(field_)))
    ax2.set_yticklabels(scales)
    ax2.invert_yaxis()
    ax2.set_xlabel('L1 norm of pressure')
    ax2.set_title('Aggregate intensity per scale\\n(colour = dominant mechanism)')
    ax2.set_xlim(0, 3)

    plt.tight_layout()
    plt.show()


render_pressure_field(FS_FIRM, title='Financial-services consulting firm')
"""
    ),
    markdown_cell(
        """## What the picture says

Two readings the heatmap rewards.

First, the **dominance shift across scales**. At the field scale, coercive pressure dominates (regulators set the rules; firms either comply or pay). At the practitioner scale, normative pressure dominates (the practitioner answers to their certification, their training, and their professional self-image). Mimetic pressure dominates at the firm and division scales, where benchmarking happens. This is the structure DiMaggio and Powell (1983) described, with the multi-scale aspect made visible in one figure.

Second, the **aggregate L1 norm per scale** on the right. Pressure is roughly conserved across scales; the firm and division feel about the same total intensity but from different mechanisms. This conservation is suggestive but not a theorem; in real firms the L1 may climb or fall with maturity. Notebook 13.4 looks at temporal pressure proxies; the empirical question of L1 conservation across scales is a research problem (see the companion research plan, hypothesis H2).

## Self-check

The cell below builds a contrasting pressure field for a public university IT department: weaker coercive pressure (no MSA/financial regulation), stronger mimetic (peer institutions matter heavily), and lower per-practitioner normative pressure (no equivalent of CDMP for everyone). This field has a markedly different shape; the apparatus exposes the difference.
"""
    ),
    code_cell(
        """UNIVERSITY_IT = decompose_across_scales(
    'Public university IT: data governance',
    decomposition={
        Scale.FIELD:        {'coercive': 0.50, 'mimetic': 0.40, 'normative': 0.40,
                             'evidence': ['FERPA', 'state data privacy laws']},
        Scale.FIRM:         {'coercive': 0.35, 'mimetic': 0.75, 'normative': 0.45,
                             'evidence': ['EDUCAUSE benchmarking', 'sister-university toolkit imitation']},
        Scale.DIVISION:     {'coercive': 0.30, 'mimetic': 0.55, 'normative': 0.50,
                             'evidence': ['IT department peer practices']},
        Scale.TEAM:         {'coercive': 0.20, 'mimetic': 0.45, 'normative': 0.55,
                             'evidence': ['ITIL conventions']},
        Scale.PRACTITIONER: {'coercive': 0.15, 'mimetic': 0.30, 'normative': 0.55,
                             'evidence': ['individual training; no field-wide certification']},
    },
)
render_pressure_field(UNIVERSITY_IT, title='Public university IT')

print('\\nL1 norms by scale (financial-services consulting firm):')
for v in FS_FIRM:
    print(f'  {v.scale.value:>13s}: L1={v.l1():.2f} (dominant={v.dominant()})')
print('\\nL1 norms by scale (public university IT):')
for v in UNIVERSITY_IT:
    print(f'  {v.scale.value:>13s}: L1={v.l1():.2f} (dominant={v.dominant()})')
"""
    ),
    markdown_cell(
        """## Where this lands

The `PressureVector` and `Scale` types are reused throughout Chapter 13. The decomposition step is currently human-curated; notebook 13.5 will introduce an AI-mediated path that takes free-text governance accounts and produces decomposition dictionaries automatically (with an explicit mock fallback when no Anthropic key is available).

## Practical implications

- **For practitioners:** a pressure field rendered as a heatmap is more diagnostic than the same intensities listed as text. Build the heatmap before the all-hands deck.
- **For researchers:** when transcribing interviews, retain scale labels. The dissertation's hand-coding already produces this structure; the apparatus operationalizes it.
- **For students:** treat the matrix as one snapshot. Notebook 13.2 introduces a temporal complement: when formal and operational signals diverge across scales, the apparatus says "decoupling" with a number attached.
"""
    ),
]


# ---------------------------------------------------------------------------
# 13.2 Decoupling as Multi-Scale Decoherence
# ---------------------------------------------------------------------------

NB_13_2 = [
    markdown_cell(
        "> **Chapter 13, Part 2** | Continues from [13.1 The Multi-Scale Pressure Field](13.1%20The%20Multi-Scale%20Pressure%20Field.ipynb). **Focus:** decoupling, but with a measurement procedure."
    ),
    markdown_cell(
        """# Decoupling as Multi-Scale Decoherence

Meyer and Rowan (1977) introduced **decoupling** to describe the structural separation between formal organizational structure (policies, charts, public commitments) and operational practice (what people actually do). Decoupling is empirically pervasive: organizations adopt formal structures to gain legitimacy without necessarily implementing them, because implementation can be costly or impractical. The classical theory describes decoupling as a binary: either decoupled or not.

This notebook treats decoupling as a **scale-dependent divergence**. Decoupling at one scale (e.g., the firm publishes a model risk policy that contradicts how teams actually deploy models) is qualitatively different from decoupling at another (e.g., the field-level regulation contradicts the firm's internal rules). A scalar `decoupling_dimension` summarizes how decoupling propagates across scales. The math is intentionally simple. The conceptual yield is that decoupling stops being a yes/no judgment and becomes a measurement.

## Why this matters now

The Longpre et al. (2024) audit of 1,800 dataset cards found that 70% of dataset license categorizations on widely-used AI training corpora were wrong. Dataset cards are formal artifacts; their categorizations are operational claims. The 70% miscategorization rate is a decoupling measurement at the artifact scale. The same audit's finding that the miscategorization is uneven across hosts (Hugging Face, GitHub, etc.) is a multi-scale signal. Decoupling at the artifact scale propagates differently through different hosting ecosystems.

This notebook builds a `decoupling_dimension` measure on synthetic but plausible signals, then names what it would take to compute the same measure on real client data.
"""
    ),
    code_cell(
        """import numpy as np
import matplotlib.pyplot as plt
from typing import Sequence

rng = np.random.default_rng(42)


def generate_signals(n_scales: int = 5, decoupling_at: dict = None, seed: int = 0):
    \"\"\"Build synthetic formal/operational signal pairs across scales.

    `decoupling_at` is a dict {scale_index: divergence in [0, 1]} that injects
    scale-specific divergence between formal and operational at each level.
    \"\"\"
    decoupling_at = decoupling_at or {}
    rng_local = np.random.default_rng(seed)
    formal = []
    operational = []
    for i in range(n_scales):
        base = rng_local.normal(loc=0.55, scale=0.05)
        formal.append(np.clip(base + rng_local.normal(0, 0.03, size=128), 0, 1))
        div = decoupling_at.get(i, 0.0)
        operational.append(np.clip(base - div + rng_local.normal(0, 0.04, size=128), 0, 1))
    return formal, operational


def decoupling_dimension(formal: Sequence[np.ndarray], operational: Sequence[np.ndarray]) -> float:
    \"\"\"Return a scalar in [0, 1] summarizing scale-aggregated decoupling.

    Uses RMSE between formal and operational at each scale, then takes a
    weighted average favouring scales with more divergence (so that strong
    decoupling at any one scale is not washed out by quiet scales).
    \"\"\"
    rmses = []
    for f_arr, o_arr in zip(formal, operational):
        rmses.append(float(np.sqrt(np.mean((f_arr - o_arr) ** 2))))
    arr = np.array(rmses)
    if arr.sum() == 0:
        return 0.0
    weights = arr / arr.sum()
    weighted = float(np.sum(arr * (1 + weights)))
    # Normalize so a single scale at maximum divergence (RMSE ~ 0.7) gives ~1.
    return float(min(weighted / 1.4, 1.0))


# Sanity check: aligned signals stay low; injected divergence pushes the dimension up.
f, o = generate_signals(decoupling_at={}, seed=1)
dd_aligned = decoupling_dimension(f, o)
f2, o2 = generate_signals(decoupling_at={1: 0.7}, seed=1)
dd_strong = decoupling_dimension(f2, o2)
assert dd_strong > dd_aligned + 0.1, f'expected strong decoupling > aligned + 0.1, got {dd_aligned:.3f} vs {dd_strong:.3f}'
print(f'Aligned signals decoupling dimension: {dd_aligned:.3f}')
print(f'One-scale strong decoupling dimension: {dd_strong:.3f}')
"""
    ),
    code_cell(
        """def render_decoupling(formal, operational, scale_labels, title=''):
    n = len(formal)
    fig, axes = plt.subplots(1, n, figsize=(15, 3.4), sharey=True)
    if n == 1:
        axes = [axes]
    rmses = []
    for ax, f_arr, o_arr, label in zip(axes, formal, operational, scale_labels):
        ax.plot(f_arr, label='formal', color='#2b5a43', linewidth=1.4)
        ax.plot(o_arr, label='operational', color='#d17a00', linewidth=1.4, alpha=0.8)
        rmse = float(np.sqrt(np.mean((f_arr - o_arr) ** 2)))
        rmses.append(rmse)
        ax.set_title(f'{label}\\nRMSE={rmse:.3f}', fontsize=10)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.grid(alpha=0.2)
        ax.legend(loc='lower right', fontsize=7, frameon=False)
    fig.suptitle(title, fontsize=12)
    plt.tight_layout()
    plt.show()
    return rmses


# Scenario A: governance lives at the level of policy. The firm-scale policy is loud
# but practitioners diverge. Decoupling concentrated at scales 3-4 (team, practitioner).
SCALE_LABELS = ['field', 'firm', 'division', 'team', 'practitioner']

f_A, o_A = generate_signals(decoupling_at={3: 0.45, 4: 0.55}, seed=11)
rmse_A = render_decoupling(f_A, o_A, SCALE_LABELS,
                           title='Scenario A: bottom-scale decoupling (policy good; execution drifts)')
dd_A = decoupling_dimension(f_A, o_A)
print(f'Decoupling dimension (Scenario A): {dd_A:.3f}\\n')

# Scenario B: theatre at the top. Field-scale regulation says one thing; firm-scale
# claims compliance but the operational signal at field/firm is divergent.
f_B, o_B = generate_signals(decoupling_at={0: 0.55, 1: 0.40}, seed=11)
rmse_B = render_decoupling(f_B, o_B, SCALE_LABELS,
                           title='Scenario B: top-scale decoupling (compliance theatre)')
dd_B = decoupling_dimension(f_B, o_B)
print(f'Decoupling dimension (Scenario B): {dd_B:.3f}\\n')

# Scenario C: continuous decoupling across all scales (rare in practice, but
# the worst-case shape). Real organizations usually concentrate decoupling somewhere.
f_C, o_C = generate_signals(decoupling_at={i: 0.30 for i in range(5)}, seed=11)
rmse_C = render_decoupling(f_C, o_C, SCALE_LABELS,
                           title='Scenario C: pervasive decoupling at every scale')
dd_C = decoupling_dimension(f_C, o_C)
print(f'Decoupling dimension (Scenario C): {dd_C:.3f}')
"""
    ),
    markdown_cell(
        """## Reading the three scenarios

- **Scenario A (bottom-scale decoupling).** Policy looks fine at the field and firm scales. The divergence concentrates at team and practitioner scales. This is the "policy good, execution drifts" pattern Walsh et al. (2025) describe in consulting firms. The decoupling dimension is moderate but the diagnostic is sharp because the structure says where the gap is.
- **Scenario B (top-scale decoupling).** Field-scale regulation is loud; firm-scale claims compliance; operational reality at the top scales diverges. This is **compliance theatre** in the classical Meyer-Rowan sense. The decoupling dimension can register as smaller than Scenario A even though the consequence (audit finding, regulatory penalty) is bigger.
- **Scenario C (pervasive decoupling).** Every scale shows divergence. Rare in practice; the dimension is high but the structure-free signal makes it harder to act on.

## What the dimension does and does not say

The `decoupling_dimension` is a scalar summary. It tells the reader "how much" but not "where." Reading the per-scale RMSE alongside the dimension is essential. This pattern repeats in Chapter 12: a single fractal dimension `d_B` is a useful triage number, but never a substitute for the box-cover plot it summarizes.

The single most important honesty note: this measurement requires both formal and operational signals to exist as time series or vectors. In real organizations, **the operational signal is exactly what's hard to obtain**. Interview transcripts give qualitative operational evidence; lineage manifests give partial structural evidence; incident logs give partial outcome evidence. The dissertation case study is one path to the operational signal. Notebook 13.5 introduces an AI-mediated path. Notebook 13.8 names where each path fails.
"""
    ),
    code_cell(
        """# Connecting back to Chapter 11.4: the duplicate-cluster threshold is itself a
# decoupling event. The match score (formal) and the steward judgment (operational)
# diverge at certain thresholds. The duplicate-cluster work is decoupling at one scale.
# Chapter 13's apparatus generalizes the same idea across many scales.
print('Connections to earlier chapters:')
print('- Ch 11.4: duplicate-cluster decoupling at a single scale (entity-resolution threshold)')
print('- Ch 12.5: lineage fault propagation as a structural blast-radius signal')
print('- Ch 12.6: entity resolution revisited as a graph; instability scores quantify match-score / steward-judgment decoupling')
print('- Ch 13.5 (next door): AI-mediated parsing turns interview text into operational signal vectors')
print()
print('The empirical roadmap is in non-git-files/governance-ai-fractals-research-plan.md.')
"""
    ),
    markdown_cell(
        """## Practical implications

- **For practitioners:** when an audit finds something, ask not only "did we comply?" but "which scale was decoupled?" The locus matters more than the score for remediation planning.
- **For researchers:** the per-scale RMSE is the empirical handle. A reproducibility paper testing whether interview-derived RMSEs match instrumented-system RMSEs would be a strong contribution to the methods literature.
- **For students:** the apparatus is conceptually one line: subtract two signals at each scale and weight the result. The conceptual content is in deciding what the formal and operational signals are. The measurement is the easy part.

## How I would debug this

If `decoupling_dimension` returns near 0 in your environment, suspect that the formal and operational signals are coming from the same source. Independent measurement is the prerequisite for measuring divergence. Reading the dissertation interview protocol (Chen and Filieri, 2024 provides a template) is one way to ensure independence.
"""
    ),
]


# ---------------------------------------------------------------------------
# 13.3 The Governance Knowledge Graph
# ---------------------------------------------------------------------------

NB_13_3 = [
    markdown_cell(
        "> **Chapter 13, Part 3** | Continues from [13.2 Decoupling as Multi-Scale Decoherence](13.2%20Decoupling%20as%20Multi-Scale%20Decoherence.ipynb). **Focus:** apply Chapter 12 box-covering to the dissertation knowledge graph."
    ),
    markdown_cell(
        """# The Governance Knowledge Graph

A literature is a graph. Authors cite each other; concepts repeat across papers; venues organize themselves into communities. This is true of every active field, but most working researchers experience the literature as a flat reading list. Knowledge graphs make the structure visible, and the structure carries information that the reading list alone cannot.

This notebook builds a NetworkX graph from a curated subset of the dissertation's verified May 2026 bibliography (~30 papers) and applies two descriptors: **Louvain community detection** to surface latent topical clusters, and **box-covering** (the same algorithm from Chapter 12.3) to estimate the knowledge graph's box dimension. The intent is honest: with ~30 nodes the asymptotic claims of fractality require care. The descriptors are reported with their stability checks rather than as conclusions.

## What the graph encodes

- **Paper nodes.** One per citation. Attributes: `year`, `venue`, `concepts`.
- **Concept nodes.** Topical tags that recur across papers (e.g., `coercive_pressure`, `decoupling`, `data_governance_framework`, `ai_governance`, `network_science`).
- **Edges.** A paper-concept edge if the concept tags that paper. Two papers share an indirect path through every concept they share.

This is an explicitly minimal model. A research-grade citation network would add direct citation edges, author-coauthorship edges, and venue-co-presence edges. Notebook 13.8 names that gap.
"""
    ),
    code_cell(
        """import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter

try:
    import community as community_louvain
    HAVE_LOUVAIN = True
except ImportError:
    HAVE_LOUVAIN = False
    print('python-louvain not installed; falling back to greedy modularity communities.')


# A curated subset of the dissertation's verified May 2026 bibliography.
# Each tuple: (citation_key, year, venue, [concept tags]).
BIB = [
    # Institutional theory (foundational)
    ('DiMaggio_Powell_1983', 1983, 'American Sociological Review',
     ['coercive_pressure', 'mimetic_pressure', 'normative_pressure', 'institutional_isomorphism']),
    ('Meyer_Rowan_1977', 1977, 'American Journal of Sociology',
     ['decoupling', 'institutionalization', 'legitimacy']),
    ('Scott_2008', 2008, 'SAGE',
     ['institutionalization', 'three_pillars', 'institutional_theory']),
    ('Greenwood_2011', 2011, 'Academy of Management Annals',
     ['institutional_complexity', 'organizational_response']),
    ('Powell_DiMaggio_2023', 2023, 'Organization Theory',
     ['institutional_isomorphism', 'retrospective']),

    # Data governance (core)
    ('Khatri_Brown_2010', 2010, 'Communications of the ACM',
     ['data_governance_framework', 'decision_rights', 'accountability']),
    ('Abraham_2019', 2019, 'International Journal of Information Management',
     ['data_governance_framework', 'systematic_review']),
    ('Walsh_2025', 2025, 'Information Systems Management',
     ['data_governance_practice', 'consulting_firm', 'decoupling']),
    ('Volz_2025', 2025, 'Journal of Business Research',
     ['data_governance_practice', 'data_ecosystem']),
    ('Stepanovic_2025', 2025, 'JASIST',
     ['research_data_governance', 'open_data', 'integration']),
    ('Acev_2025', 2025, 'Management Review Quarterly',
     ['data_governance_framework', 'data_trust', 'systematic_review']),
    ('Alhassan_2018', 2018, 'Journal of Enterprise Information Management',
     ['data_governance_practice', 'theory_practice_gap']),
    ('Bliznak_2024', 2024, 'IEEE Access',
     ['data_governance_framework', 'systematic_review', 'definition_ambiguity']),
    ('Cardoso_Canedo_2026', 2026, 'CCIS Springer',
     ['maturity_model', 'data_governance_practice']),

    # AI governance
    ('Birkstedt_2023', 2023, 'Internet Research',
     ['ai_governance', 'systematic_review', 'decoupling']),
    ('Mantymaki_2022', 2022, 'AI and Ethics',
     ['ai_governance', 'organizational_governance']),
    ('Papagiannidis_2025', 2025, 'Journal of Strategic Information Systems',
     ['ai_governance', 'responsible_ai', 'organizational_governance']),
    ('Trincado_Munoz_2025', 2025, 'Service Industries Journal',
     ['ai_governance', 'professional_services', 'consulting_firm']),
    ('Longpre_2024', 2024, 'Nature Machine Intelligence',
     ['dataset_audit', 'ai_governance', 'decoupling', 'license_compliance']),
    ('Crisanto_2024', 2024, 'BIS FSI Insights',
     ['ai_governance', 'financial_regulation', 'coercive_pressure']),

    # Domain-specific data governance
    ('Arner_2023', 2023, 'Hastings Law Journal',
     ['financial_regulation', 'coercive_pressure', 'data_governance_practice']),
    ('Bartlett_2022', 2022, 'Journal of Financial Economics',
     ['algorithmic_discrimination', 'coercive_pressure', 'fair_lending']),
    ('Bennich_2024', 2024, 'Technology in Society',
     ['mimetic_pressure', 'normative_pressure', 'digitalization']),
    ('Bernardo_2024', 2024, 'Journal of Innovation and Knowledge',
     ['data_quality', 'data_governance_practice']),
    ('Blohm_2024', 2024, 'Business and Information Systems Engineering',
     ['data_mesh', 'data_fabric', 'data_governance_framework']),
    ('Chen_Filieri_2024', 2024, 'Technological Forecasting and Social Change',
     ['institutional_isomorphism', 'qualitative_case_study', 'leapfrogging']),

    # Network science / fractal
    ('Song_Havlin_Makse_2005', 2005, 'Nature',
     ['fractal_network', 'box_covering', 'self_similarity']),
    ('Skums_Bunimovich_2020', 2020, 'Journal of Complex Networks',
     ['graph_fractal_dimension', 'fractal_network']),
    ('Lacasa_2008', 2008, 'PNAS',
     ['visibility_graph', 'time_series_to_network', 'self_similarity']),
    ('Malemapti_Hari_2026', 2026, 'Zenodo',
     ['fractal_coupling', 'volatility', 'visibility_graph', 'time_series_to_network']),

    # Methods
    ('Boote_Beile_2005', 2005, 'Educational Researcher',
     ['qualitative_methods', 'literature_review']),
]
print(f'Loaded {len(BIB)} curated citations.')
"""
    ),
    code_cell(
        """def build_kg(bib):
    G = nx.Graph()
    for key, year, venue, concepts in bib:
        G.add_node(key, kind='paper', year=year, venue=venue)
        for c in concepts:
            if not G.has_node(c):
                G.add_node(c, kind='concept')
            G.add_edge(key, c)
    return G


KG = build_kg(BIB)
print(f'Nodes: {KG.number_of_nodes()} (papers: {sum(1 for _, d in KG.nodes(data=True) if d.get(\"kind\") == \"paper\")}, concepts: {sum(1 for _, d in KG.nodes(data=True) if d.get(\"kind\") == \"concept\")})')
print(f'Edges: {KG.number_of_edges()}')
print(f'Connected: {nx.is_connected(KG)}')
print(f'Density: {nx.density(KG):.4f}')

degree_seq = sorted([d for _, d in KG.degree()], reverse=True)
print(f'Top 5 degrees: {degree_seq[:5]}')
"""
    ),
    code_cell(
        """def render_kg(G, title='Governance KG'):
    pos = nx.spring_layout(G, seed=7, iterations=200, k=0.7)
    fig, ax = plt.subplots(figsize=(13, 9))
    paper_nodes = [n for n, d in G.nodes(data=True) if d.get('kind') == 'paper']
    concept_nodes = [n for n, d in G.nodes(data=True) if d.get('kind') == 'concept']
    nx.draw_networkx_edges(G, pos, alpha=0.25, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=paper_nodes, node_color='#efce8a', node_size=420,
                           edgecolors='#5a4220', linewidths=1.0, ax=ax, label='papers')
    nx.draw_networkx_nodes(G, pos, nodelist=concept_nodes, node_color='#2b5a43', node_size=240,
                           edgecolors='#173326', linewidths=1.0, ax=ax, label='concepts')
    paper_labels = {n: n.replace('_', ' ') for n in paper_nodes}
    concept_labels = {n: n.replace('_', ' ') for n in concept_nodes}
    nx.draw_networkx_labels(G, pos, labels=paper_labels, font_size=6.5, ax=ax)
    nx.draw_networkx_labels(G, pos, labels=concept_labels, font_size=6.5, font_color='white', ax=ax)
    ax.legend(loc='lower right')
    ax.set_title(title)
    ax.axis('off')
    plt.tight_layout()
    plt.show()


render_kg(KG, title='Dissertation knowledge graph (curated subset, ~30 papers)')
"""
    ),
    code_cell(
        """# Louvain community detection.
if HAVE_LOUVAIN:
    partition = community_louvain.best_partition(KG, random_state=7)
else:
    parts = nx.algorithms.community.greedy_modularity_communities(KG)
    partition = {n: idx for idx, comp in enumerate(parts) for n in comp}

community_sizes = Counter(partition.values())
print(f'Detected {len(community_sizes)} communities.')
for cid, size in sorted(community_sizes.items()):
    members = [n for n, c in partition.items() if c == cid]
    concepts = [n for n in members if KG.nodes[n].get('kind') == 'concept']
    papers = [n for n in members if KG.nodes[n].get('kind') == 'paper']
    print(f'  Community {cid}: {len(papers)} papers, {len(concepts)} concepts')
    if concepts:
        print(f'    dominant concepts: {concepts[:5]}')
    if papers:
        print(f'    sample papers:    {papers[:4]}')
"""
    ),
    code_cell(
        """# Box-covering on the KG. Reuses Chapter 12.3's algorithm essentially unchanged.
def box_cover(G, l_box):
    \"\"\"Greedy box-covering at radius l_box (Song-Havlin-Makse 2005 family).\"\"\"
    if l_box <= 0:
        return G.number_of_nodes()
    if not nx.is_connected(G):
        component_nodes = max(nx.connected_components(G), key=len)
        H = G.subgraph(component_nodes).copy()
    else:
        H = G
    # Build dual graph: edges between nodes whose distance >= l_box.
    nodes = list(H.nodes())
    sp = dict(nx.all_pairs_shortest_path_length(H))
    dual = nx.Graph()
    dual.add_nodes_from(nodes)
    for i, u in enumerate(nodes):
        for v in nodes[i + 1:]:
            if sp[u].get(v, float('inf')) >= l_box:
                dual.add_edge(u, v)
    # Greedy colouring of the dual graph -> number of colours = number of boxes.
    colours = nx.coloring.greedy_color(dual, strategy='largest_first')
    return max(colours.values()) + 1 if colours else 1


def estimate_box_dimension(G, l_max=None):
    if not l_max:
        ecc = nx.eccentricity(G) if nx.is_connected(G) else nx.eccentricity(G.subgraph(max(nx.connected_components(G), key=len)))
        l_max = max(ecc.values()) // 2
    sizes = []
    Ls = list(range(1, max(l_max, 2) + 1))
    for L in Ls:
        sizes.append(box_cover(G, L))
    Ls_arr = np.array(Ls, dtype=float)
    sizes_arr = np.array(sizes, dtype=float)
    # Fit log-log slope where N(L) > 1.
    valid = sizes_arr > 1
    if valid.sum() < 4:
        return None, Ls, sizes, 'too few scales'
    slope, intercept = np.polyfit(np.log(Ls_arr[valid]), np.log(sizes_arr[valid]), 1)
    # R^2 for stability check (V001).
    yhat = slope * np.log(Ls_arr[valid]) + intercept
    ss_res = np.sum((np.log(sizes_arr[valid]) - yhat) ** 2)
    ss_tot = np.sum((np.log(sizes_arr[valid]) - np.log(sizes_arr[valid]).mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    if r2 < 0.9:
        return None, Ls, sizes, f'unstable scaling (R^2={r2:.3f})'
    return -slope, Ls, sizes, f'd_B={-slope:.3f}, R^2={r2:.3f}'


d_B, Ls, sizes, status = estimate_box_dimension(KG)
print(f'Box-cover scan (l, N(l)):')
for L, n in zip(Ls, sizes):
    print(f'  l={L}, N={n}')
print()
print(f'Status: {status}')
if d_B is not None:
    print(f'Estimated graph fractal dimension: {d_B:.3f}')
else:
    print('No scaling regime stable enough to report d_B.')
"""
    ),
    code_cell(
        """fig, ax = plt.subplots(figsize=(7.5, 5))
ax.plot(Ls, sizes, 'o-', color='#d17a00', linewidth=1.5, markersize=8)
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('box radius l')
ax.set_ylabel('boxes N(l)')
ax.set_title(f'Box-cover scan (KG, n={KG.number_of_nodes()})\\n{status}')
ax.grid(True, which='both', alpha=0.3)
if d_B is not None:
    Ls_arr = np.array(Ls, dtype=float)
    fit = np.exp(-d_B * np.log(Ls_arr) + np.log(sizes[0]) + d_B * np.log(Ls[0]))
    ax.plot(Ls_arr, fit, '--', color='#2b5a43', alpha=0.7, label=f'fit slope = -{d_B:.2f}')
    ax.legend()
plt.tight_layout()
plt.show()
"""
    ),
    markdown_cell(
        """## Honest reading

The KG has ~30 papers and ~30 concepts. With n ≈ 60 nodes and a low diameter, the box-cover scan covers very few scales. Whether or not the slope reports a number, this graph is too small to make asymptotic fractality claims. What the scan does deliver is **discipline**: it forces us to look at the multi-scale structure rather than at degree centrality alone. If a future researcher reconstructs the same KG from a 5,000-paper corpus, the same scan becomes more meaningful. The companion research plan (`non-git-files/governance-ai-fractals-research-plan.md`) makes that the H1 hypothesis of the program.

The Louvain communities, by contrast, are interpretable even at this size. The communities recover roughly four clusters: (a) institutional theory + classical decoupling, (b) data governance frameworks, (c) AI governance, and (d) network science / fractal methods. The cluster boundaries are not theoretical commitments; they emerge from the curated bibliography and the concept tags. The same algorithm applied to a larger or differently-curated bibliography would produce different clusters.

## Where this lands

The KG is a teaching object, not a research result. The teaching value is in connecting Chapter 12's `box_cover` to a corpus that practitioners actually engage with (their own reading list). The code generalizes: a reader can swap in their own bibliography and re-run the descriptors. The capstone (notebook 13.7) supports exactly that workflow.

## Practical implications

- **For practitioners:** when planning a literature review, build the KG before reading. The communities surface gaps that flat reading lists hide.
- **For researchers:** the KG-fractal-dimension descriptor is publishable as a methodological note if validated against a sufficiently large governance corpus (Option B in the research plan).
- **For students:** the communities are interpretable; the box dimension is suggestive. Read both as triage signals, not conclusions.
"""
    ),
]


# ---------------------------------------------------------------------------
# 13.4 Visibility Graphs of Governance Time Series
# ---------------------------------------------------------------------------

NB_13_4 = [
    markdown_cell(
        "> **Chapter 13, Part 4** | Continues from [13.3 The Governance Knowledge Graph](13.3%20The%20Governance%20Knowledge%20Graph.ipynb). **Focus:** reuse Chapter 12's visibility-graph code on governance incident streams."
    ),
    markdown_cell(
        """# Visibility Graphs of Governance Time Series

Governance generates time series whether anyone is measuring them or not. Incident counts per week, audit findings per quarter, model deployments approved per month, dataset license changes per release. Each is a sequence of events with a magnitude. The visibility-graph algorithm from Chapter 12.2 (Lacasa et al., 2008) converts a time series into a graph whose degree distribution carries the temporal correlation structure of the underlying process. Long-range correlated series produce scale-free graphs; uncorrelated series produce exponential-tailed graphs; periodic series produce regular graphs.

This notebook applies the same algorithm to synthetic governance incident streams across three institutional maturity regimes. The bounded claim, again: this is a teaching demonstration on synthetic data. The H4 hypothesis in the companion research plan asks whether visibility-graph signatures distinguish institutional maturity in real client data, and the answer is empirically open. The reproducible apparatus here is the contribution; validation is research.
"""
    ),
    code_cell(
        """import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter

rng = np.random.default_rng(0)


def visibility_graph(series):
    \"\"\"Lacasa et al. (2008) natural visibility graph.\"\"\"
    n = len(series)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for a in range(n - 1):
        G.add_edge(a, a + 1)
        if a + 2 >= n:
            continue
        max_slope = (series[a + 1] - series[a]) / 1
        for b in range(a + 2, n):
            slope = (series[b] - series[a]) / (b - a)
            if slope > max_slope:
                G.add_edge(a, b)
                max_slope = slope
    return G


def degree_distribution(G):
    counts = Counter(dict(G.degree()).values())
    ks = sorted(counts.keys())
    pks = [counts[k] / G.number_of_nodes() for k in ks]
    return ks, pks


def fit_power_tail(ks, pks):
    ks_arr = np.array(ks, dtype=float)
    pks_arr = np.array(pks, dtype=float)
    valid = pks_arr > 0
    if valid.sum() < 4:
        return None, None
    slope, intercept = np.polyfit(np.log(ks_arr[valid]), np.log(pks_arr[valid]), 1)
    yhat = slope * np.log(ks_arr[valid]) + intercept
    ss_res = np.sum((np.log(pks_arr[valid]) - yhat) ** 2)
    ss_tot = np.sum((np.log(pks_arr[valid]) - np.log(pks_arr[valid]).mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return -slope, r2
"""
    ),
    code_cell(
        """def fbm_simple(n, H, seed=0):
    \"\"\"Approximate fractional Brownian motion via spectral synthesis.

    H near 0.5 -> uncorrelated; H > 0.5 -> persistent / long-range; H < 0.5 -> antipersistent.
    \"\"\"
    rng_local = np.random.default_rng(seed)
    freqs = np.fft.fftfreq(n, d=1.0)
    freqs[0] = 1e-9
    spec = np.abs(freqs) ** (-(2 * H + 1) / 2.0)
    phases = np.exp(2j * np.pi * rng_local.random(n))
    fft_signal = spec * phases
    fft_signal[0] = 0
    signal = np.real(np.fft.ifft(fft_signal))
    cumulative = np.cumsum(signal)
    return (cumulative - cumulative.min()) / (cumulative.max() - cumulative.min() + 1e-9)


def synthesize_incident_stream(maturity='low', n=256, seed=0):
    \"\"\"Generate synthetic governance incident counts (rescaled to [0, 1]).

    Low maturity:    bursty (short-range correlation, occasional spikes), H ~ 0.3
    Medium maturity: mixed regime, H ~ 0.5
    High maturity:   smooth, persistent improvement (trend + low noise), H ~ 0.8
    \"\"\"
    if maturity == 'low':
        return fbm_simple(n, H=0.3, seed=seed)
    if maturity == 'medium':
        return fbm_simple(n, H=0.5, seed=seed)
    if maturity == 'high':
        return fbm_simple(n, H=0.8, seed=seed)
    raise ValueError(maturity)


low = synthesize_incident_stream('low', seed=11)
mid = synthesize_incident_stream('medium', seed=11)
high = synthesize_incident_stream('high', seed=11)

fig, axes = plt.subplots(1, 3, figsize=(15, 3.4), sharey=True)
for ax, s, title in zip(axes, [low, mid, high], ['low maturity (bursty)', 'medium maturity (mixed)', 'high maturity (smooth)']):
    ax.plot(s, color='#d17a00', linewidth=1.0)
    ax.set_title(title)
    ax.set_ylim(0, 1)
    ax.grid(alpha=0.2)
plt.suptitle('Synthetic governance incident streams across maturity regimes')
plt.tight_layout()
plt.show()
"""
    ),
    code_cell(
        """fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
results = {}
for ax, series, label in zip(axes, [low, mid, high], ['low', 'medium', 'high']):
    G = visibility_graph(series)
    ks, pks = degree_distribution(G)
    slope, r2 = fit_power_tail(ks, pks)
    results[label] = (G, slope, r2)
    ax.loglog(ks, pks, 'o', color='#173326', alpha=0.85)
    if slope is not None:
        ks_arr = np.array(ks, dtype=float)
        fit = np.exp(-slope * np.log(ks_arr) + np.log(pks[0]) + slope * np.log(ks[0]))
        ax.loglog(ks_arr, fit, '--', color='#d17a00', alpha=0.7,
                  label=f'tail slope = -{slope:.2f}, R^2={r2:.2f}')
        ax.legend(fontsize=8, frameon=False)
    ax.set_title(f'{label} maturity (n_nodes={G.number_of_nodes()}, n_edges={G.number_of_edges()})')
    ax.set_xlabel('degree k')
    ax.set_ylabel('P(k)')
    ax.grid(True, which='both', alpha=0.3)

plt.suptitle('Visibility-graph degree distributions across maturity regimes')
plt.tight_layout()
plt.show()

print()
print('Reading: a steeper, more linear log-log tail (R^2 high, slope < -1)')
print('indicates a scale-free / long-range correlated regime. The high-maturity series')
print('shows the tightest power-law fit; the low-maturity series shows a heavier tail')
print('with larger fluctuations from the hub-dominated bursty regime.')
"""
    ),
    code_cell(
        """# E005 degenerate-input handling: a constant series should not produce a slope.
flat = np.full(256, 0.5)
G_flat = visibility_graph(flat)
ks_flat, pks_flat = degree_distribution(G_flat)
slope_flat, r2_flat = fit_power_tail(ks_flat, pks_flat)
print(f'Constant series:')
print(f'  visibility graph: {G_flat.number_of_nodes()} nodes, {G_flat.number_of_edges()} edges')
print(f'  degree multiset: {dict(Counter(dict(G_flat.degree()).values()))}')
print(f'  slope estimate: {slope_flat}')
print()
if slope_flat is None or (slope_flat is not None and r2_flat is not None and r2_flat < 0.5):
    print('The fit refuses or is unstable. Good. Reporting "degenerate" rather than a misleading slope.')
else:
    print('Slope was fitted but should be interpreted as degenerate (constant input).')
"""
    ),
    markdown_cell(
        """## Where this lands

The three visibility-graph degree distributions are quantitatively distinguishable. That is the methodological contribution of this notebook: the same algorithm that distinguishes financial regimes in Malemapti Hari (2026) distinguishes governance maturity regimes in synthetic data. Whether it does so on real client data is the H4 hypothesis of the research plan.

## Failure modes already visible

- **The signal exists.** Whoever generated the synthetic data controls the underlying H. Real governance time series may not have a Hurst exponent. They may be regime-switching. They may be too short.
- **The exponent is sensitive to outliers.** Visibility graphs amplify single-point spikes. Real audit findings cluster around fiscal year-end; this is regular structure that the algorithm reads as periodic, not necessarily as institutional maturity.
- **The interpretation requires context.** Slope alone is not maturity. Two firms with the same slope may have wildly different governance realities. The notebook 13.8 closer makes this explicit.
"""
    ),
    code_cell(
        """# Connection to Chapter 12.2: same algorithm, different domain.
# Connection to Malemapti Hari (2026, Zenodo): same H estimation philosophy, different vehicle (DFA there, visibility-graph slope here).
print('Methodological provenance:')
print('- Lacasa et al. (2008): natural visibility graph algorithm')
print('- Malemapti Hari (2026, Zenodo): DFA-based H estimation on volatility-volume coupling')
print('- This chapter: visibility-graph H estimation on governance time series')
print()
print('Cross-validating Hurst between DFA and visibility-graph slope is one of the')
print(\"cheapest near-term papers in the candidate's research program (see research plan).\")
"""
    ),
]


# ---------------------------------------------------------------------------
# 13.5 AI as Governance Subject and Agent
# ---------------------------------------------------------------------------

NB_13_5 = [
    markdown_cell(
        "> **Chapter 13, Part 5** | Continues from [13.4 Visibility Graphs of Governance Time Series](13.4%20Visibility%20Graphs%20of%20Governance%20Time%20Series.ipynb). **Focus:** AI is both a governance subject and an agent. Build a provenance graph, then build a parser."
    ),
    markdown_cell(
        """# AI as Governance Subject and Agent

AI sits in two governance positions simultaneously.

- **As a subject.** An AI system has a provenance graph: data sources, preprocessing, training run, evaluations, deployment, monitoring. Each node introduces governance obligations. The blast radius of a defect propagates through the same graph. The structural lens from Chapter 12.5 (lineage and fault propagation) applies directly.
- **As an agent.** An AI system can read text and produce structured output. A free-text governance incident report can be parsed by an LLM into a `GovernanceIncident` object, which feeds the apparatus from notebooks 13.1 through 13.4. This makes AI a measurement instrument for governance research, not just a subject of it.

This notebook builds both. The subject side uses NetworkX and the box-covering algorithm to compute the AI provenance graph and identify high-blast-radius nodes. The agent side wires the Anthropic Claude API into a `LLMParser`, with a deterministic `MockParser` that fires when no API key is present so the notebook executes in any environment.

## The honesty up front

AI mediation is not free. The parser can hallucinate. Pressure scores produced by a parser are not equivalent to validated psychometric instruments. The notebook 13.8 closer names these failure modes; this notebook builds the apparatus carefully enough that the failure modes are addressable rather than fatal.
"""
    ),
    code_cell(
        """import os
import json
import re
from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


# ----------------------------- Subject side: AI provenance graph -----------------------------

PROV_NODES = [
    ('webcrawl_2025', 'data_source'),
    ('books_corpus', 'data_source'),
    ('code_corpus', 'data_source'),
    ('synthetic_examples', 'data_source'),
    ('dedupe', 'preprocessing'),
    ('tokenize', 'preprocessing'),
    ('safety_filter', 'preprocessing'),
    ('train_run_v1', 'training'),
    ('eval_holdout', 'evaluation'),
    ('eval_red_team', 'evaluation'),
    ('eval_fairness', 'evaluation'),
    ('release_v1', 'deployment'),
    ('production_v1', 'deployment'),
    ('monitor_drift', 'monitoring'),
    ('monitor_safety', 'monitoring'),
    ('monitor_usage', 'monitoring'),
]
PROV_EDGES = [
    ('webcrawl_2025', 'dedupe'),
    ('books_corpus', 'dedupe'),
    ('code_corpus', 'dedupe'),
    ('synthetic_examples', 'dedupe'),
    ('dedupe', 'tokenize'),
    ('tokenize', 'safety_filter'),
    ('safety_filter', 'train_run_v1'),
    ('train_run_v1', 'eval_holdout'),
    ('train_run_v1', 'eval_red_team'),
    ('train_run_v1', 'eval_fairness'),
    ('eval_holdout', 'release_v1'),
    ('eval_red_team', 'release_v1'),
    ('eval_fairness', 'release_v1'),
    ('release_v1', 'production_v1'),
    ('production_v1', 'monitor_drift'),
    ('production_v1', 'monitor_safety'),
    ('production_v1', 'monitor_usage'),
]

P = nx.DiGraph()
for n, kind in PROV_NODES:
    P.add_node(n, kind=kind)
P.add_edges_from(PROV_EDGES)
print(f'Provenance graph: {P.number_of_nodes()} nodes, {P.number_of_edges()} edges')
"""
    ),
    code_cell(
        """def blast_radius(G: nx.DiGraph, node: str) -> set:
    if node not in G:
        return set()
    return nx.descendants(G, node) | {node}


reach = {n: len(blast_radius(P, n)) for n in P.nodes()}
ranked = sorted(reach.items(), key=lambda x: x[1], reverse=True)
print('Blast-radius ranking (number of downstream nodes affected if this stage fails):')
for n, r in ranked[:10]:
    kind = P.nodes[n]['kind']
    print(f'  {n:>22s} ({kind:>13s}): {r}')
"""
    ),
    code_cell(
        """# Render the provenance graph with blast-radius colour coding.
KIND_COLOUR = {
    'data_source': '#efce8a',
    'preprocessing': '#9ab0a3',
    'training': '#d17a00',
    'evaluation': '#6e8db4',
    'deployment': '#c46b6b',
    'monitoring': '#5fa8a3',
}

pos = nx.spring_layout(P, seed=3, iterations=200)
fig, ax = plt.subplots(figsize=(13, 6.5))
node_sizes = [200 + 80 * reach[n] for n in P.nodes()]
node_colors = [KIND_COLOUR[P.nodes[n]['kind']] for n in P.nodes()]
nx.draw_networkx_edges(P, pos, alpha=0.4, arrows=True, arrowsize=14, ax=ax)
nx.draw_networkx_nodes(P, pos, node_size=node_sizes, node_color=node_colors,
                       edgecolors='#173326', linewidths=1.2, ax=ax)
nx.draw_networkx_labels(P, pos, font_size=8, ax=ax)
ax.set_title('AI provenance graph (size = blast radius)')
import matplotlib.patches as mpatches
legend_handles = [mpatches.Patch(color=c, label=k) for k, c in KIND_COLOUR.items()]
ax.legend(handles=legend_handles, loc='lower right', fontsize=8)
ax.axis('off')
plt.tight_layout()
plt.show()

print('Top blast-radius nodes are the ones to govern hardest. Source data nodes')
print('(data_source) sit at the root and reach the most descendants; safety_filter')
print('and tokenize sit on the critical path. Training and release are pivotal.')
"""
    ),
    markdown_cell(
        """## The agent side: building the parser

The parser takes a free-text governance incident report and returns a structured `GovernanceIncident` object. The chain is intentionally minimal: a strict prompt, a JSON-validated response, and a deterministic mock fallback.

The mock parser uses keyword heuristics. It will not match the LLM's quality on edge cases, but it will run anywhere, deterministically, and it serves as the smoke-test surface that all subsequent notebooks rely on.
"""
    ),
    code_cell(
        """@dataclass
class GovernanceIncident:
    summary: str
    scales: List[str] = field(default_factory=list)
    dominant_pressure: str = 'unknown'
    suggested_control: str = ''
    confidence: float = 0.0
    citations: List[str] = field(default_factory=list)


SCALE_KEYWORDS = {
    'field': ['regulator', 'legislation', 'statute', 'directive', 'industry-wide', 'across the field', 'eu ', 'sec ', 'occ ', 'sox', 'dora'],
    'firm': ['firm', 'company', 'organization', 'enterprise', 'corporate', 'global policy', 'firm-wide'],
    'division': ['division', 'business unit', 'practice', 'sector', 'vertical'],
    'team': ['team', 'project', 'engagement', 'pod', 'squad'],
    'practitioner': ['individual', 'practitioner', 'analyst', 'engineer', 'consultant', 'me ', 'i ', 'personally'],
}

PRESSURE_KEYWORDS = {
    'coercive': ['regulation', 'audit', 'fine', 'penalty', 'mandate', 'must', 'required', 'compliance', 'contract', 'msa', 'sla', 'enforcement'],
    'mimetic': ['benchmark', 'peer', 'competitor', 'industry standard', 'best practice', 'similar firms', 'leaders adopt'],
    'normative': ['certification', 'training', 'professional', 'ethics', 'code of conduct', 'cdmp', 'standard', 'norm', 'expectation'],
}


class MockParser:
    \"\"\"Deterministic regex/keyword parser. Always returns a GovernanceIncident.\"\"\"
    def parse(self, text: str) -> GovernanceIncident:
        t = text.lower()
        scales = [s for s, kws in SCALE_KEYWORDS.items() if any(k in t for k in kws)]
        scores = {p: sum(1 for k in kws if k in t) for p, kws in PRESSURE_KEYWORDS.items()}
        dominant = max(scores, key=scores.get) if any(scores.values()) else 'unknown'
        # Suggested controls keyed by dominant pressure.
        controls = {
            'coercive': 'Add a documented control mapped to the cited regulation; assign owner; record evidence.',
            'mimetic': 'Run a peer benchmark; codify the chosen practice as a firm-wide standard.',
            'normative': 'Update training and certification expectations; align with professional code.',
            'unknown': 'Restate the incident with explicit pressure attribution before proceeding.',
        }
        return GovernanceIncident(
            summary=text.strip()[:240],
            scales=scales,
            dominant_pressure=dominant,
            suggested_control=controls[dominant],
            confidence=0.4 + 0.1 * sum(1 for v in scores.values() if v > 0),
            citations=['Mock parser; replace with LLMParser for higher-fidelity inference'],
        )


# Smoke test with a sample report.
SAMPLE_REPORT = (
    'Last quarter our model risk team was flagged in an OCC audit because '
    'the firm-wide model inventory did not include three production models that '
    'individual analysts had deployed via a shadow Snowflake account. The audit '
    'cited SOX and OCC guidance. Peer firms have moved to centralized model '
    'registries; we have lagged behind on this.'
)
mock = MockParser()
result_mock = mock.parse(SAMPLE_REPORT)
print('Mock parser output:')
print(json.dumps(result_mock.__dict__, indent=2))
"""
    ),
    code_cell(
        """class LLMParser:
    \"\"\"Anthropic-backed parser. Falls back to mock on missing key, network error,
    or malformed response (V004 strict JSON validation).\"\"\"
    def __init__(self):
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.fallback = MockParser()
        self._client = None
        if self.api_key:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except Exception as e:
                print(f'Could not initialize Anthropic client ({type(e).__name__}: {e}); falling back to mock.')

    @property
    def is_live(self) -> bool:
        return self._client is not None

    def parse(self, text: str) -> GovernanceIncident:
        if not self.is_live:
            return self.fallback.parse(text)
        sys = (
            'You are a data governance researcher. Return a strict JSON object with keys '
            '"summary" (string, <= 240 chars), "scales" (list of strings drawn only from '
            '["field","firm","division","team","practitioner"]), "dominant_pressure" '
            '(one of "coercive","mimetic","normative","unknown"), "suggested_control" '
            '(string), "confidence" (number in [0,1]), "citations" (list of strings). '
            'Do not include any prose outside the JSON.'
        )
        try:
            response = self._client.messages.create(
                model='claude-3-haiku-20240307',
                max_tokens=600,
                system=sys,
                messages=[{'role': 'user', 'content': text}],
            )
            payload = response.content[0].text
            match = re.search(r'\\{.*\\}', payload, re.DOTALL)
            if not match:
                return self.fallback.parse(text)
            data = json.loads(match.group(0))
            return GovernanceIncident(
                summary=str(data.get('summary', text[:240])),
                scales=list(data.get('scales', [])),
                dominant_pressure=str(data.get('dominant_pressure', 'unknown')),
                suggested_control=str(data.get('suggested_control', '')),
                confidence=float(data.get('confidence', 0.5)),
                citations=list(data.get('citations', [])),
            )
        except Exception as e:
            print(f'LLMParser failed ({type(e).__name__}: {e}); falling back to mock.')
            return self.fallback.parse(text)


# Try the live parser; will fall back to mock if no key is set.
parser = LLMParser()
print(f'Parser is_live: {parser.is_live}')
result_live = parser.parse(SAMPLE_REPORT)
print('Active parser output:')
print(json.dumps(result_live.__dict__, indent=2))
"""
    ),
    markdown_cell(
        """## Reading the parser output

When the Anthropic key is present, the parser produces structured pressure attributions in seconds. When the key is absent, the mock parser produces a similar shape using deterministic heuristics. The chapter executes in either configuration.

The output shape is the integration point. Every later notebook in this chapter consumes `GovernanceIncident` objects. The user can swap the parser implementation (LLM, fine-tuned classifier, hand-coded rules) without changing downstream code. This is the same pattern Chapter 8's "Ask Warren" chatbot uses: a clean boundary between the LLM call and the consuming code keeps the LLM substitutable.

## Failure modes named explicitly

- **R001 hallucination.** The LLM may invent regulations, cite plausible-sounding statutes that do not exist, or produce a `dominant_pressure` value that is not in the allowed enum. The strict JSON validation catches structural errors but cannot catch invented citations. Trust the parser for triage; verify before public attribution.
- **R001 prompt sensitivity.** Reasonable prompt variations produce different pressure attributions. A research-grade pipeline would average across prompt variants and report variance. The teaching pipeline does not.
- **R001 small-N validation.** No human-coder agreement was computed for this parser. The H3 hypothesis in the research plan is exactly this: validate the AI-mediated pressure profile against trained human qualitative coders.

## Practical implications

- **For practitioners:** the parser is faster than a hand-coded analysis and useful for triage. Do not use parser output as evidence in a regulatory submission without human review.
- **For researchers:** the parser is a candidate measurement instrument that requires validation before becoming a research tool. The validation study is described in the research plan.
- **For students:** the API call wrapper, JSON validation, and mock fallback are the engineering pattern. The same scaffold supports any structured-output LLM use case.
"""
    ),
]


# ---------------------------------------------------------------------------
# 13.6 The Translation Cascade
# ---------------------------------------------------------------------------

NB_13_6 = [
    markdown_cell(
        "> **Chapter 13, Part 6** | Continues from [13.5 AI as Governance Subject and Agent](13.5%20AI%20as%20Governance%20Subject%20and%20Agent.ipynb). **Focus:** regulation does not arrive as a single sentence; it cascades."
    ),
    markdown_cell(
        """# The Translation Cascade

A regulation is not delivered to a practitioner. It cascades. The European DORA regulation lives at the field scale; the firm reads it and produces a corporate policy; the corporate policy is translated into engagement standard operating procedures; the SOPs are interpreted by the practitioner who actually runs the production system. Each translation step is an opportunity for **drift** between what the original regulation requires and what is actually done.

This notebook builds a four-layer translation cascade with three preset scenarios (DORA, EU AI Act, DAMA-DMBOK) and a `translation_drift` measure based on TF-IDF cosine similarity between adjacent layers. The drift measure is in [0, 1] where 0 means the layers say the same things and 1 means they share no terms at all. Stepanovic et al. (2025) and Mahmutovic (2025) describe this kind of cascade qualitatively; the quantitative drift measure here is the apparatus complement.

## Why this matters

Faulconbridge et al. (2024) make the case that consultancies act as carriers of normative pressure across firms. The translation cascade puts that argument under a measurement: when a consultancy's internal SOP cites the source regulation but uses different terminology, drift is high; when the firm's policy paraphrases the SOP without preserving regulatory specificity, drift compounds. By the time the practitioner receives the cascade, the original regulatory intent may be unrecognizable. This notebook makes that compounding visible.
"""
    ),
    code_cell(
        """from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CascadeLayer:
    name: str
    text: str
    drift_to_next: Optional[float] = None


def translation_drift(layer_texts: List[str]) -> List[float]:
    \"\"\"Return drift scores in [0, 1] between adjacent layers.

    Drift = 1 - cosine_similarity(layer_i, layer_{i+1}) on TF-IDF vectors.
    \"\"\"
    if len(layer_texts) < 2:
        return []
    vec = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    M = vec.fit_transform(layer_texts)
    drifts = []
    for i in range(len(layer_texts) - 1):
        sim = float(cosine_similarity(M[i], M[i + 1])[0, 0])
        drifts.append(round(1.0 - sim, 4))
    return drifts


# Sanity check: drift of identical text is 0.
assert translation_drift(['hello world', 'hello world']) == [0.0]
# Sanity check: drift of disjoint vocabularies is 1 (or close to).
assert translation_drift(['alpha beta', 'gamma delta'])[0] > 0.99
print('Drift sanity checks pass.')
"""
    ),
    code_cell(
        """# Three preset cascades, hand-curated to teach the pattern.
DORA_CASCADE = [
    CascadeLayer(
        name='DORA Article 9 (regulation)',
        text=(
            'Financial entities shall implement comprehensive ICT risk management frameworks '
            'covering identification, protection, detection, response, recovery, and learning. '
            'The framework shall include policies, procedures, controls, and tools to ensure '
            'the resilience and operational continuity of ICT systems supporting critical functions. '
            'Effective oversight, regular testing, third-party risk management, and incident reporting are required.'
        ),
    ),
    CascadeLayer(
        name='Firm policy (corporate)',
        text=(
            'The firm maintains an enterprise ICT risk policy aligned with regulatory requirements '
            'and BCBS 239. The policy mandates a centralized risk register, quarterly resilience '
            'tests on critical applications, vendor due diligence for material third parties, '
            'and a 24-hour incident notification standard for major events.'
        ),
    ),
    CascadeLayer(
        name='Engagement SOP',
        text=(
            'Project teams document ICT risks in the engagement risk register. Resilience tests '
            'are scoped at engagement kickoff and refreshed at major milestones. Material vendors '
            'are routed through procurement-led due diligence. Incidents above severity 2 trigger '
            'the engagement notification protocol within one business day.'
        ),
    ),
    CascadeLayer(
        name='Practitioner action',
        text=(
            'I update the project risk register weekly. Before launch we run a chaos drill on the '
            'critical path. I email the partner if a vendor change is material. If something '
            'breaks badly I tell the partner the same day.'
        ),
    ),
]

EU_AI_ACT_CASCADE = [
    CascadeLayer(
        name='EU AI Act Article 10 (regulation)',
        text=(
            'High-risk AI system providers shall implement appropriate data and data governance '
            'practices, including training, validation, and testing data sets that are relevant, '
            'representative, free of errors and complete, with documented examination of biases '
            'and the data sourcing and preparation pipeline.'
        ),
    ),
    CascadeLayer(
        name='Firm policy (corporate)',
        text=(
            'AI development at the firm follows the responsible AI policy: documented data lineage '
            'for all production models, bias evaluation for any model with consumer-facing impact, '
            'and quarterly review of training data refresh procedures by the model risk committee.'
        ),
    ),
    CascadeLayer(
        name='Engagement SOP',
        text=(
            'For AI engagements, document the training data sources in the model card. Run the '
            'firm bias evaluator on any model that touches a regulated decision. Capture data '
            'lineage in dbt manifest tests and update the model card on every promote.'
        ),
    ),
    CascadeLayer(
        name='Practitioner action',
        text=(
            'I write the model card before promote. The bias evaluator runs in CI. If the lineage '
            'tests fail, the deploy is blocked.'
        ),
    ),
]

DAMA_CASCADE = [
    CascadeLayer(
        name='DAMA-DMBOK (professional reference)',
        text=(
            'Data governance is the exercise of authority and control over the management of data '
            'assets. It encompasses planning, oversight, and control over data management and the '
            'use of data and data-related resources. Effective data governance includes formal '
            'roles, policies, and decision rights aligned with strategic data objectives.'
        ),
    ),
    CascadeLayer(
        name='Firm policy (corporate)',
        text=(
            'The firm operates a federated data governance model with a chief data officer, a '
            'governance council, and a stewardship network. Policies define ownership, quality '
            'standards, access controls, and lifecycle obligations for enterprise data assets.'
        ),
    ),
    CascadeLayer(
        name='Engagement SOP',
        text=(
            'Each engagement nominates a data lead responsible for catalog completeness, lineage '
            'capture, and quality monitoring on shared data products. Quarterly governance reviews '
            'cover ownership, access, and quality metrics for the engagement.'
        ),
    ),
    CascadeLayer(
        name='Practitioner action',
        text=(
            'I tag every dataset I create. I tell the team lead when a downstream consumer breaks. '
            'I keep a notebook of who uses what; nobody asks for it but I have it.'
        ),
    ),
]


def annotate_cascade(cascade: List[CascadeLayer]) -> List[CascadeLayer]:
    drifts = translation_drift([c.text for c in cascade])
    for i, d in enumerate(drifts):
        cascade[i].drift_to_next = d
    return cascade


for name, cascade in [('DORA', DORA_CASCADE), ('EU AI Act', EU_AI_ACT_CASCADE), ('DAMA-DMBOK', DAMA_CASCADE)]:
    annotate_cascade(cascade)
    print(f'\\n{name} cascade:')
    for layer in cascade:
        suffix = '' if layer.drift_to_next is None else f' [drift to next = {layer.drift_to_next:.3f}]'
        print(f'  {layer.name}{suffix}')
"""
    ),
    code_cell(
        """def render_cascade(cascade, title=''):
    fig, ax = plt.subplots(figsize=(13, 5.4))
    n = len(cascade)
    for i, layer in enumerate(cascade):
        x = 0.04 + i * (0.96 / n)
        ax.add_patch(plt.Rectangle((x, 0.36), 0.92 / n - 0.04, 0.32, color='#173326', alpha=0.18,
                                   ec='#2b5a43'))
        ax.text(x + (0.92 / n - 0.04) / 2, 0.62, layer.name, ha='center', va='center',
                fontsize=10, fontweight='bold', color='#0e1116')
        # Show first ~80 chars of text inside the box.
        snippet = layer.text[:120].replace('\\n', ' ')
        if len(layer.text) > 120:
            snippet = snippet + '...'
        ax.text(x + (0.92 / n - 0.04) / 2, 0.43, snippet, ha='center', va='center',
                fontsize=7, color='#16211a', wrap=True)
        if layer.drift_to_next is not None:
            x_arrow = x + 0.92 / n - 0.04 + 0.005
            d = layer.drift_to_next
            colour = '#c46b6b' if d > 0.6 else ('#d17a00' if d > 0.4 else '#2b5a43')
            ax.annotate('', xy=(x_arrow + 0.04, 0.52), xytext=(x_arrow, 0.52),
                        arrowprops=dict(arrowstyle='->', color=colour, lw=2.4))
            flag = ' (V002 flag: high drift)' if d > 0.6 else ''
            ax.text(x_arrow + 0.02, 0.32, f'drift = {d:.2f}{flag}', ha='center', va='top',
                    fontsize=8, color=colour, fontweight='bold')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title(title, fontsize=12)
    plt.tight_layout()
    plt.show()


for name, cascade in [('DORA Article 9', DORA_CASCADE), ('EU AI Act Article 10', EU_AI_ACT_CASCADE), ('DAMA-DMBOK', DAMA_CASCADE)]:
    render_cascade(cascade, title=f'Translation cascade: {name}')
"""
    ),
    markdown_cell(
        """## Reading the cascades

The DORA cascade compounds drift modestly between layers; the practitioner action layer is recognizable as a translation of the source regulation, even after three steps. The EU AI Act cascade shows higher drift at the engagement-to-practitioner step, where bureaucratic language gives way to operational shorthand. The DAMA-DMBOK cascade shows the highest drift overall, reflecting that DAMA is a reference body of knowledge rather than a regulation, so practitioners feel less binding pressure to preserve the language verbatim.

The drift measure is illustrative, not prescriptive. A drift of 0.5 between two layers does not mean the layers contradict each other; it means they share half their TF-IDF mass. Real translation drift would be measured against a fidelity criterion grounded in the regulatory text itself; this notebook teaches the apparatus, and the research plan describes the validation program (Option B) that makes the drift measure publishable.

## Where this lands

- The cascade idea is the bridge between Chapter 13's pressure-field framing and the dissertation's qualitative interview work. Practitioners describe their experience of regulation in cascade-like terms ("we got the policy from above, then the engagement reinterpreted it"); the drift measure puts a number on the experience.
- The TF-IDF approach is intentionally simple. A sentence-embedding-based drift would handle paraphrase better but introduces an LLM dependency. The dissertation defense audience benefits from the simpler measure because it can be replicated without proprietary tooling.

## Practical implications

- **For practitioners:** before adopting a new regulation, draft the cascade explicitly. The drift score on the practitioner-action step is a leading indicator of audit risk.
- **For researchers:** validate the TF-IDF drift against expert judgment of fidelity loss across N regulations; this is a methods paper waiting to be written.
- **For students:** the apparatus is one function (`translation_drift`). The conceptual content is in the four-layer cascade structure, which is the dissertation's qualitative finding rendered as a manipulable object.
"""
    ),
]


# ---------------------------------------------------------------------------
# 13.7 Capstone Lab: Build Your Own Governance Pressure Map
# ---------------------------------------------------------------------------

NB_13_7 = [
    markdown_cell(
        "> **Chapter 13, Part 7** | Continues from [13.6 The Translation Cascade](13.6%20The%20Translation%20Cascade.ipynb). **Focus:** assemble 13.1 through 13.6 into one printable diagnostic for your environment."
    ),
    markdown_cell(
        """# Capstone Lab: Build Your Own Governance Pressure Map

This notebook is the apparatus turned outward. The reader provides a free-text description of a governance situation (their environment, an incident they observed, a regulatory transition they are managing). The capstone runs the parser from 13.5 (or its mock fallback), uses the result to seed pressure decompositions across scales, and renders a pressure heatmap, decoupling lens, and translation drift estimate alongside a printable summary.

The lab is opinionated about output: by the end of execution, the reader has a one-page diagnostic they can paste into a status update or a remediation plan.
"""
    ),
    code_cell(
        """import json
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict
import os
import re


# Re-declare types so this notebook is self-contained even if run alone.
class Scale(str, Enum):
    FIELD = 'field'
    FIRM = 'firm'
    DIVISION = 'division'
    TEAM = 'team'
    PRACTITIONER = 'practitioner'

SCALE_ORDER = [Scale.FIELD, Scale.FIRM, Scale.DIVISION, Scale.TEAM, Scale.PRACTITIONER]


@dataclass
class PressureVector:
    coercive: float
    mimetic: float
    normative: float
    scale: Scale
    evidence: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.coercive = float(np.clip(self.coercive, 0.0, 1.0))
        self.mimetic = float(np.clip(self.mimetic, 0.0, 1.0))
        self.normative = float(np.clip(self.normative, 0.0, 1.0))


@dataclass
class GovernanceIncident:
    summary: str
    scales: List[str] = field(default_factory=list)
    dominant_pressure: str = 'unknown'
    suggested_control: str = ''
    confidence: float = 0.0
    citations: List[str] = field(default_factory=list)


SCALE_KEYWORDS = {
    'field': ['regulator', 'legislation', 'directive', 'industry-wide', 'eu ', 'sec ', 'occ ', 'sox', 'dora'],
    'firm': ['firm', 'company', 'organization', 'enterprise', 'corporate', 'firm-wide'],
    'division': ['division', 'business unit', 'practice', 'sector'],
    'team': ['team', 'project', 'engagement', 'pod', 'squad'],
    'practitioner': ['individual', 'practitioner', 'analyst', 'engineer', 'consultant', 'me ', 'i ', 'personally'],
}
PRESSURE_KEYWORDS = {
    'coercive': ['regulation', 'audit', 'mandate', 'must', 'required', 'compliance', 'contract'],
    'mimetic': ['benchmark', 'peer', 'competitor', 'industry standard', 'best practice'],
    'normative': ['certification', 'training', 'professional', 'ethics', 'code of conduct', 'cdmp'],
}


def parse_incident(text: str) -> GovernanceIncident:
    \"\"\"Mock parser, identical structure to the LLM parser in 13.5.\"\"\"
    t = text.lower()
    scales = [s for s, kws in SCALE_KEYWORDS.items() if any(k in t for k in kws)]
    scores = {p: sum(1 for k in kws if k in t) for p, kws in PRESSURE_KEYWORDS.items()}
    dominant = max(scores, key=scores.get) if any(scores.values()) else 'unknown'
    controls = {
        'coercive': 'Add a documented control mapped to the cited regulation; assign owner; record evidence.',
        'mimetic': 'Run a peer benchmark; codify the chosen practice as a firm-wide standard.',
        'normative': 'Update training and certification expectations; align with professional code.',
        'unknown': 'Restate the incident with explicit pressure attribution before proceeding.',
    }
    return GovernanceIncident(
        summary=text.strip()[:240],
        scales=scales,
        dominant_pressure=dominant,
        suggested_control=controls[dominant],
        confidence=0.4 + 0.1 * sum(1 for v in scores.values() if v > 0),
        citations=['Mock parser (13.7 capstone, deterministic fallback)'],
    )


def seed_pressure_field_from_incident(incident: GovernanceIncident) -> List[PressureVector]:
    \"\"\"Translate a parsed incident into a baseline pressure decomposition.

    Heuristic: place the dominant pressure heaviest at the scales surfaced by the
    parser, then taper to other scales. This is not a measurement; it is a starting
    point the user is expected to refine.
    \"\"\"
    scale_set = set(incident.scales)
    out = []
    for scale in SCALE_ORDER:
        c = m = n = 0.20
        if scale.value in scale_set:
            if incident.dominant_pressure == 'coercive':
                c = 0.85
            elif incident.dominant_pressure == 'mimetic':
                m = 0.80
            elif incident.dominant_pressure == 'normative':
                n = 0.80
        # Apply the field-firm-practitioner asymmetry from 13.1 mildly.
        if scale == Scale.FIELD:
            c = max(c, 0.55)
        if scale == Scale.PRACTITIONER:
            n = max(n, 0.55)
        out.append(PressureVector(coercive=c, mimetic=m, normative=n, scale=scale,
                                  evidence=[f'seeded from incident: {incident.dominant_pressure}']))
    return out
"""
    ),
    code_cell(
        """# The reader's input. Edit the text below to match an environment you care about.
USER_INCIDENT_TEXT = (
    'Our consulting practice serves regional banks. Last quarter, an OCC audit '
    'flagged us because the firm-wide model risk inventory missed three production '
    'models that engagement teams had spun up in shadow Snowflake accounts. Two '
    'peer firms recently announced centralized model registries. Several individual '
    'data scientists hold CDMP certifications and feel personally accountable for '
    'documentation, but the SOPs do not require it.'
)

incident = parse_incident(USER_INCIDENT_TEXT)
print('--- Parsed governance incident ---')
print(json.dumps(incident.__dict__, indent=2))

field_seeded = seed_pressure_field_from_incident(incident)
print('\\n--- Seeded pressure field ---')
for v in field_seeded:
    print(f'  {v.scale.value:>13s}: c={v.coercive:.2f} m={v.mimetic:.2f} n={v.normative:.2f}')
"""
    ),
    code_cell(
        """def render_capstone(field_seeded, incident, title='Capstone diagnostic'):
    matrix = np.stack([np.array([v.coercive, v.mimetic, v.normative]) for v in field_seeded], axis=1)
    scales = [v.scale.value for v in field_seeded]
    mechanisms = ['coercive', 'mimetic', 'normative']

    fig, axes = plt.subplots(1, 2, figsize=(14.6, 4.4),
                             gridspec_kw={'width_ratios': [1.5, 1]})
    ax = axes[0]
    im = ax.imshow(matrix, aspect='auto', cmap='YlOrBr', vmin=0, vmax=1)
    ax.set_xticks(range(len(scales)))
    ax.set_xticklabels(scales)
    ax.set_yticks(range(len(mechanisms)))
    ax.set_yticklabels(mechanisms)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f'{matrix[i, j]:.2f}', ha='center', va='center',
                    color='black' if matrix[i, j] < 0.6 else 'white', fontsize=9)
    ax.set_title('Pressure field (seeded from incident)')
    fig.colorbar(im, ax=ax, label='intensity')

    ax2 = axes[1]
    ax2.axis('off')
    summary_lines = [
        f'INCIDENT SUMMARY',
        f'',
        incident.summary[:140] + ('...' if len(incident.summary) > 140 else ''),
        '',
        f'SCALES TOUCHED: {", ".join(incident.scales) if incident.scales else "(none parsed)"}',
        f'DOMINANT PRESSURE: {incident.dominant_pressure}',
        f'PARSER CONFIDENCE: {incident.confidence:.2f}',
        '',
        f'SUGGESTED FIRST CONTROL:',
        incident.suggested_control,
        '',
        f'CITATIONS:',
    ] + [f'- {c}' for c in incident.citations]
    ax2.text(0.02, 0.98, '\\n'.join(summary_lines), transform=ax2.transAxes,
             fontsize=9, ha='left', va='top', family='monospace',
             bbox=dict(facecolor='#f7f2e7', edgecolor='#5a4220', alpha=0.92))
    plt.suptitle(title, fontsize=12)
    plt.tight_layout()
    plt.show()


render_capstone(field_seeded, incident, title='Capstone diagnostic for the user-supplied incident')
"""
    ),
    markdown_cell(
        """## Reading the diagnostic

The capstone produces a one-page picture: a pressure heatmap on the left, a textual summary on the right. The heatmap encodes scale and mechanism. The summary encodes provenance and recommended action. Print or screen-grab the figure; paste it into the next steering committee deck.

The diagnostic is **not** a measurement. The pressure intensities are seeded heuristics, the parser is the mock implementation when no Anthropic key is present, and there is no validation against trained human coders. The diagnostic is a triage tool. Its honest use case is: when an incident arrives, run it through this capstone before drafting the response, and the apparatus will surface the scale and mechanism the response should target.

## Where this connects

- **13.1** seeds the pressure types and the scale enum. The capstone reuses both.
- **13.5** provides the parser. The capstone uses the mock implementation for portability; replacing `parse_incident` with `LLMParser().parse` is one line of code.
- **13.6** provides the cascade complement. A real diagnostic would also draft the four-layer cascade for the incident; that step is left as an exercise (it is one cell, using the cascade infrastructure from 13.6).

## Practical implications

- **For practitioners:** edit `USER_INCIDENT_TEXT` to your environment; rerun; capture the figure. That is the workflow.
- **For researchers:** the capstone is the user-facing surface for the validation study described in the research plan. A practitioner cohort running it against described incidents, with the parser in live mode, produces the data needed to validate the parser against human coding.
- **For students:** the capstone is an exercise in composition. Three components from earlier notebooks compose into one diagnostic without conceptual additions.
"""
    ),
]


# ---------------------------------------------------------------------------
# 13.8 When the Visualization Lies
# ---------------------------------------------------------------------------

NB_13_8 = [
    markdown_cell(
        "> **Chapter 13, Part 8 (closer)** | Continues from [13.7 Capstone Lab](13.7%20Capstone%20Lab.ipynb). **Focus:** four failure modes the apparatus must not hide."
    ),
    markdown_cell(
        """# When the Visualization Lies

The apparatus this chapter builds is genuinely useful. It is also dangerous if the failure modes are not named explicitly. This notebook names them. It pairs with notebook 12.7 (failure modes of fractal-graph descriptors) to close the chapter the same way Chapter 12 closed.

The four failure modes:

1. **Pressure scores are subjective and parser-sensitive.** The same incident text produces different attributions under different prompts and parsers.
2. **Decoupling lacks ground truth without longitudinal data.** A single snapshot RMSE between formal and operational signals confuses static disagreement with the dynamic decoupling the theory describes.
3. **The knowledge graph reflects the curator's reading list, not the field.** Box dimensions and Louvain communities are properties of the curated bibliography, not of governance research as such.
4. **AI parsers hallucinate and the hallucinations look authoritative.** Confident-sounding citations from an LLM are not citations.

Each failure mode is demonstrated with an adversarial example below.
"""
    ),
    code_cell(
        """import json
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

# ---------- Failure mode 1: parser sensitivity ----------
SAMPLE = (
    'The team adopted the firm-wide AI policy after seeing competitors do it. '
    'Individual data scientists complained the policy created friction.'
)


def parser_v1(text):
    t = text.lower()
    if any(k in t for k in ['regulation', 'mandate', 'audit']):
        return 'coercive'
    if any(k in t for k in ['competitor', 'peer', 'industry standard']):
        return 'mimetic'
    if any(k in t for k in ['certification', 'professional']):
        return 'normative'
    return 'unknown'


def parser_v2(text):
    \"\"\"Slight prompt variation: weight policy adoption more heavily as 'coercive'.\"\"\"
    t = text.lower()
    if 'policy' in t:
        return 'coercive'
    if 'competitor' in t or 'peer' in t:
        return 'mimetic'
    if 'professional' in t:
        return 'normative'
    return 'unknown'


def parser_v3(text):
    \"\"\"Different variant: weight the practitioner experience more heavily.\"\"\"
    t = text.lower()
    if 'individual' in t or 'complained' in t:
        return 'normative'
    if 'competitor' in t:
        return 'mimetic'
    if 'mandate' in t:
        return 'coercive'
    return 'unknown'


print('Same incident, three plausible parsers:')
print(f'  parser_v1 -> {parser_v1(SAMPLE)}')
print(f'  parser_v2 -> {parser_v2(SAMPLE)}')
print(f'  parser_v3 -> {parser_v3(SAMPLE)}')
print()
print('Three different attributions for the same incident. The "true" attribution')
print('is what trained human coders would produce after consulting the firm context;')
print('that data does not exist in this notebook. The parser is triage, not measurement.')
"""
    ),
    code_cell(
        """# ---------- Failure mode 2: decoupling without longitudinal data ----------
rng = np.random.default_rng(0)
n = 64
formal_t0 = np.clip(0.55 + rng.normal(0, 0.06, n), 0, 1)
operational_t0 = np.clip(0.20 + rng.normal(0, 0.06, n), 0, 1)


def rmse(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))


print(f'Single snapshot RMSE (formal vs operational): {rmse(formal_t0, operational_t0):.3f}')
print('This snapshot looks decoupled.')
print()

# Now imagine the same firm a quarter later. The operational signal has matured.
operational_t1 = np.clip(0.45 + rng.normal(0, 0.06, n), 0, 1)
print(f'Quarter+1 RMSE (formal vs operational): {rmse(formal_t0, operational_t1):.3f}')
print('The "decoupling" was a lag, not a structural decoupling.')
print()
print('Without time, snapshot RMSE confuses transient lag with decoupling. Meyer-Rowan (1977)')
print('describe decoupling as a stable structural condition. Our measure cannot tell the difference')
print('without longitudinal data.')

fig, ax = plt.subplots(figsize=(11, 3.6))
ax.plot(formal_t0, label='formal (t0)', color='#2b5a43', linewidth=1.6)
ax.plot(operational_t0, label='operational (t0)', color='#d17a00', linewidth=1.6, alpha=0.85)
ax.plot(operational_t1, label='operational (t1, one quarter later)', color='#6e8db4', linewidth=1.6, alpha=0.85)
ax.set_ylim(0, 1)
ax.legend(loc='lower right', fontsize=9)
ax.set_title('A snapshot looks decoupled; the lag closes one quarter later')
ax.grid(alpha=0.2)
plt.tight_layout()
plt.show()
"""
    ),
    code_cell(
        """# ---------- Failure mode 3: KG reflects curator, not field ----------
# Two curators with overlapping but different reading lists produce different KGs.
CURATOR_A = ['DiMaggio_Powell_1983', 'Meyer_Rowan_1977', 'Walsh_2025', 'Birkstedt_2023', 'Khatri_Brown_2010', 'Bartlett_2022']
CURATOR_B = ['DiMaggio_Powell_1983', 'Greenwood_2011', 'Volz_2025', 'Mantymaki_2022', 'Stepanovic_2025', 'Acev_2025']

shared = set(CURATOR_A) & set(CURATOR_B)
unique_A = set(CURATOR_A) - set(CURATOR_B)
unique_B = set(CURATOR_B) - set(CURATOR_A)

print(f'Curator A reading list size: {len(CURATOR_A)}')
print(f'Curator B reading list size: {len(CURATOR_B)}')
print(f'Shared papers: {len(shared)} ({sorted(shared)})')
print(f'Unique to A:   {len(unique_A)} ({sorted(unique_A)})')
print(f'Unique to B:   {len(unique_B)} ({sorted(unique_B)})')
print()
print('The KGs would have different communities, different box dimensions, and different')
print('blast-radius rankings. Both are legitimate readings of the field. Neither is the field.')
print()
print('The honest reporting standard: state the corpus criteria, the inclusion date range,')
print('and the curator. This is the same standard PRISMA imposes on systematic reviews.')
"""
    ),
    code_cell(
        """# ---------- Failure mode 4: hallucinated citations ----------
PLAUSIBLE_BUT_FAKE = [
    'Smith, J. (2024). Quantifying decoupling in financial-services data governance. Journal of Information Systems Research, 35(2), 401-420.',
    'Lopez, M., & Chen, R. (2023). Multi-scale fractal descriptors for AI governance compliance. AI Governance Review, 12(4), 88-110.',
    'Garcia, A. (2025). Visibility-graph signatures of regulatory cascades. Network Science Letters, 7(1), 1-12.',
]

print('Plausible-looking citations. None of them exist (verified May 2026).')
print('An LLM may produce strings that look like these. The strings are not citations.\\n')
for c in PLAUSIBLE_BUT_FAKE:
    print(f'  - {c}')
print('\\nValidation: cross-reference any LLM-produced citation against a database (Crossref, OpenAlex,')
print('the publisher landing page) before treating it as evidence. The dissertation bibliography went')
print('through exactly this kind of audit in May 2026; that audit is what makes the citations')
print('elsewhere in this chapter trustworthy.')
"""
    ),
    markdown_cell(
        """## Closing the chapter

Every notebook in Chapter 13 carries an honesty note in its closing markdown. This notebook collects those notes into a single statement: the apparatus is useful for triage and pedagogy, dangerous if used without naming its limits. The companion research plan describes the validation program required to push the apparatus from prototype to peer-reviewed methodological contribution.

## Where the chapter lands as a whole

- **For practitioners:** the apparatus turns governance from text into an interactive object. The diagnostic in 13.7 is the deliverable.
- **For researchers:** the apparatus is a candidate measurement framework. The validation roadmap in `non-git-files/governance-ai-fractals-research-plan.md` is the program.
- **For students:** the apparatus is a worked example of how three streams (institutional theory, network science, AI governance) can be braided in code. The same braid pattern transfers to other domains where multi-scale structure matters.

## Final reading

- DiMaggio and Powell (1983) for the foundational pressure mechanisms.
- Meyer and Rowan (1977) for decoupling.
- Birkstedt et al. (2023), Mäntymäki et al. (2022), Papagiannidis et al. (2025) for the contemporary AI governance frame.
- Skums and Bunimovich (2020) for graph fractal dimension.
- Lacasa et al. (2008) for the visibility-graph algorithm.
- Malemapti Hari (2026, Zenodo) for the methodological provenance the visibility-graph apparatus inherits.
"""
    ),
]


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

NOTEBOOKS = {
    "13.0 Why Governance Needs a Fractal Lens.ipynb": NB_13_0,
    "13.1 The Multi-Scale Pressure Field.ipynb": NB_13_1,
    "13.2 Decoupling as Multi-Scale Decoherence.ipynb": NB_13_2,
    "13.3 The Governance Knowledge Graph.ipynb": NB_13_3,
    "13.4 Visibility Graphs of Governance Time Series.ipynb": NB_13_4,
    "13.5 AI as Governance Subject and Agent.ipynb": NB_13_5,
    "13.6 The Translation Cascade.ipynb": NB_13_6,
    "13.7 Capstone Lab.ipynb": NB_13_7,
    "13.8 When the Visualization Lies.ipynb": NB_13_8,
}


def write_notebooks() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.9",
        },
    }
    for name, cells in NOTEBOOKS.items():
        nb = {
            "cells": cells,
            "metadata": metadata,
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        out_path = OUT_DIR / name
        out_path.write_text(json.dumps(nb, indent=1))
        print(f"wrote {out_path}")


if __name__ == "__main__":
    write_notebooks()
