/* Side-by-side player: the same game with and without the harness. Data: assets/data/ft09-compare.json,
   built by tools/build_arc3_compare.py from the saved runs. One shared clock: step k is the k-th real action
   on both sides, so the side that finishes first simply stops and waits. */
(() => {
  const el = document.querySelector(".cmp");
  if (!el) return;
  const PALETTE = ["#ffffff", "#cccccc", "#999999", "#666666", "#333333", "#000000", "#e53aa3", "#ff7bcc",
                   "#f93c31", "#1e93ff", "#88d8f1", "#ffdc00", "#ff851b", "#921231", "#4fcc30", "#a356d6"];
  const N = 64;
  const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;

  fetch(el.dataset.src).then((r) => r.json()).then((data) => {
    const sides = [["without", el.querySelector('[data-side="without"]')], ["with", el.querySelector('[data-side="with"]')]]
      .map(([key, root]) => ({ key, root, d: data[key], ctx: root.querySelector("canvas").getContext("2d") }));
    sides.forEach((s) => {                         // frames are stored as changes; rebuild every frame once
      let cur = s.d.start.map((r) => r.split(""));
      s.frames = [s.d.start];
      s.d.steps.forEach((st) => {
        if (st.grid) cur = st.grid.map((r) => r.split(""));
        else { cur = cur.map((r) => r.slice()); st.cells.forEach(([y, x, c]) => { cur[y][x] = c.toString(16); }); }
        s.frames.push(cur.map((r) => r.join("")));
      });
    });
    const total = Math.max(...sides.map((s) => s.d.steps.length));
    const SPEEDS = [[1, 900], [2, 450], [4, 220]];
    let speed = 1;
    const range = el.querySelector(".cmp-range"), play = el.querySelector(".cmp-play"), count = el.querySelector(".cmp-count");
    range.max = total;
    let step = 0, timer = 0;

    /* Draw at the screen's real resolution: the canvas backing store is sized to the displayed size times the
       device pixel ratio, and every cell edge is rounded to a whole device pixel, so nothing is ever stretched. */
    function fit(ctx) {
      const c = ctx.canvas, px = Math.max(N, Math.round(c.clientWidth * (window.devicePixelRatio || 1)));
      if (c.width !== px) { c.width = px; c.height = px; }
      return px;
    }
    function paint(ctx, rows, prev, click) {
      const px = fit(ctx), at = (i) => Math.round(i * px / N), u = px / 384;
      ctx.imageSmoothingEnabled = false;
      for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
        ctx.fillStyle = PALETTE[parseInt(rows[y][x], 16)];
        ctx.fillRect(at(x), at(y), at(x + 1) - at(x), at(y + 1) - at(y));
      }
      if (prev) {                                  // outline the cells this action changed
        let x0 = N, y0 = N, x1 = -1, y1 = -1, n = 0;
        for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) if (rows[y][x] !== prev[y][x]) { n++; x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); }
        if (n && n < 400) {
          const bx = at(x0) - 3 * u, by = at(y0) - 3 * u, bw = at(x1 + 1) - at(x0) + 6 * u, bh = at(y1 + 1) - at(y0) + 6 * u;
          ctx.lineWidth = 3 * u; ctx.strokeStyle = "#ffffff"; ctx.strokeRect(bx, by, bw, bh);
          ctx.lineWidth = 1.5 * u; ctx.strokeStyle = "#111111"; ctx.strokeRect(bx, by, bw, bh);
        }
      }
      if (click && click.x != null) {              // where the model clicked
        const cx = (at(click.x) + at(click.x + 1)) / 2, cy = (at(click.y) + at(click.y + 1)) / 2;
        ctx.beginPath(); ctx.arc(cx, cy, 13 * u, 0, Math.PI * 2); ctx.lineWidth = 5 * u; ctx.strokeStyle = "#ffffff"; ctx.stroke();
        ctx.beginPath(); ctx.arc(cx, cy, 13 * u, 0, Math.PI * 2); ctx.lineWidth = 2.5 * u; ctx.strokeStyle = "#111111"; ctx.stroke();
      }
    }

    function render() {
      sides.forEach((s) => {
        const n = s.d.steps.length, k = Math.min(step, n), cur = k ? s.d.steps[k - 1] : null;
        const rows = s.frames[k], prev = k ? s.frames[k - 1] : null;
        const before = k > 1 ? s.d.steps[k - 2].levels : 0, levelUp = cur && cur.levels > before;
        const finished = cur && s.d.total_levels && cur.levels >= s.d.total_levels;
        paint(s.ctx, rows, levelUp ? null : prev, levelUp ? null : cur);
        s.root.querySelector(".cmp-acts").textContent = k;
        s.root.querySelector(".cmp-lv").textContent = cur ? cur.levels : 0;
        const say = s.root.querySelector(".cmp-say"), eff = s.root.querySelector(".cmp-eff");
        say.textContent = cur ? cur.say : "Opening frame. No action taken yet.";
        eff.textContent = !cur ? "" : finished ? "Level " + cur.levels + " cleared. Game complete." : levelUp ? "Level " + cur.levels + " cleared. Showing the start of level " + (cur.levels + 1) + "." : cur.changed ? cur.changed + " cells changed" : "No visible effect";
        eff.dataset.kind = !cur ? "" : levelUp ? "win" : cur.changed ? "hit" : "miss";
        s.root.classList.toggle("done", step >= n);
        s.root.classList.toggle("won", step >= n && s.d.steps[n - 1].levels > 0);
        s.root.classList.toggle("up", !!levelUp);
        s.root.querySelector(".cmp-badge").textContent = step >= n ? (s.d.steps[n - 1].levels > 0 ? "all " + s.d.steps[n - 1].levels + " levels cleared in " + n + " actions" : "stopped after " + n + " actions: no level cleared") : levelUp ? "level " + cur.levels + " cleared" : "";
      });
      range.value = step;
      count.textContent = "action " + step + " of " + total;
      play.textContent = timer ? "Pause" : step >= total ? "Replay" : "Play";
    }
    function stop() { clearInterval(timer); timer = 0; render(); }
    function start() {
      if (step >= total) step = 0;
      timer = setInterval(() => { step++; if (step >= total) { step = total; stop(); } else render(); }, SPEEDS[speed][1]);
      render();
    }
    play.addEventListener("click", () => (timer ? stop() : start()));
    el.querySelector(".cmp-prev").addEventListener("click", () => { stop(); step = Math.max(0, step - 1); render(); });
    el.querySelector(".cmp-next").addEventListener("click", () => { stop(); step = Math.min(total, step + 1); render(); });
    range.addEventListener("input", () => { stop(); step = +range.value; render(); });
    const fast = el.querySelector(".cmp-speed");
    fast.addEventListener("click", () => { speed = (speed + 1) % SPEEDS.length; fast.textContent = SPEEDS[speed][0] + "\u00d7"; if (timer) { clearInterval(timer); timer = 0; start(); } });
    fast.textContent = SPEEDS[speed][0] + "\u00d7";
    render();
    el.classList.add("ready");
    let rz = 0;
    addEventListener("resize", () => { clearTimeout(rz); rz = setTimeout(render, 120); });

    if (!calm && "IntersectionObserver" in window) {   // start once, the first time the player is on screen
      const io = new IntersectionObserver((e) => { if (e[0].isIntersecting) { io.disconnect(); setTimeout(() => { if (!timer && step === 0) start(); }, 700); } }, { threshold: 0.55 });
      io.observe(el);
    }
  }).catch(() => { el.querySelector(".cmp-count").textContent = "The comparison data could not be loaded."; });
})();
