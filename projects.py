"""Portfolio for this site: /projects/ grid, /projects/<slug>/ pages with a zoomable gallery,
a homepage Portfolio section and a "Portfolio" nav link. Called from build.py.

Sources: projects_src/<slug>.md (owner-approved copy) + projects_src/projects.json (order, card text, service).
Images:  assets/projects/<slug>/ (web-optimised, one copy each). Gallery script: assets/gallery.js.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

from PIL import Image  # reads image sizes for width/height attributes

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "projects_src"
IMG = "assets/projects"
FIVERR = "https://www.fiverr.com/mxhoaib"
EMAIL = "mxhoaib0@gmail.com"
LASTMOD = "2026-11-02"
SERVICE_LABELS = {
    "marble-shop-drawings": "Marble &amp; stone shop drawings",
    "architectural-drafting": "Architectural drafting",
    "autocad-drafting": "AutoCAD 2D &amp; 3D drafting",
    "architectural-estimation": "Estimation &amp; BOQ",
}

PF_CSS = (
    ".pf-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:28px}.pf-grid.pf-3{grid-template-columns:repeat(3,1fr);gap:22px}"
    ".pf-card{display:flex;flex-direction:column;background:#fff;border-radius:var(--r);overflow:hidden;color:var(--ink);transition:transform .3s,box-shadow .3s}"
    ".pf-card:hover{transform:translateY(-4px);box-shadow:0 18px 40px rgba(0,0,0,.08);text-decoration:none}"
    ".pf-card figure{margin:0;aspect-ratio:4/3;background:var(--gray);overflow:hidden}"
    ".pf-card img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .7s ease}.pf-card:hover img{transform:scale(1.04)}"
    ".pf-b{padding:26px 28px 30px;display:flex;flex-direction:column;gap:8px;flex:1}.pf-b h2,.pf-b h3{font-size:clamp(20px,2vw,26px);line-height:1.2;margin:0}"
    ".pf-3 .pf-b h3{font-size:19px}.pf-b p{color:var(--mute);margin:0;font-size:16px}.pf-tag{font-size:13px;color:var(--mute);letter-spacing:.02em}"
    ".pf-b .more{margin-top:auto;padding-top:6px}"
    ".dark .pf-card{background:#1d1d1f;color:#f5f5f7}.dark .pf-b p,.dark .pf-tag{color:#a1a1a6}.dark .pf-b .more{color:#2997ff}.dark .pf-card figure{background:#fff}"
    ".pf-hero{padding:72px 0 56px}.pf-hero .big{max-width:900px}.pf-by{color:var(--mute);font-size:15px;margin-top:18px}"
    ".pf-body{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(0,1fr);gap:64px;align-items:start}"
    ".pf-text p{font-size:19px;line-height:1.7;color:var(--mute);margin:0 0 1.1em}.pf-text p:first-child{color:var(--ink);font-size:21px}.pf-text strong{color:var(--ink)}"
    ".pf-facts{position:sticky;top:76px;background:var(--gray);border-radius:var(--r);padding:28px}.pf-facts dl{margin:0 0 22px;display:grid;gap:16px}"
    ".pf-facts dt{font-size:13px;color:var(--mute)}.pf-facts dd{margin:2px 0 0;font-size:17px;font-weight:600}.pf-facts .btn{display:block;text-align:center;margin:0}"
    ".pf-gallery{display:grid;grid-template-columns:repeat(2,1fr);gap:22px;margin-top:32px}"
    ".pf-shot{position:relative;display:flex;align-items:center;justify-content:center;background:#fff;border-radius:var(--r);overflow:hidden;cursor:zoom-in;aspect-ratio:4/3;padding:14px}"
    ".pf-shot:first-child{grid-column:1/-1;aspect-ratio:auto;padding:20px}.pf-shot img{max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain;display:block}"
    ".pf-shot:first-child img{max-height:80vh}.pf-zoom{position:absolute;right:14px;bottom:14px;width:40px;height:40px;border-radius:50%;background:rgba(0,0,0,.72);color:#fff;display:grid;place-items:center;font-size:22px;opacity:0;transition:opacity .25s}"
    ".pf-shot:hover .pf-zoom,.pf-shot:focus-visible .pf-zoom{opacity:1}"
    "@media (max-width:900px){.pf-grid.pf-3{grid-template-columns:1fr 1fr}.pf-body{grid-template-columns:1fr;gap:36px}.pf-facts{position:static}}"
    "@media (max-width:640px){.pf-grid,.pf-grid.pf-3,.pf-gallery{grid-template-columns:1fr;gap:18px}.pf-b{padding:22px}.pf-zoom{opacity:1}.pf-shot{aspect-ratio:auto}.pf-text p:first-child{font-size:19px}}"
)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def parse_page_md(text: str) -> dict:
    _, fm, body = text.split("---\n", 2)
    meta, key = {}, None
    for line in fm.splitlines():
        if line.startswith("  - ") and key:
            meta.setdefault(key, []).append(line[4:].strip())
        elif ":" in line:
            key, val = line.split(":", 1)
            key, val = key.strip(), val.strip()
            meta[key] = json.loads(val) if val.startswith('"') else (val or [])
    main, _, cta = body.partition("\n---\n")
    paras = []
    for block in re.split(r"\n\s*\n", main.strip()):
        b = block.strip()
        if not b or b.startswith("# ") or b.startswith("![") or b.startswith("**Software:**") or (b.startswith("*") and not b.startswith("**")):
            continue
        paras.append(b)
    meta["paragraphs"] = paras
    m = re.search(r"\*\*(.+?)\*\*\s*(.*?)\s*at \[", cta, re.S)
    meta["cta_h"], meta["cta_p"] = (m.group(1).strip(), m.group(2).strip()) if m else ("Need drawings like these?", "Send your design drawings and get a quote.")
    return meta


def load_projects() -> list[dict]:
    out = []
    for i, entry in enumerate(json.loads((SRC / "projects.json").read_text(encoding="utf-8"))):
        p = parse_page_md((SRC / f'{entry["slug"]}.md').read_text(encoding="utf-8"))
        assert p["slug"] == entry["slug"], entry["slug"]
        p.update(entry)
        p["num"] = "%02d" % (i + 1)
        p["sizes"] = {}
        for f in [p["thumbnail"]] + p["images"]:
            with Image.open(ROOT / IMG / p["slug"] / f) as im:
                p["sizes"][f] = im.size
        out.append(p)
    return out


def header(P: str, current: str = "") -> str:
    def a(path: str, label: str) -> str:
        cur = " aria-current=page" if current == path else ""
        return f'<a href="{P}{path}"{cur}>{label}</a>'
    return (f'<header class="nav"><div class="wrap nav-in"><a class="logo" href="{P or "./"}" aria-label="Shoaib Hussan home"><b>Shoaib</b> Hussan</a>'
            f'<nav class="links" aria-label="Main">{a("services/", "Services")}{a("projects/", "Portfolio")}{a("portfolio/", "Work")}'
            f'<a href="https://d3ddd.com/blog/">Blog</a>{a("about/", "About")}{a("faq/", "FAQ")}{a("contact/", "Contact")}</nav>'
            f'<a class="btn sm" href="{FIVERR}" rel="noopener">Hire me on Fiverr</a></div></header>')


def footer(P: str) -> str:
    return f'''<footer class="foot"><div class="wrap"><div class="fcols"><div><b>Shoaib Hussan</b><p>CAD drafting, shop drawings &amp; 3D design. UAE-based, working with clients in the USA, UK, Canada and UAE.</p></div>
<div><b>Services</b><a href="{P}services/marble-shop-drawings/">Marble shop drawings</a><a href="{P}services/architectural-drafting/">Architectural drafting</a><a href="{P}services/autocad-drafting/">AutoCAD 2D/3D</a><a href="{P}services/3d-rendering/">3D renders</a><a href="{P}services/bim-modeling/">BIM</a><a href="{P}services/website-development/">Websites</a><a href="{P}services/architectural-estimation/">Estimation &amp; BOQ</a></div>
<div><b>Contact</b><a href="{FIVERR}" rel="noopener me">Fiverr</a><a href="mailto:{EMAIL}">{EMAIL}</a><a href="https://d3ddd.com/blog/">Blog</a><a href="{P}rss.xml">RSS</a></div></div>
<p class="small">© 2026 Shoaib Hussan. Fiverr is a trademark of Fiverr International Ltd.; this is an independent site.</p></div></footer>'''


def cta(h: str, p: str) -> str:
    return (f'<section class="sec dark center reveal"><div class="wrap"><h2 class="big">{h}</h2><p class="lede">{p}</p>'
            f'<p><a class="btn" href="{FIVERR}" rel="noopener">Hire me on Fiverr</a> <a class="btn ghost" href="mailto:{EMAIL}">Email {EMAIL}</a></p></div></section>')


def card(p: dict, P: str, heading: str = "h3") -> str:
    th = p["thumbnail"]; w, h = p["sizes"][th]
    return (f'<a class="pf-card reveal" href="{P}projects/{p["slug"]}/"><figure><img src="{P}{IMG}/{p["slug"]}/{th}" alt="{esc(p["title"])} – thumbnail" '
            f'width="{w}" height="{h}" loading="lazy" decoding="async"></figure><div class="pf-b"><span class="pf-tag">{p["num"]} · {p["category"]}</span>'
            f'<{heading}>{esc(p["title"])}</{heading}><p>{esc(p["short"])}</p><span class="more">View project ›</span></div></a>')


def head(site: str, P: str, title: str, desc: str, path: str, style: str, schema: list, image: tuple | None = None, og_type: str = "website") -> str:
    url = f"{site}/{path}"
    img_url, iw, ih = image or (f"{site}/assets/og.png", None, None)
    dims = f'<meta property="og:image:width" content="{iw}"><meta property="og:image:height" content="{ih}">' if iw else ""
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{url}">' for l in ("en-US", "en-GB", "en-CA", "en-AE", "x-default"))
    ld = "".join('<script type="application/ld+json">' + json.dumps(s, ensure_ascii=False, separators=(", ", ": ")) + "</script>" for s in schema)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}">
<link rel="canonical" href="{url}">{alts}
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="{og_type}"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{url}"><meta property="og:image" content="{img_url}">{dims}<meta property="og:site_name" content="Shoaib Hussan"><meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{title}"><meta name="twitter:description" content="{desc}"><meta name="twitter:image" content="{img_url}">
<meta name="theme-color" content="#ffffff"><link rel="icon" href="{P}assets/logo.svg" type="image/svg+xml"><link rel="alternate" type="application/rss+xml" title="Blog" href="{P}rss.xml">
{style}{ld}</head><body>
<a class="skip" href="#main">Skip to content</a>
'''


def crumbs(site: str, items: list[tuple[str, str]]) -> dict:
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}


def render_index(site: str, projects: list[dict], style: str) -> str:
    P = "../"
    title = "Portfolio – Marble Shop Drawings &amp; Slab Layouts | Shoaib Hussan"
    desc = "Selected shop drawing projects from Dubai villas: waterjet marble medallions, flooring layouts, vanity and bathroom cladding drawings, slab cutting plans and pool tiling details."
    items = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": f'{site}/projects/{p["slug"]}/', "name": p["title"]} for i, p in enumerate(projects)]}
    schema = [crumbs(site, [("Home", f"{site}/"), ("Portfolio", f"{site}/projects/")]), items]
    return (head(site, P, title, desc, "projects/", style, schema) + header(P, "projects/") +
            '<nav class="crumbs wrap" aria-label="Breadcrumb"><ol><li><a href="../">Home</a></li><li aria-current="page">Portfolio</li></ol></nav>'
            '<main id="main"><section class="hero center"><div class="wrap"><p class="eyebrow">Selected work</p><h1 class="huge">Portfolio.</h1>'
            '<p class="lede">Marble and stone shop drawings, slab layouts and tiling details from villa projects in Dubai. Client details have been removed from every sheet.</p></div></section>'
            f'<section class="sec gray"><div class="wrap"><div class="pf-grid">{"".join(card(p, P, "h2") for p in projects)}</div></div></section>'
            + cta("Have drawings to start?", "Send your files on Fiverr and get a clear quote.") + "</main>\n" + footer(P) +
            f'\n<script src="{P}assets/main.js" defer></script></body></html>\n')


def md_inline(s: str) -> str:
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"^(Deliverables:)", r"<strong>\1</strong>", s)


def render_project(site: str, p: dict, projects: list[dict], style: str) -> str:
    P = "../../"
    i = projects.index(p)
    t = esc(p["title"])
    shots = []
    for n, f in enumerate(p["images"]):
        w, h = p["sizes"][f]
        src, alt = f'{P}{IMG}/{p["slug"]}/{f}', esc(f'{p["title"]} – drawing {n + 1}')
        shots.append(f'<a class="pf-shot" href="{src}" data-caption="{alt}"><img src="{src}" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async"><span class="pf-zoom" aria-hidden="true">+</span></a>')
    others = [projects[(i + k) % len(projects)] for k in (1, 2, 3)]
    svc = p["service"]
    first = p["images"][0]
    url = f'{site}/projects/{p["slug"]}/'
    work = {"@context": "https://schema.org", "@type": "CreativeWork", "name": p["title"], "description": p["meta_description"], "url": url,
            "image": [f'{site}/{IMG}/{p["slug"]}/{f}' for f in p["images"]], "creator": {"@type": "Person", "name": "Shoaib Hussan", "url": f"{site}/about/"},
            "locationCreated": {"@type": "Place", "name": "Dubai, United Arab Emirates"}}
    schema = [crumbs(site, [("Home", f"{site}/"), ("Portfolio", f"{site}/projects/"), (p["title"], url)]), work]
    body = (f'<nav class="crumbs wrap" aria-label="Breadcrumb"><ol><li><a href="{P}">Home</a></li><li><a href="{P}projects/">Portfolio</a></li><li aria-current="page">{t}</li></ol></nav>'
            f'<main id="main"><section class="pf-hero"><div class="wrap"><p class="eyebrow">{p["num"]} · {p["category"]} · Dubai</p><h1 class="big">{t}</h1>'
            f'<p class="lede" style="margin:0">{esc(p["short"])}</p><p class="pf-by">By Shoaib Hussan, Founder of D3DDD</p></div></section>'
            f'<section class="sec" style="padding-top:24px"><div class="wrap pf-body"><div class="pf-text">{"".join(f"<p>{md_inline(x)}</p>" for x in p["paragraphs"])}</div>'
            f'<aside class="pf-facts" aria-label="Project details"><dl><div><dt>Service</dt><dd><a href="{P}services/{svc}/">{SERVICE_LABELS[svc]}</a></dd></div>'
            f'<div><dt>Location</dt><dd>Dubai, UAE</dd></div><div><dt>Software</dt><dd>{esc(p["software"])}</dd></div><div><dt>Drawings shown</dt><dd>{len(p["images"])} sheets</dd></div></dl>'
            f'<a class="btn" href="{FIVERR}" rel="noopener">Get a quote on Fiverr</a></aside></div></section>'
            f'<section class="sec gray" aria-labelledby="gal-h"><div class="wrap"><h2 class="big" id="gal-h">The drawings.</h2>'
            f'<p class="lede" style="margin:0">Select a drawing to open it full screen. Scroll, pinch or double-tap to zoom; swipe or use the arrow keys to move between sheets.</p>'
            f'<div class="pf-gallery" data-gallery>{"".join(shots)}</div></div></section>'
            + cta(esc(p["cta_h"]), esc(p["cta_p"]) + ".") +
            f'<section class="sec"><div class="wrap"><h2 class="big">More projects.</h2><div class="pf-grid pf-3" style="margin-top:28px">{"".join(card(o, P) for o in others)}</div>'
            f'<p class="center" style="margin-top:28px"><a href="{P}projects/">All projects ›</a></p></div></section></main>\n')
    w, h = p["sizes"][first]
    return (head(site, P, t + " | Shoaib Hussan", esc(p["meta_description"]), f'projects/{p["slug"]}/', style, schema,
                 (f'{site}/{IMG}/{p["slug"]}/{first}', w, h), "article") + header(P, "projects/") + body + footer(P) +
            f'\n<script src="{P}assets/main.js" defer></script><script src="{P}assets/gallery.js" defer></script></body></html>\n')


HOME_START, HOME_END = "<!-- portfolio:start -->", "<!-- portfolio:end -->"
HOME_ANCHOR = '<section class="sec gray"><div class="wrap"><h2 class="big center reveal">Working with clients in four markets.'
CSS_START, CSS_END = "<!-- portfolio-css:start -->", "<!-- portfolio-css:end -->"


def update_home(projects: list[dict]) -> None:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    section = (f'{HOME_START}<section class="sec dark" id="portfolio"><div class="wrap"><p class="eyebrow center reveal">Portfolio</p>'
               f'<h2 class="big center reveal">Recent shop drawings.</h2><p class="lede center reveal">Real drawings from villa projects in Dubai, with client details removed.</p>'
               f'<div class="pf-grid pf-3" style="margin-top:40px">{"".join(card(p, "") for p in projects[:6])}</div>'
               f'<p class="center" style="margin-top:36px"><a class="btn ghost" href="projects/">View all {len(projects)} projects</a></p></div></section>{HOME_END}')
    if HOME_START in text:
        text = re.sub(re.escape(HOME_START) + ".*?" + re.escape(HOME_END), lambda m: section, text, count=1, flags=re.S)
    else:
        if text.count(HOME_ANCHOR) != 1:
            raise SystemExit("could not find the homepage anchor for the portfolio section")
        text = text.replace(HOME_ANCHOR, section + HOME_ANCHOR)
    css = f"{CSS_START}<style>{PF_CSS}</style>{CSS_END}"
    if CSS_START in text:
        text = re.sub(re.escape(CSS_START) + ".*?" + re.escape(CSS_END), lambda m: css, text, count=1, flags=re.S)
    else:
        text = text.replace("</head>", css + "</head>", 1)
    path.write_text(text, encoding="utf-8")


NAV_SERVICES = re.compile(r'(<nav class="links" aria-label="Main"><a href="((?:\.\./)*)services/"(?: aria-current=page)?>Services</a>)(?!<a href="(?:\.\./)*projects/")')


def add_nav_link() -> None:
    """Insert the Portfolio link after Services in every page's main nav (idempotent)."""
    for page in ROOT.rglob("*.html"):
        if ".git" in page.parts:
            continue
        text = page.read_text(encoding="utf-8")
        new = NAV_SERVICES.sub(lambda m: f'{m.group(1)}<a href="{m.group(2)}projects/">Portfolio</a>', text)
        if new != text:
            page.write_text(new, encoding="utf-8")


def update_sitemap(site: str, projects: list[dict]) -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"<url><loc>[^<]*/projects/[^<]*</loc>.*?</url>", "", text)

    def entry(loc: str) -> str:
        alts = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{loc}"/>' for l in ("en-US", "en-GB", "en-CA", "en-AE", "x-default"))
        return f"<url><loc>{loc}</loc><lastmod>{LASTMOD}</lastmod>{alts}</url>"

    entries = [entry(f"{site}/projects/")] + [entry(f'{site}/projects/{p["slug"]}/') for p in projects]
    path.write_text(text.replace("</urlset>", "".join(entries) + "</urlset>"), encoding="utf-8")


def build(site: str, base_style: str) -> None:
    projects = load_projects()
    style = base_style.replace("</style>", PF_CSS + "</style>")
    out = ROOT / "projects"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(render_index(site, projects, style), encoding="utf-8")
    for p in projects:
        d = out / p["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(render_project(site, p, projects, style), encoding="utf-8")
    update_home(projects)
    add_nav_link()
    update_sitemap(site, projects)
    print(f"built portfolio: {len(projects)} projects → projects/")
