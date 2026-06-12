// Reveal-on-scroll, mirroring fractal-graphs.js.
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

function activateButton(groupSelector, value, attr) {
  document.querySelectorAll(groupSelector).forEach((btn) => {
    btn.classList.toggle("is-active", btn.getAttribute(attr) === value);
  });
}

function clamp(v, lo, hi) {
  return Math.min(hi, Math.max(lo, v));
}

// =========================================================================
// LAB 1 — Multi-scale pressure field
// =========================================================================

const SCALES = ["field", "firm", "division", "team", "practitioner"];
const MECHANISMS = ["coercive", "mimetic", "normative"];
const MECH_COLOURS = {
  coercive: "#ef6a85",
  mimetic: "#62b6ff",
  normative: "#6d4fe0",
};

const PRESSURE_PRESETS = {
  finance: [
    [0.95, 0.40, 0.55, 0.30, 0.20], // coercive
    [0.30, 0.70, 0.65, 0.55, 0.35], // mimetic
    [0.45, 0.55, 0.60, 0.75, 0.85], // normative
  ],
  university: [
    [0.50, 0.35, 0.30, 0.20, 0.15],
    [0.40, 0.75, 0.55, 0.45, 0.30],
    [0.40, 0.45, 0.50, 0.55, 0.55],
  ],
  startup: [
    [0.30, 0.25, 0.20, 0.20, 0.20],
    [0.55, 0.85, 0.65, 0.60, 0.45],
    [0.30, 0.35, 0.40, 0.45, 0.55],
  ],
};

let pressureMatrix = PRESSURE_PRESETS.finance.map((row) => row.slice());
let activeScale = 0;
let activeCell = null;

function renderPressureHeatmap() {
  const svg = document.getElementById("pressure-canvas");
  if (!svg) return;
  const W = 720;
  const H = 380;
  const padX = 96;
  const padY = 50;
  const usableW = W - padX - 24;
  const usableH = H - padY - 30;
  const cellW = usableW / SCALES.length;
  const cellH = usableH / MECHANISMS.length;

  let svgInner = `<rect x="0" y="0" width="${W}" height="${H}" fill="rgba(0,0,0,0.18)"/>`;

  // Heatmap cells.
  for (let i = 0; i < MECHANISMS.length; i += 1) {
    for (let j = 0; j < SCALES.length; j += 1) {
      const value = pressureMatrix[i][j];
      const x = padX + j * cellW;
      const y = padY + i * cellH;
      const fill = pressureColour(value, MECHANISMS[i]);
      const isActive = j === activeScale;
      const stroke = isActive ? "rgba(238, 242, 255,0.85)" : "rgba(255,255,255,0.06)";
      svgInner += `<rect class="heatmap-cell${isActive ? " is-active" : ""}" data-i="${i}" data-j="${j}" x="${x + 2}" y="${y + 2}" width="${cellW - 4}" height="${cellH - 4}" fill="${fill}" stroke="${stroke}" rx="6"/>`;
      const labelColour = value < 0.55 ? "#04060d" : "#eef2ff";
      svgInner += `<text x="${x + cellW / 2}" y="${y + cellH / 2 + 4}" text-anchor="middle" font-size="13" fill="${labelColour}" font-weight="600">${value.toFixed(2)}</text>`;
    }
  }

  // Y-axis (mechanism labels).
  for (let i = 0; i < MECHANISMS.length; i += 1) {
    const y = padY + i * cellH + cellH / 2 + 4;
    svgInner += `<text x="${padX - 14}" y="${y}" text-anchor="end" class="dec-axis-label" font-size="13" fill="#97a3c4">${MECHANISMS[i]}</text>`;
    svgInner += `<rect x="${padX - 8}" y="${padY + i * cellH + cellH / 2 - 4}" width="6" height="8" fill="${MECH_COLOURS[MECHANISMS[i]]}" rx="1"/>`;
  }

  // X-axis (scale labels).
  for (let j = 0; j < SCALES.length; j += 1) {
    const x = padX + j * cellW + cellW / 2;
    const isActive = j === activeScale;
    svgInner += `<text x="${x}" y="${H - 12}" text-anchor="middle" class="scale-tick${isActive ? " is-active" : ""}">${SCALES[j]}</text>`;
  }

  // Title.
  svgInner += `<text x="${W / 2}" y="24" text-anchor="middle" font-size="13" fill="#ffc46b" font-weight="700" letter-spacing="2">PRESSURE FIELD INTENSITY (0..1)</text>`;

  svg.innerHTML = svgInner;

  attachHeatmapHandlers(svg, padX, padY, cellW, cellH);
}

function pressureColour(v, mechanism) {
  // Sand to ochre to deep moss / regime accents.
  const blend = (a, b, t) => Math.round(a + (b - a) * t);
  if (mechanism === "coercive") {
    const r = blend(247, 196, v);
    const g = blend(242, 107, v);
    const b = blend(231, 107, v);
    return `rgb(${r},${g},${b})`;
  }
  if (mechanism === "mimetic") {
    const r = blend(247, 110, v);
    const g = blend(242, 141, v);
    const b = blend(231, 180, v);
    return `rgb(${r},${g},${b})`;
  }
  // normative
  const r = blend(247, 43, v);
  const g = blend(242, 90, v);
  const b = blend(231, 67, v);
  return `rgb(${r},${g},${b})`;
}

function attachHeatmapHandlers(svg, padX, padY, cellW, cellH) {
  let dragging = null;
  svg.addEventListener("mousedown", (e) => {
    const target = e.target;
    if (target && target.classList && target.classList.contains("heatmap-cell")) {
      dragging = { i: Number(target.getAttribute("data-i")), j: Number(target.getAttribute("data-j")) };
      activeCell = dragging;
      activeScale = dragging.j;
      const slider = document.getElementById("scale-slider");
      if (slider) slider.value = String(activeScale);
      onScaleChange();
    }
  });
  svg.addEventListener("mousemove", (e) => {
    if (!dragging) return;
    const rect = svg.getBoundingClientRect();
    const W = 720;
    const H = 380;
    const yPx = e.clientY - rect.top;
    const yScaled = yPx * (H / rect.height);
    const cellTop = padY + dragging.i * cellH;
    const cellBot = cellTop + cellH;
    const fraction = clamp((cellBot - yScaled) / cellH, 0, 1);
    pressureMatrix[dragging.i][dragging.j] = fraction;
    renderPressureHeatmap();
    renderRadar();
    document.getElementById("pressure-status").textContent = `editing ${MECHANISMS[dragging.i]} @ ${SCALES[dragging.j]}`;
  });
  svg.addEventListener("mouseup", () => { dragging = null; });
  svg.addEventListener("mouseleave", () => { dragging = null; });
}

function renderRadar() {
  const svg = document.getElementById("radar-canvas");
  if (!svg) return;
  const cx = 160;
  const cy = 160;
  const radius = 110;
  const values = MECHANISMS.map((_, i) => pressureMatrix[i][activeScale]);
  const angles = [-Math.PI / 2, -Math.PI / 2 + (2 * Math.PI) / 3, -Math.PI / 2 + (4 * Math.PI) / 3];
  const points = values.map((v, i) => {
    const r = v * radius;
    return [cx + r * Math.cos(angles[i]), cy + r * Math.sin(angles[i])];
  });

  let inner = "";
  // Grid rings at 0.25, 0.5, 0.75, 1.0
  for (const ring of [0.25, 0.5, 0.75, 1.0]) {
    const r = radius * ring;
    let path = "";
    for (let i = 0; i < 3; i += 1) {
      const x = cx + r * Math.cos(angles[i]);
      const y = cy + r * Math.sin(angles[i]);
      path += (i === 0 ? "M" : "L") + `${x.toFixed(1)} ${y.toFixed(1)} `;
    }
    inner += `<path class="radar-axis" d="${path}Z"/>`;
  }

  // Axes (outward lines).
  for (let i = 0; i < 3; i += 1) {
    const x = cx + radius * Math.cos(angles[i]);
    const y = cy + radius * Math.sin(angles[i]);
    inner += `<line class="radar-axis" x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}"/>`;
  }

  // Mechanism labels.
  const labelOffsets = [
    { x: cx, y: cy - radius - 14, anchor: "middle" },
    { x: cx + radius + 12, y: cy + radius * Math.sin(angles[1]) + 4, anchor: "start" },
    { x: cx - radius - 12, y: cy + radius * Math.sin(angles[2]) + 4, anchor: "end" },
  ];
  MECHANISMS.forEach((mech, i) => {
    inner += `<text class="radar-axis-label" x="${labelOffsets[i].x}" y="${labelOffsets[i].y}" text-anchor="${labelOffsets[i].anchor}">${mech.slice(0, 4)}</text>`;
  });

  // Polygon for current values.
  const polyPath = points.map(([x, y], i) => (i === 0 ? "M" : "L") + `${x.toFixed(1)} ${y.toFixed(1)}`).join(" ");
  inner += `<path class="radar-poly" d="${polyPath}Z"/>`;

  // Vertices.
  points.forEach(([x, y], i) => {
    inner += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="5" fill="${MECH_COLOURS[MECHANISMS[i]]}" stroke="#eef2ff" stroke-width="1.5"/>`;
  });

  // Centre label with the dominant mechanism at this scale.
  const dominantIdx = values.indexOf(Math.max(...values));
  const dominantText = values[dominantIdx] > 0 ? MECHANISMS[dominantIdx] : "balanced";
  inner += `<text x="${cx}" y="${cy + 6}" text-anchor="middle" font-family="Syne, sans-serif" font-size="22" fill="#eef2ff">${SCALES[activeScale]}</text>`;
  inner += `<text x="${cx}" y="${cy + 28}" text-anchor="middle" font-size="11" fill="#97a3c4" letter-spacing="2">DOMINANT: ${dominantText.toUpperCase()}</text>`;

  svg.innerHTML = inner;
}

function onScaleChange() {
  const idx = activeScale;
  const readout = document.getElementById("scale-readout");
  if (readout) readout.textContent = SCALES[idx];
  document.getElementById("coercive-readout").textContent = pressureMatrix[0][idx].toFixed(2);
  document.getElementById("mimetic-readout").textContent = pressureMatrix[1][idx].toFixed(2);
  document.getElementById("normative-readout").textContent = pressureMatrix[2][idx].toFixed(2);
  const values = MECHANISMS.map((_, i) => pressureMatrix[i][idx]);
  const dominantIdx = values.indexOf(Math.max(...values));
  document.getElementById("dominant-readout").textContent = MECHANISMS[dominantIdx];
  renderPressureHeatmap();
  renderRadar();
}

function applyPressurePreset(name) {
  if (!PRESSURE_PRESETS[name]) return;
  pressureMatrix = PRESSURE_PRESETS[name].map((row) => row.slice());
  activateButton('[data-preset]', name, 'data-preset');
  onScaleChange();
}

document.querySelectorAll('[data-preset]').forEach((btn) => {
  btn.addEventListener('click', () => applyPressurePreset(btn.getAttribute('data-preset')));
});
const scaleSlider = document.getElementById('scale-slider');
if (scaleSlider) {
  scaleSlider.addEventListener('input', (e) => {
    activeScale = Number(e.target.value);
    onScaleChange();
  });
}

applyPressurePreset('finance');

// =========================================================================
// LAB 2 — The Decoupling Lens
// =========================================================================

const DEC_SCENARIOS = {
  theatre: {
    formal:      [0.78, 0.80, 0.65, 0.55, 0.50],
    operational: [0.30, 0.35, 0.55, 0.55, 0.50],
    description: 'Top-scale decoupling: field-level regulation is loud; firm-level claims compliance; operational reality at the top scales diverges.',
  },
  execution: {
    formal:      [0.65, 0.62, 0.60, 0.58, 0.55],
    operational: [0.62, 0.60, 0.55, 0.30, 0.20],
    description: 'Bottom-scale decoupling: policy looks fine at field and firm scale, then diverges sharply at team and practitioner.',
  },
  pervasive: {
    formal:      [0.70, 0.65, 0.60, 0.55, 0.50],
    operational: [0.30, 0.30, 0.30, 0.25, 0.25],
    description: 'Pervasive decoupling at every scale; rare in practice and difficult to act on without locating the dominant gap.',
  },
  aligned: {
    formal:      [0.68, 0.66, 0.64, 0.62, 0.60],
    operational: [0.66, 0.64, 0.62, 0.60, 0.58],
    description: 'Aligned signals; decoupling dimension near zero. Use as the visual control.',
  },
};

let formalSig = DEC_SCENARIOS.theatre.formal.slice();
let operationalSig = DEC_SCENARIOS.theatre.operational.slice();

function rmse(a, b) {
  let s = 0;
  for (let i = 0; i < a.length; i += 1) {
    s += (a[i] - b[i]) ** 2;
  }
  return Math.sqrt(s / a.length);
}

function decouplingDimension(formal, operational) {
  const rmses = formal.map((_, i) => Math.abs(formal[i] - operational[i]));
  const total = rmses.reduce((s, r) => s + r, 0);
  if (total === 0) return 0;
  const weights = rmses.map((r) => r / total);
  const weighted = rmses.reduce((s, r, i) => s + r * (1 + weights[i]), 0);
  return Math.min(weighted / 1.4, 1.0);
}

function renderDecoupling() {
  const svg = document.getElementById('decoupling-canvas');
  if (!svg) return;
  const W = 720;
  const H = 320;
  const padL = 60;
  const padR = 30;
  const padT = 30;
  const padB = 50;
  const usableW = W - padL - padR;
  const usableH = H - padT - padB;
  const groupW = usableW / SCALES.length;
  const halfW = (groupW - 8) / 2;

  let inner = `<rect x="0" y="0" width="${W}" height="${H}" fill="rgba(0,0,0,0.18)"/>`;

  // Y-axis ticks at 0, 0.5, 1.
  for (const t of [0, 0.25, 0.5, 0.75, 1.0]) {
    const y = padT + (1 - t) * usableH;
    inner += `<line x1="${padL}" y1="${y}" x2="${W - padR}" y2="${y}" stroke="rgba(255,255,255,0.06)"/>`;
    inner += `<text class="dec-tick" x="${padL - 8}" y="${y + 3}" text-anchor="end">${t.toFixed(2)}</text>`;
  }

  for (let i = 0; i < SCALES.length; i += 1) {
    const x0 = padL + i * groupW;
    const fH = formalSig[i] * usableH;
    const oH = operationalSig[i] * usableH;
    inner += `<rect class="dec-bar formal" data-side="formal" data-index="${i}" x="${x0 + 4}" y="${padT + usableH - fH}" width="${halfW}" height="${fH}" rx="3"/>`;
    inner += `<rect class="dec-bar operational" data-side="operational" data-index="${i}" x="${x0 + 4 + halfW}" y="${padT + usableH - oH}" width="${halfW}" height="${oH}" rx="3"/>`;
    inner += `<text class="scale-tick" x="${x0 + groupW / 2}" y="${H - 22}" text-anchor="middle">${SCALES[i]}</text>`;
    const r = Math.abs(formalSig[i] - operationalSig[i]);
    inner += `<text class="dec-tick" x="${x0 + groupW / 2}" y="${H - 8}" text-anchor="middle">RMSE ${r.toFixed(2)}</text>`;
  }

  // Legend.
  inner += `<rect x="${padL + 6}" y="6" width="12" height="10" fill="var(--formal)"/>`;
  inner += `<text class="dec-axis-label" x="${padL + 22}" y="15">formal</text>`;
  inner += `<rect x="${padL + 78}" y="6" width="12" height="10" fill="var(--operational)"/>`;
  inner += `<text class="dec-axis-label" x="${padL + 94}" y="15">operational</text>`;

  svg.innerHTML = inner;
  attachDecouplingHandlers(svg, padL, padT, usableH, groupW);
  updateDecouplingReadouts();
}

function attachDecouplingHandlers(svg, padL, padT, usableH, groupW) {
  let dragging = null;
  svg.addEventListener('mousedown', (e) => {
    const target = e.target;
    if (target && target.classList && target.classList.contains('dec-bar')) {
      dragging = { side: target.getAttribute('data-side'), idx: Number(target.getAttribute('data-index')) };
    }
  });
  svg.addEventListener('mousemove', (e) => {
    if (!dragging) return;
    const rect = svg.getBoundingClientRect();
    const H = 320;
    const y = (e.clientY - rect.top) * (H / rect.height);
    const value = clamp(1 - (y - padT) / usableH, 0, 1);
    if (dragging.side === 'formal') {
      formalSig[dragging.idx] = value;
    } else {
      operationalSig[dragging.idx] = value;
    }
    renderDecoupling();
    document.getElementById('decoupling-status').textContent = `editing ${dragging.side} @ ${SCALES[dragging.idx]}`;
  });
  svg.addEventListener('mouseup', () => { dragging = null; });
  svg.addEventListener('mouseleave', () => { dragging = null; });
}

function updateDecouplingReadouts() {
  const dim = decouplingDimension(formalSig, operationalSig);
  document.getElementById('dim-readout').textContent = dim.toFixed(2);
  const rmses = formalSig.map((_, i) => Math.abs(formalSig[i] - operationalSig[i]));
  const rmseStr = rmses.map((r, i) => `${SCALES[i].slice(0, 3)}=${r.toFixed(2)}`).join('  ');
  document.getElementById('rmse-readout').textContent = rmseStr;
  const maxIdx = rmses.indexOf(Math.max(...rmses));
  document.getElementById('locus-readout').textContent = `${SCALES[maxIdx]} (RMSE=${rmses[maxIdx].toFixed(2)})`;
}

function applyDecScenario(name) {
  if (!DEC_SCENARIOS[name]) return;
  formalSig = DEC_SCENARIOS[name].formal.slice();
  operationalSig = DEC_SCENARIOS[name].operational.slice();
  activateButton('[data-scenario]', name, 'data-scenario');
  renderDecoupling();
}

document.querySelectorAll('[data-scenario]').forEach((btn) => {
  btn.addEventListener('click', () => applyDecScenario(btn.getAttribute('data-scenario')));
});
applyDecScenario('theatre');

// =========================================================================
// LAB 3 — Regulation Translation Cascade
// =========================================================================

const CASCADE_PRESETS = {
  dora: [
    {
      name: 'DORA Article 9',
      tag: 'regulation',
      text: 'Financial entities shall implement comprehensive ICT risk management frameworks covering identification, protection, detection, response, recovery, and learning. The framework shall include policies, procedures, controls, and tools to ensure resilience and operational continuity for ICT systems supporting critical functions, with effective oversight, regular testing, third-party risk management, and incident reporting.',
    },
    {
      name: 'Firm policy',
      tag: 'corporate',
      text: 'The firm maintains an enterprise ICT risk policy aligned with regulatory requirements and BCBS 239. The policy mandates a centralized risk register, quarterly resilience tests on critical applications, vendor due diligence for material third parties, and a 24-hour incident notification standard for major events.',
    },
    {
      name: 'Engagement SOP',
      tag: 'project',
      text: 'Project teams document ICT risks in the engagement risk register. Resilience tests are scoped at engagement kickoff and refreshed at major milestones. Material vendors are routed through procurement-led due diligence. Incidents above severity 2 trigger the engagement notification protocol within one business day.',
    },
    {
      name: 'Practitioner action',
      tag: 'individual',
      text: 'I update the project risk register weekly. Before launch we run a chaos drill on the critical path. I email the partner if a vendor change is material. If something breaks badly I tell the partner the same day.',
    },
  ],
  aiact: [
    {
      name: 'EU AI Act Article 10',
      tag: 'regulation',
      text: 'High-risk AI system providers shall implement appropriate data and data governance practices, including training, validation, and testing data sets that are relevant, representative, free of errors and complete, with documented examination of biases and the data sourcing and preparation pipeline.',
    },
    {
      name: 'Firm policy',
      tag: 'corporate',
      text: 'AI development at the firm follows the responsible AI policy: documented data lineage for all production models, bias evaluation for any consumer-facing model, and quarterly review of training data refresh procedures by the model risk committee.',
    },
    {
      name: 'Engagement SOP',
      tag: 'project',
      text: 'For AI engagements, document training data sources in the model card. Run the firm bias evaluator on any model that touches a regulated decision. Capture data lineage in dbt manifest tests and update the model card on every promote.',
    },
    {
      name: 'Practitioner action',
      tag: 'individual',
      text: 'I write the model card before promote. The bias evaluator runs in CI. If the lineage tests fail, the deploy is blocked.',
    },
  ],
  dama: [
    {
      name: 'DAMA-DMBOK',
      tag: 'reference',
      text: 'Data governance is the exercise of authority and control over the management of data assets. It encompasses planning, oversight, and control over data management and the use of data and data-related resources. Effective data governance includes formal roles, policies, and decision rights aligned with strategic data objectives.',
    },
    {
      name: 'Firm policy',
      tag: 'corporate',
      text: 'The firm operates a federated data governance model with a chief data officer, a governance council, and a stewardship network. Policies define ownership, quality standards, access controls, and lifecycle obligations for enterprise data assets.',
    },
    {
      name: 'Engagement SOP',
      tag: 'project',
      text: 'Each engagement nominates a data lead responsible for catalog completeness, lineage capture, and quality monitoring on shared data products. Quarterly governance reviews cover ownership, access, and quality metrics for the engagement.',
    },
    {
      name: 'Practitioner action',
      tag: 'individual',
      text: 'I tag every dataset I create. I tell the team lead when a downstream consumer breaks. I keep a notebook of who uses what; nobody asks for it but I have it.',
    },
  ],
};

let cascadeLayers = JSON.parse(JSON.stringify(CASCADE_PRESETS.dora));

const STOPWORDS = new Set([
  'the','and','of','for','to','in','on','a','an','is','are','be','by','with','as','at','from','that','this','it','or','if','its',
  'we','i','our','their','they','have','has','was','were','will','shall','must','can','these','those',
]);

function tokenize(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter((w) => w && !STOPWORDS.has(w) && w.length > 2);
}

function tfVector(tokens) {
  const counts = {};
  for (const t of tokens) {
    counts[t] = (counts[t] || 0) + 1;
  }
  return counts;
}

function cosineSim(va, vb) {
  let dot = 0;
  let na = 0;
  let nb = 0;
  for (const k of Object.keys(va)) {
    if (vb[k]) dot += va[k] * vb[k];
    na += va[k] * va[k];
  }
  for (const k of Object.keys(vb)) {
    nb += vb[k] * vb[k];
  }
  if (na === 0 || nb === 0) return 0;
  return dot / (Math.sqrt(na) * Math.sqrt(nb));
}

function computeDrifts() {
  const vectors = cascadeLayers.map((l) => tfVector(tokenize(l.text)));
  const drifts = [];
  for (let i = 0; i < vectors.length - 1; i += 1) {
    const sim = cosineSim(vectors[i], vectors[i + 1]);
    drifts.push(clamp(1 - sim, 0, 1));
  }
  return drifts;
}

function renderCascade() {
  const stack = document.getElementById('cascade-stack');
  if (!stack) return;
  const drifts = computeDrifts();
  let html = '';
  cascadeLayers.forEach((layer, i) => {
    html += `<div class="cascade-layer" data-index="${i}">
      <div class="cascade-tag">
        <span>${layer.tag}</span>
        <span class="cascade-tag-name">${layer.name}</span>
      </div>
      <textarea class="cascade-text" data-index="${i}" rows="4">${escapeHtml(layer.text)}</textarea>
    </div>`;
    if (i < cascadeLayers.length - 1) {
      const d = drifts[i];
      const flag = d > 0.6;
      const colour = d > 0.6 ? 'var(--drift-high)' : d > 0.4 ? 'var(--drift-mid)' : 'var(--drift-low)';
      html += `<div class="cascade-edge">
        <div class="cascade-edge-line">
          <span class="cascade-edge-marker" style="left:${(d * 100).toFixed(1)}%;"></span>
        </div>
        <div class="cascade-edge-readout${flag ? ' is-flag' : ''}">drift ${d.toFixed(2)}${flag ? ' (V002 flag)' : ''}</div>
      </div>`;
    }
  });
  stack.innerHTML = html;

  const total = drifts.reduce((s, d) => s + d, 0);
  document.getElementById('total-drift').textContent = total.toFixed(2);

  // Pulse animation on layers.
  Array.from(stack.querySelectorAll('.cascade-layer')).forEach((el, i) => {
    setTimeout(() => {
      el.classList.add('is-pulse');
      setTimeout(() => el.classList.remove('is-pulse'), 240);
    }, i * 80);
  });

  // Wire textareas to recompute on input.
  stack.querySelectorAll('.cascade-text').forEach((ta) => {
    ta.addEventListener('input', (e) => {
      const i = Number(e.target.getAttribute('data-index'));
      cascadeLayers[i].text = e.target.value;
      // Recompute drifts only (don't full re-render to preserve focus).
      const newDrifts = computeDrifts();
      Array.from(stack.querySelectorAll('.cascade-edge')).forEach((edge, j) => {
        const d = newDrifts[j];
        const marker = edge.querySelector('.cascade-edge-marker');
        const readout = edge.querySelector('.cascade-edge-readout');
        if (marker) marker.style.left = `${(d * 100).toFixed(1)}%`;
        if (readout) {
          const flag = d > 0.6;
          readout.textContent = `drift ${d.toFixed(2)}${flag ? ' (V002 flag)' : ''}`;
          readout.classList.toggle('is-flag', flag);
        }
      });
      const total2 = newDrifts.reduce((s, d) => s + d, 0);
      document.getElementById('total-drift').textContent = total2.toFixed(2);
    });
  });
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function applyCascadePreset(name) {
  if (!CASCADE_PRESETS[name]) return;
  cascadeLayers = JSON.parse(JSON.stringify(CASCADE_PRESETS[name]));
  activateButton('[data-cascade]', name, 'data-cascade');
  renderCascade();
}

document.querySelectorAll('[data-cascade]').forEach((btn) => {
  btn.addEventListener('click', () => applyCascadePreset(btn.getAttribute('data-cascade')));
});
applyCascadePreset('dora');
