# ritwikareddykancharla.github.io

Portfolio site of [Ritwika Kancharla](https://ritwikareddykancharla.github.io/): project pages on
ARC Prize 2026, a 30-minute LM training competition, a long-horizon game agent, CUDA kernels, and
earlier research on neural methods for vehicle routing.

Static HTML, one stylesheet, no JavaScript. GitHub Pages publishes `main` from the repo root.

```
index.html               generated: intro, projects, publications, background
projects/*.html          generated: one page per project
assets/site.css          the theme (light, cobalt on cool paper)
assets/img/arc2, arc3    figures, generated from real run data
tools/page.py            page shell and the project-page template
tools/pages_arc.py       text of the two ARC pages
tools/pages_other.py     text of the other four project pages
tools/build_site.py      home page text; writes every HTML file
```

## Rebuilding

```bash
python3 tools/build_site.py                                # all HTML pages

PY=~/projects/arc-agi2/.venv/bin/python                    # has numpy + Pillow
$PY tools/build_arc3_figures.py ~/projects/arc-agi3/runs   # gameplay GIFs, level strips, probes
$PY tools/build_arc2_figures.py ~/projects/arc-agi2        # puzzle grids, wrong cells outlined
```

The figure scripts only read the other repos. `build_arc2_figures.py` re-runs saved model programs
through the arc-agi2 sandbox and writes `assets/img/arc2/figures.json` with image sizes and the
numbers quoted on the page.

## Writing rules for the project pages

Academic register: abstract, problem statement, approach, results, limitations. Every number is
reported with its evaluation setting, figures sit next to the claim they support, and negative
results are reported.
