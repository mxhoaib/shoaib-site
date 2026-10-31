#!/usr/bin/env python3
"""Build blog pages from posts/*.md into this site.

Requires the Markdown package: python3 -m pip install markdown

Front matter (YAML-style, JSON-quoted values):

    title, date, description, eyebrow, keywords, canonical

`canonical`, when set, becomes <link rel="canonical"> (and the matching
Open Graph / mainEntity URL). Other pages keep a self canonical.
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("build.py needs the markdown package: python3 -m pip install markdown")

ROOT = Path(__file__).resolve().parent
SITE = os.environ.get("SITE_URL", "https://mxhoaib.github.io/shoaib-site").rstrip("/")
POSTS = ROOT / "posts"

# Existing articles that are not stored as Markdown. Times keep the original
# index order when several posts share a calendar day.
LEGACY = [
    {"slug": "marble-shop-drawings-guide", "date": "2026-10-18T00:00:20+00:00", "title": "Marble Shop Drawings: A Complete Guide for Fabricators and Contractors", "description": "What marble and stone shop drawings must include, how they are approved, and how to avoid costly fabrication errors on site."},
    {"slug": "quantity-take-off-vs-bill-of-quantities", "date": "2026-10-18T00:00:19+00:00", "title": "Quantity Take-Off vs Bill of Quantities: What Is the Difference?", "description": "Quantity take-off and bill of quantities explained in plain English: what each one is, how a take-off is measured, how a BOQ is structured and which one your project needs."},
    {"slug": "how-to-calculate-marble-quantity", "date": "2026-10-17T00:00:18+00:00", "title": "How to Calculate Marble Quantity in Square Feet, Square Metres and Slabs", "description": "A practical method to calculate marble and stone quantities: measure net area, convert square feet and square metres, allow for waste and book-matching, and estimate how many slabs to order."},
    {"slug": "shop-drawings-vs-construction-drawings", "date": "2026-10-16T00:00:17+00:00", "title": "Shop Drawings vs Construction Drawings: Key Differences Explained", "description": "How shop drawings differ from construction drawings, design drawings, fabrication drawings and submittals, who prepares each, and why the difference matters on site."},
    {"slug": "autocad-drafting-services-what-to-expect", "date": "2026-10-15T00:00:16+00:00", "title": "Outsourcing AutoCAD Drafting Services: What to Expect and How to Prepare", "description": "A practical checklist for architects, contractors and homeowners hiring a freelance AutoCAD drafter, from inputs and file formats to revisions."},
    {"slug": "construction-cost-estimate-classes", "date": "2026-10-15T00:00:15+00:00", "title": "Construction Cost Estimate Classes and Accuracy Levels Explained", "description": "What the five construction cost estimate classes mean, how accurate each one is, what information each needs and how quantity take-offs move an estimate from a rough budget to a firm price."},
    {"slug": "how-to-prepare-for-3d-rendering", "date": "2026-10-12T00:00:14+00:00", "title": "How to Prepare Your Project for 3D Rendering Services", "description": "The drawings, materials and references a 3D visualiser needs to produce realistic architectural and interior renders on the first attempt."},
    {"slug": "shop-drawings-dubai-approval-process", "date": "2026-10-09T00:00:13+00:00", "title": "Shop Drawings in Dubai: Understanding the Submission and Approval Process", "description": "How shop drawings are prepared, submitted and approved on Dubai and UAE projects, with tips for subcontractors on fit-out, joinery and stone packages."},
    {"slug": "what-is-bim-small-firms", "date": "2026-10-06T00:00:12+00:00", "title": "What Is BIM? A Plain-English Guide for Small Firms and Contractors", "description": "An honest introduction to Building Information Modelling for small practices and contractors, including levels of detail, benefits and when 2D CAD is still enough."},
    {"slug": "website-for-contractors-checklist", "date": "2026-10-03T00:00:11+00:00", "title": "Website Checklist for Contractors and Stone Companies", "description": "A practical checklist for building a fast, trustworthy, search-friendly website for construction, fit-out and marble businesses in the USA, UK, Canada and UAE."},
]

EXTRA_CSS = (
    ".prose table{width:100%;border-collapse:collapse;margin:1.2em 0;font-size:16px}"
    ".prose th,.prose td{border:1px solid #d2d2d7;padding:8px 10px;text-align:left;vertical-align:top}"
    ".prose th{background:var(--gray)}.prose figure{margin:1.2em 0}"
    ".prose figcaption{font-size:15px;color:var(--mute);margin-top:.4em}"
    ".prose .key-takeaways{background:var(--gray);border-radius:var(--r);padding:8px 22px;margin:1.4em 0}"
    ".prose h3{margin-top:1.1em}"
    ".prose code{font-size:.92em;background:var(--gray);padding:.1em .35em;border-radius:6px}"
    ".prose svg{display:block;width:100%;height:auto}"
)

# Remove experience-duration claims. Patterns are specific so CSS such as 8vw is left alone.
EXPERIENCE_REPLACEMENTS = [
    ("8 years&#x27; UAE experience. ", ""),
    ("8 years' UAE experience. ", ""),
    ("CAD Drafter with 8 Years&#x27; UAE Experience", "UAE-Based CAD Drafter"),
    ("CAD Drafter with 8 Years' UAE Experience", "UAE-Based CAD Drafter"),
    ("with 8 years of experience in ", "working on "),
    (", with 8 years of drafting experience in the UAE.", ", a UAE-based CAD drafter."),
    ("a CAD drafter with 8 years of UAE experience.", "a UAE-based CAD drafter."),
    (
        "I have <strong>8 years of drafting experience</strong> in the United Arab Emirates, working mainly on ",
        "I work in the United Arab Emirates, mainly on ",
    ),
    ("based on eight years of drafting experience in the UAE", "for projects in the UAE"),
    (
        "I have spent eight years preparing drawings in the UAE, with a focus on ",
        "I prepare drawings in the UAE, with a focus on ",
    ),
    (
        "Yes. I have eight years of drafting experience in the UAE and prepare ",
        "Yes. I prepare ",
    ),
]

FORBIDDEN = re.compile(r"(?i)(\b8\s*years\b|\b8\s*yrs\b|\beight years\b)")


def parse_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise SystemExit("post is missing front matter")
    _, raw, body = text.split("---\n", 2)
    meta = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        meta[key.strip()] = json.loads(value) if value[:1] in "\"[" else value
    return meta, body.lstrip("\n")


def load_markdown_posts() -> list[dict]:
    posts = []
    for path in sorted(POSTS.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        slug = path.stem
        for key in ("title", "date", "description"):
            if not meta.get(key):
                raise SystemExit(f"{path.name} is missing {key}")
        posts.append({
            "slug": slug,
            "title": meta["title"],
            "date": meta["date"],
            "description": meta["description"],
            "eyebrow": meta.get("eyebrow") or "Guide",
            "keywords": meta.get("keywords") or "",
            "canonical": (meta.get("canonical") or "").strip(),
            "body": body,
            "markdown": True,
        })
    return posts


def slugify(text: str) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "section"


def add_heading_ids(fragment: str) -> str:
    used: dict[str, int] = {}

    def repl(match: re.Match) -> str:
        level, inner = match.group(1), match.group(2)
        base = slugify(inner)
        used[base] = used.get(base, 0) + 1
        hid = base if used[base] == 1 else f"{base}-{used[base]}"
        return f'<h{level} id="{hid}">{inner}</h{level}>'

    return re.sub(r"<h([2-4])>(.*?)</h\1>", repl, fragment, flags=re.S)


def make_toc(fragment: str) -> str:
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', fragment)
    if not heads:
        return ""
    items = "".join(f'<li><a href="#{hid}">{inner}</a></li>' for hid, inner in heads)
    return f'<nav class="toc" aria-label="Contents"><b>Contents</b><ol>{items}</ol></nav>'


def decorate_links(fragment: str) -> str:
    def repl(match: re.Match) -> str:
        href = match.group(1)
        if href.startswith("http://") or href.startswith("https://"):
            return f'<a href="{href}" rel="noopener" target="_blank">'
        return match.group(0)

    return re.sub(r'<a href="([^"]+)">', repl, fragment)


def render_markdown(body: str) -> str:
    return markdown.markdown(
        body,
        extensions=["tables", "sane_lists", "fenced_code", "md_in_html"],
        output_format="html",
    )


def plain_text(fragment: str) -> str:
    cleaned = re.sub(r"<svg\b.*?</svg>", " ", fragment, flags=re.S | re.I)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    return re.sub(r"\s+", " ", html.unescape(cleaned)).strip()


def word_count(fragment: str) -> int:
    return len(re.findall(r"[A-Za-z0-9']+", plain_text(fragment)))


def faq_schema(fragment: str) -> str | None:
    match = re.search(r'<h2 id="faq">.*?</h2>(.*)', fragment, flags=re.S)
    if not match:
        return None
    block = match.group(1)
    pairs = re.findall(r"<h3[^>]*>(.*?)</h3>\s*<p>(.*?)</p>", block, flags=re.S)
    if not pairs:
        return None
    entities = []
    for question, answer in pairs:
        entities.append({
            "@type": "Question",
            "name": plain_text(question),
            "acceptedAnswer": {"@type": "Answer", "text": plain_text(answer)},
        })
    return json.dumps(
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entities},
        ensure_ascii=False,
        separators=(", ", ": "),
    )


def hreflang(url: str) -> str:
    tags = []
    for lang in ("en-US", "en-GB", "en-CA", "en-AE", "x-default"):
        tags.append(f'<link rel="alternate" hreflang="{lang}" href="{html.escape(url, quote=True)}">')
    return "".join(tags)


def site_style() -> str:
    text = (ROOT / "blog" / "index.html").read_text(encoding="utf-8")
    match = re.search(r"<style>.*?</style>", text, flags=re.S)
    if not match:
        raise SystemExit("blog/index.html has no <style> block to reuse")
    return match.group(0).replace("</style>", EXTRA_CSS + "</style>")


def author_box() -> str:
    return (
        '<aside class="box"><b>Shoaib Hussan</b>'
        "<p>Instagram "
        '<a href="https://www.instagram.com/mxhaib/" rel="noopener">@mxhaib</a>'
        ' · <a href="https://www.linkedin.com/in/mshoaib94" rel="noopener">LinkedIn</a>'
        ' · Fiverr <a href="https://www.fiverr.com/mxhoaib" rel="noopener">mxhoaib</a>'
        ' · <a href="mailto:mxhoaib0@gmail.com">mxhoaib0@gmail.com</a></p></aside>'
    )


def render_post(post: dict, others: list[dict], style: str) -> str:
    slug = post["slug"]
    local = f"{SITE}/blog/{slug}/"
    canonical = post["canonical"] or local
    title = post["title"]
    description = post["description"]
    date = post["date"][:10]
    body = decorate_links(add_heading_ids(render_markdown(post["body"])))
    if re.search(r"<img\b|bp\.blogspot|googleusercontent", body, flags=re.I):
        raise SystemExit(f"{slug} hot-links an image; keep figures inline and skip Blogger images")
    toc = make_toc(body)
    words = word_count(body)
    minutes = max(1, round(words / 225))
    faq = faq_schema(body)
    more = "".join(
        f'<li><a href="../../blog/{item["slug"]}/">{html.escape(item["title"])}</a></li>'
        for item in others
    )
    esc_title = html.escape(title)
    esc_desc = html.escape(description)
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "datePublished": date,
        "dateModified": date,
        "author": {"@type": "Person", "name": "Shoaib Hussan", "url": f"{SITE}/about/"},
        "publisher": {"@type": "Person", "name": "Shoaib Hussan", "url": f"{SITE}/about/"},
        "mainEntityOfPage": canonical,
        "image": f"{SITE}/assets/og.png",
        "keywords": post["keywords"],
        "wordCount": words,
    }
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
            {"@type": "ListItem", "position": 3, "name": title, "item": local},
        ],
    }
    schema = (
        '<script type="application/ld+json">'
        + json.dumps(article, ensure_ascii=False, separators=(", ", ": "))
        + "</script>"
    )
    if faq:
        schema += '<script type="application/ld+json">' + faq + "</script>"
    schema += (
        '<script type="application/ld+json">'
        + json.dumps(crumbs, ensure_ascii=False, separators=(", ", ": "))
        + "</script>"
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc_title}</title><meta name="description" content="{esc_desc}">
<link rel="canonical" href="{html.escape(canonical, quote=True)}">{hreflang(local)}
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="article"><meta property="og:title" content="{esc_title}"><meta property="og:description" content="{esc_desc}"><meta property="og:url" content="{html.escape(canonical, quote=True)}"><meta property="og:image" content="{SITE}/assets/og.png"><meta property="og:site_name" content="Shoaib Hussan"><meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc_title}"><meta name="twitter:description" content="{esc_desc}"><meta name="twitter:image" content="{SITE}/assets/og.png">
<meta name="theme-color" content="#ffffff"><link rel="icon" href="../../assets/logo.svg" type="image/svg+xml"><link rel="alternate" type="application/rss+xml" title="Blog" href="../../rss.xml">
<!-- Google Search Console: set GSC_TOKEN in build.py, or verify via DNS TXT -->{style}{schema}<!-- GA4: set GA4_ID in build.py to enable Google Analytics 4 --></head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="nav"><div class="wrap nav-in"><a class="logo" href="../../" aria-label="Shoaib Hussan home"><b>Shoaib</b> Hussan</a><nav class="links" aria-label="Main"><a href="../../services/">Services</a><a href="../../portfolio/">Work</a><a href="https://d3ddd.com/blog/" aria-current=page>Blog</a><a href="../../about/">About</a><a href="../../faq/">FAQ</a><a href="../../contact/">Contact</a></nav><a class="btn sm" href="https://www.fiverr.com/mxhoaib" rel="noopener">Hire me on Fiverr</a></div></header>
<nav class="crumbs wrap" aria-label="Breadcrumb"><ol><li><a href="../../">Home</a></li><li><a href="../../blog/">Blog</a></li><li aria-current="page">{esc_title}</li></ol></nav><main id="main"><article class="sec art"><div class="wrap narrow prose"><header><p class="eyebrow">{html.escape(post["eyebrow"])}</p><h1 class="big">{esc_title}</h1>
<p class="meta">By <a href="../../about/" rel="author">Shoaib Hussan</a> · <time datetime="{date}">{date}</time> · {minutes} min read</p></header>
{toc}{body}
{author_box()}
<h2>More articles</h2><ul>{more}</ul></div></article></main>
<footer class="foot"><div class="wrap"><div class="fcols"><div><b>Shoaib Hussan</b><p>CAD drafting, shop drawings &amp; 3D design. UAE-based, working with clients in the USA, UK, Canada and UAE.</p></div>
<div><b>Services</b><a href="../../services/marble-shop-drawings/">Marble shop drawings</a><a href="../../services/architectural-drafting/">Architectural drafting</a><a href="../../services/autocad-drafting/">AutoCAD 2D/3D</a><a href="../../services/3d-rendering/">3D renders</a><a href="../../services/bim-modeling/">BIM</a><a href="../../services/website-development/">Websites</a><a href="../../services/architectural-estimation/">Estimation &amp; BOQ</a></div>
<div><b>Contact</b><a href="https://www.fiverr.com/mxhoaib" rel="noopener me">Fiverr</a><a href="mailto:mxhoaib0@gmail.com">mxhoaib0@gmail.com</a><a href="../../blog/">Blog</a><a href="../../rss.xml">RSS</a></div></div>
<p class="small">© 2026 Shoaib Hussan. Fiverr is a trademark of Fiverr International Ltd.; this is an independent site.</p></div></footer>
<script src="../../assets/main.js" defer></script></body></html>
"""


def card(post: dict, href: str) -> str:
    date = post["date"][:10]
    return (
        f'<a class="card post reveal" href="{href}">'
        f'<time datetime="{date}">{date}</time>'
        f'<h3>{html.escape(post["title"])}</h3>'
        f'<p>{html.escape(post["description"])}</p>'
        f'<span class="more">Read article ›</span></a>'
    )


def update_listings(posts: list[dict]) -> None:
    blog = ROOT / "blog" / "index.html"
    text = blog.read_text(encoding="utf-8")
    cards = "".join(card(post, f'../blog/{post["slug"]}/') for post in posts)
    updated, n = re.subn(
        r'(<section class="sec gray"><div class="wrap grid3">).*?(</div></section>)',
        lambda m: m.group(1) + cards + m.group(2),
        text,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit("could not update the blog index")
    blog.write_text(updated, encoding="utf-8")

    home = ROOT / "index.html"
    text = home.read_text(encoding="utf-8")
    home_cards = "".join(card(post, f'blog/{post["slug"]}/') for post in posts[:3])
    updated, n = re.subn(
        r'(<h2 class="big center reveal">From the blog\.</h2><div class="grid3">).*?(</div><p class="center"><a href=")[^"]*(">)',
        lambda m: m.group(1) + home_cards + m.group(2) + "blog/" + m.group(3),
        text,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit("could not update the homepage blog strip")
    home.write_text(updated, encoding="utf-8")


def update_sitemap(posts: list[dict]) -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    kept = [block for block in re.findall(r"<url>.*?</url>", text) if "/blog" not in block]

    def entry(loc: str, lastmod: str) -> str:
        alts = "".join(
            f'<xhtml:link rel="alternate" hreflang="{lang}" href="{loc}"/>'
            for lang in ("en-US", "en-GB", "en-CA", "en-AE", "x-default")
        )
        return f"<url><loc>{loc}</loc><lastmod>{lastmod}</lastmod>{alts}</url>"

    newest = posts[0]["date"][:10]
    blog_entries = [entry(f"{SITE}/blog/", newest)]
    blog_entries.extend(entry(f"{SITE}/blog/{post['slug']}/", post["date"][:10]) for post in posts)
    head = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
    path.write_text(head + "".join(kept) + "".join(blog_entries) + "</urlset>\n", encoding="utf-8")


def update_rss(posts: list[dict]) -> None:
    items = []
    for post in posts:
        day = datetime.strptime(post["date"][:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        loc = f"{SITE}/blog/{post['slug']}/"
        items.append(
            "<item>"
            f"<title>{html.escape(post['title'])}</title>"
            f"<link>{loc}</link><guid>{loc}</guid>"
            f"<pubDate>{format_datetime(day)}</pubDate>"
            f"<description>{html.escape(post['description'])}</description>"
            "</item>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<rss version=\"2.0\"><channel>"
        "<title>Shoaib Hussan – Blog</title>"
        f"<link>{SITE}/blog/</link>"
        "<description>Guides on shop drawings, CAD and 3D.</description>"
        "<language>en</language>"
        + "".join(items)
        + "</channel></rss>\n"
    )
    (ROOT / "rss.xml").write_text(xml, encoding="utf-8")


def strip_experience_claims() -> None:
    for path in ROOT.rglob("*"):
        if path.suffix.lower() not in {".html", ".xml", ".md", ".txt", ".js"}:
            continue
        if "posts" in path.parts and path.suffix == ".md":
            # Source posts are republished articles; still reject the phrase.
            pass
        original = path.read_text(encoding="utf-8")
        updated = original
        for old, new in EXPERIENCE_REPLACEMENTS:
            updated = updated.replace(old, new)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
        if FORBIDDEN.search(updated):
            raise SystemExit(f"forbidden experience phrase remains in {path.relative_to(ROOT)}")


def check_internal_links() -> None:
    missing = []
    for page in ROOT.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        text = re.sub(r"<script\b.*?</script>", "", text, flags=re.S | re.I)
        for href in re.findall(r'(?:href|src)="([^"]*)"', text):
            if not href or href.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
                continue
            target = (page.parent / href.split("#", 1)[0]).resolve()
            if target.is_dir():
                target = target / "index.html"
            try:
                target.relative_to(ROOT)
            except ValueError:
                missing.append((str(page.relative_to(ROOT)), href))
                continue
            if not target.is_file():
                missing.append((str(page.relative_to(ROOT)), href))
    if missing:
        for page, href in missing:
            print(f"broken link in {page}: {href}")
        raise SystemExit(f"{len(missing)} broken internal link(s)")


def main() -> None:
    fresh = load_markdown_posts()
    legacy_slugs = {item["slug"] for item in LEGACY}
    for post in fresh:
        if post["slug"] in legacy_slugs:
            raise SystemExit(f"slug collides with an existing post: {post['slug']}")
        if not post["canonical"]:
            raise SystemExit(f"{post['slug']} is missing a canonical URL")
    posts = sorted(fresh + LEGACY, key=lambda item: item["date"], reverse=True)
    style = site_style()
    for index, post in enumerate(posts):
        if not post.get("markdown"):
            continue
        others = [item for item in posts if item["slug"] != post["slug"]][:3]
        page = render_post(post, others, style)
        dest = ROOT / "blog" / post["slug"] / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page, encoding="utf-8")
        if f'rel="canonical" href="{post["canonical"]}"' not in page:
            raise SystemExit(f"canonical link missing for {post['slug']}")
        print(f"wrote blog/{post['slug']}/")
    update_listings(posts)
    update_sitemap(posts)
    update_rss(posts)
    strip_experience_claims()
    check_internal_links()
    print(f"built {len(fresh)} new posts; blog index lists {len(posts)}")


if __name__ == "__main__":
    main()
