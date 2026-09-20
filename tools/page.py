"""Shared page shell. Every page of the site is written by tools/build_site.py through these two functions."""

import hashlib
import re
from pathlib import Path

FONTS = ("https://fonts.googleapis.com/css2?family=Martian+Mono:wght@400;500"
         "&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400"
         "&family=Schibsted+Grotesk:wght@400;500;700;800;900&display=swap")
EMAIL = "ritwikareddykancharla@gmail.com"
GITHUB = "https://github.com/ritwikareddykancharla"
# the stylesheet keeps its name, so browsers holding an older copy must be told it changed
def _ver(name):
    return hashlib.sha1((Path(__file__).resolve().parent.parent / "assets" / name).read_bytes()).hexdigest()[:8]


CSS_VERSION = hashlib.sha1((Path(__file__).resolve().parent.parent / "assets" / "site.css").read_bytes()).hexdigest()[:8]

SHELL = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="@DESC@">
  <meta name="theme-color" content="#f2f5fa">
  <title>@TITLE@</title>
  <link rel="icon" href="@ROOT@favicon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="@FONTS@" rel="stylesheet">
  <link rel="stylesheet" href="@ROOT@assets/site.css?v=@CSSV@">
</head>
<body id="top">
<header class="site"><div class="bar">
  <a class="brand" href="@ROOT@index.html"><span class="mark">RK</span><span class="name">Ritwika Kancharla</span></a>
  <nav aria-label="Site">
    <a href="@ROOT@index.html#projects"@ON_PROJECTS@>Projects</a>
    <a href="@ROOT@about.html"@ON_ABOUT@>About</a>
    <a href="@GITHUB@">GitHub</a>
  </nav>
  <a class="btn contact" href="mailto:@EMAIL@">Email</a>
</div></header>
@BODY@
<footer class="site-foot"><div class="wrap">
  <span>Ritwika Kancharla, 2026</span>
  <span><a href="mailto:@EMAIL@">Email</a> &nbsp; <a href="@GITHUB@">GitHub</a></span>
</div></footer>
<a class="totop" href="#top" aria-label="Back to top"><svg viewBox="0 0 48 48" aria-hidden="true"><circle class="ring-bg" cx="24" cy="24" r="21"/><circle class="ring" cx="24" cy="24" r="21"/><path d="M24 31V18M18 23.5l6-6 6 6"/></svg></a>
<script src="@ROOT@assets/site.js?v=@JSV@" defer></script>
</body>
</html>
"""


def shell(*, root, title, description, body, on_projects=False, on_about=False):
    out = SHELL
    for key, val in (("@BODY@", body), ("@TITLE@", title), ("@DESC@", description), ("@FONTS@", FONTS),
                     ("@ON_PROJECTS@", ' class="on"' if on_projects else ""),
                     ("@ON_ABOUT@", ' class="on"' if on_about else ""), ("@ROOT@", root),
                     ("@EMAIL@", EMAIL), ("@GITHUB@", GITHUB), ("@CSSV@", _ver("site.css")), ("@JSV@", _ver("site.js"))):
        out = out.replace(key, val)
    return out


def project(*, title, description, eyebrow, h1, meta, links, abstract, body, hero, prev=None, nxt=None):
    """A project page. Every <h2 id="x"> in `body` is numbered; h2 and h3 headings build the sticky contents sidebar."""
    sections = []  # [id, title, [(sub id, sub title)]]

    def heading(m):
        level, attrs, inner = m.group(1), m.group(2), m.group(3)
        text = re.sub(r"<[^>]+>", "", inner)
        if level == "2":
            sid = re.search(r'id="([^"]+)"', attrs).group(1)
            sections.append([sid, text, []])
            return f'<h2 id="{sid}"><span class="num">{len(sections):02d}</span>{inner}</h2>'
        if not sections:
            return m.group(0)
        sid = f"{sections[-1][0]}-{len(sections[-1][2]) + 1}"
        sections[-1][2].append((sid, text))
        return f'<h3 id="{sid}">{inner}</h3>'

    body = re.sub(r"<h([23])([^>]*)>(.*?)</h\1>", heading, body)
    toc = "".join(f'<a class="chip" href="#{i}">{n}. {t}</a>' for n, (i, t, _) in enumerate(sections, 1))
    side = ""
    for n, (i, t, subs) in enumerate(sections, 1):
        sub = "".join(f'<li><a href="#{si}">{st}</a></li>' for si, st in subs)
        sub = f'<div class="sub"><ol>{sub}</ol></div>' if subs else ""
        side += f'<li><a href="#{i}"><span class="sn">{n:02d}</span><span>{t}</span></a>{sub}</li>'
    meta_html = "".join(f"<span>{m}</span>" for m in meta)
    meta_html += "".join(f'<span><a href="{u}">{t}</a></span>' for t, u in links)
    foot = ""
    if prev or nxt:
        a = f'<a class="btn" href="{prev[1]}">Previous: {prev[0]}</a>' if prev else "<span></span>"
        b = f'<a class="btn primary" href="{nxt[1]}">Next: {nxt[0]}</a>' if nxt else "<span></span>"
        foot = f'<div class="next">{a}{b}</div>'
    credit = f'<figcaption>{hero["credit"]}</figcaption>' if hero.get("credit") else ""
    html = f"""
<main><article class="demo" style="--accent:{hero["accent"]}"><div class="wrap">
  <a class="crumb" href="../index.html#projects">&larr; All projects</a>
  <header class="post-head">
    <div class="head-text">
      <p class="eyebrow">{eyebrow}</p>
      <h1 class="post-title">{h1}</h1>
      <p class="meta">{meta_html}</p>
    </div>
    <figure class="hero-img"><img src="../assets/img/heroes/{hero["img"]}.jpg" alt="{hero["alt"]}" style="object-position:{hero.get("pos", "50% 50%")}">{credit}</figure>
    <div class="toc">{toc}</div>
  </header>
  <div class="post-grid">
    <aside class="side" aria-label="Contents"><div class="side-in">
      <p class="side-k"><span>Contents</span><span class="side-pct" aria-hidden="true">0%</span></p>
      <div class="side-bar" aria-hidden="true"><i></i></div>
      <ol class="side-list"><i class="side-ind" aria-hidden="true"></i>{side}</ol>
      <a class="side-top" href="#top">Back to top</a>
    </div></aside>
    <div class="post-body">
      <div class="tldr"><p class="tk">Abstract</p>{abstract}</div>
{body}
      {foot}
    </div>
  </div>
</div></article></main>"""
    return shell(root="../", title=title, description=description, body=html, on_projects=True)
