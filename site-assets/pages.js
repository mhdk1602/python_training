const hero = document.querySelector(".hero");

if (hero) {
  hero.addEventListener("pointermove", (event) => {
    const rect = hero.getBoundingClientRect();
    const offsetX = ((event.clientX - rect.left) / rect.width - 0.5) * 28;
    const offsetY = ((event.clientY - rect.top) / rect.height - 0.5) * 22;
    hero.style.setProperty("--hero-shift-x", `${offsetX}px`);
    hero.style.setProperty("--hero-shift-y", `${offsetY}px`);
  });

  hero.addEventListener("pointerleave", () => {
    hero.style.setProperty("--hero-shift-x", "0px");
    hero.style.setProperty("--hero-shift-y", "0px");
  });
}

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.16 }
);

document.querySelectorAll("[data-reveal]").forEach((node) => observer.observe(node));

document.querySelectorAll("[data-count]").forEach((node) => {
  const target = Number(node.getAttribute("data-count") || "0");
  const duration = 900;
  const start = performance.now();

  const tick = (now) => {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    node.textContent = String(Math.round(target * eased));

    if (progress < 1) {
      requestAnimationFrame(tick);
    } else {
      node.textContent = String(target);
    }
  };

  requestAnimationFrame(tick);
});
