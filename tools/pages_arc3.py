"""ARC-AGI-3 project page. Facts: schema_agent/README.md and research/public-game-hardening-ledger.md (arc-agi3 PR #6)."""

I3 = "../assets/img/arc3/"


# ---------------------------------------------------------------------------------------------
# Presentation devices adapted from the Schema project page [1]: a diagram of the loop, evidence
# cards that walk through one trace step by step, per-level efficiency bars, a takeaway line under
# each case study, and a citation block. All numbers come from the hardening ledger (PR #6).
# ---------------------------------------------------------------------------------------------
def _box(x, y, n, title, sub, owner):
    cls = "lp-m" if owner == "model" else "lp-h"
    who = "model" if owner == "model" else "harness"
    return (f'<g class="{cls}"><rect x="{x}" y="{y}" width="232" height="76"/>'
            f'<text class="lp-n" x="{x + 14}" y="{y + 22}">{n:02d}  {who}</text>'
            f'<text class="lp-t" x="{x + 14}" y="{y + 45}">{title}</text>'
            f'<text class="lp-s" x="{x + 14}" y="{y + 63}">{sub}</text></g>')


LOOP = ('<figure class="fig"><div class="plate"><svg class="loop" viewBox="0 0 860 340" role="img" '
        'aria-label="The control loop: the harness perceives, the model proposes, the harness replays the proposal on all history, searches, the model commits a plan, and the harness executes and records it.">'
        '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="lp-ah"/></marker>'
        '<marker id="ahd" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="lp-ahd"/></marker></defs>'
        + _box(24, 48, 1, "Perceive", "objects, motion, relations", "harness")
        + _box(314, 48, 2, "Propose", "what it is, how it moves, the goal", "model")
        + _box(604, 48, 3, "Replay on all history", "first failing transition reported", "harness")
        + _box(604, 222, 4, "Search inside the model", "bounded, explicit outcome", "harness")
        + _box(314, 222, 5, "Commit a plan", "every action carries its prediction", "model")
        + _box(24, 222, 6, "Execute and record", "halt at the first mismatch", "harness")
        + '<g class="lp-a"><path d="M256 86H312" marker-end="url(#ah)"/><path d="M546 86H602" marker-end="url(#ah)"/><path d="M720 124V220" marker-end="url(#ah)"/>'
          '<path d="M604 260H548" marker-end="url(#ah)"/><path d="M314 260H258" marker-end="url(#ah)"/><path d="M140 222V126" marker-end="url(#ah)"/></g>'
          '<g class="lp-d"><path d="M700 48C700 8 450 8 430 46" marker-end="url(#ahd)"/><path d="M230 222L350 126" marker-end="url(#ahd)"/></g>'
          '<text class="lp-l" x="566" y="14" text-anchor="middle">replay fails: revise the rule or the representation</text>'
          '<text class="lp-l" x="300" y="182" text-anchor="start">mismatch: the rest of the plan is void</text>'
        '</svg></div><figcaption><b>Figure 4.</b> The control loop, after Schema [1] and Retrodict [2]. Outlined steps belong to the language model and filled steps to the deterministic harness. '
        'Only step 6 spends real game actions. Dashed arrows are the two ways evidence returns to the model.</figcaption></figure>')


def evidence(tag, game, title, stat, steps, source):
    rows = "".join(f'<li class="tl-{role}"><span class="tl-role">{label}</span><div>{text}</div></li>' for role, label, text in steps)
    return (f'<details class="ev"><summary><span class="ev-tag">Evidence {tag}</span><code>{game}</code>'
            f'<span class="ev-title">{title}</span><span class="ev-stat">{stat}</span></summary>'
            f'<ol class="tl">{rows}</ol><p class="ev-src">Source: {source}</p></details>')


EVIDENCE = "".join([
    evidence("A", "bp35", "Reasoning about a fact the harness had already proved", "247 s &rarr; 5.4 s", [
        ("obs", "Observed", "At step 3 the harness proved that two actions produce the same masked transition from the same state. The model stated this at once, then spent 36,514 reasoning characters and about four minutes deriving it again before choosing another probe."),
        ("diag", "Diagnosis", "The decision was correct and the cost was latency. The evidence was settled, so a full reasoning turn could add nothing."),
        ("fix", "Change", "A newly established conditional equivalence now forces the next call to be a short commit turn with reasoning disabled. The turn receives the exact relation and must choose a new low-risk probe. All other diagnostic turns keep the full budget."),
        ("ok", "Verified", "On a fresh run the forced commit took 5.37 s and 97 tokens with no reasoning tokens. The full suite passed (132 tests)."),
    ], "PR #6, commit <code>bcf4386</code>, runs <code>bp35-axis-v3</code> and <code>bp35-equivalence-v4</code>"),
    evidence("B", "ar25", "Two objects moving in opposite directions under one action", "exact motion recovered", [
        ("obs", "Observed", "The model's notes stated that both pieces move together horizontally, and it executed a long plan from that belief."),
        ("diag", "Diagnosis", "Exact replay shows one action moving a 45-cell component left by 3 and a 40-cell component right by 3. The colour-delta representation only sees strips entering and leaving when a shape overlaps its old position, so it reported no rigid translation at all."),
        ("fix", "Change", "The harness now matches normalised connected components across frames and reports a complete translation for every object, including several objects that move differently under one action."),
        ("ok", "Verified", "Real steps 18, 22 and 32 replay correctly. Level 1 was then cleared at action 21 of a fresh run."),
    ], "PR #6, commit <code>10833d0</code>"),
    evidence("C", "r11l", "A collision test that was wrong by one diagonal cell", "6 / 6 in 138 actions", [
        ("obs", "Observed", "A capture plan placed the system marker at offset (4,4) from a pickup. The game did not collect it (step 131)."),
        ("diag", "Diagnosis", "Collision had been approximated as a centre distance of at most four cells. The two 21-cell octagons have their corners removed and share no cell at that offset."),
        ("fix", "Change", "Capture checks compare the rendered cell sets. The observed successful offsets (2,4), (4,1) and (0,0) remain valid and (4,4) is rejected. Signatures accept only the item palette, after a connector line had added a structural colour to one inventory."),
        ("ok", "Verified", "The next captures succeeded at the predicted centroids, all sparse expectations matched, and the game returned WIN at step 138. The suite passed (156 tests)."),
    ], "hardening ledger, section on <code>r11l</code>"),
    evidence("D", "ka59", "More tokens did not substitute for executable state", "614,648 tokens &rarr; 7 / 7", [
        ("obs", "Observed", "Across 152 calls the model produced 614,648 completion tokens and never cleared level 2. At step 60 the selected token stayed fixed while another token moved five lattice cells; the model called the selected token &ldquo;blocked&rdquo;."),
        ("diag", "Diagnosis", "The decisive evidence was already in the trace. The model planned in screen coordinates and never promoted contact launching to a transition rule. The missing capability was executable state and not a larger prose memory."),
        ("fix", "Change", "A harness-owned state model for this mechanic family: a 3-pixel lattice parser, direct movement, bump launches, shoves, overshoot and countdown launches, transition replay and A* planning, with checked execution of at most 16 actions per batch."),
        ("ok", "Verified", "The simulator reproduces 417 of 417 reference transitions and 110 of 110 original Qwen transitions. A clean run then won all seven levels in 300 actions. Level 7 used a disclosed prior from a public trace."),
    ], "hardening ledger, section on <code>ka59</code>; PR #6, commit <code>906bc96</code>"),
    evidence("E", "dc22", "A checkpoint too large for the context on its own", "170,280 &rarr; 97,912 characters", [
        ("obs", "Observed", "The run failed at action 17 with an oversized request, although every raw exchange had already been evicted."),
        ("diag", "Diagnosis", "The remaining checkpoint was 170,280 characters. Exact cell arrays were duplicated in the verified ledger, the recent evidence and the last feedback, and the full structural graph was repeated as well. A second compaction had nothing left to evict."),
        ("fix", "Change", "Compact checkpoints keep the relational facts a decision needs (counts, bounding boxes, colour transitions, component motions, level changes) and omit the duplicated arrays, which stay available in the immutable artifacts."),
        ("ok", "Verified", "The same 17-action trace now produces a 97,912-character checkpoint: 96,416 of 131,072 tokens with the full 32,768-token diagnostic reserve. The game resumes with its actions, notes and board state intact."),
    ], "PR #6, commit <code>e18ce1a</code>"),
])

def _side(key, title, sub):
    return (f'<div class="cmp-side" data-side="{key}"><p class="cmp-h"><b>{title}</b><span>{sub}</span></p>'
            '<div class="cmp-screen"><canvas width="384" height="384" aria-hidden="true"></canvas><span class="cmp-badge"></span></div>'
            '<p class="cmp-stats"><span>actions <b class="cmp-acts">0</b></span><span>levels cleared <b class="cmp-lv">0</b></span><span class="cmp-name"></span><span class="cmp-eff"></span></p>'
            '<p class="cmp-k">What the model said before this action</p><p class="cmp-say" aria-live="off"></p></div>')


COMPARE = ('<figure class="fig wide"><div class="plate"><div class="cmp" data-src="../assets/data/ft09-compare.json">'
           '<div class="cmp-grid">'
           + _side("without", "Without the harness", "plain loop: look at the frame, reason, act")
           + _side("with", "With the harness", "perception, record and verification in code")
           + '</div><div class="cmp-ctrl"><button class="btn primary cmp-play" type="button">Play</button>'
             '<button class="btn cmp-prev" type="button" aria-label="Previous action">&larr;</button>'
             '<button class="btn cmp-next" type="button" aria-label="Next action">&rarr;</button>'
             '<button class="btn cmp-speed" type="button" aria-label="Playback speed">2&times;</button>'
             '<input class="cmp-range" type="range" min="0" max="75" value="0" step="1" aria-label="Action number">'
             '<span class="cmp-count">loading</span></div>'
             '<noscript><p>This comparison needs JavaScript. Without it: the plain loop used 17 actions on ft09 and cleared nothing; with the harness, all six levels were cleared in 75 actions.</p></noscript>'
           '</div></div><figcaption><b>Figure 3.</b> The game <code>ft09</code>, played twice from the same opening frame. Both sides advance one real action per step, so the left side stops after its 17 actions while the right side continues through all six levels. '
           'The circle marks the click and the outline marks the cells that changed. Below each game is what the model said immediately before that action. '
           'The left frames were regenerated by replaying the 17 recorded clicks through the game engine; the replay reproduces the recorded changed-cell count on all 17 actions.</figcaption></figure>'
           '<p>Without the harness, the model clicks seven times with no visible effect, then discovers that a click flips a tile and adopts the goal of turning every blue tile red. '
           'That is not the rule: the tiles must match the miniature pattern in the centre of each panel. After 17 actions and 31 model calls it has cleared no level, and the run ended when the accumulated context '
           '(1.48 million prompt tokens) exceeded the server limit. With the harness, the first click is a stated probe, the next three remove the remaining mismatches against the miniature, and the level clears on the fourth action. '
           'The same run then clears the remaining five levels, at actions 11, 25, 41, 62 and 75, without a single action whose outcome the model had not predicted.</p>'
           '<div class="note"><b>Not a controlled experiment</b><p>The two runs differ in more than the harness. The left run used an earlier checkpoint (Qwen3.6-27B-FP8) and the right run used Qwen3.8-27B. '
           'The comparison illustrates the failure modes listed above; it does not measure the size of the harness effect.</p></div>')


CTRL = ('<div class="cmp-ctrl"><button class="btn primary cmp-play" type="button">Play</button>'
        '<button class="btn cmp-prev" type="button" aria-label="Previous action">&larr;</button>'
        '<button class="btn cmp-next" type="button" aria-label="Next action">&rarr;</button>'
        '<button class="btn cmp-speed" type="button" aria-label="Playback speed">2&times;</button>'
        '<input class="cmp-range" type="range" min="0" max="1" value="0" step="1" aria-label="Action number">'
        '<span class="cmp-count">loading</span></div>')


DUCK = {"tn36": [2, 7], "lf52": [1, 10], "cn04": [1, 6], "bp35": [0, 9], "wa30": [0, 9], "lp85": [4, 8], "r11l": [1, 6], "tu93": [4, 9], "sp80": [0, 6], "m0r0": [1, 6], "vc33": [2, 7], "ar25": [1, 8], "ka59": [0, 7], "sc25": [0, 6], "sk48": [0, 8], "dc22": [1, 6], "cd82": [2, 6], "ft09": [2, 6], "g50t": [1, 7], "ls20": [1, 7], "re86": [4, 8], "s5i5": [1, 8], "sb26": [1, 8], "su15": [1, 9], "tr87": [1, 6]}


def game(name, levels, actions, calls, agent, human, condition, stuck, harness, helps, note=""):
    top = max(human)
    rows = "".join(f'<div class="bar-row"><span class="bar-l">L{i}</span><div class="bar-pair">'
                   f'<i class="bar-h" style="width:{h / top * 84:.1f}%"><em>{h}</em></i>'
                   f'<i class="bar-a" style="width:{a / top * 84:.1f}%"><em>{a}</em></i></div></div>'
                   for i, (a, h) in enumerate(zip(agent, human), 1))
    items = "".join(f"<li>{x}</li>" for x in harness)
    note = f'<p class="game-note">{note}</p>' if note else ""
    return (f'<details class="ev game"><summary><span class="ev-tag">{levels} / {levels}</span><code>{name}</code>'
            f'<span class="ev-title">{condition}</span><span class="ev-stat">{actions} actions &middot; human {sum(human)}</span></summary>'
            f'<div class="game-body"><div class="cmp" data-src="../assets/data/replay-{name}.json">'
            f'<div class="cmp-side" data-side="run"><div class="cmp-screen"><canvas width="384" height="384" aria-hidden="true"></canvas><span class="cmp-badge"></span></div>'
            '<p class="cmp-stats"><span>actions <b class="cmp-acts">0</b></span><span>levels cleared <b class="cmp-lv">0</b></span><span class="cmp-name"></span><span class="cmp-eff"></span></p>'
            '<p class="cmp-k">Reason logged with this action</p><p class="cmp-say"></p></div>' + CTRL + '</div>'
            f'<div class="game-notes"><h4>Where the model alone got stuck</h4><p>{stuck}</p>'
            f'<h4>What the harness supplies</h4><ul>{items}</ul>'
            f'<h4>Why that is enough</h4><p>{helps}</p>{note}'
            f'<h4>Actions per level</h4><div class="bars">{rows}</div>'
            f'<p class="bars-key"><i class="bar-h"></i>human baseline <i class="bar-a"></i>this system &nbsp; {calls} model calls in total</p>'
            f'<p class="game-duck">Duck baseline on this game <a href="#ref-8">[8]</a>: {DUCK[name][0]} of {DUCK[name][1]} levels.</p></div></div></details>')


GAMES = "".join([
    game("ft09", 6, 75, 26, [4, 7, 14, 16, 21, 13], [43, 12, 23, 28, 65, 37],
         "Single run from empty memory; no mispredicted action",
         "A flat list of coloured regions hides the fact that each panel contains a worked example of its own target. The model treated the panels as separate puzzles, and on later levels it lost track of palettes that change from level to level and of glyphs that cycle through several colours.",
         ["A table of tile positions for every repeated lattice, in panel coordinates and not pixel coordinates", "Ordered runs of solid swatches, so that a miniature can be read as a sequence", "Observed forward and reverse palette edges: which colour a click turns into which", "A guard that stops an empty marker with a uniform surround from being read as a tile", "Replay certification of a complete glyph plan, followed by deterministic execution"],
         "With panel coordinates and the miniature side by side, the comparison between them is a lookup that the model performs reliably. The plan for a level is then certified by replay before any action is spent, which is why no action in this run had an outcome the model had not predicted."),
    game("sb26", 8, 124, 90, [9, 15, 15, 15, 17, 19, 17, 17], [18, 28, 18, 19, 31, 23, 58, 18],
         "Completed across resumed sessions; 13 mispredicted actions",
         "Flat objects cannot express containers nested inside containers, hollow tokens that refer to another box, a reading order that recurses or cycles, or a stable assignment of tokens to slots. The model described individual boxes correctly and could not combine them.",
         ["A container and reference graph: boxes contain slots, slots contain solid tokens or hollow references", "A finite recursive assignment solver over that graph", "Verification of the goal predicate against real submissions", "Decision guidance that points at the contradicting transition when notes and record disagree", "Certified plan compilation and automatic execution, including cyclic traversal"],
         "The graph gives the model one object to reason about in place of dozens of rectangles. It proposed the depth-first reading itself; the harness checked that reading against every completed level and then solved the assignment, so later levels were mostly bookkeeping.",
         "Every one of the 13 mispredicted actions halted its plan at once, which is visible in the replay as a highlighted step."),
    game("r11l", 6, 138, 145, [10, 18, 39, 18, 28, 25], [22, 33, 51, 26, 52, 49],
         "Every level below its human baseline; pickup representation informed by a public reference trace",
         "The model treated the markers at the centre of each graph as decoration, so it never formed the idea that a marker is the mean position of its nodes. Later, the harness itself approximated octagon collisions with bounding boxes, and a connector line that crossed a marker contaminated its colour signature.",
         ["A graph parser that recovers systems, nodes and the floor-mean marker of each system", "Ordered pickup signatures restricted to the item palette", "Exact octagon overlap computed from rendered cells", "A planner for capture and docking that moves whole footprints", "Verified execution across several systems, protecting docks that are already complete"],
         "Once the marker is defined as a computed quantity, moving it to a target is a geometry problem that the planner solves exactly. The model's role reduces to choosing which system to complete next and to designing the probe that confirmed how pickups are collected."),
    game("ka59", 7, 300, 2, [11, 38, 33, 39, 20, 46, 113], [28, 109, 51, 51, 33, 132, 326],
         "Levels 1 to 6 planned by the simulator; level 7 used a disclosed prior from a public trace",
         "The model represented boxes on the screen and not objects on a lattice, read the digits on tokens as labels when they are launch distances, and kept retrying direct movement after contact had launched a different object. In 152 calls and 614,648 completion tokens it never cleared level 2.",
         ["A parser for tokens, frames, walls and countdown gauges on a 3-pixel lattice", "An object and contact simulator: direct moves, bump launches, shoves, overshoot, ranged countdown launches", "Replay of the simulator against recorded transitions (417 of 417 reference and 110 of 110 original)", "An A* planner and a compiler from plans to sparse per-action expectations", "Checked execution in batches of at most 16 actions"],
         "The mechanics are deterministic, so once they are executable the game becomes a search problem. This run needed only two model calls; the rest was planning and checked execution.",
         "On level 7 the generic search exceeded one million states. The 113 actions shown for that level come from a prior pruned from a public Schema trajectory and verified from the real entry state, so that level is not evidence of generalisation."),
    game("lp85", 8, 162, 147, [7, 41, 23, 17, 14, 20, 13, 27], [17, 38, 31, 16, 41, 60, 26, 159],
         "Completed across resumed sessions; the final 21 actions needed no model call",
         "Level 2 couples several tokens on interlocking tracks, and the model spent a full ten-action lap on one row and reversed its only useful move. Level 3 replaces the rectangular layout with two overlapping sparse cycles, which a rectangular parser split into unrelated columns. On level 8 it transcribed visible squares repeatedly and did not see that one operation appears at three scales.",
         ["Exact tile permutations learned from observed transitions, for rows, perimeters, pinwheels and sparse cycles", "A sparse lattice parser: dominant aligned phase, eight-neighbour tile graph, bounded cycle enumeration", "Tracks recovered as a diagonal lead-in followed by a straight stem, with entry registers and a shared conveyor", "Joint search over all token positions, with tokens tracked by halo colour", "Plans compiled to checked actions: every token coordinate is verified after every click"],
         "Each control is a permutation of tile positions, and a permutation can be learned exactly from one or two observations. After that, reaching the targets is a joint shortest-path search. On level 8 the controller found a 20-action plan after six probes and used 27 actions in total against a human reference of 159."),
    game("tr87", 6, 189, 65, [32, 38, 41, 36, 18, 24], [54, 58, 40, 45, 71, 146],
         "Completed with no resets and no mispredicted action; the final 23 actions needed no model call",
         "The game is about symbols and a dictionary that maps one symbol to another. The model read editable glyph identities as rotations and reflections of one another, transcribed the finite symbol wheels again and again, took editable dictionary boxes for fixed examples, and could not compose the final chain of two mappings (10 to 7 to 11).",
         ["Neutral identities for framed glyphs, so that a symbol is a name and not a picture to be rotated", "Persistent edges for each finite symbol wheel and for the cursor, learned once from observed transitions", "A guard that stops the agent from undoing its own last edit", "A parser for framed words and a direct constraint solver for the editable dictionary", "Composition of chained finite transducers, with checked execution one step at a time"],
         "Once glyphs are names and each wheel is a known cycle, a level is a small constraint problem: which dictionary entries must change so that the input word maps to the target word. The solver answers that exactly, including when two mappings have to be chained, and the plan is executed with a frame check after every action."),
])


# ---------------------------------------------------------------------------------------------
# Diagrams for the planned test-time communication section (same visual language as the loop figure)
# ---------------------------------------------------------------------------------------------
def _b(x, y, w, h, title, sub="", cls="lp-m", small=False):
    ty = y + h / 2 + (5 if not sub else -3)
    t = f'<text class="{"lp-t2" if small else "lp-t"}" x="{x + w / 2}" y="{ty}" text-anchor="middle">{title}</text>'
    if sub:
        t += f'<text class="lp-s" x="{x + w / 2}" y="{ty + 17}" text-anchor="middle">{sub}</text>'
    return f'<g class="{cls}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/>{t}</g>'


def _dg(uid, w, h, label, body):
    return (f'<svg class="loop" viewBox="0 0 {w} {h}" role="img" aria-label="{label}"><defs>'
            f'<marker id="a{uid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="lp-ah"/></marker>'
            f'<marker id="d{uid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="lp-ahd"/></marker>'
            f'</defs>{body}</svg>')


def _fig(n, svg, caption):
    return f'<figure class="fig"><div class="plate">{svg}</div><figcaption><b>Figure {n}.</b> {caption}</figcaption></figure>'


def _fig_best_vs_team():
    ys = [64 + i * 58 for i in range(4)]
    body = ('<text class="lp-h1" x="20" y="28">Best-of-4</text><text class="lp-h2" x="20" y="46">every agent must make every discovery</text>'
            '<text class="lp-h1" x="470" y="28">Team-of-4</text><text class="lp-h2" x="470" y="46">a discovery is made once and adopted by the others</text>')
    arrows, dashed = "", ""
    for i, y in enumerate(ys):
        body += _b(20, y, 84, 40, "game", "", "lp-h", True) + _b(142, y, 118, 40, f"agent {i}", "", "lp-m", True)
        arrows += f'<path d="M106 {y + 20}H140" marker-start="url(#a6)" marker-end="url(#a6)"/><path d="M262 {y + 20}H306" marker-end="url(#a6)"/>'
        body += _b(470, y, 84, 40, "game", "", "lp-h", True) + _b(592, y, 118, 40, f"agent {i}", "", "lp-m", True)
        arrows += f'<path d="M556 {y + 20}H590" marker-start="url(#a6)" marker-end="url(#a6)"/>'
        dashed += f'<path d="M712 {y + 20}H746" marker-start="url(#d6)" marker-end="url(#d6)"/>'
    body += _b(308, 64, 100, 214, "keep the", "best result", "lp-h", True)
    body += _b(748, 64, 96, 214, "shared log", "append-only", "lp-x", True)
    body += '<path class="lp-rule" d="M440 14V300"/>'
    body += '<text class="lp-l" x="592" y="298">findings, disconfirmations, scores</text>'
    return _dg(6, 860, 310, "Best-of-4 runs four isolated agents and keeps the best result. Team-of-4 gives each agent its own game and connects all of them through one shared append-only log.",
               body + f'<g class="lp-a">{arrows}</g><g class="lp-d">{dashed}</g>')


def _fig_one_stream():
    ys = [40 + i * 56 for i in range(4)]
    body = _b(16, 96, 170, 96, "Frozen state", "observation + verified history", "lp-h", True)
    arrows = ""
    for i, y in enumerate(ys):
        body += _b(246, y, 150, 40, f"agent {i}", "inspect, test, search", "lp-m", True)
        arrows += f'<path d="M188 144C215 144 215 {y + 20} 244 {y + 20}" marker-end="url(#a7)"/><path d="M398 {y + 20}C428 {y + 20} 428 144 456 144" marker-end="url(#a7)"/>'
    body += _b(458, 96, 176, 96, "Harness", "verify, accept one proposal", "lp-h", True)
    body += _b(694, 96, 150, 96, "Game", "one real action or batch", "lp-h", True)
    arrows += '<path d="M636 144H692" marker-end="url(#a7)"/>'
    body += _b(246, 286, 388, 44, "shared log", "discoveries, proposals, verification outcomes", "lp-x", True)
    dashed = '<path d="M769 194V308H636" marker-end="url(#d7)"/><path d="M244 308H100V194" marker-end="url(#d7)"/>'
    body += '<text class="lp-l" x="650" y="330">transition is recorded</text><text class="lp-l" x="16" y="352">every context resumes from the common new state</text>'
    return _dg(7, 860, 366, "One synchronised discovery round with a single action stream: four agents work from the same frozen state, the harness verifies and accepts one proposal, one action is executed, and the transition is broadcast through the shared log.",
               body + f'<g class="lp-a">{arrows}</g><g class="lp-d">{dashed}</g>')


def _fig_event_bus():
    body = (_b(60, 36, 230, 84, "Master", "strategy, objective, decision criteria", "lp-m")
            + _b(60, 230, 230, 84, "World modeler", "exact board, mechanics, backtests", "lp-m")
            + _b(400, 36, 130, 278, "Event bus", "append-only", "lp-h")
            + _b(596, 36, 240, 84, "Coordinator", "deduplicates, flags conflicts", "lp-m")
            + _b(596, 230, 240, 84, "Compact handoff", "evidence, conflicts, assignments", "lp-x"))
    arrows = ('<path d="M292 78H398" marker-end="url(#a8)"/><path d="M292 272H398" marker-end="url(#a8)"/>'
              '<path d="M532 78H594" marker-end="url(#a8)"/><path d="M716 122V228" marker-end="url(#a8)"/>')
    dashed = ('<path d="M716 316V350H24V78H58" marker-end="url(#d8)"/><path d="M24 272H58" marker-end="url(#d8)"/>')
    body += ('<text class="lp-l" x="300" y="66">reasoning and</text><text class="lp-l" x="300" y="98">tool events</text>'
             '<text class="lp-l" x="300" y="260">reasoning and</text><text class="lp-l" x="300" y="292">tool events</text>'
             '<text class="lp-l" x="40" y="368">injected before each worker&#8217;s next inference call</text>'
             '<text class="lp-l" x="728" y="180">compaction</text>')
    return _dg(8, 860, 380, "Asynchronous event bus: the master and the world modeler append reasoning and tool events to an append-only bus, a coordinator compacts them into a handoff, and the handoff is injected before each worker's next inference call.",
               body + f'<g class="lp-a">{arrows}</g><g class="lp-d">{dashed}</g>')


def _fig_fifo():
    body, n = "", 16
    for i in range(n):
        x = 20 + i * 36
        cls = "lp-g" if i < 6 else "lp-m"
        body += f'<g class="{cls}"><rect x="{x}" y="62" width="30" height="30"/><text class="lp-s" x="{x + 15}" y="82" text-anchor="middle">{i + 1}</text></g>'
    body += _b(616, 54, 228, 46, "reserved", "32,768-token reply + tool schemas", "lp-h", True)
    body += ('<text class="lp-h2" x="20" y="22">shared event log: append-only, nothing is ever deleted</text>'
             '<path class="lp-br2" d="M236 50H844"/><text class="lp-h2" x="236" y="44" style="font-size:10.5px">one request</text>'
             '<path class="lp-br" d="M20 108V116H230V108"/><text class="lp-l" x="20" y="134">dropped from the prompt first</text><text class="lp-l" x="20" y="149">(still in the log)</text>'
             '<path class="lp-br" d="M236 108V116H590V108"/><text class="lp-l" x="236" y="134">newest suffix that passes the provider&#8217;s fits() check</text>')
    return _dg(9, 860, 162, "The event log keeps every event. A prompt takes the newest events that fit after reserving the reply window and tool schemas; older events are dropped from the prompt but stay in the log.", body)


FIG_TEAM = _fig(6, _fig_best_vs_team(), "Best-of-<em>N</em> against team-of-<em>N</em>, as studied by Park et al. [9]. In both, every agent has its own game session. The only difference is the shared append-only log.")
FIG_STREAM = _fig(7, _fig_one_stream(), "The submission adaptation: one synchronised discovery round with a single action stream. Outlined boxes are language-model contexts and filled boxes are deterministic. Dashed arrows carry the result of the one real action back to every context.")
FIG_BUS = _fig(8, _fig_event_bus(), "The revised live design. Two workers append completed reasoning and tool events to a lossless bus; a coordinator, which never acts, compacts them; the handoff is injected before each worker's next inference call. In the architecture probe the commit tool is not exposed, so no real action is executed.")
FIG_FIFO = _fig(9, _fig_fifo(), "The FIFO inbox. Each request reserves the reply window and the tool schemas, then takes the newest events that fit. Older events leave the active context without leaving the log.")


# ---- scoreboard of all 25 public games: this system against the Duck baseline run (tools/data/duck_kaggle_public25.json)
import json as _json
from pathlib import Path as _Path
_DUCK = _json.loads((_Path(__file__).parent / "data" / "duck_kaggle_public25.json").read_text())
_MINE = {  # game: (levels cleared, actions, note, actions per cleared level); games not listed have not been attempted
    "ft09": (6, 75, "single run from empty memory", [4, 7, 14, 16, 21, 13]),
    "sb26": (8, 124, "across resumed sessions", [9, 15, 15, 15, 17, 19, 17, 17]),
    "r11l": (6, 138, "every level below its human baseline", [10, 18, 39, 18, 28, 25]),
    "ka59": (7, 300, "level 7 used a disclosed public-trace prior", [11, 38, 33, 39, 20, 46, 113]),
    "lp85": (8, 162, "across resumed sessions", [7, 41, 23, 17, 14, 20, 13, 27]),
    "tr87": (6, 189, "no resets, no mispredicted action", [32, 38, 41, 36, 18, 24]),
    "su15": (6, 212, "level 7 in progress", [25, 15, 18, 19, 9, 41], 45.12),
    "re86": (6, 641, "level 7 in progress", [27, 42, 64, 141, 156, 209], 47.58),
    "lf52": (2, 289, "level 3 in progress", [38, 108], 3.33),
    "ar25": (1, 42, "checkpointed on level 2", [21], 2.78), "cn04": (1, 133, "level 2 in progress", [21], 4.76),
    "bp35": (0, 30, "checkpointed", []), "dc22": (0, 100, "checkpointed", []), "g50t": (0, 149, "in progress", []),
    "ls20": (0, None, "pilot run", []), "cd82": (0, None, "pilot run", []),
}


# Unofficial names (community backronyms; g50t, su15, re86 and tr87 changed after checking the public Schema
# notes [1]) and a one-paragraph description of each game, from those notes and the hardening ledger.
_GAMES = {
    "ar25": ("axis-reflections-25", "Pieces sit on either side of a mirror axis. Pieces and the axis can both be moved, and the reflected copies have to cover the targets."),
    "bp35": ("buoyancy-puzzle-35", "A balloon character moves left or right and then rises by itself until something stops it. Clicking pops blocking tiles from a distance, coming to rest under spikes ends the attempt, and the world scrolls as the balloon climbs towards its cradle."),
    "cd82": ("color-drop-82", "A colour is chosen in a legend, a pouring piece is rotated, and colour is poured into a tank from above. The layers in the tank have to form the required pattern."),
    "cn04": ("connector-network-04", "Pieces on a three-cell lattice carry connectors. Pieces are selected, rotated and moved so that their connectors bond, within a move budget that differs by level."),
    "dc22": ("drawbridge-controls-22", "A walker has to reach a goal tile. Buttons and ports drive machines that open the route: a rotating arm that serves as a bridge, a cage on a track, conveyors and portals."),
    "ft09": ("flip-tiles-09", "Clicking a tile advances its colour. Small patterned tiles state which of their eight neighbours must match a colour and which must not. Later levels add buttons that flip several neighbours at once."),
    "g50t": ("ghost-50-teamwork", "A ring moves through corridors. One action sends it back to the start and switches state, and a ghost then replays the path recorded in the other state. The ghost holds a spring-loaded barrier open while the ring passes to the goal."),
    "ka59": ("knockback-alignment-59", "Tokens stand on a lattice. Walking the selected token into another one launches that token by the number printed on it, through walls if necessary. Every token has to end in its frame."),
    "lf52": ("leap-frog-52", "Peg solitaire: a peg jumps over a neighbour into an empty cell and removes it. Carts on rails carry pegs between boards. A level ends when one peg is left and no jump remains."),
    "lp85": ("loop-placement-85", "Buttons rotate tiles around loops: rows, rings, diagonal cycles and, on the last level, entry registers feeding a shared conveyor. Coloured tiles have to reach their brackets within a click budget."),
    "ls20": ("lock-smith-20", "A block walks a map one block-width at a time. Stepping on rotators and changers alters the key pattern shown in the display, and the block enters the lock when the key matches it."),
    "m0r0": ("mirror-0-reunion-0", "Two avatars move as mirror images of each other. Both have to be steered past deadly tiles, keys and gates so that they meet on the axis."),
    "r11l": ("rigging-11-links", "Clicking selects a node or moves the selected one. Each group of linked nodes has a marker at the average of its nodes, and every marker has to dock on the ring with the same colour signature. Later levels require collecting coloured pickups with the marker first."),
    "re86": ("reshape-elements-86", "Shapes are selected, moved in three-cell steps, recoloured at palettes and, from level 6, deformed by pushing them against obstacles, until each silhouette covers the boxes of its colour."),
    "s5i5": ("stretch-5-insert-5", "Control boxes lengthen or shorten bars by three cells, and bars push one another. Every bar's pointer has to dock in its diamond."),
    "sb26": ("sequence-builder-26", "The top row shows a code. Tokens are placed into slots inside boxes, and some slots are references to other boxes. The sequence read from the boxes, following the references, has to equal the code before it is submitted."),
    "sc25": ("spell-casting-25", "A head walks a field. Cards on the left act as spells: the pattern is the verb (resize, teleport, dissolve) and the colour selects what it applies to. The spells clear the way to the dock."),
    "sk48": ("sliding-kebab-48", "An engine on a vertical track extends a rope that skewers and pushes blocks, and fixed vertical chains thread blocks so that they can only slide along them."),
    "sp80": ("spill-planning-80", "Rectangular pieces are moved to deflect water falling from dispensers. A pour succeeds only if every cup fills and no water touches the floor."),
    "su15": ("size-up-15", "A click moves a piece. Pieces that meet merge into the next size tier, and the required tier has to be delivered to a disk. Wandering glyphs chase pieces and eat them, and on some levels a glyph itself has to be parked on a disk."),
    "tn36": ("toggle-navigation-36", "A row of icons is a program. Each instruction can be switched on or off and its direction changed. Running the program has to move the key onto the lock, and a failed run costs time."),
    "tr87": ("translate-runes-87", "A dictionary pairs rotated glyphs, sometimes in chains. The answer word, and on later levels the dictionary itself, is edited with a cursor and a symbol wheel until translating the clue gives the answer."),
    "tu93": ("traverse-unharmed-93", "A maze has to be walked from start to goal. From the later levels, sentries chase the player along the shortest path and kill on contact."),
    "vc33": ("volume-control-33", "Tanks are separated by rods. Valves move water between tanks, floats ride the surface, and a door opens when the levels on both sides are flush with it. Every float has to reach the gate of its colour."),
    "wa30": ("warehouse-agents-30", "Boxes are grabbed, carried and released onto goal areas. Autonomous carrier agents move boxes as well, one step per player action, and some walls let a carried box through and stop the player."),
}


def _strip(label, cls, values, total, cleared=None):
    """One line of the per-level grid. `cleared` is how many leading levels count as cleared (None: all shown plainly)."""
    cells = ""
    for k in range(total):
        v = values[k] if k < len(values) and values[k] else ""
        on = cleared is not None and k < cleared
        cells += f'<i class="{"on" if on else ""}">{v if (on or cleared is None) else ""}</i>'
    return f'<span class="lv-l">{label}</span>{cells}'


def _board():
    def rank(g):
        mine = _MINE.get(g)
        complete = bool(mine) and mine[0] == _DUCK[g]["of"]
        return (-complete, -(mine[0] if mine else -1), -_DUCK[g]["levels"], g)
    rows = ""
    for g in sorted(_DUCK, key=rank):
        d, total = _DUCK[g], _DUCK[g]["of"]
        mine = _MINE.get(g)
        state = "done" if mine and mine[0] == total else "prog" if mine else "todo"
        label = {"done": "complete", "prog": "in progress", "todo": "not attempted"}[state]
        head = "".join(f"<i>L{k + 1}</i>" for k in range(total))
        grid = (f'<div class="lv" style="--n:{total}"><span class="lv-l"></span>{head}'
                + _strip("human", "h", d["human"], total)
                + _strip("this system", "me", mine[3] if mine else [], total, mine[0] if mine else 0)
                + _strip("Duck", "duck", d["per_level"], total, d["levels"]) + "</div>")
        if mine:
            acts = f'{mine[1]} actions' if mine[1] else "actions not recorded"
            score = "score 100" if state == "done" else f"score {mine[4]:g} so far" if len(mine) > 4 else "score not final"
            me = f'<td class="b-num"><b>{mine[0]} / {total}</b><span>{acts}</span><span>{score}</span></td>'
        else:
            me = f'<td class="b-num"><b class="dim">0 / {total}</b></td>'
        human_total = sum(d["human"])
        note = f'<span class="b-note">{mine[2]}</span>' if mine else ""
        name, desc = _GAMES[g]
        rows += (f'<tr class="b-{state}"><th scope="row"><code>{g}</code><span class="st st-{state}">{label}</span>'
                 f'<button class="b-tog" type="button" aria-expanded="true" aria-controls="about-{g}">{name}</button>{note}</th>'
                 f'<td class="b-bar">{grid}</td><td class="b-num"><b>{human_total}</b><span>actions</span></td>{me}'
                 f'<td class="b-num"><b>{d["levels"]} / {total}</b><span>{d["actions"]} actions</span><span>score {d["score"]:g}</span></td></tr>'
                 f'<tr class="b-desc b-{state}" id="about-{g}"><td colspan="5"><p><b>{name}.</b> {desc}</p></td></tr>')
    mine_levels = sum(v[0] for v in _MINE.values())
    duck_levels = sum(v["levels"] for v in _DUCK.values())
    total_levels = sum(v["of"] for v in _DUCK.values())
    return ('<div class="board-wrap"><table class="board"><thead><tr><th scope="col">Game</th>'
            '<th scope="col">Actions per level <em>a filled cell is a cleared level; the number is the actions it took</em></th>'
            '<th scope="col" class="b-num">Human <em>all levels</em></th>'
            '<th scope="col" class="b-num">This system <em>Qwen3.8-27B, H200</em></th>'
            '<th scope="col" class="b-num">Duck baseline <em>Flash-Next, Kaggle GPU</em></th></tr></thead>'
            f'<tbody>{rows}</tbody><tfoot><tr><th scope="row" colspan="2">Levels cleared</th><td></td>'
            f'<td class="b-num"><b>{mine_levels} / {total_levels}</b><span>{len(_MINE)} games attempted</span><span>6 games at score 100</span></td>'
            f'<td class="b-num"><b>{duck_levels} / {total_levels}</b><span>25 games played</span><span>mean score 5.74</span></td></tr></tfoot></table></div>')


BOARD = _board()


def bars(game, agent, human):
    top = max(human)
    rows = ""
    for i, (a, h) in enumerate(zip(agent, human), 1):
        rows += (f'<div class="bar-row"><span class="bar-l">L{i}</span><div class="bar-pair">'
                 f'<i class="bar-h" style="width:{h / top * 86:.1f}%"><em>{h}</em></i>'
                 f'<i class="bar-a" style="width:{a / top * 86:.1f}%"><em>{a}</em></i></div></div>')
    return (f'<div class="bars"><p class="bars-k"><code>{game}</code><span>{sum(agent)} actions against a human baseline of {sum(human)}</span></p>{rows}</div>')


CHARTS = ('<figure class="fig"><div class="plate"><div class="bars-grid">'
          + bars("r11l", [10, 18, 39, 18, 28, 25], [22, 33, 51, 26, 52, 49])
          + bars("ka59", [11, 38, 33, 39, 20, 46, 113], [28, 109, 51, 51, 33, 132, 326])
          + '</div><p class="bars-key"><i class="bar-h"></i>human baseline <i class="bar-a"></i>this system</p></div>'
          '<figcaption><b>Figure 6.</b> Real actions per level against the human baseline, for the two games where per-level counts were recorded. '
          'Level 7 of <code>ka59</code> used a disclosed action prior from a public trace. Shorter is better.</figcaption></figure>')

CITE = """    <h2 id="cite">Cite this page</h2>
    <pre><code>@misc{kancharla2026verified,
  title        = {Verified World Models for Interactive Reasoning in ARC-AGI-3},
  author       = {Kancharla, Ritwika},
  year         = {2026},
  howpublished = {\\url{https://ritwikareddykancharla.github.io/projects/arc-agi-3.html}},
  note         = {Work in progress}
}</code></pre>
"""

ARC3 = dict(
    hero=dict(img="grotto", accent="#0f7a5a", pos="50% 60%", alt="A hidden grotto with a waterfall falling into a clear green pool, stone steps leading away through ferns and flowers."),
    title="Verified World Models for ARC-AGI-3 | Ritwika Kancharla",
    description="An open 27B language model paired with a deterministic verification harness completes six public ARC-AGI-3 games without fine-tuning. Method, per-game results, negative results and limitations.",
    eyebrow="ARC Prize 2026, ongoing",
    h1="Verified World Models for Interactive Reasoning in ARC-AGI-3",
    scripts=("compare.js",),
    meta=["Ritwika Kancharla", "September 2026", "Work in progress"],
    links=[("Competition", "https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3"),
           ("Hardening sweep (PR #6)", "https://github.com/ritwikareddykancharla/arc-agi3/pull/6")],
    abstract="""<p>ARC-AGI-3 evaluates an agent on small interactive games for which no rules, goals or instructions are provided. This project studies whether an open-weight 27B language model (Qwen3.8-27B), used without any fine-tuning, can solve such games when it is paired with a deterministic software harness. The model proposes hypotheses about the game. The harness owns perception, an immutable record of every transition, replay verification of each proposed rule, bounded search, and guarded execution of plans.</p>
<p>The system has completed six of the 25 released public games with the maximum local score of 100: <code>ft09</code> (6 of 6 levels, 75 actions), <code>sb26</code> (8 of 8, 124 actions), <code>r11l</code> (6 of 6, 138 actions), <code>ka59</code> (7 of 7, 300 actions), <code>lp85</code> (8 of 8, 162 actions) and <code>tr87</code> (6 of 6, 189 actions). The final level of <code>ka59</code> used an action prior derived from a public reference trace, which is disclosed below. Ten further games have been attempted and are partially solved or unsolved. All results are on public games that were studied during development. They validate the harness design and are not an estimate of leaderboard performance.</p>""",
    body=f"""
    <figure class="fig"><div class="plate"><div class="frames">
      <div><div class="frame"><img src="{I3}ft09-play.gif" width="256" height="270" alt="Animation of the game ft09 played from the first level to the last. Tiles in a grid change colour one click at a time until each level completes."></div><span class="cap">ft09: 6 of 6 levels, 75 actions</span></div>
      <div><div class="frame"><img src="{I3}sb26-play.gif" width="256" height="270" alt="Animation of the game sb26. Coloured tokens are selected from a row at the bottom and placed into slots inside framed containers, level after level."></div><span class="cap">sb26: 8 of 8 levels, 124 actions</span></div>
    </div></div>
    <figcaption><b>Figure 1.</b> Qwen3.8-27B playing two public games. Every frame is taken from the saved run logs. The row of squares beneath each game counts completed levels. The model received no description of the games, the actions or the objective.</figcaption></figure>

    <h2 id="problem">Problem statement</h2>
    <p>In ARC-AGI-2 a solver receives several solved examples and one test input. ARC-AGI-3 removes the examples. The agent receives a 64&times;64 frame with 16 colours and a small action set: directional actions, a few buttons, a click at a chosen coordinate, and a reset. It must determine, by acting, which parts of the frame belong to the game world, which parts are counters or legends, what each action does, and what condition completes a level. Levels within one game share their mechanics and increase in difficulty.</p>
    <p>The official metric is relative human action efficiency (RHAE) <a href="#ref-7">[7]</a>. It compares the number of real actions used on each level with the actions of a first-time human player, penalises the excess quadratically, gives no credit for a level that is not finished, and weights later levels more heavily than earlier ones. A wasted action is therefore expensive, and knowledge that carries over to later levels is valuable. Twenty-five games have been released publicly. The competition itself runs as a Kaggle code competition on hidden games with internet access disabled, which means that a submitted agent must carry its model with it.</p>

    <figure class="fig wide"><div class="plate">
      <div class="frame"><img src="{I3}ft09-levels.png" width="1192" height="192" alt="Six opening frames of ft09, one per level. Each shows a grid of square tiles in two colours with a few small patterned tiles."></div>
      <span class="cap" style="margin-bottom:18px">ft09, levels 1 to 6</span>
      <div class="frame"><img src="{I3}sb26-levels.png" width="1592" height="192" alt="Eight opening frames of sb26, one per level. Each has a row of coloured outlines at the top, framed boxes with empty slots in the middle, and a row of coloured tokens at the bottom."></div>
      <span class="cap">sb26, levels 1 to 8</span>
    </div>
    <figcaption><b>Figure 2.</b> Opening frames of every level of two games. In <code>ft09</code> a few tiles carry a small pattern that specifies the target state of a panel. In <code>sb26</code> a target row at the top specifies the order in which tokens must be read from the boxes below; from level 2 onward, boxes refer to other boxes.</figcaption></figure>

    <h2 id="related">Prior work and what this project borrows</h2>
    <p>This project did not invent its central idea. It belongs to the family of executable world models: a language model writes a program that describes the environment, the program is tested against what has actually been observed, and planning happens inside the tested program. WorldCoder <a href="#ref-3">[3]</a> introduced this for structured environments. Two systems for ARC-AGI-3, Schema <a href="#ref-1">[1]</a> and Retrodict <a href="#ref-2">[2]</a>, are the direct sources of the design described below, and Tycho <a href="#ref-4">[4]</a> belongs to the same family. An ablation study <a href="#ref-5">[5]</a> reports that an executable model that is not verified by replay can perform worse than plain text notes, which is why verification against the record is the centre of this design.</p>

    <h3>Schema</h3>
    <p>Schema (Zeng et al., Impossible Research, UC Berkeley and CMU) treats the agent as a physicist. The agent must decide what the pixels are and how they move, and it keeps both decisions in one editable Python program with three functions: <code>parse_obs</code> (what the world is), <code>step</code> (how it changes) and <code>is_goal</code> (what counts as winning). A failed prediction may revise either the rules or the representation itself. Every real transition is appended to an immutable timeline. Inside one deliberation the agent writes code, replays the program against the full timeline, and searches inside the program only after the replay succeeds; a separate commit channel is the only operation that spends real actions, and one mismatch voids the rest of a committed plan. The authors report that the same frontier models improve from 42.83% under a generic coding-agent harness to 98.98% mean RHAE on the 25 public games. That figure is self-reported, on the public set, with a fallback to a second model on low-scoring games. The source code is not released, but 50 full trajectories and a scorer are public <a href="#ref-1">[1]</a>.</p>

    <h3>Retrodict</h3>
    <p>Retrodict (Ryan Brown) is the inexpensive end of the same family. It treats each game as a laboratory notebook: every frame is appended to a log, a device it takes from RGB-Agent <a href="#ref-6">[6]</a>, and a hypothesis is first replayed over the recorded frames in a few lines of Python. This check is the retrodiction that gives the system its name, and a hypothesis that fails it costs no game action. Each model reply must end with a plan in which every action carries the cells it expects to see afterwards; the runner executes the plan without further model calls and halts at the first expectation that fails. A short playbook file survives context resets and marks each statement as checked against the log or still assumed. A full simulator is written only as an escalation, after a level has consumed about 300 actions or two resets. Retrodict reports 99.86% mean RHAE on the public games on an official scorecard, using 7,703 actions and about 660 million tokens of a frontier model <a href="#ref-2">[2]</a>.</p>

    <h3>What was adopted, and how it was changed</h3>
    <div class="tablewrap wide"><table>
      <thead><tr><th>Idea</th><th>Source</th><th>How it is used here</th><th>What changed for a 27B model</th></tr></thead>
      <tbody>
        <tr><td>State and mechanism in one editable program</td><td>Schema</td><td>The world model exposes <code>parse_obs</code>, <code>step</code>, <code>render</code> and <code>is_goal</code>, with optional <code>is_dead</code> and <code>legal_actions</code></td><td>The harness owns the scaffold, and the model submits small exact source patches. A 27B model that is asked for a complete simulator produces a broken one more often than a working one</td></tr>
        <tr><td>Immutable timeline of real transitions</td><td>Schema, Retrodict</td><td>Every action is stored with both frames and the exact changed cells; the model can edit its notes and its program but never the record</td><td>The harness also cites the contradicting transition whenever a note disagrees with the record</td></tr>
        <tr><td>Replay the program against all history before trusting it</td><td>Schema (backtest), Retrodict (retrodiction)</td><td>Sequential replay from the first frame of each level or reset segment, with no later true frame injected</td><td>The verdict is graded and not binary: whether the code ran, how many transitions are exact, the fraction of correct cells and the first failing transition. A pass-or-fail check gave the weaker model nothing to improve on</td></tr>
        <tr><td>Check small hypotheses against the log before acting</td><td>Retrodict</td><td>Each proposed rule is replayed over the recorded transitions, and the first counterexample is returned</td><td>Unchanged in spirit; used for single rules as well as for full models</td></tr>
        <tr><td>Search only inside a verified program</td><td>Schema</td><td>Bounded breadth-first search with explicit outcomes</td><td>For two mechanic families the search and the state model are owned by the harness (token contact and centroid docking), because the model could not maintain them as prose</td></tr>
        <tr><td>Plans that carry their own predictions and stop at the first mismatch</td><td>Retrodict (<code>expect</code>), Schema (commit queue)</td><td>Batches of at most 32 actions with sparse expected cells and level changes, executed without further model calls</td><td>The harness reconciles a sparse expectation with exact component motion, so that a correct action on a hollow object is not recorded as a failed hypothesis</td></tr>
        <tr><td>Actions chosen to discriminate between hypotheses</td><td>Schema</td><td>Single-action probes with a stated question</td><td>When the evidence is already settled, a gate replaces the reasoning turn with a short commit turn</td></tr>
        <tr><td>Files that survive a context reset, with checked and assumed statements kept apart</td><td>Retrodict (playbook), Schema (notes)</td><td>Notes divided into evidence and hypotheses, a scratch memory, saved helper functions and the current world model</td><td>Notes are shown with their age, and a structural upgrade triggers one short turn that rewrites contradicted notes</td></tr>
        <tr><td>Counters and timer strips are not gameplay</td><td>Retrodict, following the Duck agent</td><td>Repeated one- or two-cell changes at the frame edge are labelled as display candidates</td><td>Computed by the harness from the record and not left to a prompt instruction</td></tr>
        <tr><td>Expensive modelling only when cheap play has stalled</td><td>Retrodict (escalation), Tycho</td><td>A structured critique is forced when an objective has been exhausted without progress, and a game is given a minimum discovery window</td><td>The trigger is an exact condition on the record, for example every matching component removed while the level is unchanged</td></tr>
        <tr><td>Model-written code cannot reach the game engine</td><td>Retrodict</td><td>Subprocess sandbox with restricted imports and no file or network access</td><td>Unchanged</td></tr>
      </tbody>
    </table></div>
    <p>The main departure from both systems is the division of labour. Schema and Retrodict leave perception and bookkeeping to a frontier model and enforce discipline around it. With a 27B model that division fails, so this harness computes perception and structural relations itself and asks the model only for the hypotheses that connect them.</p>

    <h3>An earlier attempt: running Retrodict unchanged on a smaller model</h3>
    <p>Before this harness was written, the unmodified Retrodict prompt and runner were ported to a smaller local model (Qwen3.8-Flash-Next) with a 32,768-token context, where the original uses about 150,000. The first runs on <code>ls20</code> and <code>ft09</code> scored a mean of 2.38 and failed at the level of the protocol and not of the idea. One game ended when a 24,577-token prompt plus an 8,192-token completion exceeded the context. The other ended because the model used its entire completion for reasoning and returned an empty reply with no action block. A direct-interaction baseline (the Duck agent) on the same model scored 8.94 on the 25 public games in one run on rented hardware, and 5.74 in the Kaggle notebook run reported in the results table. These results motivated the move to a 27B model and to a harness that carries more of the work.</p>

    <h3>Use of the public Schema traces</h3>
    <p>The published Schema trajectories were used in four ways, all of them offline. First, they were read as a reference when diagnosing a failed game, to compare the representation a frontier model had reached with the one Qwen had reached; for example, the reference run of <code>bp35</code> describes a 6-pixel lattice in a persistent scrolling world, where Qwen had described two unrelated layouts. Second, they served as replay tests: the token simulator reproduces 417 of 417 transitions of the reference <code>ka59</code> trajectory. Third, the pickup abstraction used for <code>r11l</code> was taken from the reference trajectory and was labelled as a hypothesis until a live Qwen transition confirmed it. Fourth, level 7 of <code>ka59</code> used an action prior pruned from the reference trajectory. No reference action, coordinate or game-specific rule is placed in the model's prompt, and the first three uses shape reusable machinery only. The fourth is a direct use of a solution and is reported as such in the results.</p>
    <p>The research question that remains is one of transfer: how much of this approach stays effective when the model is a 27B open-weight model that can be served on a single GPU, and which responsibilities must move from the model into the harness to make it work.</p>

    <h2 id="baseline">Baseline and its failure modes</h2>
    <p>The baseline agent presents the current frame to the model, lets it reason, executes the action it names, and repeats. This agent fails in the same three ways on almost every game. Figure 3 shows one such run next to a run of the full system on the same game.</p>
    <ol>
      <li><strong>Perception.</strong> Given a 64&times;64 grid as text, the model spends thousands of tokens transcribing rows and still misplaces object boundaries.</li>
      <li><strong>Untested hypotheses.</strong> The model holds several explanations of an action at once (select, toggle, move) and does not design an action that would distinguish them.</li>
      <li><strong>Loss of established facts.</strong> Once the context fills, a fact established on level 1 is derived again, sometimes incorrectly, on level 4.</li>
    </ol>
    {COMPARE}

    <p>A larger reasoning budget does not remove any of these failures. Additional reasoning is useful only after the model is given a correct structured description of the game.</p>

    <h2 id="system">System design</h2>
    <p>The system separates proposing from checking. The language model proposes what the objects are, what an action does, and what completes a level. A deterministic Python harness, which contains no learned components, owns every operation that can be computed or verified exactly. No game identifier, coordinate, or level-specific answer is ever placed in the prompt or the harness.</p>

    {LOOP}

    <h3>Observation and tools</h3>
    <p>Each observation is presented losslessly as 64 rows of hexadecimal characters, one character per cell, with coordinates always given as <code>grid[y][x]</code>. The model can request numeric crops, connected components for every colour, and paginated retrieval of any earlier observation. Numeric colour identifiers are authoritative; rendered images are provided for geometry only, after one run spent more than 10,000 reasoning characters renaming colours it could already read as numbers. The model can also run Python in a compute tool and store reusable helper functions.</p>

    <h3>Memory</h3>
    <p>Every real action is stored as an immutable transition: the frame before, the action, the frame after and the exact set of changed cells. The model keeps persistent notes, divided into evidence and hypotheses, and a JSON scratch memory. When a note contradicts the transition record, the harness cites the contradicting transition. Context compaction keeps the current observation and the notes, removes raw exchanges oldest first, and leaves all removed content retrievable. Compact checkpoints retain relational facts (counts, bounding boxes, colour transitions, component motions, level changes) and omit duplicated cell lists, which remain in the immutable artifacts.</p>

    <h3>Executable world model and replay verification</h3>
    <p>The harness provides a scaffold for an executable model of the game with cloning, raw-grid state and common grid helpers. The language model supplies only the game-specific parts through exact source patches: <code>parse_obs</code>, <code>step</code>, <code>render</code>, <code>is_goal</code>, and optionally <code>is_dead</code> and <code>legal_actions</code>. Verification replays the model sequentially from the initial observation of each level or reset segment and never injects a later true frame to conceal drift. At a completed level the verifier checks the goal prediction and does not require the model to predict the next, unseen layout. Agreement with history is treated as evidence and not as proof of rules that have not yet been observed.</p>

    <h3>Search and guarded execution</h3>
    <p>A bounded breadth-first search runs inside the verified model and reports one of five explicit outcomes: found, exhausted, depth limit, budget limit or error. Exploratory probes are single actions. A plan may contain at most 32 actions and carries either sparse expected cells and level changes or full model predictions. The harness executes one action at a time and halts at the first mismatch, level boundary or terminal state. An inaccurate model does not prevent a probe, because probes are how the model is corrected.</p>

    <figure class="fig text"><div class="plate"><div class="frame"><img src="{I3}sb26-probe-1.png" width="656" height="320" alt="Two frames side by side. On the left a circle marks a token in the bottom row being clicked. On the right the same token has a white ring around it."></div></div>
    <figcaption><b>Figure 5.</b> A probe action, before and after. The circle marks the click; the box on the right marks the 20 cells that changed. The model's stated purpose was: &ldquo;click bottom solid piece to learn interaction model (select vs move). Expect it to be removed from source if it moves.&rdquo; The token was not removed and gained a ring, which establishes that a click selects.</figcaption></figure>

    <h3>Structural relations computed by the harness</h3>
    <p>Most of the engineering effort went into relations that the harness computes exactly from recorded transitions and reports to the model as hypotheses. Each was added after a specific failure in a live trace and was validated by replaying that trace.</p>
    <div class="tablewrap wide"><table>
      <thead><tr><th>Relation</th><th>What it establishes</th><th>Motivating evidence</th></tr></thead>
      <tbody>
        <tr><td>Conditional action relations</td><td>Equivalences, reversals and two-state toggles between actions, stated only for the observed state</td><td><code>bp35</code>: two actions produced the same masked transition from the same state</td></tr>
        <tr><td>Exact component motion</td><td>Per-object rigid translations obtained by matching normalised connected components across frames, including overlapping positions</td><td><code>ar25</code>: one action moved a 45-cell component left by 3 and a 40-cell component right by 3; colour-delta strips had reported no translation</td></tr>
        <tr><td>Component transforms and pose</td><td>Matches under the seven non-identity dihedral transforms, and the current pose relative to the level-entry frame</td><td><code>cn04</code>: a 135-cell component rotated 90&deg; clockwise; the model later lost track of two composed turns</td></tr>
        <tr><td>Reversible viewport edges</td><td>A small rigid motion coupled to a large, exactly reversible scene replacement, reported as a candidate room or camera change</td><td><code>bp35</code>: 816 cells changed over a box covering 64.06% of the frame and were restored exactly on return</td></tr>
        <tr><td>Boundary display candidates</td><td>Repeated one- or two-cell changes at the frame edge across distinct actions, labelled as possible counters</td><td><code>cn04</code>, <code>ka59</code>: a border tick was attributed to object contact</td></tr>
        <tr><td>Changed shells with stable cores</td><td>Regions whose outline changes while the enclosed component is pixel-identical</td><td><code>dc22</code>: two 40-cell shells changed around unchanged 47-cell glyphs; the model alternated between &ldquo;disappeared&rdquo; and &ldquo;unchanged&rdquo;</td></tr>
        <tr><td>Return-to-anchor mode changes</td><td>An exact return of a component to its level-entry position together with a disjoint change, reported with four competing explanations</td><td><code>g50t</code>: a 24-cell ring returned to its anchor while a distant copy was removed and a legend edited</td></tr>
        <tr><td>Container and reference graph</td><td>Boxes contain slots; slots contain solid tokens or hollow references to other boxes</td><td><code>sb26</code>: nested and cyclic reading order</td></tr>
        <tr><td>Persistent lattice map</td><td>World coordinates stitched across scrolling views, tile transition rules and settlement evidence</td><td><code>bp35</code>: a scrolling world on a 6-pixel lattice</td></tr>
        <tr><td>Token and contact simulator</td><td>Tokens on a 3-pixel lattice with direct movement, bump launches, shoves, overshoot and countdown launches, with A* planning</td><td><code>ka59</code></td></tr>
        <tr><td>Centroid docking graph</td><td>Graph systems whose marker is the floor mean of member centres, ordered pickup signatures, exact octagon overlap</td><td><code>r11l</code></td></tr>
      </tbody>
    </table></div>

    <h3>Decision gates</h3>
    <p>Trace analysis showed that a large share of wall-clock time was spent reasoning about facts that the harness had already established. Three narrow gates replace a reasoning turn with a short commit turn when the evidence is settled. Other diagnostic turns keep the full reasoning budget.</p>
    <div class="tablewrap wide"><table>
      <thead><tr><th>Gate</th><th>Condition</th><th class="r">Before</th><th class="r">After</th></tr></thead>
      <tbody>
        <tr><td>Settled equivalence</td><td>A conditional action equivalence has just been established</td><td class="r">247 s, 36,514 reasoning characters</td><td class="r">5.4 s, 97 tokens</td></tr>
        <tr><td>Exact no-op</td><td>Zero changed cells, no level change, unchanged environment state</td><td class="r">325.7 s, 15,919 tokens</td><td class="r">12.8 s, 112 tokens</td></tr>
        <tr><td>Boundary-only feedback</td><td>Only one or two edge cells changed</td><td class="r">thousands of reasoning characters</td><td class="r">21.3 s, 696 tokens</td></tr>
      </tbody>
    </table></div>
    <p>The no-op gate would not have fired in either of the first two completed games: <code>ft09</code> has no no-op among its 75 actions and <code>sb26</code> has none among 124. A fourth mechanism is a structured critique that is triggered when an objective has been exhausted without progress, for example when every matching component has been removed and the level has not advanced. The model must keep verified facts, list unexplained observations, compare three to five hypotheses from at least three families (including passive or support dynamics and multi-object contact dynamics), and commit to one discriminating probe.</p>

    <h3>Code execution, logging and resumption</h3>
    <p>Model-written Python runs in disposable subprocesses with no inherited credentials, a restricted syntax tree and import list, no file or network access, and limits on CPU time, wall time and output. Each run stores an ordered event log, content-addressed copies of every request and raw response, every streamed chunk with its arrival time, all frames, and every version of the notes and the world model. An interrupted game can be resumed without repeating paid inference: the saved actions are replayed through the local engine, and every before and after frame is asserted to match.</p>

    <h2 id="setup">Experimental setup</h2>
    <div class="tablewrap"><table>
      <thead><tr><th>Item</th><th>Setting</th></tr></thead>
      <tbody>
        <tr><td>Model</td><td>Qwen3.8-27B, open weights, no fine-tuning</td></tr>
        <tr><td>Serving</td><td>Self-hosted endpoint on one NVIDIA H200; an earlier baseline used hosted inference providers</td></tr>
        <tr><td>Context</td><td>131,072 tokens, with 32,768 tokens reserved for a diagnostic reply</td></tr>
        <tr><td>Hosted baseline limits</td><td>60 model calls, 500 actions and 16,384 output tokens per call, under a fixed spending ledger</td></tr>
        <tr><td>Game engine</td><td>The official local <code>arc-agi</code> engine and scorecard, seed 0</td></tr>
        <tr><td>Regression suite</td><td>156 tests, run after every change to the controller</td></tr>
      </tbody>
    </table></div>
    <h3>Evaluation protocol</h3>
    <ol>
      <li>Each game starts from an empty workspace. No notes, actions, programs or facts are inherited from another game.</li>
      <li>Complete requests, responses, reasoning, tool calls, observations, actions and notes are preserved.</li>
      <li>The earliest causal failure in a trace is diagnosed, because a later error is often a consequence of one incorrect representation.</li>
      <li>Only reusable perception, memory, verification, planning or execution machinery is added to the harness.</li>
      <li>A change is credited only when a new run exercises it and improves the failed decision without breaking a previously solved game.</li>
      <li>Discovery on a new game is given at least the larger of 40 actions and 1.5 times the human baseline for level 1 before the game is set aside.</li>
    </ol>

    <h2 id="cases">Case studies</h2>
    <h3>ft09: a relation between distant regions</h3>
    <p>Without assistance the model treated each panel of tiles as a separate puzzle. The missing element was a relation between regions that are far apart on screen: the small patterned tile inside a panel is a miniature of that panel's target state. Clicking a tile toggles its colour, and the level completes when every panel matches its miniature. The harness was not changed to state this rule. It was changed to report panels in pairs, to express tile coordinates in panel space, and to list reflections and colour permutations between regions as candidate relations. After this change the model's plans took the following form.</p>
    <blockquote><p>Toggle BR tile (36,52) from blue to red to match micro swatch 0 at row2,col0. This is the last mismatch; expect level completion.</p><cite>Qwen3.8-27B, third action of the completed ft09 run</cite></blockquote>
    <p>The run completed all six levels in 75 actions and 26 model calls, in about eleven minutes. No action produced a result that the model had not predicted.</p>
    <p class="takeaway"><b>Observed pattern.</b> The model did not need to be told the rule. It needed the two regions presented side by side in the same coordinates, after which it found the relation itself.</p>

    <h3>sb26: references between containers</h3>
    <p>The top row gives the order in which tokens must appear. The boxes in the middle contain slots. From level 2 onward, some slots contain a hollow token in the colour of another box, which means that reading continues inside that box. A depth-first reading of the boxes yields one sequence, and the level completes when that sequence equals the top row. A flat list of connected regions cannot express this structure, so the harness constructs the container and reference graph, in 12 to 15 ms per frame, without interpreting its edges. Given the graph, the model proposed the depth-first reading, the harness verified it against every completed level, and a finite recursive assignment solver produced the remaining placements. The run used 124 actions and 90 model calls over 44 minutes across resumed sessions. Thirteen actions produced an outcome the model had not predicted, and in each case the harness halted the plan.</p>
    <p class="takeaway"><b>Observed pattern.</b> When the structure of a game is a graph, a list of objects is the wrong data structure, and no amount of reasoning over the list recovers it.</p>

    <h3>r11l: docking the centroid of a graph</h3>
    <p>Clicking a diamond-shaped node transfers a selection, and clicking free ground moves the selected node. Each system of connected nodes has a marker at the floor mean of its members' centres, and a level completes when every marker rests on the ring with the matching colour signature. The model initially treated the markers as decoration. After four levels the game changes its representation: the system markers begin black, and separate half-coloured octagons must be collected by passing the marker over them before docking.</p>
    <p>Two exact-geometry errors were found through live mismatches. Collision had been approximated by a centre distance of at most four cells, which accepted the diagonal offset (4,4); the two 21-cell octagons have their corners removed and share no cell at that offset, and the game confirmed that nothing was collected. Collision is now computed from the rendered cell sets. Separately, a connector line crossing a marker added a structural colour to its signature, so signatures now accept only the item palette. The run completed all six levels in 138 actions and 145 model calls, with per-level counts of 10, 18, 39, 18, 28 and 25 actions against human baselines of 22, 33, 51, 26, 52 and 49.</p>
    <p class="takeaway"><b>Observed pattern.</b> Both errors were in geometry that the harness computed and not in the model's reasoning. Guarded execution exposed each one with a single wasted action.</p>

    <h3>ka59: when the missing capability is executable state</h3>
    <p>In the first attempt the model made 152 calls and produced 614,648 completion tokens without clearing level 2. The decisive evidence was present in its own trace: at step 60 the selected token stayed fixed while a second token moved five lattice cells. The model described the selected token as &ldquo;blocked&rdquo;, continued to plan in screen coordinates, and never turned contact launching into a transition rule. The harness now owns a state model for this family of mechanics: it parses tokens on a 3-pixel lattice, models direct movement, bump launches, shoves, overshoot and countdown launches, replays recorded transitions, and plans with A*. It reproduces 417 of 417 transitions of a public reference trace and 110 of 110 transitions of the original Qwen trace.</p>
    <p>A clean run with this controller completed all seven levels in 300 actions with no resets, using 11, 38, 33, 39, 20, 46 and 113 actions against human baselines of 28, 109, 51, 51, 33, 132 and 326. Levels 1 to 6 were planned by the simulator. On level 7 the generic A* search exceeded one million states, so the run used a 113-action prior that was pruned from a 117-action public Schema trajectory and verified from the actual entry state. This level is therefore a result about the integrated system on public data and is not evidence of generalisation to hidden games.</p>
    <p class="takeaway"><b>Observed pattern.</b> A 27B model can describe a mechanic in prose and still be unable to plan with it. Turning the description into executable state is what made planning possible.</p>

    <h2 id="evidence">Evidence from the traces</h2>
    <p>Each card below follows one failure from the live trace to the verified change, in four steps: what was observed, what caused it, what was changed in the harness, and how the change was checked. The format follows the evidence cards of the Schema write-up <a href="#ref-1">[1]</a>.</p>
    {EVIDENCE}

    <h2 id="results">Results</h2>
    <p>Six of the 25 public games are complete with the maximum local score of 100. Each entry below opens to a replay of the actual run, recorded action by action, together with an account of where the model alone got stuck, what the harness supplies for that game family, and why that is sufficient. A replay loads only when its entry is opened.</p>
    {GAMES}
    <h3>All 25 public games</h3>
    <p>Six games are complete, ten are in progress (the furthest are <code>su15</code> with 6 of 9 levels and <code>re86</code> with 6 of 8) and nine have not been attempted. Scores for games in progress are the local scorecard values so far and will change. The four-character identifiers are the official ones. The longer names are unofficial backronyms from a community list; I changed four of them (<code>g50t</code>, <code>su15</code>, <code>re86</code>, <code>tr87</code>) after checking the mechanics in the public Schema notes <a href="#ref-1">[1]</a>. Select a name to read what the game asks for. For every level the table gives the human reference actions next to the actions this system used. The last line of each game is a reference point: the levels, actions and score of the Duck agent <a href="#ref-8">[8]</a>, the open-source winner of the first milestone, in my Kaggle notebook run of 14 September 2026. That run cleared 32 of 183 levels across the 25 games, cleared at least one level in 19 games, completed no game, and had a mean score of 5.74. On the six games completed here it cleared 9 of 41 levels.</p>
    <div class="note"><b>Not a like-for-like comparison</b><p>The Duck run used a smaller model (Qwen3.8-Flash-Next, NVFP4) on the Kaggle GPU and played all 25 games in 2 hours 12 minutes. The runs reported on this page use Qwen3.8-27B on an H200 with no time limit, across several sessions per game. Each cell is one level: the first line gives the actions a first-time human needed, the second the actions this system used on the levels it cleared, and the third the same for Duck. The comparison shows where a published direct-interaction agent stands on the same games; it does not isolate the effect of the harness.</p></div>
    {BOARD}
    <div class="note"><b>Interpretation</b><p>A score of 100 is the local scorecard value for one public game. Public development results are not Kaggle leaderboard results, and a completed public game is evidence about the harness and not about hidden games.</p></div>

    <h2 id="negative">Negative results</h2>
    <h3>An all-or-nothing verifier provides no gradient</h3>
    <p>The first verifier asked the model for a complete simulator and counted a transition as correct only if all 4,096 cells matched. One wrong cell scored the same as a crash, and because the simulated state was rolled forward, one early error invalidated every later transition. The verifier now reports separately whether the code ran, how many transitions are exact, what fraction of cells is correct, and which transition fails first. New code replaces old code only if it improves on this backtest.</p>
    <h3>Persistent memory can preserve an incorrect belief</h3>
    <p>In one resumed <code>sb26</code> session the model's notes still stated that a click erases and repaints a token, long after the transition record showed the token moving as a block. Notes are now presented with their age and with the harness's own record of what each action caused. After a structural upgrade, a single short turn rewrites notes that the new relations contradict; on <code>dc22</code> this took 33.6 seconds and 805 tokens and removed a false claim that two glyphs had disappeared.</p>
    <h3>A checkpoint can overflow the context on its own</h3>
    <p>On <code>dc22</code> the run failed at action 17 even though every raw exchange had already been evicted. The remaining checkpoint was 170,280 characters, because exact cell arrays were duplicated in the ledger, the recent evidence and the last feedback. Compact checkpoints reduced the same trace to 97,912 characters, which fits in 96,416 of 131,072 tokens with the full diagnostic reserve.</p>
    <h3>More reasoning about settled evidence is not useful reasoning</h3>
    <p>The clearest example is the 325-second reply on <code>ar25</code>, in which the model selected the correct next probe near the start and then spent 15,919 tokens constructing an expectation for it. The probe changed 487 cells and was informative. The failure was latency and not judgement, which is why the decision gates are narrow.</p>

    <h2 id="limitations">Limitations</h2>
    <ul>
      <li>All results are on public games that were inspected during development. They constitute a development set.</li>
      <li>Several harness components were written after studying a failure on a specific game, and two of them (the token simulator and the pickup representation) were informed by public Schema traces. No game identifier or solution is encoded, but the risk that the harness is fitted to the public mechanics is real and can only be measured on games that were not studied.</li>
      <li>The <code>sb26</code>, <code>ka59</code> and <code>lp85</code> results were obtained across resumed sessions, and level 7 of <code>ka59</code> used a public-trace prior.</li>
      <li>The model is served on an H200. The competition requires an offline submission, and the model and harness have not yet been packaged for it.</li>
      <li>Nine of the 25 public games have not been attempted.</li>
    </ul>

    <h2 id="team">Planned direction: test-time communication</h2>
    <div class="note"><b>Status</b><p>This section describes a design that is planned and not yet enabled. None of the results on this page use it.</p></div>
    <p>Park, Kontonis, Garg, Krishnamurthy and Papailiopoulos <a href="#ref-9">[9]</a> compare two ways of spending the same number of agents on a task. In best-of-<em>N</em>, the agents work in isolation and the best result is kept, so every agent has to make every discovery by itself. In team-of-<em>N</em>, the agents share an append-only channel, so a discovery has to be made only once. On ARC-AGI-3 they report that a team of <em>k</em> communicating agents matches the success rate of about 4<em>k</em> independent agents, that the advantage grows with <em>k</em> (a team of five matches best-of-33), and that a team can reliably solve a game that no single agent solved. They also state the conditions: communication costs tokens and time, and independent agents can do better when compute is limited or when there is no clear measure of progress. It helps most when the task needs several successive discoveries, partial progress transfers between attempts, and a dense verifier exists.</p>
    {FIG_TEAM}

    <h3>What the paper's protocol actually is</h3>
    <ul>
      <li><strong>Homogeneous agents.</strong> Every agent has the same model, tools, task instruction and communication prompt. There are no assigned roles such as player, critic or planner.</li>
      <li><strong>Private work, shared findings.</strong> Each agent keeps a private context and scratch directory. All agents share append-only records of findings, disconfirmations, scores and coordination.</li>
      <li><strong>Approach slots.</strong> Agents claim distinct approach slots at the start to avoid early herding, publish concise reproducible evidence, and adopt a peer's approach only after a measured improvement or a genuine block.</li>
      <li><strong>Separate game sessions.</strong> On ARC-AGI-3 each agent has its own authenticated game session and its own per-level action budget. An action or a level clear by one agent does not advance a peer's game. Only discoveries are shared.</li>
      <li><strong>Synchronisation barrier.</strong> Every half-level action budget, an agent that is ahead of the slowest live teammate cannot spend another game action until its peers catch up or leave the live set. It can still read files, run code and exchange notes.</li>
      <li><strong>Pooled metric.</strong> A level counts as solved if any member clears it, and a game counts as solved if any member clears all its levels. The RHAE analysis reports the best and the average individual member separately and does not merge the agents' actions into one trajectory.</li>
    </ul>
    <p>The paper therefore supports several communicating sessions directly. It does not validate several agents writing to one board, and its pooled accounting cannot be assumed to match how a competition submission is scored.</p>
    <div class="note"><b>Artifact audit, 21 September 2026</b><p>The repository linked from the paper (<a href="https://github.com/jerryjonghopark/test-time-communication">jerryjonghopark/test-time-communication</a>) was empty on this date: no commits, files or ARC trajectories, and I found no separate trace archive. The paper itself gives the communication prompt, aggregate per-game results, budget ablations and the synchronisation rules, so the protocol can be reproduced from the appendix. How a particular breakthrough travelled from one agent to another, message by message, cannot yet be inspected.</p></div>

    <h3>Why it fits this harness</h3>
    <p>The paper's conditions describe this setting. A game is a chain of discoveries (what the objects are, what each action does, what the goal is), a discovery made on one level carries to the next, and replay against the transition record is a dense and exact verifier. The mechanism I intend to borrow is narrow: independent search followed by rapid adoption of <strong>verified</strong> discoveries. Agreement or commentary between agents that is not verified adds cost and no capability.</p>
    <p>When the 27B model finds the right representation it completes whole games. Its recurring failures are failures of the search process: it stays committed to one interpretation for too long, it recounts geometry by hand that code could compute, it knows the local mechanics and lacks the global objective, it describes a simulator without writing or testing one, and it loses or reinterprets a fact it had already established. Four independent contexts can search different representations without disturbing one another's working state, and the verifier lets one good partial discovery cross between contexts without importing unsupported conclusions.</p>
    <p>All agents call the same Qwen3.8-27B server, so no additional copy of the weights is loaded. The cost is four KV caches, more generated tokens, contention for decoding throughput and, in the paper-faithful variant, four times the environment actions. The development server holds well over four full 131,072-token sequences; four is its scheduler cap. Whether four contexts fit the throughput and the nine-hour limit of the Kaggle GPU has to be measured there.</p>

    <h3>Two variants</h3>
    <p><strong>Paper-faithful: four identical agents, four game sessions.</strong> Each agent has its own context, scratch space, game instance and action budget, and all publish to the shared logs. One agent may discover that an action translates an arm while another discovers that a different action rotates it; the others reproduce or build on those facts in their own sessions. This is the closest reproduction and the strongest source of independent experimental evidence. It multiplies environment usage by four, and it is a development technique until it is known whether the hidden evaluation permits several scored sessions and how it would aggregate them.</p>
    <p><strong>Submission adaptation: four identical agents, one action stream.</strong> All four receive the same prompt, tools, current observation, verified history and shared log, and all may inspect frames, write code, patch candidate models, backtest, search and propose experiments. Only one real action or batch is committed at a time. There is no permanent player: the harness owns the action endpoint, any agent may submit a proposal with its prediction and evidence, and the harness accepts one, executes it, records the transition and broadcasts the result. This serialises a contested resource; it does not assign a cognitive role. It keeps one scored action stream and avoids stale-state races. It departs from the paper in that the other three agents cannot gather distinct real observations in parallel. They can still mine the shared history, test competing representations and, once an executable world model exists, search private simulated branches without spending real actions.</p>
    <p>For the single action stream, play proceeds in synchronised discovery rounds:</p>
    <pre><code>freeze the current observation and the verified history
-> four agents independently inspect, test and search
-> agents append concise discoveries and action proposals
-> the harness verifies what can be checked
-> exactly one proposed real action or batch is committed
-> the transition and the verification outcome enter the shared log
-> every private context continues from the common new state</code></pre>
    {FIG_STREAM}

    <h3>What is shared, and who decides what is true</h3>
    <p>Agents receive evidence and not one another's reasoning: frames and component tables, transitions, harness-derived changes and object tracks, verified notes, rejected hypotheses, the current world model with its backtest report, and the remaining budgets. A contribution names a representation, hypotheses, a discriminating experiment with its prediction, a simulator patch or a candidate plan, and the evidence it used. The verifier, and no model, owns the truth: a contribution enters shared memory only after replay (for a transition rule), an exact structural check (for a claim about a frame), predicted against observed (for a probe), search replay (for a plan) and a contradiction check against all retained evidence. The channel is append-only and typed, because silently replacing a belief would destroy the evidence trail, and raw monologues stay in per-agent traces.</p>
    <pre><code>{{
  "kind": "discovery | disconfirmation | model_patch | plan | request",
  "level": 6,
  "state_id": "...",
  "author": "agent-0 | agent-1 | agent-2 | agent-3",
  "claim": "...",
  "evidence": ["transition ids"],
  "prediction": "...",
  "verification": "pending | passed | failed",
  "artifact": "optional model or plan reference"
}}</code></pre>
    <p>Diversity does not come from different prompts, which stay identical as in the paper. It comes from atomically claimed approach slots, private scratch space, distinct working hypotheses, and the instruction to keep one meaningful variation even after adopting a peer's better result. The design fails if all four agents repeat one interpretation and only critique its wording.</p>

    <h3>Revised live design: an asynchronous three-context event bus</h3>
    <p><strong>A negative result first.</strong> On 21 September a probe on the development server rejected the simplest version, two independent contexts whose answers are merged at the end. Both contexts spent roughly the same first 8,000 reasoning tokens reconstructing the same cross geometry on level 6 of a game and arriving at the same contradiction about coverage. Merging two duplicate answers is best-of-2. It is not the communication effect.</p>
    <p>The next probe therefore uses three Qwen3.8-27B contexts on one board, and for this probe they do have distinct responsibilities, which departs from the homogeneous design above:</p>
    <ul>
      <li><strong>Master.</strong> Owns strategic continuity, hypotheses about the objective and the decision criteria, and will eventually be the only context allowed to take real actions. It must not spend its context transcribing geometry by hand.</li>
      <li><strong>World modeler.</strong> Owns the exact representation of the board, the causal mechanics, executable helpers and models, backtests and discriminating experiments.</li>
      <li><strong>Communication coordinator.</strong> Receives completed reasoning, tool calls, tool results and structured reports from both workers. It removes duplicates, keeps evidence references, flags conflicts and assigns distinct next questions. It never acts and should not try to solve the board itself.</li>
    </ul>
    {FIG_BUS}
    <p>Communication is asynchronous at inference boundaries. A transformer request cannot absorb new context while it is generating, so the harness appends an event to the shared bus as soon as a context finishes a reasoning or tool turn, and every context receives all unseen events from the others before its next inference call. This is the same steering point at which a tool-using agent receives a message between two tool calls. Every event carries a sequence number, an author, a kind, a board state version, a timestamp and a payload. A report about an older board version remains useful as historical evidence and cannot authorise an action against a newer state.</p>
    <p><strong>What is shared.</strong> Completed raw reasoning goes to the coordinator, because it shows which paths were already explored, which alternatives were discarded, which leaps were unsupported, and which insights never reached the final report. Tool calls and results are shared at once, so that a second worker does not repeat an exact measurement or a program that already failed. The coordinator turns these into a compact handoff: new discoveries grounded in evidence, contradictions with their provenance, open questions, separate assignments for the master and the world modeler, and the references needed to audit each claim. Workers may also see newly completed raw events before the next compaction, which allows fast steering between tool calls. The compact handoffs are the durable shared memory; raw monologues are diagnostic evidence and not permanent prompt state.</p>
    <p><strong>Context policy.</strong> The event file is append-only and lossless, and each prompt uses a bounded first-in, first-out inbox:</p>
    <ol>
      <li>Before a request, collect all unseen events.</li>
      <li>Reserve the 32,768-token completion window and the current tool schemas.</li>
      <li>Ask the provider's own <code>fits()</code> check whether the request fits.</li>
      <li>If it does not, remove the oldest raw event and retry until the newest suffix fits.</li>
      <li>Record the included sequence range and the number of omitted events in the trace.</li>
    </ol>
    {FIG_FIFO}
    <p>Old reasoning therefore leaves the active context without being deleted. Persistent notes and coordinator handoffs keep the useful conclusions, the full log remains available for audit or targeted retrieval, and at the next collaboration round each role starts from a clean role-specific checkpoint.</p>
    <p><strong>Test criterion.</strong> The architecture is useful only if the trace shows causal transfer: (1) one worker discovers information that was absent from the other worker's previous turn; (2) the receiving worker explicitly changes or narrows its next investigation; (3) duplicated reasoning decreases after the event arrives; (4) the coordinator preserves the discovery without promoting speculation; and (5) the final master plan contains a verified improvement over either worker's initial report alone. The probe runs with reasoning enabled and the full 32,768-token reply ceiling, with no smaller cap on diagnostics or handoffs.</p>

    <h3>How it composes with the existing harness</h3>
    <p>Retrodict <a href="#ref-2">[2]</a> contributes explicit predictions, expectations, contradiction handling and a compact evidence log. Schema <a href="#ref-1">[1]</a> contributes executable models, replay backtests, repair and planning inside the inferred model. Test-time communication lets separate contexts discover and improve those artifacts while sharing only verified progress. It is not a teacher: every agent is the same base model, sees only the current game's evidence, and receives no released solutions or privileged action sequences.</p>

    <h3>Experiment required before adoption</h3>
    <div class="tablewrap"><table>
      <thead><tr><th>Arm</th><th class="r">Agents</th><th>Communication</th><th>Environment</th></tr></thead>
      <tbody>
        <tr><td>A</td><td class="r">1</td><td>None (the current system)</td><td>One session</td></tr>
        <tr><td>B</td><td class="r">4</td><td>None (best-of-4)</td><td>Four separate sessions</td></tr>
        <tr><td>C</td><td class="r">4</td><td>Shared logs, paper-faithful</td><td>Four separate sessions</td></tr>
        <tr class="best"><td>D</td><td class="r">4</td><td>Shared logs, serialised actions</td><td>One session and one action stream</td></tr>
      </tbody>
    </table></div>
    <p>Arm C measures whether the paper's effect reproduces with a 27B model. Arm D measures whether the effect survives the single action stream that a submission is likely to need. The measures are levels and games completed, actions and RHAE, wall time and tokens, actions to the first correct representation, the number of proposed discoveries that pass verification, the rate of repeated hypotheses and contradictions, improvement in the model backtest, peak KV-cache memory and decoding throughput, and whether a communicated discovery is actually adopted and reused. Adoption requires an improvement in completion or action efficiency across several mechanic families within the Kaggle runtime limits, and not a higher success rate on one public game.</p>
    <p>Open questions: whether all four agents should run continuously or only while a mechanic is unresolved; how the single-stream harness should choose among simultaneous proposals without becoming a learned central orchestrator; how long a synchronised round may last before an action must be taken; which discoveries transfer across levels and which are local to one; and when the harness should abandon communication and take the best verified action available.</p>

    <h2 id="future">Future work</h2>
    <ul>
      <li>Run the four-arm test-time communication experiment described above (one agent, best-of-4, team-of-4 with separate sessions, team-of-4 with one action stream) on games with known stalls.</li>
      <li>Complete the sweep over all 25 public games, recording the earliest causal failure on each.</li>
      <li>Freeze the harness and repeat the completed games from empty memory several times to measure reliability, with <code>ft09</code> and <code>sb26</code> as regression sentinels.</li>
      <li>Report time, tokens, real actions and the number of harness interventions as separate quantities.</li>
      <li>Package the model and harness for the offline Kaggle environment and measure how many games can run concurrently within the available KV cache.</li>
      <li>Train on intermediate decisions (object roles, discriminating probes, repair location, stopping) and not only on final action sequences.</li>
    </ul>

{CITE}
    <h2 id="references">References</h2>
    <ol class="refs">
      <li id="ref-1">G. Zeng, J. Wang, W. Ma, S. Yin, C. Wang, S. Liu, A. Kanazawa, W. Ni, X. Li, A. Zanette and H. Feng. <em>Schema</em>. Project page, 2026. <a href="https://schema-harness.github.io/">schema-harness.github.io</a>. Trajectories and scorer: <a href="https://huggingface.co/datasets/schema-harness/arc-agi-3-schema-traces">schema-harness/arc-agi-3-schema-traces</a>.</li>
      <li id="ref-2">R. Brown. <em>Retrodict</em>. Source code, 2026. <a href="https://github.com/ryanbbrown/Retrodict">github.com/ryanbbrown/Retrodict</a>. Write-up: <a href="https://blog.ryanbbrown.com/p/how-i-accidentally-got-the-top-score">How I accidentally got the top score</a>. Official scorecard: <a href="https://arcprize.org/scorecards/9c403765-db5b-40b1-beab-6fa3f40119b0">arcprize.org/scorecards/9c403765</a>.</li>
      <li id="ref-3">H. Tang, D. Key and K. Ellis. <em>WorldCoder, a Model-Based LLM Agent: Building World Models by Writing Code and Interacting with the Environment</em>. 2024. <a href="https://arxiv.org/abs/2402.12275">arXiv:2402.12275</a>.</li>
      <li id="ref-4"><em>Tycho</em>. 2026. <a href="https://arxiv.org/abs/2607.28287">arXiv:2607.28287</a>.</li>
      <li id="ref-5">Rodionov. Executable world models for ARC-AGI-3, 2026, <a href="https://arxiv.org/abs/2605.05138">arXiv:2605.05138</a>, and the accompanying ablation study, <a href="https://arxiv.org/abs/2607.15439">arXiv:2607.15439</a>, which reports that an executable model without replay verification can perform worse than plain text.</li>
      <li id="ref-6"><em>RGB-Agent</em> (alexisfox7). Source code. <a href="https://github.com/alexisfox7/RGB-Agent">github.com/alexisfox7/RGB-Agent</a>. The append-only log and the action queue in Retrodict follow this agent.</li>
      <li id="ref-7">ARC Prize Foundation. <em>ARC-AGI-3 methodology and the RHAE metric</em>. <a href="https://docs.arcprize.org/methodology">docs.arcprize.org/methodology</a>.</li>
      <li id="ref-8">Tufa Labs. <em>The Duck</em>, first place in ARC-AGI-3 Milestone Prize #1, open-sourced as a Kaggle notebook. Announcement: <a href="https://arcprize.org/blog/arc-prize-2026-milestone-1">arcprize.org/blog/arc-prize-2026-milestone-1</a>.</li>
      <li id="ref-9">J. Park, V. Kontonis, S. Garg, A. Krishnamurthy and D. Papailiopoulos. <em>Scaling Discovery through Test-Time Communication</em>. 2026. <a href="https://arxiv.org/abs/2609.21032">arXiv:2609.21032</a>.</li>
    </ol>
""",
)
