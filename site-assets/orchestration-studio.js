"use strict";

const SVGNS = "http://www.w3.org/2000/svg";
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const STATE_FILL = {
  idle: "#2b3450",
  running: "#ffc46b",
  done: "#22c97a",
  failed: "#ef6a85",
  skipped: "#49506e",
};
const DARK_TEXT = new Set(["running", "done", "failed"]);

const sleep = (ms) => new Promise((r) => setTimeout(r, reduceMotion ? 0 : ms));

function el(name, attrs) {
  const node = document.createElementNS(SVGNS, name);
  for (const k in attrs) node.setAttribute(k, attrs[k]);
  return node;
}

/* ---------- the trading-platform asset graph (Labs 1 and 3) ---------- */

const GRAPH_NODES = [
  { id: "market_data", label: "market_data", x: 80, y: 64, deps: [] },
  { id: "price_history", label: "price_history", x: 270, y: 64, deps: ["market_data"] },
  { id: "positions", label: "positions", x: 460, y: 64, deps: ["price_history"] },
  { id: "daily_pnl", label: "daily_pnl", x: 650, y: 64, deps: ["positions"] },
  { id: "risk_flags", label: "risk_flags", x: 460, y: 210, deps: ["positions"] },
  { id: "news_feed", label: "news_feed", x: 270, y: 356, deps: [] },
  { id: "warren_context", label: "warren_context", x: 650, y: 356, deps: ["daily_pnl", "news_feed"] },
];

const NODE_W = 132;
const NODE_H = 44;

function nodeById(id) {
  return GRAPH_NODES.find((n) => n.id === id);
}

function topoOrder(nodes) {
  const indeg = {};
  const down = {};
  nodes.forEach((n) => { indeg[n.id] = 0; down[n.id] = []; });
  nodes.forEach((n) => n.deps.forEach((d) => { indeg[n.id] += 1; down[d].push(n.id); }));
  const queue = nodes.filter((n) => indeg[n.id] === 0).map((n) => n.id).sort();
  const order = [];
  while (queue.length) {
    const id = queue.shift();
    order.push(id);
    down[id].sort().forEach((m) => { indeg[m] -= 1; if (indeg[m] === 0) queue.push(m); });
  }
  return order;
}

function levelsOf(nodes) {
  const level = {};
  topoOrder(nodes).forEach((id) => {
    const deps = nodeById(id).deps;
    level[id] = deps.length ? 1 + Math.max(...deps.map((d) => level[d])) : 0;
  });
  return level;
}

function descendants(id) {
  const down = {};
  GRAPH_NODES.forEach((n) => { down[n.id] = []; });
  GRAPH_NODES.forEach((n) => n.deps.forEach((d) => down[d].push(n.id)));
  const seen = new Set();
  const stack = [...down[id]];
  while (stack.length) {
    const n = stack.pop();
    if (seen.has(n)) continue;
    seen.add(n);
    down[n].forEach((m) => stack.push(m));
  }
  return seen;
}

function renderGraph(svg, { onNodeClick } = {}) {
  svg.innerHTML = "";
  const defs = el("defs", {});
  const marker = el("marker", {
    id: "arrow", viewBox: "0 0 10 10", refX: "9", refY: "5",
    markerWidth: "7", markerHeight: "7", orient: "auto-start-reverse",
  });
  marker.appendChild(el("path", { d: "M0 0 L10 5 L0 10 z", fill: "#7c5cff" }));
  defs.appendChild(marker);
  svg.appendChild(defs);

  const edgeEls = {};
  GRAPH_NODES.forEach((n) => {
    n.deps.forEach((d) => {
      const a = nodeById(d);
      const line = el("line", {
        x1: a.x, y1: a.y, x2: n.x, y2: n.y,
        class: "edge", "marker-end": "url(#arrow)",
      });
      svg.appendChild(line);
      edgeEls[d + "->" + n.id] = line;
    });
  });

  const nodeEls = {};
  GRAPH_NODES.forEach((n) => {
    const g = el("g", { style: onNodeClick ? "cursor:pointer" : "" });
    const rect = el("rect", {
      x: n.x - NODE_W / 2, y: n.y - NODE_H / 2, width: NODE_W, height: NODE_H,
      rx: 11, class: "node-box", fill: STATE_FILL.idle,
      stroke: "rgba(255,255,255,0.18)", "stroke-width": "1.5",
    });
    const text = el("text", {
      x: n.x, y: n.y + 4, "text-anchor": "middle", class: "node-label",
    });
    text.textContent = n.label;
    g.appendChild(rect);
    g.appendChild(text);
    if (onNodeClick) g.addEventListener("click", () => onNodeClick(n.id));
    svg.appendChild(g);
    nodeEls[n.id] = { rect, text };
  });

  function setState(id, state) {
    const e = nodeEls[id];
    e.rect.setAttribute("fill", STATE_FILL[state]);
    e.text.setAttribute("fill", DARK_TEXT.has(state) ? "#04060d" : "#e9edfb");
    e.rect.setAttribute("opacity", state === "skipped" ? "0.6" : "1");
  }

  function setEdge(from, to, cls) {
    const e = edgeEls[from + "->" + to];
    if (e) e.setAttribute("class", "edge" + (cls ? " " + cls : ""));
  }

  return { nodeEls, edgeEls, setState, setEdge };
}

/* ---------- Lab 1: materializer ---------- */

function initMaterializer() {
  const svg = document.getElementById("mat-canvas");
  if (!svg) return;
  const statusEl = document.getElementById("mat-status");
  const doneEl = document.getElementById("mat-done");
  const currentEl = document.getElementById("mat-current");
  const speed = document.getElementById("mat-speed");
  const speedReadout = document.getElementById("mat-speed-readout");
  const runBtn = document.getElementById("mat-run");
  const resetBtn = document.getElementById("mat-reset");

  let view = renderGraph(svg);
  let token = 0;
  const total = GRAPH_NODES.length;
  const levels = levelsOf(GRAPH_NODES);

  function reset() {
    token += 1;
    view = renderGraph(svg);
    GRAPH_NODES.forEach((n) => view.setState(n.id, "idle"));
    doneEl.textContent = "0 / " + total;
    currentEl.textContent = "--";
    statusEl.textContent = "ready";
  }

  async function run() {
    const my = ++token;
    GRAPH_NODES.forEach((n) => view.setState(n.id, "idle"));
    let built = 0;
    const maxLevel = Math.max(...Object.values(levels));
    statusEl.textContent = "running";
    for (let L = 0; L <= maxLevel; L += 1) {
      if (my !== token) return;
      const group = GRAPH_NODES.filter((n) => levels[n.id] === L);
      currentEl.textContent = group.map((n) => n.label).join(", ");
      group.forEach((n) => {
        view.setState(n.id, "running");
        n.deps.forEach((d) => view.setEdge(d, n.id, "is-active"));
      });
      await sleep(Number(speed.value) * 0.7);
      if (my !== token) return;
      group.forEach((n) => {
        view.setState(n.id, "done");
        built += 1;
      });
      doneEl.textContent = built + " / " + total;
      await sleep(Number(speed.value) * 0.4);
    }
    if (my !== token) return;
    currentEl.textContent = "done";
    statusEl.textContent = "materialized";
  }

  speed.addEventListener("input", () => { speedReadout.textContent = speed.value; });
  runBtn.addEventListener("click", run);
  resetBtn.addEventListener("click", reset);
  reset();
}

/* ---------- Lab 3: blast radius ---------- */

function initBlast() {
  const svg = document.getElementById("blast-canvas");
  if (!svg) return;
  const statusEl = document.getElementById("blast-status");
  const countEl = document.getElementById("blast-count");
  const listEl = document.getElementById("blast-list");
  const resetBtn = document.getElementById("blast-reset");
  const retryBtn = document.getElementById("blast-retry");

  let view;
  let token = 0;
  let retries = false;

  function healthy() {
    token += 1;
    view = renderGraph(svg, { onNodeClick: fail });
    GRAPH_NODES.forEach((n) => view.setState(n.id, "done"));
    countEl.textContent = "0";
    statusEl.textContent = "click a node";
    listEl.innerHTML = '<li><span>click a node to fail it</span><span class="tag">idle</span></li>';
  }

  async function fail(id) {
    const my = ++token;
    GRAPH_NODES.forEach((n) => view.setState(n.id, "done"));
    GRAPH_NODES.forEach((n) => n.deps.forEach((d) => view.setEdge(d, n.id, "")));

    if (retries) {
      for (let attempt = 1; attempt <= 3; attempt += 1) {
        if (my !== token) return;
        view.setState(id, "running");
        statusEl.textContent = "retry " + attempt + " / 3";
        await sleep(420);
        if (my !== token) return;
        view.setState(id, "idle");
        await sleep(140);
      }
    }
    if (my !== token) return;

    const hit = descendants(id);
    view.setState(id, "failed");
    hit.forEach((d) => {
      view.setState(d, "skipped");
      nodeById(d).deps.forEach((p) => view.setEdge(p, d, "is-dead"));
    });
    nodeById(id).deps.forEach((p) => view.setEdge(p, id, "is-dead"));

    countEl.textContent = String(hit.size);
    statusEl.textContent = hit.size ? "blast radius " + hit.size : "leaf, nothing downstream";

    const rows = ['<li class="is-fail"><span>' + id + "</span><span class=\"tag\">failed</span></li>"];
    [...hit].sort().forEach((d) => {
      rows.push("<li><span>" + d + "</span><span class=\"tag\">skipped</span></li>");
    });
    if (!hit.size) rows.push("<li><span>no downstream descendants</span><span class=\"tag\">leaf</span></li>");
    listEl.innerHTML = rows.join("");
  }

  retryBtn.addEventListener("click", () => {
    retries = !retries;
    retryBtn.textContent = "Retries: " + (retries ? "on" : "off");
    retryBtn.classList.toggle("chip-active", retries);
  });
  resetBtn.addEventListener("click", healthy);
  healthy();
}

/* ---------- Lab 2: backfill grid ---------- */

function initBackfill() {
  const svg = document.getElementById("bf-canvas");
  if (!svg) return;
  const statusEl = document.getElementById("bf-status");
  const startEl = document.getElementById("bf-start");
  const endEl = document.getElementById("bf-end");
  const startReadout = document.getElementById("bf-start-readout");
  const endReadout = document.getElementById("bf-end-readout");
  const newEl = document.getElementById("bf-new");
  const skipEl = document.getElementById("bf-skip");
  const coverageEl = document.getElementById("bf-coverage");
  const runBtn = document.getElementById("bf-run");
  const resetBtn = document.getElementById("bf-reset");

  const ASSETS = ["ingest", "clean", "rollup", "publish"];
  const DAYS = 12;
  const GX = 118, GY = 44, CW = 50, CH = 52, GAP = 5;

  let done = [];
  let cellEls = [];
  let token = 0;

  function initialState() {
    // a ragged frontier: early days fully done, a few holes near the edge
    done = ASSETS.map((_, r) =>
      Array.from({ length: DAYS }, (_, c) => {
        if (c < 3) return true;
        if (c === 3) return r < 2;     // partial day 4
        if (c === 4) return r < 1;     // just ingest on day 5
        return false;
      })
    );
  }

  function draw() {
    svg.innerHTML = "";
    cellEls = ASSETS.map(() => []);
    // day headers
    for (let c = 0; c < DAYS; c += 1) {
      const t = el("text", {
        x: GX + c * (CW + GAP) + CW / 2, y: 28, "text-anchor": "middle",
        fill: "#97a3c4", "font-size": "12", "font-family": "Manrope, sans-serif",
      });
      t.textContent = String(c + 1);
      svg.appendChild(t);
    }
    ASSETS.forEach((asset, r) => {
      const label = el("text", {
        x: 104, y: GY + r * (CH + GAP) + CH / 2 + 4, "text-anchor": "end",
        fill: "#dbe3fb", "font-size": "12.5", "font-weight": "600", "font-family": "Manrope, sans-serif",
      });
      label.textContent = asset;
      svg.appendChild(label);
      for (let c = 0; c < DAYS; c += 1) {
        const rect = el("rect", {
          x: GX + c * (CW + GAP), y: GY + r * (CH + GAP),
          width: CW, height: CH, rx: 7, class: "cell",
          fill: done[r][c] ? "#6d4fe0" : "rgba(255,255,255,0.04)",
          stroke: "rgba(255,255,255,0.08)", "stroke-width": "1",
        });
        svg.appendChild(rect);
        cellEls[r][c] = rect;
      }
    });
    highlightRange();
    updateCoverage();
  }

  function highlightRange() {
    const lo = Math.min(Number(startEl.value), Number(endEl.value)) - 1;
    const hi = Math.max(Number(startEl.value), Number(endEl.value)) - 1;
    for (let r = 0; r < ASSETS.length; r += 1) {
      for (let c = 0; c < DAYS; c += 1) {
        const inRange = c >= lo && c <= hi;
        cellEls[r][c].setAttribute("stroke", inRange ? "#ffc46b" : "rgba(255,255,255,0.08)");
        cellEls[r][c].setAttribute("stroke-width", inRange ? "2" : "1");
      }
    }
  }

  function updateCoverage() {
    let filled = 0;
    done.forEach((row) => row.forEach((v) => { if (v) filled += 1; }));
    const pct = Math.round((filled / (ASSETS.length * DAYS)) * 100);
    coverageEl.textContent = pct + "%";
  }

  async function run() {
    const my = ++token;
    const lo = Math.min(Number(startEl.value), Number(endEl.value)) - 1;
    const hi = Math.max(Number(startEl.value), Number(endEl.value)) - 1;
    let built = 0, skipped = 0;
    statusEl.textContent = "backfilling";
    runBtn.classList.add("chip-active");
    for (let c = lo; c <= hi; c += 1) {
      for (let r = 0; r < ASSETS.length; r += 1) {   // dependency order: top to bottom
        if (my !== token) return;
        if (done[r][c]) { skipped += 1; continue; }
        done[r][c] = true;
        built += 1;
        const cell = cellEls[r][c];
        cell.setAttribute("fill", "#22c97a");          // flash green as it materializes
        newEl.textContent = String(built);
        await sleep(70);
        if (my !== token) return;
        cell.setAttribute("fill", "#6d4fe0");          // settle to materialized
      }
    }
    skipEl.textContent = String(skipped);
    updateCoverage();
    statusEl.textContent = built === 0 ? "no-op: all skipped" : "materialized " + built;
  }

  function reset() {
    token += 1;
    initialState();
    draw();
    newEl.textContent = "0";
    skipEl.textContent = "0";
    statusEl.textContent = "ready";
  }

  startEl.addEventListener("input", () => { startReadout.textContent = startEl.value; highlightRange(); });
  endEl.addEventListener("input", () => { endReadout.textContent = endEl.value; highlightRange(); });
  runBtn.addEventListener("click", run);
  resetBtn.addEventListener("click", reset);
  reset();
}

/* ---------- reveal + boot ---------- */

function initReveal() {
  const obs = new IntersectionObserver(
    (entries) => entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("is-visible"); obs.unobserve(e.target); } }),
    { threshold: 0.1 }
  );
  document.querySelectorAll("[data-reveal]").forEach((n) => obs.observe(n));
}

document.addEventListener("DOMContentLoaded", () => {
  initReveal();
  initMaterializer();
  initBackfill();
  initBlast();
});
