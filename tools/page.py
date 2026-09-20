"""Shared page shell. Every page of the site is written by tools/build_site.py through these two functions."""

import hashlib
import re
from pathlib import Path

FONTS = ("https://fonts.googleapis.com/css2?family=Martian+Mono:wght@400;500"
         "&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400"
         "&family=Schibsted+Grotesk:wght@400;500;700;800;900&display=swap")
EMAIL = "ritwikareddykancharla@gmail.com"
GITHUB = "https://github.com/ritwikareddykancharla"
# the stylesheet keeps its name, so browsers holding an older copy must be told it changed
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
<body>
<header class="site"><div class="bar">
  <a class="brand" href="@ROOT@index.html"><span class="mark">RK</span><span class="name">Ritwika Kancharla</span></a>
  <nav aria-label="Site">
    <a href="@ROOT@index.html#projects"@ON_PROJECTS@>Projects</a>
    <a href="@ROOT@index.html#publications">Publications</a>
    <a href="@ROOT@index.html#background">Background</a>
    <a href="@GITHUB@">GitHub</a>
  </nav>
  <a class="btn contact" href="mailto:@EMAIL@">Email</a>
</div></header>
@BODY@
<footer class="site-foot"><div class="wrap">
  <span>Ritwika Kancharla, 2026</span>
  <span><a href="mailto:@EMAIL@">@EMAIL@</a> &nbsp; <a href="@GITHUB@">GitHub</a></span>
</div></footer>
</body>
</html>
"""


def shell(*, root, title, description, body, on_projects=False):
    out = SHELL
    for key, val in (("@BODY@", body), ("@TITLE@", title), ("@DESC@", description), ("@FONTS@", FONTS),
                     ("@ON_PROJECTS@", ' class="on"' if on_projects else ""), ("@ROOT@", root),
                     ("@EMAIL@", EMAIL), ("@GITHUB@", GITHUB), ("@CSSV@", CSS_VERSION)):
        out = out.replace(key, val)
    return out


def project(*, title, description, eyebrow, h1, meta, links, abstract, body, prev=None, nxt=None):
    """A project page. Every <h2 id="x">Title</h2> in `body` is numbered and listed in the contents row."""
    sections = []

    def number(m):
        sections.append((m.group(1), re.sub(r"<[^>]+>", "", m.group(2))))
        return f'<h2 id="{m.group(1)}"><span class="num">{len(sections):02d}</span>{m.group(2)}</h2>'

    body = re.sub(r'<h2 id="([^"]+)">(.*?)</h2>', number, body)
    toc = "".join(f'<a class="chip" href="#{i}">{n}. {t}</a>' for n, (i, t) in enumerate(sections, 1))
    meta_html = "".join(f"<span>{m}</span>" for m in meta)
    meta_html += "".join(f'<span><a href="{u}">{t}</a></span>' for t, u in links)
    foot = ""
    if prev or nxt:
        a = f'<a class="btn" href="{prev[1]}">Previous: {prev[0]}</a>' if prev else "<span></span>"
        b = f'<a class="btn primary" href="{nxt[1]}">Next: {nxt[0]}</a>' if nxt else "<span></span>"
        foot = f'<div class="next">{a}{b}</div>'
    html = f"""
<main><article class="demo"><div class="wrap">
  <a class="crumb" href="../index.html#projects">&larr; All projects</a>
  <header class="post-head">
    <p class="eyebrow">{eyebrow}</p>
    <h1 class="post-title">{h1}</h1>
    <p class="meta">{meta_html}</p>
    <div class="toc">{toc}</div>
  </header>
  <div class="post-body">
    <div class="tldr"><p class="tk">Abstract</p>{abstract}</div>
{body}
  </div>
  {foot}
</div></article></main>"""
    return shell(root="../", title=title, description=description, body=html, on_projects=True)
