const bridgePoints = [
  { id: "parks-1", title: "Accessible trail guide", domain: "parks", x: -0.82, y: 0.56, blurb: "paved route, shuttle access, first stop" },
  { id: "parks-2", title: "Shuttle stop instructions", domain: "parks", x: -0.68, y: 0.42, blurb: "arrival plan, shuttle timing, signage" },
  { id: "parks-3", title: "River overlook notes", domain: "parks", x: -0.74, y: 0.18, blurb: "viewpoint, access, family route" },
  { id: "finance-1", title: "Portfolio volatility memo", domain: "finance", x: 0.58, y: -0.48, blurb: "risk, volatility, drawdown" },
  { id: "finance-2", title: "Dividend yield snapshot", domain: "finance", x: 0.74, y: -0.34, blurb: "yield, income, holdings" },
  { id: "finance-3", title: "Position sizing guide", domain: "finance", x: 0.44, y: -0.62, blurb: "allocation, risk budget, exposure" },
  { id: "gov-1", title: "Golden record policy", domain: "governance", x: 0.16, y: 0.82, blurb: "survivorship, stewardship, lineage" },
  { id: "gov-2", title: "Reference data standard", domain: "governance", x: 0.36, y: 0.72, blurb: "controlled vocabulary, code drift" },
  { id: "gov-3", title: "Duplicate cluster review", domain: "governance", x: 0.06, y: 0.62, blurb: "entity resolution, boundary instability" },
];

const queryPresets = {
  parks: { x: -0.76, y: 0.46, label: "accessible trail" },
  finance: { x: 0.60, y: -0.42, label: "portfolio risk" },
  governance: { x: 0.18, y: 0.76, label: "golden record" },
};

const domainColors = {
  parks: "#83dcc4",
  finance: "#ffc46b",
  governance: "#a2b8ff",
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

const svg = document.getElementById("embedding-map");
const semanticResults = document.getElementById("semantic-results");
const filteredResults = document.getElementById("filtered-results");
const domainFilter = document.getElementById("domain-filter");
const topkRange = document.getElementById("topk-range");
const topkValue = document.getElementById("topk-value");
const candidateCount = document.getElementById("candidate-count");
const semanticTop = document.getElementById("semantic-top");
const filteredTop = document.getElementById("filtered-top");

const state = {
  queryX: queryPresets.parks.x,
  queryY: queryPresets.parks.y,
  queryLabel: queryPresets.parks.label,
  filter: "all",
  topK: Number(topkRange?.value || 3),
};
let isDragging = false;

function normalize([x, y]) {
  const norm = Math.hypot(x, y) || 1;
  return [x / norm, y / norm];
}

function cosine(left, right) {
  const [lx, ly] = normalize(left);
  const [rx, ry] = normalize(right);
  return lx * rx + ly * ry;
}

function searchPoints(filter = "all") {
  const query = [state.queryX, state.queryY];
  const ranked = bridgePoints
    .filter((point) => filter === "all" || point.domain === filter)
    .map((point) => ({
      ...point,
      score: cosine(query, [point.x, point.y]),
    }))
    .sort((left, right) => right.score - left.score);

  return ranked.slice(0, state.topK);
}

function project(point) {
  return {
    x: ((point.x + 1) / 2) * 620 + 40,
    y: ((1 - (point.y + 1) / 2) * 340) + 40,
  };
}

function resultMarkup(results) {
  if (!results.length) {
    return "<div class=\"result-item\"><h4>No candidates</h4><p>The active filter removed every point from the candidate pool.</p></div>";
  }

  return results
    .map((row, index) => `
      <article class="result-item">
        <h4>${index + 1}. ${row.title}</h4>
        <p>${row.blurb}</p>
        <small>${row.domain} · score ${row.score.toFixed(3)}</small>
      </article>
    `)
    .join("");
}

function updatePanels() {
  const semantic = searchPoints("all");
  const filtered = searchPoints(state.filter);

  semanticResults.innerHTML = resultMarkup(semantic);
  filteredResults.innerHTML = resultMarkup(filtered);

  candidateCount.textContent = String(
    bridgePoints.filter((point) => state.filter === "all" || point.domain === state.filter).length
  );
  semanticTop.textContent = semantic[0]?.id ?? "--";
  filteredTop.textContent = filtered[0]?.id ?? "--";
}

function renderMap() {
  if (!svg) {
    return;
  }

  const semanticIds = new Set(searchPoints("all").map((row) => row.id));
  const filteredIds = new Set(searchPoints(state.filter).map((row) => row.id));
  const queryPosition = project({ x: state.queryX, y: state.queryY });

  const pointMarkup = bridgePoints
    .map((point) => {
      const { x, y } = project(point);
      const dimmed = state.filter !== "all" && point.domain !== state.filter;
      const isSemantic = semanticIds.has(point.id);
      const isFiltered = filteredIds.has(point.id);
      return `
        <g>
          <circle cx="${x}" cy="${y}" r="${isFiltered ? 11 : isSemantic ? 9 : 7}" fill="${domainColors[point.domain]}" opacity="${dimmed ? 0.18 : 0.88}" stroke="${isFiltered ? "#fff1dd" : "#04060d"}" stroke-width="${isFiltered ? 3 : 1.5}"></circle>
          <text x="${x + 12}" y="${y + 4}" fill="${dimmed ? "rgba(255,255,255,0.22)" : "#e2e8fc"}" font-size="12" font-family="Manrope, sans-serif">${point.id}</text>
        </g>
      `;
    })
    .join("");

  svg.innerHTML = `
    <rect x="40" y="40" width="620" height="340" rx="28" fill="rgba(255,255,255,0.02)" stroke="rgba(255,255,255,0.08)"></rect>
    <line x1="350" y1="40" x2="350" y2="380" stroke="rgba(255,255,255,0.08)" stroke-dasharray="6 10"></line>
    <line x1="40" y1="210" x2="660" y2="210" stroke="rgba(255,255,255,0.08)" stroke-dasharray="6 10"></line>
    <text x="56" y="68" fill="rgba(255,255,255,0.48)" font-size="12" font-family="Manrope, sans-serif">embedding map</text>
    <text x="56" y="394" fill="rgba(255,255,255,0.48)" font-size="12" font-family="Manrope, sans-serif">left/right latent direction</text>
    <text x="540" y="68" fill="rgba(255,255,255,0.48)" font-size="12" font-family="Manrope, sans-serif">top/bottom latent direction</text>
    ${pointMarkup}
    <circle id="query-handle" cx="${queryPosition.x}" cy="${queryPosition.y}" r="13" fill="#ffc46b" stroke="#fff1dd" stroke-width="4" style="cursor: grab;"></circle>
    <text x="${queryPosition.x + 16}" y="${queryPosition.y + 4}" fill="#fff1dd" font-size="13" font-family="Manrope, sans-serif">${state.queryLabel}</text>
  `;

  const handle = document.getElementById("query-handle");

  const move = (clientX, clientY) => {
    const rect = svg.getBoundingClientRect();
    const x = Math.min(Math.max(clientX - rect.left, 40), 660);
    const y = Math.min(Math.max(clientY - rect.top, 40), 380);
    state.queryX = ((x - 40) / 620) * 2 - 1;
    state.queryY = (1 - (y - 40) / 340) * 2 - 1;
    state.queryLabel = "custom query";
    document.querySelectorAll(".chip-button").forEach((button) => button.classList.remove("is-active"));
    updatePanels();
    renderMap();
  };

  handle?.addEventListener("pointerdown", (event) => {
    isDragging = true;
    handle.setPointerCapture?.(event.pointerId);
  });

  svg.onpointermove = (event) => {
    if (isDragging) {
      move(event.clientX, event.clientY);
    }
  };

  svg.onpointerup = () => {
    isDragging = false;
  };

  svg.onpointerleave = () => {
    isDragging = false;
  };
}

document.querySelectorAll(".chip-button").forEach((button) => {
  button.addEventListener("click", () => {
    const preset = queryPresets[button.dataset.query];
    state.queryX = preset.x;
    state.queryY = preset.y;
    state.queryLabel = preset.label;
    document.querySelectorAll(".chip-button").forEach((node) => node.classList.toggle("is-active", node === button));
    updatePanels();
    renderMap();
  });
});

domainFilter?.addEventListener("change", () => {
  state.filter = domainFilter.value;
  updatePanels();
  renderMap();
});

topkRange?.addEventListener("input", () => {
  state.topK = Number(topkRange.value);
  topkValue.textContent = String(state.topK);
  updatePanels();
  renderMap();
});

updatePanels();
renderMap();
