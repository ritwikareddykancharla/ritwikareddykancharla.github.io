#!/usr/bin/env python
"""Render ARC-AGI-2 figures for the site: puzzle grids and the model's answers.

Reads (never writes) the arc-agi2 repo: the public evaluation data and the saved induction
traces, and re-runs saved programs through that repo's sandbox to get their outputs.
Every image is ONE grid with no text in it; the page lays grids out and labels them in HTML.

    ~/projects/arc-agi2/.venv/bin/python tools/build_arc2_figures.py ~/projects/arc-agi2
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "assets" / "img" / "arc2"

# the usual ARC colours 0..9
PALETTE = ["#000000", "#0074d9", "#ff4136", "#2ecc40", "#ffdc00", "#aaaaaa", "#f012be", "#ff851b",
           "#7fdbff", "#870c25"]  # fmt: skip
LINE = "#4d4d4d"


def draw(grid, name: str, target: int = 300, mark=None, segments=None) -> dict:
    """One grid -> PNG. `mark`: cells to outline (wrong cells). `segments`: lines to overlay."""
    h, w = len(grid), len(grid[0])
    cell = max(6, min(28, target // max(h, w)))
    img = Image.new("RGB", (w * cell + 1, h * cell + 1), LINE)
    d = ImageDraw.Draw(img)
    for y in range(h):
        for x in range(w):
            d.rectangle([x * cell + 1, y * cell + 1, (x + 1) * cell - 1, (y + 1) * cell - 1],
                        fill=PALETTE[int(grid[y][x])])  # fmt: skip
    for (y0, x0), (y1, x1) in segments or []:
        p = [(x0 + 0.5) * cell, (y0 + 0.5) * cell, (x1 + 0.5) * cell, (y1 + 0.5) * cell]
        d.line(p, fill="#ffffff", width=5)
        d.line(p, fill="#111111", width=2)
    if mark:  # outlines of edge cells extend past the grid: give them a transparent margin
        pad = 4
        framed = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
        framed.paste(img, (pad, pad))
        img, d = framed, ImageDraw.Draw(framed)
        for y, x in mark:
            x0, y0 = x * cell + pad, y * cell + pad
            d.rectangle([x0 - 1, y0 - 1, x0 + cell + 1, y0 + cell + 1], outline="#ffffff", width=3)
            d.rectangle([x0 - 2, y0 - 2, x0 + cell + 2, y0 + cell + 2], outline="#e4002b", width=2)
    path = OUT / f"{name}.png"
    img.save(path, optimize=True)
    return {"file": path.name, "w": img.width, "h": img.height, "rows": h, "cols": w}


def diff(a, b):
    if len(a) != len(b) or len(a[0]) != len(b[0]):
        return None
    return [(y, x) for y in range(len(a)) for x in range(len(a[0])) if a[y][x] != b[y][x]]


def main() -> None:
    repo = Path(sys.argv[1]).expanduser()
    sys.path.insert(0, str(repo))
    from arc.data import load_split
    from arc.induction.facts import DIRECTIONS  # noqa: F401  (documents where segments come from)
    from arc.induction.verify import verify

    tasks = load_split("evaluation", repo / "data")
    runs = repo / "outputs" / "induction"
    OUT.mkdir(parents=True, exist_ok=True)
    man: dict = {}

    def task_grids(tid: str, pairs=None, tests=True, target=300):
        t = tasks[tid]
        for i, p in enumerate(t.train):
            if pairs is None or i in pairs:
                man[f"{tid}-train{i}-in"] = draw(p.input, f"{tid}-train{i}-in", target)
                man[f"{tid}-train{i}-out"] = draw(p.output, f"{tid}-train{i}-out", target)
        if tests:
            for i, p in enumerate(t.test):
                man[f"{tid}-test{i}-in"] = draw(p.input, f"{tid}-test{i}-in", target)
                man[f"{tid}-test{i}-out"] = draw(p.output, f"{tid}-test{i}-out", target)

    def programs(run: str, tid: str):
        ev = json.loads((runs / run / "traces" / f"{tid}.json").read_text())["events"]
        return [e for e in ev if e.get("code")]

    # 1. what a puzzle looks like: nested rings (two of its three train pairs + first test)
    task_grids("13e47133", pairs=[1, 2], target=260)

    # 2. the mirror puzzle across harness versions: same model, better facts
    tid = "0934a4d8"
    t = tasks[tid]
    task_grids(tid, pairs=[0], target=330)
    truth = t.test[0].output
    story = {}
    for label, run, pick in (("v7", "qwen38-27b-v7-mirror", 0), ("v9", "qwen38-27b-v9-mirror", 0),
                             ("v11", "qwen38-27b-v11-32k", 1)):  # fmt: skip
        cand = json.loads((runs / run / "traces" / f"{tid}.json").read_text())["candidates"][0][pick]
        wrong = diff(cand, truth)
        man[f"{tid}-{label}"] = draw(cand, f"{tid}-{label}", 150, mark=wrong)
        story[label] = {"wrong": len(wrong), "cells": len(truth) * len(truth[0])}
    man[f"{tid}-truth"] = draw(truth, f"{tid}-truth", 150)
    man["mirror_story"] = story

    # 3. the anchor trap: rows counted from the top vs from the marker (221dfab4)
    tid = "221dfab4"
    t = tasks[tid]
    task_grids(tid, pairs=[0], target=300)
    shown = {}
    for e in programs("qwen38-27b-eval20-c", tid):
        rep = verify(e["code"], t)
        if not rep.verified or rep.test_outputs[0] is None:
            continue
        ok = rep.test_outputs[0] == t.test[0].output
        key = "right" if ok else "wrong"
        if key not in shown:
            wrong = diff(rep.test_outputs[0], t.test[0].output)
            man[f"{tid}-{key}"] = draw(rep.test_outputs[0], f"{tid}-{key}", 300, mark=None if ok else wrong)
            shown[key] = {"wrong_cells": len(wrong), "robustness": round(rep.robustness, 2)}
    man["anchor_story"] = shown

    # 4. a train-exact program that is still wrong: water fills level by level (28a6681f)
    tid = "28a6681f"
    t = tasks[tid]
    task_grids(tid, pairs=[0, 1], target=220)
    best = None
    for e in programs("qwen38-27b-eval20-c", tid):
        rep = verify(e["code"], t)
        if rep.verified and rep.test_outputs[0] is not None:
            wrong = diff(rep.test_outputs[0], t.test[0].output)
            if best is None or len(wrong) < len(best[1]):
                best = (rep.test_outputs[0], wrong)
    man[f"{tid}-pred"] = draw(best[0], f"{tid}-pred", 220, mark=best[1])
    man["water_story"] = {"wrong_cells": len(best[1])}

    # 5. rays that bounce: the added cells as segments (142ca369)
    tid = "142ca369"
    p = tasks[tid].train[0]
    h, w = len(p.input), len(p.input[0])
    added = {(y, x) for y in range(h) for x in range(w) if p.input[y][x] != p.output[y][x]}
    segs = []
    for dy, dx in ((1, 1), (1, -1)):
        for y, x in sorted(added):
            if (y - dy, x - dx) in added:
                continue
            n = 1
            while (y + n * dy, x + n * dx) in added:
                n += 1
            if n >= 3:
                segs.append(((y, x), (y + (n - 1) * dy, x + (n - 1) * dx)))
    man[f"{tid}-in"] = draw(p.input, f"{tid}-in", 320)
    man[f"{tid}-out"] = draw(p.output, f"{tid}-out", 320)
    man[f"{tid}-segments"] = draw(p.output, f"{tid}-segments", 320, segments=segs)
    man["segments_story"] = {"segments": len(segs)}

    # 6. the first solve through the repair loop (247ef758): one train pair
    task_grids("247ef758", pairs=[0], tests=False, target=300)

    (OUT / "figures.json").write_text(json.dumps(man, indent=1))
    print(json.dumps({k: v for k, v in man.items() if k.endswith("_story")}, indent=1))
    print(len([k for k in man if not k.endswith("_story")]), "images")


if __name__ == "__main__":
    main()
