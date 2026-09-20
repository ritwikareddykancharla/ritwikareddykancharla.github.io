#!/usr/bin/env python
"""Render ARC-AGI-3 figures for the site from saved agent traces.

Reads (never writes) run directories of the arc-agi3 repo:
    <run>/events.jsonl      one JSON event per line; `action_taken` has before/after artifacts
    <run>/artifacts/*.json  {"grid": 64x64 ints 0..15, "levels": int, "state": str}

Writes GIFs and PNGs under assets/img/arc3/. Usage:

    python tools/build_arc3_figures.py ~/projects/arc-agi3/runs
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "assets" / "img" / "arc3"

# ARC-AGI-3 palette, colours 0..15 (same values the official viewer uses)
PALETTE = ["#ffffff", "#cccccc", "#999999", "#666666", "#333333", "#000000", "#e53aa3", "#ff7bcc",
           "#f93c31", "#1e93ff", "#88d8f1", "#ffdc00", "#ff851b", "#921231", "#4fcc30", "#a356d6"]  # fmt: skip
RGB = [tuple(int(c[i : i + 2], 16) for i in (1, 3, 5)) for c in PALETTE]

RUNS = {
    "ft09": "schema-final-fresh-v1-ft09/27b_job/ft09",
    "sb26": "schema-final-fresh-v1-sb26-autoexec-resume4/27b_job/sb26",
}


def frame_image(grid, scale: int) -> Image.Image:
    h, w = len(grid), len(grid[0])
    img = Image.new("P", (w, h))
    img.putpalette([v for rgb in RGB for v in rgb] + [0] * (768 - 48))
    img.putdata([int(c) for row in grid for c in row])
    return img.resize((w * scale, h * scale), Image.NEAREST)


def load(run: Path, ref: str):
    return json.loads((run / ref).read_text())


def actions(run: Path) -> list[dict]:
    return [e for line in (run / "events.jsonl").open() if '"kind":"action_taken"' in line
            for e in [json.loads(line)]]  # fmt: skip


def with_bar(img: Image.Image, level: int, total: int, step: int, n_steps: int) -> Image.Image:
    """Frame plus a thin status strip: level pips and a progress line (no text: stays crisp)."""
    w, h = img.size
    bar = 14
    out = Image.new("RGB", (w, h + bar), "#ffffff")
    out.paste(img.convert("RGB"), (0, 0))
    d = ImageDraw.Draw(out)
    pip, gap = 8, 4
    for k in range(total):
        x0 = 2 + k * (pip + gap)
        colour = "#1e93ff" if k < level else "#d9dde3"
        d.rectangle([x0, h + 3, x0 + pip, h + 3 + pip], fill=colour)
    x1 = 2 + total * (pip + gap) + 6
    d.rectangle([x1, h + 6, w - 3, h + 8], fill="#e6e9ee")
    d.rectangle([x1, h + 6, x1 + int((w - 3 - x1) * step / max(n_steps, 1)), h + 8], fill="#555b66")
    return out


def gameplay_gif(name: str, run: Path, scale: int = 4, ms: int = 140, every: int = 1) -> dict:
    acts = actions(run)
    total = load(run, acts[-1]["after"])["levels"]
    frames = [with_bar(frame_image(load(run, acts[0]["before"])["grid"], scale), 0, total, 0, len(acts))]
    durations = [900]
    prev_level = 0
    for i, a in enumerate(acts, 1):
        if i % every and i != len(acts):
            continue
        after = load(run, a["after"])
        frames.append(with_bar(frame_image(after["grid"], scale), after["levels"], total, i, len(acts)))
        held = after["levels"] > prev_level
        durations.append(900 if held else ms)  # pause on the frame that starts a new level
        prev_level = after["levels"]
    durations[-1] = 2500
    path = OUT / f"{name}-play.gif"
    quant = [f.quantize(colors=32, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
             for f in frames]  # fmt: skip
    quant[0].save(path, save_all=True, append_images=quant[1:], duration=durations, loop=0,
                  optimize=True, disposal=1)  # fmt: skip
    return {"file": path.name, "frames": len(frames), "actions": len(acts), "levels": total,
            "kb": round(path.stat().st_size / 1024)}  # fmt: skip


def level_starts(name: str, run: Path, scale: int = 3) -> dict:
    """One still per level: the first frame of each level, side by side."""
    acts = actions(run)
    grids, seen = [load(run, acts[0]["before"])["grid"]], 0
    for a in acts:
        after = load(run, a["after"])
        if after["levels"] > seen and after["state"] != "WIN":
            grids.append(after["grid"])
        seen = max(seen, after["levels"])
    tiles = [frame_image(g, scale).convert("RGB") for g in grids]
    gap = 8
    w = sum(t.width for t in tiles) + gap * (len(tiles) - 1)
    sheet = Image.new("RGB", (w, tiles[0].height), "#ffffff")
    x = 0
    for t in tiles:
        sheet.paste(t, (x, 0))
        x += t.width + gap
    path = OUT / f"{name}-levels.png"
    sheet.save(path, optimize=True)
    return {"file": path.name, "levels_shown": len(tiles), "kb": round(path.stat().st_size / 1024)}


def probe_pair(name: str, run: Path, step: int, scale: int = 5) -> dict:
    """Before / after of one real action, changed cells outlined, plus the model's stated reason."""
    a = actions(run)[step - 1]
    before, after = load(run, a["before"])["grid"], load(run, a["after"])["grid"]
    left, right = frame_image(before, scale).convert("RGB"), frame_image(after, scale).convert("RGB")
    d = ImageDraw.Draw(right)
    changed = [(x, y) for y in range(64) for x in range(64) if before[y][x] != after[y][x]]
    if changed:
        xs, ys = [c[0] for c in changed], [c[1] for c in changed]
        d.rectangle([min(xs) * scale - 3, min(ys) * scale - 3, (max(xs) + 1) * scale + 2,
                     (max(ys) + 1) * scale + 2], outline="#111111", width=3)  # fmt: skip
    act = a["action"]
    if "x" in act:  # where the click landed, on the before frame
        cx, cy = act["x"] * scale + scale // 2, act["y"] * scale + scale // 2
        ImageDraw.Draw(left).ellipse([cx - 9, cy - 9, cx + 9, cy + 9], outline="#111111", width=3)
    gap = 16
    sheet = Image.new("RGB", (left.width * 2 + gap, left.height), "#ffffff")
    sheet.paste(left, (0, 0))
    sheet.paste(right, (left.width + gap, 0))
    path = OUT / f"{name}-probe-{step}.png"
    sheet.save(path, optimize=True)
    return {"file": path.name, "action": act, "changed_cells": len(changed), "reason": a.get("reason", "")}


def main() -> None:
    root = Path(sys.argv[1]).expanduser()
    OUT.mkdir(parents=True, exist_ok=True)
    report = {}
    for name, rel in RUNS.items():
        run = root / rel
        report[name] = {"play": gameplay_gif(name, run), "levels": level_starts(name, run)}
    report["ft09"]["probe"] = probe_pair("ft09", root / RUNS["ft09"], 1)
    report["sb26"]["probe"] = probe_pair("sb26", root / RUNS["sb26"], 1)
    (OUT / "figures.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
