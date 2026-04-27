const rankingScenarios = {
  parks: {
    label: "accessible stop",
    rows: [
      {
        id: "c1",
        title: "Accessible riverside stop",
        domain: "parks",
        snippet: "Paved route, shuttle access, and clear signage make this a strong first stop.",
        semantic: 0.92,
        lexical: 2,
        bonus: 0.04,
        relevant: true,
      },
      {
        id: "c2",
        title: "General shuttle operations",
        domain: "parks",
        snippet: "Shuttle timing and stop intervals for mid-day visitors.",
        semantic: 0.88,
        lexical: 1,
        bonus: 0.0,
        relevant: false,
      },
      {
        id: "c3",
        title: "Trail safety briefing",
        domain: "parks",
        snippet: "Steep sections, weather changes, and uneven ground warnings.",
        semantic: 0.81,
        lexical: 0,
        bonus: 0.0,
        relevant: false,
      },
      {
        id: "c4",
        title: "Accessible visitor guide",
        domain: "parks",
        snippet: "Low-grade walking route, paved access, and signage for families.",
        semantic: 0.84,
        lexical: 3,
        bonus: 0.06,
        relevant: true,
      },
      {
        id: "c5",
        title: "Evening ranger program",
        domain: "parks",
        snippet: "Talk schedule, amphitheater location, and evening topics.",
        semantic: 0.73,
        lexical: 0,
        bonus: 0.0,
        relevant: false,
      },
    ],
  },
  finance: {
    label: "portfolio risk",
    rows: [
      {
        id: "f1",
        title: "Portfolio volatility memo",
        domain: "finance",
        snippet: "Recent drawdown, volatility regime, and concentration risk.",
        semantic: 0.93,
        lexical: 3,
        bonus: 0.03,
        relevant: true,
      },
      {
        id: "f2",
        title: "Dividend income snapshot",
        domain: "finance",
        snippet: "Yield, quarterly cash flow, and income screens.",
        semantic: 0.74,
        lexical: 0,
        bonus: 0.0,
        relevant: false,
      },
      {
        id: "f3",
        title: "Position sizing guide",
        domain: "finance",
        snippet: "Sizing by exposure limits, volatility budgets, and stop distance.",
        semantic: 0.84,
        lexical: 2,
        bonus: 0.05,
        relevant: true,
      },
      {
        id: "f4",
        title: "Market breadth note",
        domain: "finance",
        snippet: "Index participation and breadth deterioration across sectors.",
        semantic: 0.77,
        lexical: 1,
        bonus: 0.0,
        relevant: false,
      },
      {
        id: "f5",
        title: "Hedging summary",
        domain: "finance",
        snippet: "Protective puts and downside hedging for concentrated positions.",
        semantic: 0.86,
        lexical: 2,
        bonus: 0.04,
        relevant: true,
      },
    ],
  },
  governance: {
    label: "golden record",
    rows: [
      {
        id: "g1",
        title: "Golden record policy",
        domain: "governance",
        snippet: "Survivorship logic, steward review, and lineage requirements.",
        semantic: 0.94,
        lexical: 3,
        bonus: 0.06,
        relevant: true,
      },
      {
        id: "g2",
        title: "Reference data standard",
        domain: "governance",
        snippet: "Code systems, controlled vocabularies, and domain ownership.",
        semantic: 0.83,
        lexical: 1,
        bonus: 0.02,
        relevant: false,
      },
      {
        id: "g3",
        title: "Duplicate cluster review",
        domain: "governance",
        snippet: "Threshold sensitivity, merge ambiguity, and escalation rules.",
        semantic: 0.89,
        lexical: 2,
        bonus: 0.05,
        relevant: true,
      },
      {
        id: "g4",
        title: "Lineage exception log",
        domain: "governance",
        snippet: "Missing upstream references and broken downstream mappings.",
        semantic: 0.78,
        lexical: 0,
        bonus: 0.01,
        relevant: false,
      },
      {
        id: "g5",
        title: "Entity stewardship memo",
        domain: "governance",
        snippet: "Manual review triggers, authority boundaries, and unresolved entities.",
        semantic: 0.87,
        lexical: 2,
        bonus: 0.04,
        relevant: true,
      },
    ],
  },
};

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.14 }
);

document.querySelectorAll("[data-reveal]").forEach((node) => observer.observe(node));

const semanticRange = document.getElementById("semantic-range");
const lexicalRange = document.getElementById("lexical-range");
const rerankRange = document.getElementById("rerank-range");
const semanticValue = document.getElementById("semantic-value");
const lexicalValue = document.getElementById("lexical-value");
const rerankValue = document.getElementById("rerank-value");
const domainFilter = document.getElementById("domain-filter");
const candidateBoard = document.getElementById("candidate-board");
const semanticWinner = document.getElementById("semantic-winner");
const hybridWinner = document.getElementById("hybrid-winner");
const rerankWinner = document.getElementById("rerank-winner");
const semanticPrecision = document.getElementById("semantic-precision");
const hybridPrecision = document.getElementById("hybrid-precision");
const rerankPrecision = document.getElementById("rerank-precision");

const state = {
  scenario: "parks",
  semanticWeight: Number(semanticRange?.value || 0.7),
  lexicalWeight: Number(lexicalRange?.value || 0.3),
  rerankScale: Number(rerankRange?.value || 1),
  filter: "all",
};

function scaleLexical(rows) {
  const max = Math.max(...rows.map((row) => row.lexical), 1);
  return rows.map((row) => ({ ...row, lexicalScaled: row.lexical / max }));
}

function precisionAt3(rows, scoreKey) {
  const top = [...rows].sort((a, b) => b[scoreKey] - a[scoreKey]).slice(0, 3);
  return (top.filter((row) => row.relevant).length / 3).toFixed(2);
}

function computeRows() {
  let rows = rankingScenarios[state.scenario].rows;
  if (state.filter !== "all") {
    rows = rows.filter((row) => row.domain === state.filter);
  }

  rows = scaleLexical(rows).map((row) => {
    const hybrid = state.semanticWeight * row.semantic + state.lexicalWeight * row.lexicalScaled;
    const rerank = hybrid + state.rerankScale * row.bonus;
    return { ...row, hybrid, rerank };
  });

  return rows;
}

function topId(rows, scoreKey) {
  if (!rows.length) {
    return "--";
  }
  return [...rows].sort((a, b) => b[scoreKey] - a[scoreKey])[0].id;
}

function renderBoard() {
  const rows = computeRows();
  const semanticTop = topId(rows, "semantic");
  const hybridTop = topId(rows, "hybrid");
  const rerankTop = topId(rows, "rerank");

  semanticWinner.textContent = semanticTop;
  hybridWinner.textContent = hybridTop;
  rerankWinner.textContent = rerankTop;
  semanticPrecision.textContent = rows.length ? precisionAt3(rows, "semantic") : "--";
  hybridPrecision.textContent = rows.length ? precisionAt3(rows, "hybrid") : "--";
  rerankPrecision.textContent = rows.length ? precisionAt3(rows, "rerank") : "--";

  if (!rows.length) {
    candidateBoard.innerHTML = `
      <article class="candidate-card">
        <div class="candidate-head">
          <div>
            <h3>No candidates</h3>
            <p class="candidate-meta">The active filter removed every row from the ranking set.</p>
          </div>
        </div>
      </article>
    `;
    return;
  }

  const maxHybrid = Math.max(...rows.map((row) => row.hybrid), 1);
  const maxRerank = Math.max(...rows.map((row) => row.rerank), 1);

  candidateBoard.innerHTML = rows
    .map((row) => {
      const badges = [];
      if (row.id === semanticTop) badges.push("semantic winner");
      if (row.id === hybridTop) badges.push("hybrid winner");
      if (row.id === rerankTop) badges.push("rerank winner");
      if (row.relevant) badges.push("relevant");

      return `
        <article class="candidate-card">
          <div class="candidate-head">
            <div>
              <h3>${row.id} · ${row.title}</h3>
              <p class="candidate-meta">${row.domain} · ${row.snippet}</p>
            </div>
            <div class="winner-badges">
              ${badges.map((badge) => `<span class="winner-badge">${badge}</span>`).join("")}
            </div>
          </div>

          <div class="score-grid">
            <div class="score-row">
              <span>semantic</span>
              <div class="bar-track"><div class="bar-fill fill-semantic" style="width:${row.semantic * 100}%"></div></div>
              <strong>${row.semantic.toFixed(2)}</strong>
            </div>
            <div class="score-row">
              <span>lexical</span>
              <div class="bar-track"><div class="bar-fill fill-lexical" style="width:${row.lexicalScaled * 100}%"></div></div>
              <strong>${row.lexicalScaled.toFixed(2)}</strong>
            </div>
            <div class="score-row">
              <span>hybrid</span>
              <div class="bar-track"><div class="bar-fill fill-hybrid" style="width:${(row.hybrid / maxHybrid) * 100}%"></div></div>
              <strong>${row.hybrid.toFixed(2)}</strong>
            </div>
            <div class="score-row">
              <span>rerank</span>
              <div class="bar-track"><div class="bar-fill fill-rerank" style="width:${(row.rerank / maxRerank) * 100}%"></div></div>
              <strong>${row.rerank.toFixed(2)}</strong>
            </div>
          </div>
        </article>
      `;
    })
    .join("");
}

function setDisplayedValues() {
  semanticValue.textContent = state.semanticWeight.toFixed(2);
  lexicalValue.textContent = state.lexicalWeight.toFixed(2);
  rerankValue.textContent = state.rerankScale.toFixed(2);
}

document.querySelectorAll(".chip-button").forEach((button) => {
  button.addEventListener("click", () => {
    state.scenario = button.dataset.query;
    state.filter = "all";
    if (domainFilter) {
      domainFilter.value = "all";
    }
    document.querySelectorAll(".chip-button").forEach((node) => node.classList.toggle("is-active", node === button));
    renderBoard();
  });
});

semanticRange?.addEventListener("input", () => {
  state.semanticWeight = Number(semanticRange.value);
  setDisplayedValues();
  renderBoard();
});

lexicalRange?.addEventListener("input", () => {
  state.lexicalWeight = Number(lexicalRange.value);
  setDisplayedValues();
  renderBoard();
});

rerankRange?.addEventListener("input", () => {
  state.rerankScale = Number(rerankRange.value);
  setDisplayedValues();
  renderBoard();
});

domainFilter?.addEventListener("change", () => {
  state.filter = domainFilter.value;
  renderBoard();
});

setDisplayedValues();
renderBoard();
