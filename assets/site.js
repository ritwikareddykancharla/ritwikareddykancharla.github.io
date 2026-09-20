/* Navigation and motion. The pages read fine without this file; it adds:
   eased in-page scrolling, the contents sidebar (active section, sliding marker, subsections that
   open and close, reading progress), a back-to-top button, and reveal-on-scroll. */
(() => {
  const root = document.documentElement;
  const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;
  root.classList.add("js");
  const HEADER = 92;

  /* ---------- light / dark ---------- */
  const themeBtn = document.querySelector(".theme");
  if (themeBtn) themeBtn.addEventListener("click", () => {
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    root.dataset.theme = next;
    try { localStorage.setItem("theme", next); } catch (e) { /* private window: the choice lasts for this page only */ }
  });

  /* ---------- eased scrolling: duration grows with distance, so long jumps do not whip ---------- */
  let raf = 0;
  const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  function glide(to, done) {
    cancelAnimationFrame(raf);
    const from = scrollY;
    to = Math.max(0, Math.min(to, root.scrollHeight - innerHeight));
    const dist = Math.abs(to - from);
    if (calm || dist < 4) { scrollTo(0, to); done && done(); return; }
    const ms = Math.min(1500, Math.max(650, 420 + dist * 0.28));
    const t0 = performance.now();
    const step = (now) => {
      const p = Math.min(1, (now - t0) / ms);
      scrollTo(0, from + (to - from) * ease(p));
      if (p < 1) raf = requestAnimationFrame(step); else done && done();
    };
    raf = requestAnimationFrame(step);
  }
  ["wheel", "touchstart", "keydown"].forEach((e) => addEventListener(e, () => cancelAnimationFrame(raf), { passive: true }));

  function arrive(el) {
    if (!el || el === document.body) return;
    el.classList.remove("arrive"); void el.offsetWidth; el.classList.add("arrive");
    setTimeout(() => el.classList.remove("arrive"), 1600);
  }
  document.addEventListener("click", (ev) => {
    const a = ev.target.closest("a[href]");
    if (!a || ev.metaKey || ev.ctrlKey || ev.shiftKey || a.target === "_blank") return;
    const url = new URL(a.href, location.href);
    if (url.pathname !== location.pathname || !url.hash) return;
    const el = document.getElementById(decodeURIComponent(url.hash.slice(1)));
    if (!el) return;
    ev.preventDefault();
    const top = el.id === "top" ? 0 : el.getBoundingClientRect().top + scrollY - HEADER;
    glide(top, () => arrive(el));
    history.pushState(null, "", el.id === "top" ? location.pathname : url.hash);
  });

  /* ---------- contents sidebar, header highlight, progress, back to top ---------- */
  const side = document.querySelector(".side");
  const body = document.querySelector(".post-body");
  const links = side ? [...side.querySelectorAll(".side-list a")] : [];
  const targets = links.map((a) => document.getElementById(a.hash.slice(1)));
  const ind = side && side.querySelector(".side-ind");
  const bar = side && side.querySelector(".side-bar i");
  const pct = side && side.querySelector(".side-pct");
  const toTop = document.querySelector(".totop");
  const ring = toTop && toTop.querySelector(".ring");
  const RING = 2 * Math.PI * 21;
  if (ring) ring.style.strokeDasharray = RING;
  const homeNav = [...document.querySelectorAll(".site nav a")].filter((a) => a.hash && new URL(a.href).pathname === location.pathname);
  const homeTargets = homeNav.map((a) => document.getElementById(a.hash.slice(1)));
  let current = null;

  function update() {
    const y = scrollY;
    const max = root.scrollHeight - innerHeight;
    const whole = max > 0 ? y / max : 0;
    if (toTop) { toTop.classList.toggle("show", y > 700); ring.style.strokeDashoffset = RING * (1 - whole); }

    if (side && body) {
      const r = body.getBoundingClientRect();
      const read = Math.min(1, Math.max(0, (innerHeight * 0.4 - r.top) / r.height));
      bar.style.transform = `scaleX(${read})`;
      pct.textContent = Math.round(read * 100) + "%";
      let active = null;
      targets.forEach((t, i) => { if (t && t.getBoundingClientRect().top <= HEADER + 60) active = links[i]; });
      if (active !== current) {
        current = active;
        links.forEach((a) => a.classList.remove("on"));
        side.querySelectorAll(".side-list > li").forEach((li) => li.classList.remove("open"));
        if (active) {
          active.classList.add("on");
          const li = active.closest(".side-list > li");
          li.classList.add("open");
          li.firstElementChild.classList.add("on");
        }
        setTimeout(moveMarker, 360);   // after the subsection list has finished opening
        moveMarker();
      }
    }
    if (homeNav.length) {
      let on = null;
      homeTargets.forEach((t, i) => { if (t && t.getBoundingClientRect().top <= HEADER + 120) on = homeNav[i]; });
      homeNav.forEach((a) => a.classList.toggle("on", a === on));
    }
  }
  function moveMarker() {
    if (!ind) return;
    const a = current;
    if (!a) { ind.style.opacity = 0; return; }
    const list = side.querySelector(".side-list").getBoundingClientRect();
    const r = a.getBoundingClientRect();
    ind.style.opacity = 1;
    ind.style.transform = `translateY(${r.top - list.top}px)`;
    ind.style.height = r.height + "px";
    const box = side.getBoundingClientRect();   // keep the active entry visible when the list is long
    if (r.bottom > box.bottom - 40 || r.top < box.top + 40) side.scrollTo({ top: side.scrollTop + r.top - box.top - box.height / 2, behavior: calm ? "auto" : "smooth" });
  }
  let ticking = false;
  addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(() => { update(); ticking = false; }); } }, { passive: true });
  addEventListener("resize", () => { update(); moveMarker(); });
  addEventListener("load", () => { update(); moveMarker(); });
  update();
  if (side) requestAnimationFrame(() => side.classList.add("ready"));

  /* ---------- reveal on scroll (checked in the scroll handler, so nothing can stay hidden) ---------- */
  const sel = ".post-body h2, .tldr, .fig, .tablewrap, .note, blockquote, pre, .hero-img, .feature, .row, .pubs li, .cv article, .reach, .sec-head, .next, .stats a";
  let waiting = calm ? [] : [...document.querySelectorAll(sel)];
  waiting.forEach((el) => el.classList.add("reveal"));
  function reveal() {
    if (!waiting.length) return;
    let shown = 0;
    waiting = waiting.filter((el) => {
      const r = el.getBoundingClientRect();
      if (r.top > innerHeight * 0.92) return true;
      el.style.transitionDelay = (r.bottom < 0 ? 0 : Math.min(shown++, 4) * 70) + "ms";   // stagger only what is on screen
      el.classList.add("in");
      return false;
    });
  }
  addEventListener("scroll", reveal, { passive: true });
  addEventListener("resize", reveal);
  addEventListener("load", reveal);
  reveal();
  if (location.hash) { const el = document.getElementById(location.hash.slice(1)); if (el) setTimeout(() => arrive(el), 400); }
})();
