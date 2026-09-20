#!/usr/bin/env python
"""Data for the "with and without the harness" player on the ARC-AGI-3 page.

Reads (never writes) the arc-agi3 repo:
  without: runs/20260911-092451-Qwen3_6-27B-FP8-kaggle/ft09/transcript.jsonl  (clicks and the model's stated reasons)
           The transcript truncates frames, so the 17 recorded clicks were replayed through the local game
           engine in a scratch copy (tools/data/ft09_baseline_replay.json). The replay reproduces the
           transcript's changed-cell count on every one of the 17 actions.
  with:    runs/schema-final-fresh-v1-ft09/27b_job/ft09  (events.jsonl + artifacts, level 1 only)

    python tools/build_arc3_compare.py ~/projects/arc-agi3/runs
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
runs = Path(sys.argv[1]).expanduser()
hexrow = lambda row: "".join(format(int(c), "x") for c in row)
pack = lambda grid: [hexrow(r) for r in grid]
clean = lambda t: " ".join((t or "").split())


def delta(before, after):
    """Changed cells as [y, x, colour] triples, or the whole frame when most of it changed (a new level)."""
    cells = [[y, x, int(c1)] for y, (r0, r1) in enumerate(zip(before, after)) for x, (c0, c1) in enumerate(zip(r0, r1)) if c0 != c1]
    return ({"grid": pack(after)} if len(cells) > 500 else {"cells": cells}), len(cells)


# ---- without the harness
rows = [json.loads(l) for l in (runs / "20260911-092451-Qwen3_6-27B-FP8-kaggle/ft09/transcript.jsonl").open()]
reasons, last = [], ""
for r in rows:                      # a reason is the most recent thing the model said before acting
    if r.get("type") == "assistant" and clean(r.get("content")):
        last = clean(r["content"])
    if r.get("type") != "tool" or r.get("name") != "arc3":
        continue
    for part in json.loads(r["args"])["args"].split(";"):
        bits = part.split()
        if bits[:2] == ["act", "ACTION6"]:
            reasons.append((int(bits[2]), int(bits[3]), last))
replay = json.loads((HERE / "data" / "ft09_baseline_replay.json").read_text())
assert [(l["x"], l["y"]) for l in replay["log"]] == [(x, y) for x, y, _ in reasons], "replay and transcript disagree"
result = json.loads((runs / "20260911-092451-Qwen3_6-27B-FP8-kaggle/ft09/result.json").read_text())
without = {
    "start": pack(replay["frames"][0]),
    "steps": [{"x": x, "y": y, "say": say, **delta(g0, g1)[0], "levels": l["levels"], "changed": l["changed"]}
              for (x, y, say), g0, g1, l in zip(reasons, replay["frames"], replay["frames"][1:], replay["log"])],
    "model": result["model"], "model_calls": result["model_calls"], "prompt_tokens": result["prompt_tokens"],
    "levels": result["levels_completed"], "finish": result["finish"].split(":")[0],
}

# ---- with the harness (the whole completed run)
run = runs / "schema-final-fresh-v1-ft09/27b_job/ft09"
acts = [json.loads(l) for l in (run / "events.jsonl").open() if '"kind":"action_taken"' in l]
load = lambda ref: json.loads((run / ref).read_text())
steps = []
for a in acts:
    before, after = load(a["before"]), load(a["after"])
    d, changed = delta(before["grid"], after["grid"])
    steps.append({"x": a["action"].get("x"), "y": a["action"].get("y"), "say": clean(a["reason"]), **d,
                  "levels": after["levels"], "changed": changed, "mispredicted": bool(a.get("mismatches"))})
withh = {"start": pack(load(acts[0]["before"])["grid"]), "steps": steps, "model": "Qwen3.8-27B",
         "total_actions": len(acts), "total_levels": load(acts[-1]["after"])["levels"], "state": load(acts[-1]["after"])["state"]}

out = HERE.parent / "assets" / "data" / "ft09-compare.json"
out.write_text(json.dumps({"game": "ft09", "without": without, "with": withh}, separators=(",", ":")))
print("without:", len(without["steps"]), "actions, levels", without["levels"], "| with:", len(withh["steps"]), "actions, levels", withh["total_levels"], withh["state"], "|", out.stat().st_size // 1024, "KB")
