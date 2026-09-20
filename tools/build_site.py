#!/usr/bin/env python
"""Write every page of the site: index.html and projects/*.html.   python3 tools/build_site.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from page import EMAIL, GITHUB, project, shell
from pages_arc import ARC2
from pages_arc3 import ARC3
from pages_other import CUDA, KAGG, ROUTING, TRAINIUM

ROOT = Path(__file__).resolve().parent.parent

PAGES = [("arc-agi-3", "ARC-AGI-3", ARC3), ("arc-agi-2", "ARC-AGI-2", ARC2),
         ("trainium-of-thought", "Trainium", TRAINIUM), ("kaggriculture", "Kaggriculture", KAGG),
         ("cuda-optimization", "CUDA kernels", CUDA), ("routing-foundation-model", "Routing", ROUTING)]

for i, (slug, _, spec) in enumerate(PAGES):
    prev = (PAGES[i - 1][1], f"{PAGES[i - 1][0]}.html") if i else None
    nxt = (PAGES[i + 1][1], f"{PAGES[i + 1][0]}.html") if i + 1 < len(PAGES) else None
    html = project(**spec, prev=prev, nxt=nxt)
    (ROOT / "projects" / f"{slug}.html").write_text(html)
    print("wrote", slug, len(html))


def row(when, status, href, title, text, result, note, img):
    live = f'<em class="live">{status}</em>' if status == "Ongoing" else f"<em>{status}</em>"
    return f"""<article class="row">
      <div class="row-side"><a class="thumb" href="{href}" tabindex="-1" aria-hidden="true"><img src="./assets/img/heroes/{img}-thumb.jpg" alt="" width="520" height="347"></a><div class="pm"><em>{when}</em>{live}</div></div>
      <div class="main"><h3><a href="{href}">{title}</a></h3><p>{text}</p></div>
      <div class="result"><b>{result}</b><br>{note}</div>
    </article>"""


HOME = f"""
<main>
<section class="hero" style="--accent:#b3245f"><div class="hero-in">
  <div>
    <p class="kicker"><i></i>Portfolio</p>
    <h1>Ritwika Kancharla&rsquo;s portfolio</h1>
    <p class="lede">I am an <strong>ML/AI engineer</strong> focused on large language models, from training and optimization to GPU kernel design. My current research is on the <strong>ARC Prize 2026 benchmarks</strong> with an <strong>open 27B language model</strong>.</p>
    <div class="actions"><a class="btn primary" href="#projects">View projects</a><a class="btn" href="./about.html">About me</a><a class="btn" href="{GITHUB}">GitHub</a></div>
  </div>
  <figure class="hero-img"><img src="./assets/img/heroes/coffee-cat.jpg" width="736" height="414" alt="A painted Siamese cat holding a glass of iced coffee against a deep pink background with pressed flowers." style="object-position:50% 35%"></figure>
</div></section>

<section class="sec" id="projects"><div class="wrap">
  <div class="sec-head"><h2>Projects</h2><p>Each project page states the problem, describes the approach, and reports results together with their evaluation setting and limitations.</p></div>

  <div class="features">
    <a class="feature" href="./projects/arc-agi-3.html">
      <div class="media"><img src="./assets/img/arc3/ft09-play.gif" width="256" height="270" alt="The game ft09 being played by the model, level by level."><img src="./assets/img/arc3/sb26-play.gif" width="256" height="270" alt="The game sb26 being played by the model, level by level."></div>
      <div class="feature-body">
        <div class="pm"><em>2026</em><em class="live">Ongoing</em><em>ARC Prize 2026</em></div>
        <h3><span>Verified World Models for Interactive Reasoning in ARC-AGI-3</span></h3>
        <p>ARC-AGI-3 places an agent in a small game with no instructions. An open 27B model proposes the rules of the game, and a deterministic harness handles perception, records every transition, tests each proposed rule against that record, and executes plans under guard conditions.</p>
        <div class="result"><b>14 of 14 levels</b> on two public games, without fine-tuning. Development-set result; not a leaderboard score.</div>
      </div>
    </a>
    <a class="feature" href="./projects/arc-agi-2.html">
      <div class="media"><img src="./assets/img/arc2/13e47133-test0-in.png" width="241" height="241" alt="An ARC-AGI-2 test input grid divided into regions."><img src="./assets/img/arc2/13e47133-test0-out.png" width="241" height="241" alt="The expected output grid, with each region filled by nested coloured rings."></div>
      <div class="feature-body">
        <div class="pm"><em>2026</em><em class="live">Ongoing</em><em>ARC Prize 2026</em></div>
        <h3><span>Verified Program Induction for ARC-AGI-2</span></h3>
        <p>A second solver for abstract grid puzzles. The model writes each puzzle's rule as a program, and the program must reproduce every training pair exactly before its answer is considered. The study measures how often such verified programs are still wrong on the test grid.</p>
        <div class="result"><b>33.89</b> leaderboard score (transductive baseline). Verified programs are correct on <b>10 of 15</b> test grids.</div>
      </div>
    </a>
  </div>

  <div class="rows">
    {row("2026", "Ongoing", "./projects/trainium-of-thought.html", "Trainium of Thought: Model and Kernel Co-Design under a 30-Minute Training Budget",
         "My entry in the AWS Trainium Frontier Competition on Devpost, a language-model training competition on a single Trainium2 chip in which wall-clock time is the only budget. The architecture and the fused kernels were developed together so that more useful optimizer steps fit into 30 minutes.",
         "1.3951 to 0.9656 val bpb", "Phase 1 ongoing. Currently 2nd on the public leaderboard; 1st at its peak.", "surfers")}
    {row("2026", "Ongoing", "./projects/kaggriculture.html", "Imitation Learning for a Long-Horizon Economic Game",
         "Recurrent behaviour cloning on a 719-decision farming economy. A strict evaluation audit showed that the first results were inflated by games in which the agent had failed, and it identified the cause.",
         "100,660 expert decisions", "140 complete games with seed-disjoint splits.", "tulips")}
    {row("2026", "Ongoing", "./projects/cuda-optimization.html", "A Verification-First Workflow for CUDA Kernel Optimization on Blackwell",
         "Contract work on the NVIDIA RTX PRO 6000. A kernel is accepted only if it is numerically correct, free of memory errors and at least 1.2&times; faster than PyTorch on every workload variant.",
         "sm_120, 16 workload variants", "Two task tracks completed.", "citrus")}
    {row("2025 to 2026", "Proposal", "./projects/routing-foundation-model.html", "Routing Foundation Models: Learned Warm Starts for Vehicle-Routing Solvers",
         "A hybrid design in which a learned model supplies an exact solver with diverse starting solutions, using a MILP-structured encoder, diffusion-based generation, state-space decoding and feasibility repair.",
         "83-page monograph", "Three manuscripts and prototype code. Not yet benchmarked.", "lakeside")}
  </div>
</div></section>

<section class="sec" id="contact"><div class="wrap">
  <div class="reach">
    <img src="./assets/img/heroes/sleeping-cat.jpg" width="735" height="412" alt="A woodblock-style print of a tabby cat asleep on a deep blue background." loading="lazy">
    <div><h2>Contact</h2>
      <p>For questions about any of these projects, or to discuss research and engineering work, send me an email.</p>
      <div class="actions"><a class="btn primary" href="mailto:{EMAIL}">Email me</a><a class="btn" href="{GITHUB}">GitHub</a></div></div>
  </div>
</div></section>
</main>
"""


ABOUT = f"""
<main>
<section class="hero about" style="--accent:#1d6b72"><div class="hero-in">
  <div>
    <p class="kicker"><i></i>About me</p>
    <h1>Ritwika Kancharla</h1>
    <p class="lede">I am an <strong>ML/AI engineer</strong> focused on large language models. I am interested in every part of the stack, from training and optimization to GPU kernel design and the agents built on top of the models.</p>
    <p class="lede">My current research is on the <strong>ARC Prize 2026 benchmarks</strong>, where I pair an <strong>open 27B language model</strong> with software that verifies each of its hypotheses before acting on it.</p>
    <p class="lede">I hold an M.S. in Computer Science from Purdue University and a B.Tech in Computer Science from IIT Madras. Previously I was a Software Development Engineer in Amazon's Supply Chain Optimization Technologies group.</p>
    <div class="actions"><a class="btn primary" href="mailto:{EMAIL}">Email me</a><a class="btn" href="./index.html#projects">Projects</a><a class="btn" href="{GITHUB}">GitHub</a></div>
  </div>
  <div class="about-side">
    <figure class="hero-img"><img src="./assets/img/heroes/terrace.jpg" width="735" height="490" alt="A stone terrace with flower urns under green branches, looking out over a bright turquoise lake." style="object-position:50% 70%"></figure>
    <aside class="now" aria-label="Current work">
      <p class="now-k">Current work</p>
      <ul>
        <li><b>ARC-AGI-3</b><span>Interactive games solved with verified world models</span></li>
        <li><b>ARC-AGI-2</b><span>Program induction checked against the training pairs</span></li>
        <li><b>CUDA kernels</b><span>Cross-attention backward pass on Blackwell</span></li>
      </ul>
    </aside>
  </div>
</div></section>

<section class="sec" id="background"><div class="wrap">
  <div class="sec-head"><h2>Background</h2><p>My interests developed from supply chain systems to learned optimization, and from there to reasoning agents and efficient model execution.</p></div>
  <div class="cv">
    <article><span class="when">M.S.</span><h3>Purdue University</h3><p class="role">Computer Science</p><p>Coursework and projects in machine learning systems, distributed systems and high-performance computing.</p></article>
    <article><span class="when">Industry</span><h3>Amazon</h3><p class="role">Software Development Engineer, SCOT</p><p>Supply Chain Optimization Technologies, working close to routing and middle-mile logistics.</p></article>
    <article><span class="when">B.Tech</span><h3>IIT Madras</h3><p class="role">Computer Science</p><p>Foundations in algorithms, computer systems and mathematical optimization.</p></article>
  </div>
</div></section>

<section class="sec" id="contact"><div class="wrap">
  <div class="reach">
    <img src="./assets/img/heroes/sleeping-cat.jpg" width="735" height="412" alt="A woodblock-style print of a tabby cat asleep on a deep blue background." loading="lazy">
    <div><h2>Contact</h2>
      <p>For questions about any of these projects, or to discuss research and engineering work, send me an email.</p>
      <div class="actions"><a class="btn primary" href="mailto:{EMAIL}">Email me</a><a class="btn" href="{GITHUB}">GitHub</a></div></div>
  </div>
</div></section>
</main>
"""

index = shell(root="./", title="Ritwika Kancharla | Portfolio",
              description="Ritwika Kancharla. Research and engineering in reasoning agents (ARC Prize 2026), language-model training under fixed compute, CUDA kernel optimization, and neural methods for vehicle routing.",
              body=HOME)
(ROOT / "index.html").write_text(index)
print("wrote index", len(index))

about = shell(root="./", title="About | Ritwika Kancharla",
              description="About Ritwika Kancharla: ML/AI engineer focused on large language models. Current work, education and experience, and contact.",
              body=ABOUT, on_about=True)
(ROOT / "about.html").write_text(about)
print("wrote about", len(about))
