const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/* ---------- scroll progress ---------- */

const progressBar = document.querySelector(".scroll-progress");

if (progressBar) {
  const updateProgress = () => {
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    const ratio = scrollable > 0 ? window.scrollY / scrollable : 0;
    progressBar.style.width = `${Math.min(ratio * 100, 100)}%`;
  };
  window.addEventListener("scroll", updateProgress, { passive: true });
  updateProgress();
}

/* ---------- staggered reveals ---------- */

const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.12 }
);

document.querySelectorAll("[data-reveal]").forEach((node, index) => {
  node.style.setProperty("--reveal-delay", `${(index % 4) * 70}ms`);
  revealObserver.observe(node);
});

/* ---------- metric count-up ---------- */

const countObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      countObserver.unobserve(entry.target);

      const node = entry.target;
      const target = Number(node.getAttribute("data-count") || "0");

      if (reducedMotion) {
        node.textContent = String(target);
        return;
      }

      const duration = 1100;
      const start = performance.now();
      const tick = (now) => {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        node.textContent = String(Math.round(target * eased));
        if (progress < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  },
  { threshold: 0.4 }
);

document.querySelectorAll("[data-count]").forEach((node) => countObserver.observe(node));

/* ---------- cursor spotlight on cards ---------- */

document.querySelectorAll(".glow-card").forEach((card) => {
  card.addEventListener("pointermove", (event) => {
    const rect = card.getBoundingClientRect();
    card.style.setProperty("--mx", `${event.clientX - rect.left}px`);
    card.style.setProperty("--my", `${event.clientY - rect.top}px`);
  });
});

/* ---------- copy buttons on run cards ---------- */

document.querySelectorAll(".run-card").forEach((card) => {
  const pre = card.querySelector("pre");
  if (!pre || !navigator.clipboard) return;

  const button = document.createElement("button");
  button.className = "copy-btn";
  button.type = "button";
  button.textContent = "copy";
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(pre.textContent.trim());
      button.textContent = "copied";
      button.classList.add("copied");
      setTimeout(() => {
        button.textContent = "copy";
        button.classList.remove("copied");
      }, 1600);
    } catch {
      button.textContent = "failed";
    }
  });
  card.appendChild(button);
});

/* ---------- hero canvas: Hilbert curve + particle drift ---------- */

const canvas = document.querySelector(".hero-canvas");
const hero = document.querySelector(".hero");

if (canvas && hero) {
  const ctx = canvas.getContext("2d");
  const dpr = Math.min(window.devicePixelRatio || 1, 2);

  let width = 0;
  let height = 0;
  let points = [];
  let drawn = 0;
  let holdUntil = 0;
  let fadeStart = 0;
  let phase = "draw"; // draw -> hold -> fade
  let hueShift = 0;
  let pointerX = 0.5;
  let pointerY = 0.5;
  let running = true;

  const ORDER = 5; // 32x32 grid, 1024 vertices
  const SIDE = 1 << ORDER;
  const SPEED = 7; // vertices revealed per frame

  // Hilbert curve: distance along curve -> (x, y) grid cell
  function d2xy(d) {
    let rx;
    let ry;
    let t = d;
    let x = 0;
    let y = 0;
    for (let s = 1; s < SIDE; s *= 2) {
      rx = 1 & Math.floor(t / 2);
      ry = 1 & (t ^ rx);
      if (ry === 0) {
        if (rx === 1) {
          x = s - 1 - x;
          y = s - 1 - y;
        }
        const swap = x;
        x = y;
        y = swap;
      }
      x += s * rx;
      y += s * ry;
      t = Math.floor(t / 4);
    }
    return [x, y];
  }

  const particles = Array.from({ length: 70 }, (_, i) => ({
    x: (i * 137.5) % 100 / 100,
    y: ((i * 73.3) % 100) / 100,
    r: 0.6 + (i % 5) * 0.35,
    vx: ((i % 7) - 3) * 0.00003,
    vy: ((i % 5) - 2) * 0.00004,
    tw: (i % 9) / 9,
  }));

  function layout() {
    const rect = hero.getBoundingClientRect();
    width = rect.width;
    height = rect.height;
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // Curve occupies the right portion of the hero, vertically centered
    const size = Math.min(width * 0.46, height * 0.92);
    const cell = size / SIDE;
    const originX = width - size - Math.max(width * 0.03, 16);
    const originY = (height - size) / 2;

    points = [];
    for (let d = 0; d < SIDE * SIDE; d += 1) {
      const [gx, gy] = d2xy(d);
      points.push([originX + gx * cell + cell / 2, originY + gy * cell + cell / 2]);
    }
  }

  function strokeGradient(alpha) {
    const gradient = ctx.createLinearGradient(width * 0.45, 0, width, height);
    gradient.addColorStop(0, `hsla(${190 + hueShift}, 95%, 68%, ${alpha})`);
    gradient.addColorStop(0.5, `hsla(${258 + hueShift}, 88%, 74%, ${alpha})`);
    gradient.addColorStop(1, `hsla(${326 + hueShift}, 86%, 70%, ${alpha})`);
    return gradient;
  }

  function drawCurve(count, alpha) {
    if (count < 2) return;

    const ox = (pointerX - 0.5) * 14;
    const oy = (pointerY - 0.5) * 10;

    ctx.save();
    ctx.translate(ox, oy);
    ctx.lineJoin = "round";
    ctx.lineCap = "round";

    // halo pass
    ctx.beginPath();
    ctx.moveTo(points[0][0], points[0][1]);
    for (let i = 1; i < count; i += 1) ctx.lineTo(points[i][0], points[i][1]);
    ctx.strokeStyle = strokeGradient(alpha * 0.16);
    ctx.lineWidth = 5;
    ctx.stroke();

    // core pass
    ctx.strokeStyle = strokeGradient(alpha * 0.85);
    ctx.lineWidth = 1.4;
    ctx.stroke();

    // bright head while drawing
    if (phase === "draw" && count < points.length) {
      const [hx, hy] = points[count - 1];
      ctx.beginPath();
      ctx.arc(hx, hy, 3, 0, Math.PI * 2);
      ctx.fillStyle = `hsla(${190 + hueShift}, 100%, 80%, ${alpha})`;
      ctx.fill();
    }

    ctx.restore();
  }

  function drawParticles(now) {
    particles.forEach((p) => {
      p.x = (p.x + p.vx + 1) % 1;
      p.y = (p.y + p.vy + 1) % 1;
      const twinkle = 0.35 + 0.4 * Math.abs(Math.sin(now / 1700 + p.tw * Math.PI * 2));
      ctx.beginPath();
      ctx.arc(p.x * width, p.y * height, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(167, 180, 255, ${twinkle * 0.35})`;
      ctx.fill();
    });
  }

  function frame(now) {
    if (!running) return;
    ctx.clearRect(0, 0, width, height);
    drawParticles(now);

    if (phase === "draw") {
      drawn = Math.min(drawn + SPEED, points.length);
      drawCurve(drawn, 1);
      if (drawn >= points.length) {
        phase = "hold";
        holdUntil = now + 3200;
      }
    } else if (phase === "hold") {
      drawCurve(points.length, 1);
      if (now >= holdUntil) {
        phase = "fade";
        fadeStart = now;
      }
    } else {
      const fade = Math.min((now - fadeStart) / 900, 1);
      drawCurve(points.length, 1 - fade);
      if (fade >= 1) {
        phase = "draw";
        drawn = 0;
        hueShift = (hueShift + 18) % 90;
      }
    }

    requestAnimationFrame(frame);
  }

  layout();

  if (reducedMotion) {
    // static render, no animation loop
    drawParticles(0);
    drawCurve(points.length, 1);
  } else {
    hero.addEventListener("pointermove", (event) => {
      const rect = hero.getBoundingClientRect();
      pointerX = (event.clientX - rect.left) / rect.width;
      pointerY = (event.clientY - rect.top) / rect.height;
    });

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        running = false;
      } else if (!running) {
        running = true;
        requestAnimationFrame(frame);
      }
    });

    window.addEventListener("resize", () => {
      layout();
      if (drawn > points.length) drawn = points.length;
    });

    requestAnimationFrame(frame);
  }
}
