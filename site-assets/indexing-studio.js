// Reveal-on-scroll, mirroring governance-studio.js.
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
    btn.classList.toggle("chip-active", btn.getAttribute(attr) === value);
  });
}

function clamp(v, lo, hi) {
  return Math.min(hi, Math.max(lo, v));
}

function makeSvg(tag, attrs) {
  const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const k in attrs) {
    el.setAttribute(k, attrs[k]);
  }
  return el;
}

function svgPoint(svg, evt) {
  const pt = svg.createSVGPoint();
  pt.x = evt.clientX;
  pt.y = evt.clientY;
  const ctm = svg.getScreenCTM();
  if (!ctm) return { x: 0, y: 0 };
  const p = pt.matrixTransform(ctm.inverse());
  return { x: p.x, y: p.y };
}

// =========================================================================
// Curve generators
// =========================================================================

function hilbertOrderPath(n) {
  const path = [];
  for (let d = 0; d < n * n; d++) {
    let x = 0, y = 0;
    let t = d;
    let s = 1;
    while (s < n) {
      const rx = 1 & Math.floor(t / 2);
      const ry = 1 & (t ^ rx);
      if (ry === 0) {
        if (rx === 1) {
          x = s - 1 - x;
          y = s - 1 - y;
        }
        const tmp = x; x = y; y = tmp;
      }
      x += s * rx;
      y += s * ry;
      t = Math.floor(t / 4);
      s *= 2;
    }
    path.push([x, y]);
  }
  return path;
}

function zorderPath(n) {
  const order = Math.log2(n);
  const path = [];
  for (let d = 0; d < n * n; d++) {
    let x = 0, y = 0;
    for (let i = 0; i < order; i++) {
      x |= ((d >> (2 * i)) & 1) << i;
      y |= ((d >> (2 * i + 1)) & 1) << i;
    }
    path.push([x, y]);
  }
  return path;
}

function rowMajorPath(n) {
  const path = [];
  for (let y = 0; y < n; y++) {
    for (let x = 0; x < n; x++) {
      path.push([x, y]);
    }
  }
  return path;
}

// =========================================================================
// LAB 1 - Curve Trace Animator
// =========================================================================

const CURVE_N = 32;
const CURVE_PAGE_SIZE = 16;
const CURVE_VIEW = { w: 720, h: 540 };
const CURVE_PAD = 32;
const CURVE_SIZE = Math.min(CURVE_VIEW.h - 2 * CURVE_PAD, CURVE_VIEW.w - 2 * CURVE_PAD - 200);
const CURVE_CELL = CURVE_SIZE / CURVE_N;
const CURVE_OX = CURVE_PAD;
const CURVE_OY = (CURVE_VIEW.h - CURVE_SIZE) / 2;

const CURVE_PATHS = {
  hilbert: hilbertOrderPath(CURVE_N),
  zorder: zorderPath(CURVE_N),
  row: rowMajorPath(CURVE_N),
};
const CURVE_COLOURS = {
  hilbert: "#1e40af",
  zorder: "#d97706",
  row: "#a3a3a3",
};

let curveType = "hilbert";
let curveSpeed = 14;
let curvePlaying = true;
let curveStep = CURVE_N * CURVE_N;
let curveTimer = null;
let curveQueryRect = { cx: 16, cy: 16, w: 8, h: 8 };
let curveDrag = null;

const curveCanvas = document.getElementById("curve-canvas");
const curveStatus = document.getElementById("curve-status");
const curvePagesEl = document.getElementById("curve-pages");
const curvePagesRowEl = document.getElementById("curve-pages-row");
const curveSavingsEl = document.getElementById("curve-savings");

function pagesTouched(curveName, query) {
  const path = CURVE_PATHS[curveName];
  let touched = 0;
  const totalPages = path.length / CURVE_PAGE_SIZE;
  for (let p = 0; p < totalPages; p++) {
    let xMin = Infinity, xMax = -Infinity, yMin = Infinity, yMax = -Infinity;
    for (let i = p * CURVE_PAGE_SIZE; i < (p + 1) * CURVE_PAGE_SIZE; i++) {
      const [x, y] = path[i];
      if (x < xMin) xMin = x;
      if (x > xMax) xMax = x;
      if (y < yMin) yMin = y;
      if (y > yMax) yMax = y;
    }
    const qx0 = query.cx - query.w / 2;
    const qx1 = query.cx + query.w / 2;
    const qy0 = query.cy - query.h / 2;
    const qy1 = query.cy + query.h / 2;
    if (!(xMax < qx0 || xMin > qx1 || yMax < qy0 || yMin > qy1)) touched++;
  }
  return { touched, total: totalPages };
}

function renderCurve() {
  curveCanvas.innerHTML = "";
  const path = CURVE_PATHS[curveType];
  const visibleSteps = Math.min(curveStep, path.length);

  // Grid background
  for (let i = 0; i <= CURVE_N; i++) {
    const offset = i * CURVE_CELL;
    curveCanvas.appendChild(makeSvg("line", {
      x1: CURVE_OX, y1: CURVE_OY + offset,
      x2: CURVE_OX + CURVE_SIZE, y2: CURVE_OY + offset,
      stroke: "rgba(255,255,255,0.05)", "stroke-width": 0.5,
    }));
    curveCanvas.appendChild(makeSvg("line", {
      x1: CURVE_OX + offset, y1: CURVE_OY,
      x2: CURVE_OX + offset, y2: CURVE_OY + CURVE_SIZE,
      stroke: "rgba(255,255,255,0.05)", "stroke-width": 0.5,
    }));
  }

  // Draw curve as polyline (cell centers)
  const colour = CURVE_COLOURS[curveType];
  if (visibleSteps >= 2) {
    let pts = "";
    for (let i = 0; i < visibleSteps; i++) {
      const [x, y] = path[i];
      const cx = CURVE_OX + (x + 0.5) * CURVE_CELL;
      const cy = CURVE_OY + (y + 0.5) * CURVE_CELL;
      pts += (i === 0 ? "M" : "L") + cx.toFixed(2) + "," + cy.toFixed(2) + " ";
    }
    curveCanvas.appendChild(makeSvg("path", {
      d: pts, stroke: colour, "stroke-width": 1.4, fill: "none", opacity: 0.85,
    }));
  }

  // Highlight current head
  if (visibleSteps > 0 && visibleSteps < path.length) {
    const [hx, hy] = path[visibleSteps - 1];
    curveCanvas.appendChild(makeSvg("rect", {
      x: CURVE_OX + hx * CURVE_CELL,
      y: CURVE_OY + hy * CURVE_CELL,
      width: CURVE_CELL, height: CURVE_CELL,
      fill: colour, opacity: 0.6,
    }));
  }

  // Query rect
  const qx = CURVE_OX + (curveQueryRect.cx - curveQueryRect.w / 2) * CURVE_CELL;
  const qy = CURVE_OY + (curveQueryRect.cy - curveQueryRect.h / 2) * CURVE_CELL;
  const qw = curveQueryRect.w * CURVE_CELL;
  const qh = curveQueryRect.h * CURVE_CELL;
  const queryGroup = makeSvg("g", { id: "curve-query", style: "cursor: move" });
  queryGroup.appendChild(makeSvg("rect", {
    x: qx, y: qy, width: qw, height: qh,
    fill: "rgba(22,163,74,0.18)", stroke: "#16a34a", "stroke-width": 2,
    rx: 3, "stroke-dasharray": "4 3",
  }));
  queryGroup.appendChild(makeSvg("circle", {
    cx: qx + qw, cy: qy + qh, r: 5, fill: "#16a34a",
  }));
  curveCanvas.appendChild(queryGroup);

  // Legend / labels
  const legendX = CURVE_OX + CURVE_SIZE + 28;
  const legendY = CURVE_OY + 10;
  const legend = makeSvg("g", {});
  const labels = [
    { name: "Hilbert curve", c: "#1e40af" },
    { name: "Z-order curve", c: "#d97706" },
    { name: "Row-major", c: "#a3a3a3" },
    { name: "Query rectangle", c: "#16a34a" },
  ];
  labels.forEach((lbl, idx) => {
    legend.appendChild(makeSvg("rect", {
      x: legendX, y: legendY + idx * 22, width: 12, height: 12, fill: lbl.c, rx: 2,
    }));
    const t = makeSvg("text", {
      x: legendX + 18, y: legendY + idx * 22 + 10,
      fill: "#afbbb3", "font-size": 11,
    });
    t.textContent = lbl.name;
    legend.appendChild(t);
  });
  curveCanvas.appendChild(legend);

  // Counters
  const { touched: t1 } = pagesTouched(curveType, curveQueryRect);
  const { touched: t2 } = pagesTouched("row", curveQueryRect);
  curvePagesEl.textContent = t1.toString();
  curvePagesRowEl.textContent = t2.toString();
  const savings = t2 > 0 ? Math.round(((t2 - t1) / t2) * 100) : 0;
  curveSavingsEl.textContent = (savings >= 0 ? "+" : "") + savings + "%";
}

function tickCurve() {
  if (!curvePlaying) return;
  const path = CURVE_PATHS[curveType];
  if (curveStep < path.length) {
    curveStep = Math.min(path.length, curveStep + Math.max(1, Math.floor(curveSpeed / 4)));
    renderCurve();
    curveStatus.textContent = "tracing " + curveStep + "/" + path.length;
  } else {
    curveStatus.textContent = "complete";
  }
  curveTimer = setTimeout(tickCurve, 1000 / curveSpeed);
}

function setCurveType(t) {
  curveType = t;
  curveStep = CURVE_PATHS[t].length;
  renderCurve();
  activateButton("[data-curve]", t, "data-curve");
}

curveCanvas.addEventListener("pointerdown", (e) => {
  const p = svgPoint(curveCanvas, e);
  const qx = CURVE_OX + (curveQueryRect.cx - curveQueryRect.w / 2) * CURVE_CELL;
  const qy = CURVE_OY + (curveQueryRect.cy - curveQueryRect.h / 2) * CURVE_CELL;
  const qw = curveQueryRect.w * CURVE_CELL;
  const qh = curveQueryRect.h * CURVE_CELL;
  if (p.x >= qx - 6 && p.x <= qx + qw + 6 && p.y >= qy - 6 && p.y <= qy + qh + 6) {
    curveDrag = { offX: p.x - qx, offY: p.y - qy };
    curveCanvas.setPointerCapture(e.pointerId);
  }
});

curveCanvas.addEventListener("pointermove", (e) => {
  if (!curveDrag) return;
  const p = svgPoint(curveCanvas, e);
  const newX = (p.x - curveDrag.offX - CURVE_OX) / CURVE_CELL;
  const newY = (p.y - curveDrag.offY - CURVE_OY) / CURVE_CELL;
  curveQueryRect.cx = clamp(newX + curveQueryRect.w / 2, curveQueryRect.w / 2, CURVE_N - curveQueryRect.w / 2);
  curveQueryRect.cy = clamp(newY + curveQueryRect.h / 2, curveQueryRect.h / 2, CURVE_N - curveQueryRect.h / 2);
  renderCurve();
});

curveCanvas.addEventListener("pointerup", (e) => {
  curveDrag = null;
  try { curveCanvas.releasePointerCapture(e.pointerId); } catch (_) {}
});

document.querySelectorAll("[data-curve]").forEach((btn) => {
  btn.addEventListener("click", () => setCurveType(btn.getAttribute("data-curve")));
});

document.getElementById("curve-speed").addEventListener("input", (e) => {
  curveSpeed = parseInt(e.target.value, 10);
  document.getElementById("curve-speed-readout").textContent = curveSpeed.toString();
});

document.getElementById("curve-play").addEventListener("click", () => {
  curvePlaying = !curvePlaying;
  curveStatus.textContent = curvePlaying ? "playing" : "paused";
  if (curvePlaying && !curveTimer) tickCurve();
  if (!curvePlaying && curveTimer) {
    clearTimeout(curveTimer);
    curveTimer = null;
  }
});

document.getElementById("curve-restart").addEventListener("click", () => {
  curveStep = 0;
  curvePlaying = true;
  if (!curveTimer) tickCurve();
});

renderCurve();
tickCurve();

// =========================================================================
// LAB 2 - Index Race Track
// =========================================================================

const RACE_VIEW = { w: 720, h: 480 };
const RACE_PAD = 24;
const RACE_SIZE = Math.min(RACE_VIEW.h - 2 * RACE_PAD, RACE_VIEW.w - 2 * RACE_PAD);
const RACE_OX = RACE_PAD;
const RACE_OY = (RACE_VIEW.h - RACE_SIZE) / 2;
const RACE_GRID = 1024;
const RACE_PAGE = 100;
const RACE_N = 5000;

let racePoints = [];
let raceOrderings = {};
let raceQuery = { cx: 512, cy: 512, w: 160, h: 160 };
let raceDrag = null;
let raceSkew = 60;

const raceCanvas = document.getElementById("race-canvas");
const raceChart = document.getElementById("race-chart");
const racePointsEl = document.getElementById("race-points");
const raceWinnerEl = document.getElementById("race-winner");
const raceStatus = document.getElementById("race-status");

function racePosToCanvas(x, y) {
  return [RACE_OX + (x / RACE_GRID) * RACE_SIZE, RACE_OY + (y / RACE_GRID) * RACE_SIZE];
}

function raceCanvasToPos(cx, cy) {
  return [
    ((cx - RACE_OX) / RACE_SIZE) * RACE_GRID,
    ((cy - RACE_OY) / RACE_SIZE) * RACE_GRID,
  ];
}

function rngNormal() {
  let u = 0, v = 0;
  while (u === 0) u = Math.random();
  while (v === 0) v = Math.random();
  return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
}

function generateRacePoints(skew) {
  const f = skew / 100;
  const centers = [
    [200, 200], [800, 250], [500, 700], [870, 870],
  ];
  const weights = [0.4, 0.3, 0.2, 0.1];
  const sigma = 50 + (1 - f) * 250;
  const pts = [];
  for (let i = 0; i < RACE_N; i++) {
    let r = Math.random();
    let cidx = 0;
    let acc = 0;
    for (let j = 0; j < centers.length; j++) {
      acc += weights[j];
      if (r <= acc) { cidx = j; break; }
    }
    let x, y;
    if (f > 0.05) {
      x = centers[cidx][0] + rngNormal() * sigma;
      y = centers[cidx][1] + rngNormal() * sigma;
    } else {
      x = Math.random() * RACE_GRID;
      y = Math.random() * RACE_GRID;
    }
    pts.push([clamp(x, 0, RACE_GRID - 1), clamp(y, 0, RACE_GRID - 1)]);
  }
  return pts;
}

function hilbertKey(x, y, n) {
  let rx = 0, ry = 0, d = 0, s = n / 2;
  let xi = Math.floor(x), yi = Math.floor(y);
  while (s > 0) {
    rx = (xi & s) > 0 ? 1 : 0;
    ry = (yi & s) > 0 ? 1 : 0;
    d += s * s * ((3 * rx) ^ ry);
    if (ry === 0) {
      if (rx === 1) {
        xi = s - 1 - xi;
        yi = s - 1 - yi;
      }
      const tmp = xi; xi = yi; yi = tmp;
    }
    s = Math.floor(s / 2);
  }
  return d;
}

function zorderKey(x, y, order) {
  let d = 0;
  const xi = Math.floor(x), yi = Math.floor(y);
  for (let i = 0; i < order; i++) {
    d |= ((xi >> i) & 1) << (2 * i);
    d |= ((yi >> i) & 1) << (2 * i + 1);
  }
  return d;
}

function buildRaceOrderings() {
  const indices = racePoints.map((_, i) => i);
  const hkeys = racePoints.map(([x, y]) => hilbertKey(x, y, RACE_GRID));
  const zkeys = racePoints.map(([x, y]) => zorderKey(x, y, 10));

  const hilbertSorted = indices.slice().sort((a, b) => hkeys[a] - hkeys[b]);
  const zorderSorted = indices.slice().sort((a, b) => zkeys[a] - zkeys[b]);
  const rtreeSorted = indices.slice().sort((a, b) => racePoints[a][1] === racePoints[b][1]
    ? racePoints[a][0] - racePoints[b][0]
    : racePoints[a][1] - racePoints[b][1]);

  raceOrderings = {
    rowmajor: indices,
    zorder: zorderSorted,
    hilbert: hilbertSorted,
    rtree: rtreeSorted,
  };
}

function pageBoxes(ordering) {
  const boxes = [];
  for (let p = 0; p < ordering.length; p += RACE_PAGE) {
    let xMin = Infinity, xMax = -Infinity, yMin = Infinity, yMax = -Infinity;
    for (let i = p; i < Math.min(p + RACE_PAGE, ordering.length); i++) {
      const [x, y] = racePoints[ordering[i]];
      if (x < xMin) xMin = x; if (x > xMax) xMax = x;
      if (y < yMin) yMin = y; if (y > yMax) yMax = y;
    }
    boxes.push([xMin, xMax, yMin, yMax]);
  }
  return boxes;
}

function pagesForQuery(ordering, query) {
  const boxes = pageBoxes(ordering);
  const qx0 = query.cx - query.w / 2, qx1 = query.cx + query.w / 2;
  const qy0 = query.cy - query.h / 2, qy1 = query.cy + query.h / 2;
  let touched = 0;
  for (const [bx0, bx1, by0, by1] of boxes) {
    if (!(bx1 < qx0 || bx0 > qx1 || by1 < qy0 || by0 > qy1)) touched++;
  }
  return { touched, total: boxes.length };
}

function pointsInQuery(query) {
  const qx0 = query.cx - query.w / 2, qx1 = query.cx + query.w / 2;
  const qy0 = query.cy - query.h / 2, qy1 = query.cy + query.h / 2;
  let count = 0;
  for (const [x, y] of racePoints) {
    if (x >= qx0 && x <= qx1 && y >= qy0 && y <= qy1) count++;
  }
  return count;
}

function renderRace() {
  raceCanvas.innerHTML = "";
  // Background frame
  raceCanvas.appendChild(makeSvg("rect", {
    x: RACE_OX, y: RACE_OY, width: RACE_SIZE, height: RACE_SIZE,
    fill: "rgba(0,0,0,0.3)", stroke: "rgba(255,255,255,0.06)",
  }));
  // Points
  for (const [x, y] of racePoints) {
    const [cx, cy] = racePosToCanvas(x, y);
    raceCanvas.appendChild(makeSvg("circle", {
      cx, cy, r: 1.2, fill: "#6e8db4", opacity: 0.55,
    }));
  }
  // Query rect
  const [qcx0, qcy0] = racePosToCanvas(raceQuery.cx - raceQuery.w / 2, raceQuery.cy - raceQuery.h / 2);
  const [qcx1, qcy1] = racePosToCanvas(raceQuery.cx + raceQuery.w / 2, raceQuery.cy + raceQuery.h / 2);
  raceCanvas.appendChild(makeSvg("rect", {
    x: qcx0, y: qcy0, width: qcx1 - qcx0, height: qcy1 - qcy0,
    fill: "rgba(22,163,74,0.16)", stroke: "#16a34a", "stroke-width": 2,
    "stroke-dasharray": "4 3", style: "cursor: move",
  }));
  raceCanvas.appendChild(makeSvg("circle", {
    cx: qcx1, cy: qcy1, r: 5, fill: "#16a34a", style: "cursor: nwse-resize",
  }));

  // Compute counters
  const labels = ["rowmajor", "zorder", "hilbert", "rtree"];
  const colors = { rowmajor: "#a3a3a3", zorder: "#d97706", hilbert: "#1e40af", rtree: "#16a34a" };
  const niceNames = { rowmajor: "Row-major", zorder: "Z-order", hilbert: "Hilbert", rtree: "R-tree (Y-sorted)" };

  const stats = {};
  let best = null;
  for (const label of labels) {
    const { touched, total } = pagesForQuery(raceOrderings[label], raceQuery);
    stats[label] = { touched, total };
    if (best === null || touched < stats[best].touched) best = label;
  }

  racePointsEl.textContent = pointsInQuery(raceQuery).toString();
  raceWinnerEl.textContent = niceNames[best] + " (" + stats[best].touched + " pages)";
  raceStatus.textContent = "skew " + raceSkew;

  // Render bar chart
  raceChart.innerHTML = "";
  const chartW = 320, chartH = 220;
  const padL = 80, padR = 12, padT = 24, padB = 28;
  const chartArea = { w: chartW - padL - padR, h: chartH - padT - padB };
  const maxPages = Math.max(...labels.map((l) => stats[l].touched), 1);
  const barH = chartArea.h / labels.length - 6;

  labels.forEach((label, idx) => {
    const v = stats[label].touched;
    const y = padT + idx * (barH + 6);
    const w = (v / maxPages) * chartArea.w;
    raceChart.appendChild(makeSvg("rect", {
      x: padL, y, width: w, height: barH, fill: colors[label], rx: 4,
      opacity: label === best ? 1 : 0.7,
    }));
    const lblText = makeSvg("text", {
      x: 6, y: y + barH / 2 + 4, fill: "#edf1ec", "font-size": 11, "font-weight": 600,
    });
    lblText.textContent = niceNames[label];
    raceChart.appendChild(lblText);
    const valText = makeSvg("text", {
      x: padL + w + 6, y: y + barH / 2 + 4, fill: "#afbbb3", "font-size": 11,
    });
    valText.textContent = v + " / " + stats[label].total;
    raceChart.appendChild(valText);
  });

  const titleText = makeSvg("text", {
    x: padL, y: 16, fill: "#efce8a", "font-size": 11, "letter-spacing": "0.18em",
  });
  titleText.textContent = "PAGES READ (LOWER IS BETTER)";
  raceChart.appendChild(titleText);
}

raceCanvas.addEventListener("pointerdown", (e) => {
  const p = svgPoint(raceCanvas, e);
  const [qx0, qy0] = racePosToCanvas(raceQuery.cx - raceQuery.w / 2, raceQuery.cy - raceQuery.h / 2);
  const [qx1, qy1] = racePosToCanvas(raceQuery.cx + raceQuery.w / 2, raceQuery.cy + raceQuery.h / 2);
  if (Math.hypot(p.x - qx1, p.y - qy1) < 14) {
    raceDrag = { mode: "resize" };
  } else if (p.x >= qx0 && p.x <= qx1 && p.y >= qy0 && p.y <= qy1) {
    raceDrag = { mode: "move", offX: p.x - qx0, offY: p.y - qy0 };
  } else {
    return;
  }
  raceCanvas.setPointerCapture(e.pointerId);
});

raceCanvas.addEventListener("pointermove", (e) => {
  if (!raceDrag) return;
  const p = svgPoint(raceCanvas, e);
  if (raceDrag.mode === "move") {
    const [pX, pY] = raceCanvasToPos(p.x - raceDrag.offX, p.y - raceDrag.offY);
    raceQuery.cx = clamp(pX + raceQuery.w / 2, raceQuery.w / 2, RACE_GRID - raceQuery.w / 2);
    raceQuery.cy = clamp(pY + raceQuery.h / 2, raceQuery.h / 2, RACE_GRID - raceQuery.h / 2);
  } else if (raceDrag.mode === "resize") {
    const [pX, pY] = raceCanvasToPos(p.x, p.y);
    const newW = clamp((pX - (raceQuery.cx - raceQuery.w / 2)) * 1, 30, 600);
    const newH = clamp((pY - (raceQuery.cy - raceQuery.h / 2)) * 1, 30, 600);
    raceQuery.w = newW; raceQuery.h = newH;
    raceQuery.cx = clamp(raceQuery.cx, raceQuery.w / 2, RACE_GRID - raceQuery.w / 2);
    raceQuery.cy = clamp(raceQuery.cy, raceQuery.h / 2, RACE_GRID - raceQuery.h / 2);
  }
  renderRace();
});

raceCanvas.addEventListener("pointerup", (e) => {
  raceDrag = null;
  try { raceCanvas.releasePointerCapture(e.pointerId); } catch (_) {}
});

document.getElementById("race-skew").addEventListener("input", (e) => {
  raceSkew = parseInt(e.target.value, 10);
  document.getElementById("race-skew-readout").textContent = raceSkew.toString();
});

document.getElementById("race-regenerate").addEventListener("click", () => {
  raceStatus.textContent = "regenerating";
  racePoints = generateRacePoints(raceSkew);
  buildRaceOrderings();
  renderRace();
});

racePoints = generateRacePoints(raceSkew);
buildRaceOrderings();
renderRace();

// =========================================================================
// LAB 3 - HNSW Climber
// =========================================================================

const HNSW_VIEW = { w: 720, h: 540 };
const HNSW_PAD = 30;

let hnswM = 5;
let hnswN = 80;
let hnswPoints = [];
let hnswLayerOf = [];
let hnswGraph = []; // [layer][node] = Set
let hnswEntry = -1;
let hnswMaxLayer = 0;
let hnswQuery = null;
let hnswPath = []; // ordered list of {layer, node}
let hnswVisited = new Set();

const hnswCanvas = document.getElementById("hnsw-canvas");
const hnswStatus = document.getElementById("hnsw-status");
const hnswLayersEl = document.getElementById("hnsw-layers");
const hnswVisitsEl = document.getElementById("hnsw-visits");
const hnswSpeedupEl = document.getElementById("hnsw-speedup");

function hnswDist(a, b) {
  const dx = a[0] - b[0], dy = a[1] - b[1];
  return Math.sqrt(dx * dx + dy * dy);
}

function buildHnsw() {
  hnswPoints = [];
  hnswLayerOf = [];
  hnswGraph = [];
  hnswEntry = -1;
  hnswMaxLayer = 0;
  const ml = 1 / Math.log(2);
  for (let i = 0; i < hnswN; i++) {
    const x = HNSW_PAD + Math.random() * (HNSW_VIEW.w - 2 * HNSW_PAD - 220);
    const y = HNSW_PAD + Math.random() * (HNSW_VIEW.h - 2 * HNSW_PAD);
    const layer = Math.floor(-Math.log(Math.random() + 1e-9) * ml);
    hnswPoints.push([x, y]);
    hnswLayerOf.push(Math.min(layer, 4));
    if (Math.min(layer, 4) > hnswMaxLayer) hnswMaxLayer = Math.min(layer, 4);
  }
  // Initialize graph layers
  for (let L = 0; L <= hnswMaxLayer; L++) {
    hnswGraph.push({});
    for (let i = 0; i < hnswN; i++) {
      if (hnswLayerOf[i] >= L) hnswGraph[L][i] = new Set();
    }
  }
  // Connect nearest M neighbors at each layer
  for (let L = 0; L <= hnswMaxLayer; L++) {
    const nodes = Object.keys(hnswGraph[L]).map(Number);
    nodes.forEach((i) => {
      const dists = nodes.filter((j) => j !== i)
        .map((j) => ({ j, d: hnswDist(hnswPoints[i], hnswPoints[j]) }))
        .sort((a, b) => a.d - b.d)
        .slice(0, hnswM);
      dists.forEach(({ j }) => {
        hnswGraph[L][i].add(j);
        hnswGraph[L][j].add(i);
      });
    });
  }
  // Pick entry as node with highest layer
  hnswEntry = hnswLayerOf.indexOf(Math.max(...hnswLayerOf));
  hnswPath = [];
  hnswVisited = new Set();
}

function searchHnsw(q) {
  let curr = hnswEntry;
  hnswPath = [{ layer: hnswMaxLayer, node: curr }];
  hnswVisited = new Set([curr]);
  for (let L = hnswMaxLayer; L >= 0; L--) {
    let improved = true;
    while (improved) {
      improved = false;
      const nbrs = hnswGraph[L][curr] || new Set();
      let bestD = hnswDist(hnswPoints[curr], q);
      let best = curr;
      nbrs.forEach((n) => {
        const d = hnswDist(hnswPoints[n], q);
        hnswVisited.add(n);
        if (d < bestD) {
          bestD = d;
          best = n;
        }
      });
      if (best !== curr) {
        curr = best;
        improved = true;
      }
    }
    if (L > 0) hnswPath.push({ layer: L - 1, node: curr });
  }
}

function renderHnsw() {
  hnswCanvas.innerHTML = "";
  const layerColors = ["#1e40af", "#6e8db4", "#c46b6b", "#d97706", "#efce8a"];

  // Edges (bottom layer, faded)
  Object.entries(hnswGraph[0] || {}).forEach(([i, nbrs]) => {
    const a = hnswPoints[+i];
    nbrs.forEach((j) => {
      if (j > +i) {
        const b = hnswPoints[j];
        hnswCanvas.appendChild(makeSvg("line", {
          x1: a[0], y1: a[1], x2: b[0], y2: b[1],
          stroke: "rgba(110,141,180,0.2)", "stroke-width": 0.5,
        }));
      }
    });
  });

  // Highlight layer-> edges (top layers brighter)
  for (let L = 1; L <= hnswMaxLayer; L++) {
    Object.entries(hnswGraph[L] || {}).forEach(([i, nbrs]) => {
      const a = hnswPoints[+i];
      nbrs.forEach((j) => {
        if (j > +i) {
          const b = hnswPoints[j];
          hnswCanvas.appendChild(makeSvg("line", {
            x1: a[0], y1: a[1], x2: b[0], y2: b[1],
            stroke: layerColors[L], "stroke-width": 1.0 + 0.6 * L, opacity: 0.45,
          }));
        }
      });
    });
  }

  // Visited nodes ring
  hnswVisited.forEach((n) => {
    const [x, y] = hnswPoints[n];
    hnswCanvas.appendChild(makeSvg("circle", {
      cx: x, cy: y, r: 9, fill: "none", stroke: "#efce8a", "stroke-width": 1.5, opacity: 0.85,
    }));
  });

  // Search path arrows
  for (let i = 0; i < hnswPath.length - 1; i++) {
    const a = hnswPoints[hnswPath[i].node];
    const b = hnswPoints[hnswPath[i + 1].node];
    hnswCanvas.appendChild(makeSvg("line", {
      x1: a[0], y1: a[1], x2: b[0], y2: b[1],
      stroke: "#efce8a", "stroke-width": 2.5, "stroke-linecap": "round",
    }));
  }

  // Nodes (size by layer)
  hnswPoints.forEach((p, i) => {
    const L = hnswLayerOf[i];
    hnswCanvas.appendChild(makeSvg("circle", {
      cx: p[0], cy: p[1], r: 3 + L * 1.4,
      fill: layerColors[L], stroke: "rgba(0,0,0,0.4)", "stroke-width": 0.8,
    }));
  });

  // Query
  if (hnswQuery) {
    hnswCanvas.appendChild(makeSvg("circle", {
      cx: hnswQuery[0], cy: hnswQuery[1], r: 9,
      fill: "#16a34a", stroke: "#fff", "stroke-width": 2,
    }));
    const t = makeSvg("text", {
      x: hnswQuery[0] + 12, y: hnswQuery[1] + 4,
      fill: "#16a34a", "font-size": 11, "font-weight": 700,
    });
    t.textContent = "query";
    hnswCanvas.appendChild(t);
  }

  // Layer legend
  const legendX = HNSW_VIEW.w - 200;
  const legendY = HNSW_PAD + 10;
  const legend = makeSvg("g", {});
  for (let L = hnswMaxLayer; L >= 0; L--) {
    legend.appendChild(makeSvg("circle", {
      cx: legendX, cy: legendY + (hnswMaxLayer - L) * 24, r: 3 + L * 1.4,
      fill: layerColors[L],
    }));
    const t = makeSvg("text", {
      x: legendX + 14, y: legendY + (hnswMaxLayer - L) * 24 + 4,
      fill: "#afbbb3", "font-size": 11,
    });
    const count = Object.keys(hnswGraph[L] || {}).length;
    t.textContent = "layer " + L + ": " + count + " nodes";
    legend.appendChild(t);
  }
  hnswCanvas.appendChild(legend);

  // Counters
  hnswLayersEl.textContent = (hnswMaxLayer + 1).toString();
  hnswVisitsEl.textContent = hnswVisited.size.toString();
  if (hnswVisited.size > 0) {
    const speedup = (hnswN / hnswVisited.size).toFixed(1);
    hnswSpeedupEl.textContent = speedup + "x";
  } else {
    hnswSpeedupEl.textContent = "--";
  }
}

hnswCanvas.addEventListener("click", (e) => {
  const p = svgPoint(hnswCanvas, e);
  hnswQuery = [p.x, p.y];
  searchHnsw(hnswQuery);
  hnswStatus.textContent = "search descended " + hnswPath.length + " layer" + (hnswPath.length > 1 ? "s" : "");
  renderHnsw();
});

document.getElementById("hnsw-m").addEventListener("input", (e) => {
  hnswM = parseInt(e.target.value, 10);
  document.getElementById("hnsw-m-readout").textContent = hnswM.toString();
});

document.getElementById("hnsw-n").addEventListener("input", (e) => {
  hnswN = parseInt(e.target.value, 10);
  document.getElementById("hnsw-n-readout").textContent = hnswN.toString();
});

document.getElementById("hnsw-rebuild").addEventListener("click", () => {
  hnswStatus.textContent = "rebuilding";
  buildHnsw();
  hnswQuery = null;
  renderHnsw();
});

buildHnsw();
renderHnsw();
