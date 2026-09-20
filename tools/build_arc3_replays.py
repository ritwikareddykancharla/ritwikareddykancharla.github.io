#!/usr/bin/env python
"""One replay file per completed ARC-AGI-3 game, for the players in the results section.

Reads (never writes) run directories of the arc-agi3 repo and writes assets/data/replay-<game>.json:
the opening frame, then for every real action the click or action name, what the agent logged as its
reason, the cells that changed (or the whole frame when a new level loads), and the level count.

    python tools/build_arc3_replays.py ~/projects/arc-agi3/runs
"""
import json
import sys
from pathlib import Path

RUNS = {
    "ft09": "schema-final-fresh-v1-ft09/27b_job/ft09",
    "sb26": "schema-final-fresh-v1-sb26-autoexec-resume4/27b_job/sb26",
    "r11l": "r11l-v25/27b_job/r11l",
    "ka59": "ka59-token-clean-v5/27b_job/ka59",
    "lp85": "lp85-v24/27b_job/lp85",
    "tr87": "tr87-v15/27b_job/tr87",
}
root = Path(sys.argv[1]).expanduser()
out_dir = Path(__file__).resolve().parent.parent / "assets" / "data"
hexrow = lambda row: "".join(format(int(c), "x") for c in row)
clean = lambda t: " ".join(str(t or "").split())

for game, rel in RUNS.items():
    run = root / rel
    load = lambda ref: json.loads((run / ref).read_text())
    acts = [json.loads(l) for l in (run / "events.jsonl").open() if '"kind":"action_taken"' in l]
    steps, per_level, last_levels, count = [], [], 0, 0
    for a in acts:
        before, after = load(a["before"])["grid"], load(a["after"])
        cells = [[y, x, int(c1)] for y, (r0, r1) in enumerate(zip(before, after["grid"])) for x, (c0, c1) in enumerate(zip(r0, r1)) if c0 != c1]
        act = a["action"]
        say = clean(a.get("reason"))
        step = {"a": act["action"], "say": say[:420] + ("..." if len(say) > 420 else ""), "levels": after["levels"], "changed": len(cells)}
        if act.get("x") is not None:
            step["x"], step["y"] = act["x"], act["y"]
        step.update({"grid": [hexrow(r) for r in after["grid"]]} if len(cells) > 500 else {"cells": cells})
        if a.get("mismatches"):
            step["mispredicted"] = True
        steps.append(step)
        count += 1
        if after["levels"] > last_levels:
            per_level.append(count); count, last_levels = 0, after["levels"]
    summary = json.loads((run / "summary.json").read_text()) if (run / "summary.json").exists() else {}
    data = {"game": game, "run": {"start": [hexrow(r) for r in load(acts[0]["before"])["grid"]], "steps": steps,
                                  "total_levels": steps[-1]["levels"], "per_level": per_level}}
    path = out_dir / f"replay-{game}.json"
    path.write_text(json.dumps(data, separators=(",", ":")))
    print(f"{game}: {len(steps)} actions, {steps[-1]['levels']} levels, per level {per_level}, "
          f"mispredicted {sum(1 for s in steps if s.get('mispredicted'))}, {path.stat().st_size // 1024} KB, "
          f"empty reasons {sum(1 for s in steps if not s['say'])}, calls {summary.get('calls')}")
