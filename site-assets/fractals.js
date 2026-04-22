const presets = {
  main: { centerX: -0.75, centerY: 0, width: 3.5, label: "Main set" },
  seahorse: { centerX: -0.745, centerY: 0.112, width: 0.05, label: "Seahorse valley" },
  elephant: { centerX: 0.282, centerY: 0.01, width: 0.07, label: "Elephant valley" },
  mini: { centerX: -1.25066, centerY: 0.02012, width: 0.01, label: "Mini-brot" },
};

const palettes = {
  ember: (t) => {
    const r = Math.round(35 + 220 * Math.pow(t, 0.82));
    const g = Math.round(18 + 110 * Math.pow(t, 1.05));
    const b = Math.round(22 + 70 * (1 - t));
    return [r, g, b];
  },
  moss: (t) => {
    const r = Math.round(20 + 120 * t);
    const g = Math.round(34 + 170 * Math.pow(t, 0.9));
    const b = Math.round(28 + 90 * (1 - t * 0.7));
    return [r, g, b];
  },
  night: (t) => {
    const r = Math.round(18 + 160 * t);
    const g = Math.round(28 + 120 * Math.pow(t, 1.2));
    const b = Math.round(44 + 210 * Math.pow(t, 0.65));
    return [r, g, b];
  },
};

const lensContent = {
  field: {
    kicker: "Field scale",
    title: "Start with one governed attribute.",
    body: "Examples: null bursts in customer email, inconsistent country codes, unstable product labels, or missing effective dates. At this level the work is about definitions, allowed values, and validation rules.",
    points: [
      "good candidates: missingness pockets, code drift, sparsity",
      "governance move: define a standard and enforce it",
    ],
  },
  record: {
    kicker: "Record scale",
    title: "Then move to the row as a decision unit.",
    body: "Record-level governance starts when individual fields no longer fail independently. One stale address, one malformed identifier, and one outdated status can combine into a row the business should not trust.",
    points: [
      "good candidates: conflicting attributes, survivorship failures",
      "governance move: decide what a valid record state means",
    ],
  },
  entity: {
    kicker: "Entity scale",
    title: "This is where MDM becomes unavoidable.",
    body: "At the entity level the problem is no longer one row. It is a cluster of rows that may or may not refer to the same customer, supplier, or product. Match logic, survivorship rules, and stewardship queues live here.",
    points: [
      "good candidates: duplicate clusters, merge-threshold instability",
      "governance move: define the golden record and escalation path",
    ],
  },
  domain: {
    kicker: "Domain scale",
    title: "Hierarchies and reference domains carry their own risk.",
    body: "Product trees, customer segments, and reference taxonomies are usually governed at the domain level. The concern is not only correctness, but uneven branching, orphan nodes, and code families that drift from the standard.",
    points: [
      "good candidates: branch sparsity, orphan nodes, hierarchy irregularity",
      "governance move: stabilize the taxonomy and ownership model",
    ],
  },
  enterprise: {
    kicker: "Enterprise scale",
    title: "The graph now matters more than the row.",
    body: "At enterprise scale the object of interest is often the integration graph, the lineage graph, or the issue-propagation graph. This is the most plausible place for graph-based fractal descriptors to become analytically useful.",
    points: [
      "good candidates: lineage fragility, mapping boundaries, issue propagation",
      "governance move: rank stewardship and control work where boundary risk concentrates",
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

const canvas = document.getElementById("mandelbrot-canvas");
const ctx = canvas?.getContext("2d");
const iterRange = document.getElementById("iter-range");
const iterValue = document.getElementById("iter-value");
const renderStatus = document.getElementById("render-status");
const statCenter = document.getElementById("stat-center");
const statWidth = document.getElementById("stat-width");
const statBoundary = document.getElementById("stat-boundary");
const statEscape = document.getElementById("stat-escape");

let state = {
  centerX: presets.main.centerX,
  centerY: presets.main.centerY,
  width: presets.main.width,
  maxIter: Number(iterRange?.value || 220),
  palette: "ember",
  isRendering: false,
};
let pendingRender = false;

function setStatus(text) {
  if (renderStatus) {
    renderStatus.textContent = text;
  }
}

function complexWindow() {
  const aspect = canvas.height / canvas.width;
  return {
    xmin: state.centerX - state.width / 2,
    xmax: state.centerX + state.width / 2,
    ymin: state.centerY - (state.width * aspect) / 2,
    ymax: state.centerY + (state.width * aspect) / 2,
  };
}

function colorize(iter, maxIter) {
  if (iter >= maxIter) {
    return [6, 8, 12];
  }
  const t = iter / maxIter;
  return palettes[state.palette](t);
}

function updateReadout(boundaryRatio, meanEscape) {
  if (statCenter) {
    statCenter.textContent = `${state.centerX.toFixed(5)}, ${state.centerY.toFixed(5)}`;
  }
  if (statWidth) {
    statWidth.textContent = state.width.toFixed(5);
  }
  if (statBoundary) {
    statBoundary.textContent = `${(boundaryRatio * 100).toFixed(2)}%`;
  }
  if (statEscape) {
    statEscape.textContent = meanEscape.toFixed(1);
  }
}

function renderMandelbrot() {
  if (!canvas || !ctx) {
    return;
  }

  if (state.isRendering) {
    pendingRender = true;
    return;
  }

  state.isRendering = true;
  setStatus("Rendering...");

  const { xmin, xmax, ymin, ymax } = complexWindow();
  const image = ctx.createImageData(canvas.width, canvas.height);
  const data = image.data;
  const maxIter = state.maxIter;
  const dx = (xmax - xmin) / canvas.width;
  const dy = (ymax - ymin) / canvas.height;

  let y = 0;
  let boundaryHits = 0;
  let totalEscape = 0;

  const chunk = 6;

  function paintChunk() {
    for (let step = 0; step < chunk && y < canvas.height; step += 1, y += 1) {
      const cy = ymin + y * dy;

      for (let x = 0; x < canvas.width; x += 1) {
        const cx = xmin + x * dx;
        let zx = 0;
        let zy = 0;
        let iter = 0;

        while (zx * zx + zy * zy <= 4 && iter < maxIter) {
          const nextX = zx * zx - zy * zy + cx;
          zy = 2 * zx * zy + cy;
          zx = nextX;
          iter += 1;
        }

        if (iter > maxIter * 0.9 && iter < maxIter) {
          boundaryHits += 1;
        }
        totalEscape += iter;

        const [r, g, b] = colorize(iter, maxIter);
        const index = (y * canvas.width + x) * 4;
        data[index] = r;
        data[index + 1] = g;
        data[index + 2] = b;
        data[index + 3] = 255;
      }
    }

    ctx.putImageData(image, 0, 0);

    if (y < canvas.height) {
      requestAnimationFrame(paintChunk);
      return;
    }

    state.isRendering = false;
    const totalPixels = canvas.width * canvas.height;
    updateReadout(boundaryHits / totalPixels, totalEscape / totalPixels);
    setStatus("Rendered");

    if (pendingRender) {
      pendingRender = false;
      requestAnimationFrame(renderMandelbrot);
    }
  }

  paintChunk();
}

function activateButton(groupSelector, value, attr) {
  document.querySelectorAll(groupSelector).forEach((button) => {
    button.classList.toggle("is-active", button.getAttribute(attr) === value);
  });
}

document.querySelectorAll(".preset-button").forEach((button) => {
  button.addEventListener("click", () => {
    const preset = presets[button.dataset.preset];
    state = { ...state, centerX: preset.centerX, centerY: preset.centerY, width: preset.width };
    activateButton(".preset-button", button.dataset.preset, "data-preset");
    renderMandelbrot();
  });
});

document.querySelectorAll(".palette-button").forEach((button) => {
  button.addEventListener("click", () => {
    state = { ...state, palette: button.dataset.palette };
    activateButton(".palette-button", button.dataset.palette, "data-palette");
    renderMandelbrot();
  });
});

iterRange?.addEventListener("input", () => {
  const value = Number(iterRange.value);
  state = { ...state, maxIter: value };
  if (iterValue) {
    iterValue.textContent = String(value);
  }
  renderMandelbrot();
});

canvas?.addEventListener("click", (event) => {
  const rect = canvas.getBoundingClientRect();
  const px = ((event.clientX - rect.left) / rect.width) * canvas.width;
  const py = ((event.clientY - rect.top) / rect.height) * canvas.height;
  const { xmin, xmax, ymin, ymax } = complexWindow();
  const cx = xmin + (px / canvas.width) * (xmax - xmin);
  const cy = ymin + (py / canvas.height) * (ymax - ymin);
  const nextWidth = event.shiftKey ? state.width / 0.45 : state.width * 0.45;

  state = { ...state, centerX: cx, centerY: cy, width: nextWidth };
  renderMandelbrot();
});

document.querySelectorAll(".lens-button").forEach((button) => {
  button.addEventListener("click", () => {
    const key = button.dataset.scale;
    const content = lensContent[key];
    if (!content) {
      return;
    }

    document.querySelectorAll(".lens-button").forEach((node) => node.classList.toggle("is-active", node === button));
    document.querySelectorAll(".lens-layer").forEach((node) => {
      node.classList.remove("is-active");
    });
    document.querySelector(`.layer-${key}`)?.classList.add("is-active");

    document.getElementById("lens-kicker").textContent = content.kicker;
    document.getElementById("lens-title").textContent = content.title;
    document.getElementById("lens-body").textContent = content.body;
    const list = document.getElementById("lens-points");
    list.innerHTML = content.points.map((point) => `<li>${point}</li>`).join("");
  });
});

renderMandelbrot();
