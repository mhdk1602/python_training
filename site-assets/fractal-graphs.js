// Reveal-on-scroll, mirroring the existing studio pages.
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
  document.querySelectorAll(groupSelector).forEach((button) => {
    button.classList.toggle("is-active", button.getAttribute(attr) === value);
  });
}

// ---------------------------------------------------------------------------
// LAB 1 - Visibility Graph
// ---------------------------------------------------------------------------

const N_BARS = 32;

const seriesPresets = {
  periodic: () => Array.from({ length: N_BARS }, (_, i) => 0.5 + 0.4 * Math.sin((i * 2 * Math.PI) / 8)),
  random: () => Array.from({ length: N_BARS }, () => Math.random()),
  trend: () => Array.from({ length: N_BARS }, (_, i) => 0.2 + (i / (N_BARS - 1)) * 0.7 + 0.1 * (Math.random() - 0.5)),
  fbm: () => {
    // Lightweight pseudo-fBm: cumulative sum of Gaussian increments with persistence
    const out = [];
    let v = 0.5;
    for (let i = 0; i < N_BARS; i += 1) {
      v += 0.7 * (Math.random() - 0.5);
      out.push(v);
    }
    const min = Math.min(...out);
    const max = Math.max(...out);
    return out.map((value) => 0.05 + 0.9 * ((value - min) / (max - min || 1)));
  },
};

let series = seriesPresets.periodic();

function visibilityEdges(values) {
  const edges = [];
  const n = values.length;
  for (let a = 0; a < n - 1; a += 1) {
    edges.push([a, a + 1]);
    if (a + 2 >= n) continue;
    let maxSlope = (values[a + 1] - values[a]) / 1;
    for (let b = a + 2; b < n; b += 1) {
      const slope = (values[b] - values[a]) / (b - a);
      if (slope > maxSlope) {
        edges.push([a, b]);
        maxSlope = slope;
      }
    }
  }
  return edges;
}

function regimeGuess(degrees) {
  const max = Math.max(...degrees);
  const mean = degrees.reduce((a, b) => a + b, 0) / degrees.length;
  const std = Math.sqrt(
    degrees.reduce((acc, d) => acc + (d - mean) ** 2, 0) / degrees.length
  );
  if (std < 0.7) return "periodic / regular";
  if (max <= mean * 2.2) return "random / exponential tail";
  return "fractal / scale-free tail";
}

function renderSeries() {
  const svg = document.getElementById("series-canvas");
  if (!svg) return;
  const W = 720;
  const H = 320;
  const padX = 24;
  const padY = 24;
  const usableW = W - 2 * padX;
  const usableH = H - 2 * padY;
  const barW = usableW / series.length;

  let inner = `<rect x="0" y="0" width="${W}" height="${H}" fill="rgba(255,255,255,0.01)"/>`;

  series.forEach((value, i) => {
    const x = padX + i * barW;
    const barH = value * usableH;
    const y = H - padY - barH;
    inner += `<rect class="series-bar" data-index="${i}" x="${x + 1}" y="${y}" width="${Math.max(barW - 2, 2)}" height="${barH}" fill="#efce8a" rx="2"></rect>`;
  });
  svg.innerHTML = inner;

  // Drag bars to edit the series.
  let dragging = null;
  svg.addEventListener("mousedown", (event) => {
    const target = event.target;
    if (target && target.classList && target.classList.contains("series-bar")) {
      dragging = Number(target.getAttribute("data-index"));
    }
  });
  svg.addEventListener("mousemove", (event) => {
    if (dragging === null) return;
    const rect = svg.getBoundingClientRect();
    const yPx = event.clientY - rect.top;
    const value = Math.max(0.05, Math.min(0.95, 1 - (yPx - padY * (rect.height / H)) / (usableH * (rect.height / H))));
    series[dragging] = value;
    renderSeries();
    renderVisibilityGraph();
  });
  svg.addEventListener("mouseup", () => { dragging = null; });
  svg.addEventListener("mouseleave", () => { dragging = null; });
}

function renderVisibilityGraph() {
  const svg = document.getElementById("vg-canvas");
  if (!svg) return;
  const W = 720;
  const H = 320;
  const cx = W / 2;
  const cy = H / 2;
  const radius = Math.min(W, H) / 2 - 28;

  const edges = visibilityEdges(series);
  const positions = series.map((_, i) => {
    const theta = (i / series.length) * Math.PI * 2 - Math.PI / 2;
    return { x: cx + radius * Math.cos(theta), y: cy + radius * Math.sin(theta) };
  });

  let edgeLines = "";
  for (const [a, b] of edges) {
    const pa = positions[a];
    const pb = positions[b];
    edgeLines += `<line x1="${pa.x}" y1="${pa.y}" x2="${pb.x}" y2="${pb.y}" stroke="rgba(239,206,138,0.32)" stroke-width="0.8"/>`;
  }

  const degrees = series.map(() => 0);
  for (const [a, b] of edges) {
    degrees[a] += 1;
    degrees[b] += 1;
  }
  const maxDeg = Math.max(...degrees);

  let nodes = "";
  positions.forEach((pos, i) => {
    const r = 4 + 12 * (degrees[i] / Math.max(maxDeg, 1));
    nodes += `<circle cx="${pos.x}" cy="${pos.y}" r="${r}" fill="#d17a00" stroke="#fbe6b3" stroke-width="0.8"/>`;
  });

  svg.innerHTML = `<rect x="0" y="0" width="${W}" height="${H}" fill="rgba(255,255,255,0.01)"/>${edgeLines}${nodes}`;

  document.getElementById("vg-stat-n").textContent = series.length;
  document.getElementById("vg-stat-edges").textContent = edges.length;
  document.getElementById("vg-stat-mean").textContent = (degrees.reduce((a, b) => a + b, 0) / degrees.length).toFixed(2);
  document.getElementById("vg-stat-max").textContent = maxDeg;
  document.getElementById("vg-stat-regime").textContent = regimeGuess(degrees);
  document.getElementById("vg-status").textContent = `${edges.length} edges`;
}

document.querySelectorAll(".preset-button[data-series]").forEach((button) => {
  button.addEventListener("click", () => {
    activateButton(".preset-button[data-series]", button.dataset.series, "data-series");
    series = seriesPresets[button.dataset.series]();
    renderSeries();
    renderVisibilityGraph();
  });
});

// ---------------------------------------------------------------------------
// LAB 2 - Box Covering on Graphs
// ---------------------------------------------------------------------------

function buildAdjacency(nodeList, edges) {
  const adj = {};
  nodeList.forEach((id) => { adj[id] = new Set(); });
  edges.forEach(([u, v]) => {
    adj[u].add(v);
    adj[v].add(u);
  });
  return adj;
}

function bfsDistances(adj, source) {
  const dist = { [source]: 0 };
  const queue = [source];
  while (queue.length) {
    const u = queue.shift();
    for (const v of adj[u]) {
      if (dist[v] === undefined) {
        dist[v] = dist[u] + 1;
        queue.push(v);
      }
    }
  }
  return dist;
}

function allPairsDist(nodes, adj) {
  const out = {};
  for (const node of nodes) out[node] = bfsDistances(adj, node);
  return out;
}

function greedyColor(nodes, conflictAdj) {
  // largest_first ordering by conflict-degree
  const order = nodes
    .map((n) => ({ n, deg: (conflictAdj[n] || new Set()).size }))
    .sort((a, b) => b.deg - a.deg)
    .map((x) => x.n);
  const color = {};
  for (const node of order) {
    const used = new Set();
    for (const neighbor of conflictAdj[node] || []) {
      if (color[neighbor] !== undefined) used.add(color[neighbor]);
    }
    let c = 0;
    while (used.has(c)) c += 1;
    color[node] = c;
  }
  return color;
}

function boxCover(nodes, adj, lb) {
  const dist = allPairsDist(nodes, adj);
  const conflict = {};
  for (const u of nodes) conflict[u] = new Set();
  for (let i = 0; i < nodes.length; i += 1) {
    for (let j = i + 1; j < nodes.length; j += 1) {
      const u = nodes[i];
      const v = nodes[j];
      const d = dist[u][v];
      if (d === undefined || d >= lb) {
        conflict[u].add(v);
        conflict[v].add(u);
      }
    }
  }
  return greedyColor(nodes, conflict);
}

function buildSierpinski(iterations) {
  const nodes = new Set([0, 1, 2]);
  const edges = new Set(["0-1", "1-2", "0-2"]);
  let triangles = [[0, 1, 2]];
  let nextId = 3;
  for (let it = 0; it < iterations; it += 1) {
    const newTriangles = [];
    for (const [u, v, w] of triangles) {
      const muv = nextId++;
      const mvw = nextId++;
      const muw = nextId++;
      [muv, mvw, muw].forEach((n) => nodes.add(n));
      [`${u}-${v}`, `${v}-${w}`, `${u}-${w}`].forEach((e) => {
        const [a, b] = e.split("-").map(Number).sort((x, y) => x - y);
        edges.delete(`${a}-${b}`);
      });
      const addEdge = (a, b) => {
        const [x, y] = [a, b].sort((p, q) => p - q);
        edges.add(`${x}-${y}`);
      };
      addEdge(u, muv); addEdge(muv, v);
      addEdge(v, mvw); addEdge(mvw, w);
      addEdge(u, muw); addEdge(muw, w);
      addEdge(muv, mvw); addEdge(mvw, muw); addEdge(muv, muw);
      newTriangles.push([u, muv, muw], [muv, v, mvw], [muw, mvw, w], [muv, mvw, muw]);
    }
    triangles = newTriangles;
  }
  const nodeArr = Array.from(nodes);
  const edgeArr = Array.from(edges).map((e) => e.split("-").map(Number));
  return { nodes: nodeArr, edges: edgeArr };
}

function buildHsf() {
  // Simplified hierarchical scale-free: a 5-node module replicated 4 times
  // and connected to a central hub.
  const nodes = new Set();
  const edges = new Set();
  const addEdge = (u, v) => {
    const [a, b] = [u, v].sort();
    edges.add(`${a}-${b}`);
    nodes.add(u);
    nodes.add(v);
  };
  // central hub
  const hub = "h";
  for (let copy = 0; copy < 4; copy += 1) {
    const peripheral = [`p${copy}_1`, `p${copy}_2`, `p${copy}_3`, `p${copy}_4`];
    const center = `c${copy}`;
    peripheral.forEach((p) => addEdge(center, p));
    for (let i = 0; i < peripheral.length; i += 1) {
      for (let j = i + 1; j < peripheral.length; j += 1) {
        addEdge(peripheral[i], peripheral[j]);
      }
    }
    peripheral.forEach((p) => addEdge(p, hub));
  }
  return {
    nodes: Array.from(nodes),
    edges: Array.from(edges).map((e) => e.split("-")),
  };
}

function buildKarate() {
  // Zachary's Karate club edge list (canonical 78 edges, 34 nodes)
  const edges = [[1,2],[1,3],[1,4],[1,5],[1,6],[1,7],[1,8],[1,9],[1,11],[1,12],[1,13],[1,14],[1,18],[1,20],[1,22],[1,32],[2,3],[2,4],[2,8],[2,14],[2,18],[2,20],[2,22],[2,31],[3,4],[3,8],[3,9],[3,10],[3,14],[3,28],[3,29],[3,33],[4,8],[4,13],[4,14],[5,7],[5,11],[6,7],[6,11],[6,17],[7,17],[9,31],[9,33],[9,34],[10,34],[14,34],[15,33],[15,34],[16,33],[16,34],[19,33],[19,34],[20,34],[21,33],[21,34],[23,33],[23,34],[24,26],[24,28],[24,30],[24,33],[24,34],[25,26],[25,28],[25,32],[26,32],[27,30],[27,34],[28,34],[29,32],[29,34],[30,33],[30,34],[31,33],[31,34],[32,33],[32,34],[33,34]];
  const nodes = new Set();
  edges.forEach(([u, v]) => { nodes.add(u); nodes.add(v); });
  return { nodes: Array.from(nodes), edges };
}

function buildER(n, p, seed) {
  // Deterministic-ish via seeded LCG
  let state = seed;
  const rand = () => {
    state = (state * 1664525 + 1013904223) % 2 ** 32;
    return state / 2 ** 32;
  };
  const edges = [];
  const nodes = Array.from({ length: n }, (_, i) => i);
  for (let i = 0; i < n; i += 1) {
    for (let j = i + 1; j < n; j += 1) {
      if (rand() < p) edges.push([i, j]);
    }
  }
  return { nodes, edges };
}

const networks = {
  sierpinski: buildSierpinski(2),
  hsf: buildHsf(),
  karate: buildKarate(),
  er: buildER(40, 0.15, 7),
};

let bcState = { network: "sierpinski", lb: 2 };

function drawBoxCover() {
  const svg = document.getElementById("bc-canvas");
  const fitSvg = document.getElementById("bc-fit");
  if (!svg || !fitSvg) return;

  const W = 720;
  const H = 420;
  const { nodes, edges } = networks[bcState.network];

  const adj = buildAdjacency(nodes.map(String), edges.map(([u, v]) => [String(u), String(v)]));
  const nodeStrs = nodes.map(String);

  // Coloring at the active box size.
  const coloring = boxCover(nodeStrs, adj, bcState.lb);
  const palette = ["#efce8a", "#9ab0a3", "#d17a00", "#c46b6b", "#6e8db4", "#b59ad1", "#f0b67f", "#5fa8a3", "#9d7e57", "#6f8a72"];
  const colorOf = (id) => palette[coloring[id] % palette.length];

  // Layout via simple force-style (deterministic spring iterations).
  const positions = {};
  const N = nodeStrs.length;
  nodeStrs.forEach((id, i) => {
    const theta = (i / N) * 2 * Math.PI;
    const r = 150 + 30 * Math.sin(i * 1.3);
    positions[id] = { x: W / 2 + r * Math.cos(theta), y: H / 2 + r * Math.sin(theta) };
  });
  // a few light spring iterations to spread nodes
  for (let k = 0; k < 60; k += 1) {
    const fx = {};
    const fy = {};
    nodeStrs.forEach((id) => { fx[id] = 0; fy[id] = 0; });
    for (let i = 0; i < nodeStrs.length; i += 1) {
      for (let j = i + 1; j < nodeStrs.length; j += 1) {
        const a = nodeStrs[i];
        const b = nodeStrs[j];
        const dx = positions[a].x - positions[b].x;
        const dy = positions[a].y - positions[b].y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 0.1;
        const f = 1200 / (dist * dist);
        fx[a] += (dx / dist) * f;
        fy[a] += (dy / dist) * f;
        fx[b] -= (dx / dist) * f;
        fy[b] -= (dy / dist) * f;
      }
    }
    for (const [u, v] of edges) {
      const a = String(u);
      const b = String(v);
      const dx = positions[a].x - positions[b].x;
      const dy = positions[a].y - positions[b].y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 0.1;
      const f = (dist - 80) * 0.05;
      fx[a] -= (dx / dist) * f;
      fy[a] -= (dy / dist) * f;
      fx[b] += (dx / dist) * f;
      fy[b] += (dy / dist) * f;
    }
    nodeStrs.forEach((id) => {
      positions[id].x = Math.max(30, Math.min(W - 30, positions[id].x + fx[id] * 0.04));
      positions[id].y = Math.max(30, Math.min(H - 30, positions[id].y + fy[id] * 0.04));
    });
  }

  let edgeLines = "";
  for (const [u, v] of edges) {
    const a = String(u);
    const b = String(v);
    const same = coloring[a] === coloring[b];
    edgeLines += `<line x1="${positions[a].x}" y1="${positions[a].y}" x2="${positions[b].x}" y2="${positions[b].y}" stroke="${same ? colorOf(a) : 'rgba(255,255,255,0.12)'}" stroke-width="${same ? 1.6 : 0.8}"/>`;
  }

  let circles = "";
  for (const id of nodeStrs) {
    circles += `<circle cx="${positions[id].x}" cy="${positions[id].y}" r="6" fill="${colorOf(id)}" stroke="#173326" stroke-width="0.6"/>`;
  }

  svg.innerHTML = `<rect x="0" y="0" width="${W}" height="${H}" fill="rgba(255,255,255,0.01)"/>${edgeLines}${circles}`;

  // Compute counts across box sizes for the fit.
  const lValues = [1, 2, 3, 4, 5, 6];
  const counts = lValues.map((l) => {
    const c = boxCover(nodeStrs, adj, l);
    return new Set(Object.values(c)).size;
  });

  const xs = lValues.map((l) => Math.log(1 / l));
  const ys = counts.map((c) => Math.log(c));
  const meanX = xs.reduce((a, b) => a + b, 0) / xs.length;
  const meanY = ys.reduce((a, b) => a + b, 0) / ys.length;
  const num = xs.reduce((acc, x, i) => acc + (x - meanX) * (ys[i] - meanY), 0);
  const den = xs.reduce((acc, x) => acc + (x - meanX) ** 2, 0);
  const slope = den === 0 ? 0 : num / den;
  const intercept = meanY - slope * meanX;

  const padX = 60;
  const padY = 40;
  const FW = 720;
  const FH = 420;
  const xMin = Math.min(...xs);
  const xMax = Math.max(...xs);
  const yMin = Math.min(...ys);
  const yMax = Math.max(...ys);
  const sx = (x) => padX + ((x - xMin) / (xMax - xMin || 1)) * (FW - 2 * padX);
  const sy = (y) => FH - padY - ((y - yMin) / (yMax - yMin || 1)) * (FH - 2 * padY);

  let fitSvgInner = `<rect x="0" y="0" width="${FW}" height="${FH}" fill="rgba(255,255,255,0.01)"/>`;
  fitSvgInner += `<line x1="${padX}" y1="${FH - padY}" x2="${FW - padX}" y2="${FH - padY}" stroke="rgba(255,255,255,0.18)"/>`;
  fitSvgInner += `<line x1="${padX}" y1="${padY}" x2="${padX}" y2="${FH - padY}" stroke="rgba(255,255,255,0.18)"/>`;
  fitSvgInner += `<text x="${padX}" y="${FH - 14}" fill="rgba(255,255,255,0.55)" font-size="12">log(1 / l)</text>`;
  fitSvgInner += `<text x="6" y="${padY + 4}" fill="rgba(255,255,255,0.55)" font-size="12">log(N_B)</text>`;
  // line of best fit
  fitSvgInner += `<line x1="${sx(xMin)}" y1="${sy(slope * xMin + intercept)}" x2="${sx(xMax)}" y2="${sy(slope * xMax + intercept)}" stroke="#d17a00" stroke-width="1.6"/>`;
  // points
  xs.forEach((x, i) => {
    fitSvgInner += `<circle cx="${sx(x)}" cy="${sy(ys[i])}" r="6" fill="#efce8a" stroke="#173326"/>`;
    fitSvgInner += `<text x="${sx(x) + 8}" y="${sy(ys[i]) + 4}" fill="rgba(255,255,255,0.55)" font-size="11">l=${lValues[i]}, N_B=${counts[i]}</text>`;
  });
  fitSvg.innerHTML = fitSvgInner;

  // Stability: how much does slope move if we trim ends?
  const slopeMid = (() => {
    const xMid = xs.slice(1, -1);
    const yMid = ys.slice(1, -1);
    if (xMid.length < 2) return slope;
    const mx = xMid.reduce((a, b) => a + b, 0) / xMid.length;
    const my = yMid.reduce((a, b) => a + b, 0) / yMid.length;
    const n = xMid.reduce((acc, x, i) => acc + (x - mx) * (yMid[i] - my), 0);
    const d = xMid.reduce((acc, x) => acc + (x - mx) ** 2, 0);
    return d === 0 ? slope : n / d;
  })();
  const stab = Math.abs(slope - slopeMid);
  const stabLabel = stab < 0.15 ? "stable" : stab < 0.35 ? "moderate" : "unstable";

  document.getElementById("bc-l-value").textContent = bcState.lb;
  document.getElementById("bc-stat-n").textContent = nodeStrs.length;
  document.getElementById("bc-stat-e").textContent = edges.length;
  document.getElementById("bc-stat-boxes").textContent = new Set(Object.values(coloring)).size;
  document.getElementById("bc-stat-d").textContent = slope.toFixed(2);
  document.getElementById("bc-stat-stab").textContent = stabLabel;
  document.getElementById("bc-status").textContent = `${new Set(Object.values(coloring)).size} boxes at l_B = ${bcState.lb}`;
  document.getElementById("bc-fit-status").textContent = `slope shift on trim: ${stab.toFixed(2)}`;
}

document.querySelectorAll(".preset-button[data-network]").forEach((button) => {
  button.addEventListener("click", () => {
    activateButton(".preset-button[data-network]", button.dataset.network, "data-network");
    bcState.network = button.dataset.network;
    drawBoxCover();
  });
});

document.getElementById("bc-l-range")?.addEventListener("input", (event) => {
  bcState.lb = Number(event.target.value);
  drawBoxCover();
});

// ---------------------------------------------------------------------------
// LAB 3 - Lineage Risk
// ---------------------------------------------------------------------------

function buildLineage() {
  const sources = ["src_0", "src_1", "src_2", "src_3"];
  const staging = ["stg_0", "stg_1", "stg_2", "stg_3", "stg_4", "stg_5"];
  const marts = ["mart_0", "mart_1", "mart_2"];
  const exposures = ["exp_0", "exp_1"];
  const adjOut = {};
  const layers = { source: sources, staging, mart: marts, exposure: exposures };
  Object.values(layers).flat().forEach((n) => { adjOut[n] = new Set(); });

  const wire = (parent, child) => {
    adjOut[parent].add(child);
  };

  // Deterministic edges so labs are reproducible.
  wire("src_0", "stg_0"); wire("src_0", "stg_1");
  wire("src_1", "stg_1"); wire("src_1", "stg_2");
  wire("src_2", "stg_2"); wire("src_2", "stg_3");
  wire("src_3", "stg_4"); wire("src_3", "stg_5");

  wire("stg_0", "mart_0"); wire("stg_1", "mart_0"); wire("stg_2", "mart_0");
  wire("stg_2", "mart_1"); wire("stg_3", "mart_1");
  wire("stg_4", "mart_2"); wire("stg_5", "mart_2");

  wire("mart_0", "exp_0");
  wire("mart_1", "exp_0"); wire("mart_1", "exp_1");
  wire("mart_2", "exp_1");

  return { layers, adjOut };
}

const lineage = buildLineage();

function descendants(node) {
  const result = new Set();
  const queue = [node];
  while (queue.length) {
    const u = queue.shift();
    for (const v of lineage.adjOut[u] || []) {
      if (!result.has(v)) {
        result.add(v);
        queue.push(v);
      }
    }
  }
  return result;
}

function blastScore(node) {
  const desc = descendants(node);
  if (desc.size === 0) return { touched: 0, boxes: 0, score: 0 };
  // Build undirected subgraph
  const subset = new Set([node, ...desc]);
  const adjU = {};
  subset.forEach((n) => { adjU[n] = new Set(); });
  for (const u of subset) {
    for (const v of lineage.adjOut[u] || []) {
      if (subset.has(v)) {
        adjU[u].add(v);
        adjU[v].add(u);
      }
    }
  }
  const nodeArr = Array.from(subset);
  const coloring = boxCover(nodeArr, adjU, 2);
  const boxes = new Set(Object.values(coloring)).size;
  return { touched: desc.size, boxes, score: boxes / Math.max(desc.size, 1) };
}

function priorityList() {
  const all = Object.values(lineage.layers).flat();
  const rows = all.map((n) => {
    const r = blastScore(n);
    return { node: n, ...r };
  });
  return rows.sort((a, b) => b.boxes - a.boxes || b.touched - a.touched).slice(0, 5);
}

let activeDefect = null;

function renderLineage() {
  const svg = document.getElementById("lineage-canvas");
  if (!svg) return;
  const W = 720;
  const H = 480;
  const layerOrder = ["source", "staging", "mart", "exposure"];
  const layerX = { source: 80, staging: 280, mart: 480, exposure: 640 };
  const layerColor = { source: "#efce8a", staging: "#9ab0a3", mart: "#d17a00", exposure: "#173326" };

  const positions = {};
  layerOrder.forEach((layer) => {
    const nodes = lineage.layers[layer];
    const stride = (H - 80) / Math.max(nodes.length, 1);
    nodes.forEach((n, i) => {
      positions[n] = { x: layerX[layer], y: 40 + i * stride + stride / 2 };
    });
  });

  const touched = activeDefect ? new Set([activeDefect, ...descendants(activeDefect)]) : new Set();

  let edgeStr = "";
  for (const u of Object.keys(lineage.adjOut)) {
    for (const v of lineage.adjOut[u] || []) {
      const lit = touched.has(u) && touched.has(v);
      edgeStr += `<line x1="${positions[u].x}" y1="${positions[u].y}" x2="${positions[v].x}" y2="${positions[v].y}" stroke="${lit ? '#d17a00' : 'rgba(255,255,255,0.18)'}" stroke-width="${lit ? 1.6 : 0.8}"/>`;
    }
  }

  let nodeStr = "";
  for (const layer of layerOrder) {
    for (const n of lineage.layers[layer]) {
      const lit = touched.has(n);
      const fill = lit ? "#d17a00" : layerColor[layer];
      const stroke = activeDefect === n ? "#fbe6b3" : "#173326";
      nodeStr += `<g class="lineage-node" data-node="${n}">`;
      nodeStr += `<circle cx="${positions[n].x}" cy="${positions[n].y}" r="${lit ? 14 : 10}" fill="${fill}" stroke="${stroke}" stroke-width="${activeDefect === n ? 2 : 0.8}"/>`;
      nodeStr += `<text x="${positions[n].x + 16}" y="${positions[n].y + 4}" fill="rgba(255,255,255,0.78)" font-size="11">${n}</text>`;
      nodeStr += `</g>`;
    }
  }

  // Layer labels
  let labelStr = "";
  layerOrder.forEach((layer) => {
    labelStr += `<text x="${layerX[layer]}" y="22" fill="rgba(255,255,255,0.55)" font-size="12" text-anchor="middle">${layer}</text>`;
  });

  svg.innerHTML = `<rect x="0" y="0" width="${W}" height="${H}" fill="rgba(255,255,255,0.01)"/>${labelStr}${edgeStr}${nodeStr}`;

  // Node click
  svg.querySelectorAll(".lineage-node").forEach((g) => {
    g.style.cursor = "pointer";
    g.addEventListener("click", (event) => {
      activeDefect = event.currentTarget.getAttribute("data-node");
      renderLineage();
      updateLineageReadout();
    });
  });

  document.getElementById("lineage-status").textContent = activeDefect ? `defect at ${activeDefect}` : "click a node to inject a defect";
}

function updateLineageReadout() {
  const def = document.getElementById("lineage-defect");
  const touched = document.getElementById("lineage-stat-touched");
  const boxes = document.getElementById("lineage-stat-boxes");
  const blast = document.getElementById("lineage-stat-blast");
  const list = document.getElementById("lineage-priority");

  if (!activeDefect) {
    def.textContent = "none";
    touched.textContent = "--";
    boxes.textContent = "--";
    blast.textContent = "--";
    list.innerHTML = priorityList().map((row, i) => `<li>${row.node}<span>boxes ${row.boxes}, touched ${row.touched}</span></li>`).join("");
    return;
  }
  const r = blastScore(activeDefect);
  def.textContent = activeDefect;
  touched.textContent = r.touched;
  boxes.textContent = r.boxes;
  blast.textContent = r.score.toFixed(2);
  list.innerHTML = priorityList().map((row) => `<li>${row.node}<span>boxes ${row.boxes}, touched ${row.touched}</span></li>`).join("");
}

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------

renderSeries();
renderVisibilityGraph();
drawBoxCover();
renderLineage();
updateLineageReadout();
