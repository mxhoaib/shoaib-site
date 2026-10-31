#!/usr/bin/env python3
"""Build blog pages from Markdown files in posts/.

Front matter:

    title, description, date (YYYY-MM-DD), category, keywords
    published (optional ISO timestamp, used only for sort order)
    canonical (optional absolute URL). When set, <link rel="canonical">
    points at that URL (the original article) instead of this site.

Run: SITE_URL=https://mxhoaib.github.io/shoaib-site python3 build.py
"""
from __future__ import annotations

import html
import json
import os
import re
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
POSTS = ROOT / "posts"
SITE = os.environ.get("SITE_URL", "https://mxhoaib.github.io/shoaib-site").rstrip("/")
BANNED = re.compile(r"\b8\s*[- ]?\s*(?:years|yrs)\b", re.I)
HOTLINK = re.compile(
    r"https?://[^\"'\s>]*(?:blogspot|googleusercontent|ggpht|blogger\.com)[^\"'\s>]*\.(?:png|jpe?g|gif|webp)",
    re.I,
)

AUTHOR_BOX = (
    '<aside class="box"><b>Shoaib Hussan</b>'
    '<p>Instagram <a href="https://www.instagram.com/mxhaib/" rel="noopener">@mxhaib</a>'
    ' · <a href="https://www.linkedin.com/in/mshoaib94" rel="noopener">LinkedIn</a>'
    ' · Fiverr <a href="https://www.fiverr.com/mxhoaib" rel="noopener">mxhoaib</a>'
    ' · <a href="mailto:mxhoaib0@gmail.com">mxhoaib0@gmail.com</a></p>'
    '<a class="btn" href="https://www.fiverr.com/mxhoaib" rel="noopener">Hire me on Fiverr</a></aside>'
)

EXTRA_CSS = (
    ".prose table{border-collapse:collapse;width:100%;margin:1.2em 0;font-size:16px}"
    ".prose th,.prose td{border:1px solid #d2d2d7;padding:8px 10px;text-align:left;vertical-align:top}"
    ".prose th{background:var(--gray)}"
    ".prose figure{margin:0 0 1.4em}"
    ".prose figcaption{color:var(--mute);font-size:15px;margin-top:8px}"
    ".prose code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.92em;"
    "background:var(--gray);padding:.1em .35em;border-radius:6px}"
    ".prose h3{margin-top:1.15em}"
    ".key-takeaways{background:var(--gray);border-radius:var(--r);padding:8px 22px;margin:18px 0}"
)


def load_css() -> str:
    sample = (ROOT / "blog/what-is-bim-small-firms/index.html").read_text(encoding="utf-8")
    match = re.search(r"<style>(.*?)</style>", sample, re.S)
    if not match:
        raise SystemExit("could not read site CSS from an existing article")
    css = match.group(1)
    if ".prose table{" not in css:
        css += EXTRA_CSS
    return css


def parse_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise SystemExit("post is missing front matter")
    end = text.find("\n---\n", 3)
    if end == -1:
        raise SystemExit("front matter is not closed")
    raw = text[4:end]
    body = text[end + 5 :]
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            try:
                value = json.loads(value) if value[0] == '"' else value[1:-1]
            except json.JSONDecodeError:
                value = value[1:-1]
        meta[key.strip()] = value
    return meta, body.lstrip("\n")


def heading_id(text: str, used: dict[str, int]) -> str:
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-") or "section"
    count = used.get(slug, 0)
    used[slug] = count + 1
    return slug if count == 0 else f"{slug}-{count + 1}"


def link_html(url: str, inner: str) -> str:
    extra = ""
    if url.startswith("http://") or url.startswith("https://"):
        extra = ' rel="noopener" target="_blank"'
    return f'<a href="{html.escape(url, quote=True)}"{extra}>{inner}</a>'


def render_inline(src: str) -> str:
    out: list[str] = []
    i = 0
    n = len(src)

    def eat_until(delim: str, start: int) -> int | None:
        j = start
        while j < n:
            if src[j] == "\\":
                j += 2
                continue
            if src.startswith(delim, j):
                return j
            j += 1
        return None

    while i < n:
        if src[i] == "\\" and i + 1 < n:
            out.append(html.escape(src[i + 1]))
            i += 2
            continue
        if src[i] == "`":
            j = src.find("`", i + 1)
            if j == -1:
                out.append(html.escape(src[i:]))
                break
            out.append(f"<code>{html.escape(src[i + 1:j])}</code>")
            i = j + 1
            continue
        if src.startswith("**", i):
            j = eat_until("**", i + 2)
            if j is None:
                out.append(html.escape(src[i:]))
                break
            out.append(f"<strong>{render_inline(src[i + 2:j])}</strong>")
            i = j + 2
            continue
        if src[i] == "*":
            j = eat_until("*", i + 1)
            if j is None:
                out.append(html.escape(src[i:]))
                break
            out.append(f"<em>{render_inline(src[i + 1:j])}</em>")
            i = j + 1
            continue
        if src[i] == "[":
            match = re.match(r"\[(.*?)\]\(([^)\s]+)\)", src[i:])
            if match:
                out.append(link_html(match.group(2), render_inline(match.group(1))))
                i += match.end()
                continue
        nxt = i + 1
        while nxt < n and src[nxt] not in "\\`*[":
            nxt += 1
        out.append(html.escape(src[i:nxt]))
        i = nxt
    return "".join(out)


def plain_text(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def sanitize_html(raw: str) -> str:
    raw = re.sub(r"<img\b[^>]*>", "", raw, flags=re.I)
    raw = re.sub(r"<script\b[^>]*>.*?</script>", "", raw, flags=re.I | re.S)
    if HOTLINK.search(raw):
        raise SystemExit("refusing to emit a hotlinked Blogger image")
    return raw


def is_table_sep(line: str) -> bool:
    return bool(re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", line))


def split_row(line: str) -> list[str]:
    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|"):
        text = text[:-1]
    cells: list[str] = []
    buf: list[str] = []
    escaped = False
    for char in text:
        if escaped:
            buf.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "|":
            cells.append("".join(buf).strip())
            buf = []
        else:
            buf.append(char)
    cells.append("".join(buf).strip())
    return cells


def markdown_to_html(md: str) -> tuple[str, list[tuple[str, str]]]:
    lines = md.replace("\r\n", "\n").split("\n")
    i = 0
    blocks: list[str] = []
    toc: list[tuple[str, str]] = []
    used: dict[str, int] = {}

    def list_block(ordered: bool) -> str:
        nonlocal i
        items = []
        while i < len(lines):
            line = lines[i]
            match = re.match(r"\d+\. (.*)" if ordered else r"- (.*)", line)
            if not match:
                break
            items.append(f"<li>{render_inline(match.group(1).strip())}</li>")
            i += 1
        tag = "ol" if ordered else "ul"
        return f"<{tag}>{''.join(items)}</{tag}>"

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            lang = line[3:].strip().lower()
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            raw = "\n".join(buf)
            if lang == "html":
                blocks.append(sanitize_html(raw))
            else:
                blocks.append(f"<pre><code>{html.escape(raw)}</code></pre>")
            continue
        if line.startswith("### "):
            inner = render_inline(line[4:].strip())
            hid = heading_id(plain_text(inner), used)
            blocks.append(f'<h3 id="{hid}">{inner}</h3>')
            i += 1
            continue
        if line.startswith("## "):
            inner = render_inline(line[3:].strip())
            label = plain_text(inner)
            hid = heading_id(label, used)
            toc.append((hid, label))
            blocks.append(f'<h2 id="{hid}">{inner}</h2>')
            i += 1
            continue
        if line.startswith("- "):
            blocks.append(list_block(False))
            continue
        if re.match(r"\d+\. ", line):
            blocks.append(list_block(True))
            continue
        if "|" in line and i + 1 < len(lines) and is_table_sep(lines[i + 1]):
            header = split_row(line)
            i += 2
            body_rows = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                body_rows.append(split_row(lines[i]))
                i += 1
            head_html = "".join(f"<th>{render_inline(cell)}</th>" for cell in header)
            rows_html = []
            for row in body_rows:
                cells = "".join(f"<td>{render_inline(cell)}</td>" for cell in row)
                rows_html.append(f"<tr>{cells}</tr>")
            blocks.append(f"<table><thead><tr>{head_html}</tr></thead><tbody>{''.join(rows_html)}</tbody></table>")
            continue
        para = [line.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "```", "- ")) and not re.match(r"\d+\. ", lines[i]):
            if "|" in lines[i] and i + 1 < len(lines) and is_table_sep(lines[i + 1]):
                break
            para.append(lines[i].strip())
            i += 1
        blocks.append(f"<p>{render_inline(' '.join(para))}</p>")
    return "".join(blocks), toc


def words_of(fragment: str) -> int:
    text = plain_text(fragment)
    return len(re.findall(r"[A-Za-z0-9']+", text))


def hreflang(url: str) -> str:
    langs = ("en-US", "en-GB", "en-CA", "en-AE", "x-default")
    return "".join(f'<link rel="alternate" hreflang="{lang}" href="{url}">' for lang in langs)


def sitemap_links(url: str) -> str:
    langs = ("en-US", "en-GB", "en-CA", "en-AE", "x-default")
    return "".join(
        f'<xhtml:link rel="alternate" hreflang="{lang}" href="{url}"/>' for lang in langs
    )


def chrome(prefix: str) -> tuple[str, str]:
    header = (
        f'<a class="skip" href="#main">Skip to content</a>\n'
        f'<header class="nav"><div class="wrap nav-in"><a class="logo" href="{prefix}" aria-label="Shoaib Hussan home"><b>Shoaib</b> Hussan</a>'
        f'<nav class="links" aria-label="Main"><a href="{prefix}services/">Services</a><a href="{prefix}portfolio/">Work</a>'
        f'<a href="https://d3ddd.com/blog/" aria-current=page>Blog</a><a href="{prefix}about/">About</a>'
        f'<a href="{prefix}faq/">FAQ</a><a href="{prefix}contact/">Contact</a></nav>'
        f'<a class="btn sm" href="https://www.fiverr.com/mxhoaib" rel="noopener">Hire me on Fiverr</a></div></header>'
    )
    footer = (
        '<footer class="foot"><div class="wrap"><div class="fcols"><div><b>Shoaib Hussan</b>'
        '<p>CAD drafting, shop drawings &amp; 3D design. UAE-based, working with clients in the USA, UK, Canada and UAE.</p></div>\n'
        f'<div><b>Services</b><a href="{prefix}services/marble-shop-drawings/">Marble shop drawings</a>'
        f'<a href="{prefix}services/architectural-drafting/">Architectural drafting</a>'
        f'<a href="{prefix}services/autocad-drafting/">AutoCAD 2D/3D</a>'
        f'<a href="{prefix}services/3d-rendering/">3D renders</a>'
        f'<a href="{prefix}services/bim-modeling/">BIM</a>'
        f'<a href="{prefix}services/website-development/">Websites</a>'
        f'<a href="{prefix}services/architectural-estimation/">Estimation &amp; BOQ</a></div>\n'
        f'<div><b>Contact</b><a href="https://www.fiverr.com/mxhoaib" rel="noopener me">Fiverr</a>'
        f'<a href="mailto:mxhoaib0@gmail.com">mxhoaib0@gmail.com</a>'
        f'<a href="https://d3ddd.com/blog/">Blog</a><a href="{prefix}rss.xml">RSS</a></div></div>\n'
        '<p class="small">© 2026 Shoaib Hussan. Fiverr is a trademark of Fiverr International Ltd.; this is an independent site.</p></div></footer>\n'
        f'<script src="{prefix}assets/main.js" defer></script>'
    )
    return header, footer


def render_post(post: dict, css: str, related: list[dict]) -> str:
    local = f"{SITE}/blog/{post['slug']}/"
    canonical = post.get("canonical") or local
    title = post["title"]
    description = post["description"]
    body = post["html"]
    toc_html = ""
    if post["toc"]:
        items = "".join(f'<li><a href="#{hid}">{html.escape(label)}</a></li>' for hid, label in post["toc"])
        toc_html = f'<nav class="toc" aria-label="Contents"><b>Contents</b><ol>{items}</ol></nav>'
    end_note = ""
    if post.get("canonical"):
        end_note = (
            f'<p class="meta">Originally published on '
            f'<a href="{html.escape(post["canonical"], quote=True)}" rel="noopener">ShoaibSite</a>.</p>'
        )
    more = ""
    if related:
        lis = "".join(
            f'<li><a href="../../blog/{item["slug"]}/">{html.escape(item["title"])}</a></li>' for item in related
        )
        more = f"<h2>More articles</h2><ul>{lis}</ul>"
    eyebrow = f'<p class="eyebrow">{html.escape(post["category"])}</p>' if post.get("category") else ""
    minutes = max(1, round(post["words"] / 300))
    header, footer = chrome("../../")
    article_ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "datePublished": post["date"],
        "dateModified": post["date"],
        "author": {"@type": "Person", "name": "Shoaib Hussan", "url": f"{SITE}/about/"},
        "publisher": {"@type": "Person", "name": "Shoaib Hussan", "url": f"{SITE}/about/"},
        "mainEntityOfPage": local,
        "image": f"{SITE}/assets/og.png",
        "keywords": post.get("keywords") or post.get("category") or "",
        "wordCount": post["words"],
    }
    crumbs_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
            {"@type": "ListItem", "position": 3, "name": title, "item": local},
        ],
    }
    esc_title = html.escape(title)
    esc_desc = html.escape(description)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc_title}</title><meta name="description" content="{esc_desc}">
<link rel="canonical" href="{html.escape(canonical, quote=True)}">{hreflang(local)}
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="article"><meta property="og:title" content="{esc_title}"><meta property="og:description" content="{esc_desc}"><meta property="og:url" content="{local}"><meta property="og:image" content="{SITE}/assets/og.png"><meta property="og:site_name" content="Shoaib Hussan"><meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc_title}"><meta name="twitter:description" content="{esc_desc}"><meta name="twitter:image" content="{SITE}/assets/og.png">
<meta name="theme-color" content="#ffffff"><link rel="icon" href="../../assets/logo.svg" type="image/svg+xml"><link rel="alternate" type="application/rss+xml" title="Blog" href="../../rss.xml">
<!-- Google Search Console: set GSC_TOKEN in build.py, or verify via DNS TXT --><style>{css}</style><script type="application/ld+json">{json.dumps(article_ld, ensure_ascii=False)}</script><script type="application/ld+json">{json.dumps(crumbs_ld, ensure_ascii=False)}</script><!-- GA4: set GA4_ID in build.py to enable Google Analytics 4 --></head><body>
{header}
<nav class="crumbs wrap" aria-label="Breadcrumb"><ol><li><a href="../../">Home</a></li><li><a href="../../blog/">Blog</a></li><li aria-current="page">{esc_title}</li></ol></nav><main id="main"><article class="sec art"><div class="wrap narrow prose"><header>{eyebrow}<h1 class="big">{esc_title}</h1>
<p class="meta">By <a href="../../about/" rel="author">Shoaib Hussan</a> · <time datetime="{post["date"]}">{post["date"]}</time> · {minutes} min read</p></header>
{toc_html}{body}
{end_note}
{AUTHOR_BOX}
{more}</div></article></main>
{footer}</body></html>
"""


def card(post: dict, prefix: str) -> str:
    return (
        f'<a class="card post reveal" href="{prefix}{post["slug"]}/">'
        f'<time datetime="{post["date"]}">{post["date"]}</time>'
        f'<h3>{html.escape(post["title"])}</h3>'
        f'<p>{html.escape(post["description"])}</p>'
        f'<span class="more">Read article ›</span></a>'
    )


def load_markdown_posts() -> list[dict]:
    posts = []
    if not POSTS.exists():
        raise SystemExit("posts directory not found")
    for path in sorted(POSTS.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        for key in ("title", "description", "date"):
            if not meta.get(key):
                raise SystemExit(f"{path.name} is missing {key}")
        fragment, toc = markdown_to_html(body)
        if HOTLINK.search(fragment) or "<img" in fragment.lower():
            raise SystemExit(f"{path.name} contains an image; blogger images are not hotlinked")
        post = {
            "slug": path.stem,
            "title": meta["title"],
            "description": meta["description"],
            "date": meta["date"],
            "published": meta.get("published") or meta["date"],
            "category": meta.get("category") or "",
            "keywords": meta.get("keywords") or "",
            "canonical": meta.get("canonical") or "",
            "html": fragment,
            "toc": toc,
            "words": words_of(fragment),
            "source": "markdown",
        }
        posts.append(post)
    return posts


def load_existing(known: set[str]) -> list[dict]:
    found = []
    blog = ROOT / "blog"
    if not blog.exists():
        return found
    for directory in sorted(blog.iterdir()):
        if not directory.is_dir() or directory.name in known:
            continue
        page = directory / "index.html"
        if not page.exists():
            continue
        text = page.read_text(encoding="utf-8")
        title_m = re.search(r'<h1 class="big">(.*?)</h1>', text)
        date_m = re.search(r'<time datetime="(\d{4}-\d{2}-\d{2})"', text)
        desc_m = re.search(r'<meta name="description" content="(.*?)"', text)
        if not (title_m and date_m and desc_m):
            continue
        found.append(
            {
                "slug": directory.name,
                "title": html.unescape(title_m.group(1)),
                "description": html.unescape(desc_m.group(1)),
                "date": date_m.group(1),
                "published": date_m.group(1),
                "source": "html",
            }
        )
    return found


def sort_posts(posts: list[dict]) -> list[dict]:
    return sorted(posts, key=lambda post: (post["date"], post.get("published") or ""), reverse=True)


def update_blog_index(posts: list[dict]) -> None:
    path = ROOT / "blog/index.html"
    text = path.read_text(encoding="utf-8")
    cards = "".join(card(post, "../blog/") for post in posts)
    updated, count = re.subn(
        r'(<section class="sec gray"><div class="wrap grid3">).*?(</div></section>)',
        lambda match: match.group(1) + cards + match.group(2),
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit("could not update the blog index")
    path.write_text(updated, encoding="utf-8")


def update_home(posts: list[dict]) -> None:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    cards = "".join(card(post, "blog/") for post in posts[:3])

    def repl(match: re.Match) -> str:
        return match.group(1) + cards + match.group(2) + '<a href="blog/">All articles ›</a>'

    updated, count = re.subn(
        r'(<h2 class="big center reveal">From the blog\.</h2><div class="grid3">).*?(</div><p class="center">)<a href="[^"]*">All articles ›</a>',
        repl,
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit("could not update the homepage blog strip")
    path.write_text(updated, encoding="utf-8")


def update_sitemap(posts: list[dict]) -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    newest = posts[0]["date"] if posts else "2026-10-26"
    text, count = re.subn(
        r"(<loc>" + re.escape(SITE) + r"/blog/</loc><lastmod>)[^<]+",
        r"\g<1>" + newest,
        text,
        count=1,
    )
    if count != 1:
        raise SystemExit("could not update blog lastmod in sitemap")
    additions = []
    for post in posts:
        loc = f"{SITE}/blog/{post['slug']}/"
        if loc in text:
            continue
        additions.append(f"<url><loc>{loc}</loc><lastmod>{post['date']}</lastmod>{sitemap_links(loc)}</url>")
    if additions:
        text = text.replace("</urlset>", "".join(additions) + "</urlset>")
    path.write_text(text, encoding="utf-8")


def update_rss(posts: list[dict]) -> None:
    path = ROOT / "rss.xml"
    text = path.read_text(encoding="utf-8")
    items = []
    for post in posts:
        loc = f"{SITE}/blog/{post['slug']}/"
        stamp = datetime.strptime(post["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        items.append(
            "<item>"
            f"<title>{html.escape(post['title'])}</title>"
            f"<link>{loc}</link><guid>{loc}</guid>"
            f"<pubDate>{format_datetime(stamp)}</pubDate>"
            f"<description>{html.escape(post['description'])}</description>"
            "</item>"
        )
    updated, count = re.subn(
        r"<item>.*</item>",
        "".join(items),
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit("could not update rss.xml")
    path.write_text(updated, encoding="utf-8")


def assert_clean(fragment: str, label: str) -> None:
    if BANNED.search(fragment):
        raise SystemExit(f"{label} contains a banned experience phrase")
    if re.search(r"whatsapp|wa\.me|\+971", fragment, re.I):
        raise SystemExit(f"{label} contains a phone or WhatsApp contact")
    if HOTLINK.search(fragment):
        raise SystemExit(f"{label} hotlinks a Blogger image")


def main() -> None:
    css = load_css()
    markdown_posts = load_markdown_posts()
    known = {post["slug"] for post in markdown_posts}
    combined = sort_posts(markdown_posts + load_existing(known))
    by_slug = {post["slug"]: post for post in combined}
    for post in markdown_posts:
        related = [item for item in combined if item["slug"] != post["slug"]][:3]
        page = render_post(post, css, related)
        assert_clean(page, post["slug"])
        if post.get("canonical") and f'rel="canonical" href="{post["canonical"]}"' not in page:
            raise SystemExit(f"canonical link missing for {post['slug']}")
        if "Originally published on" not in page or "ShoaibSite" not in page:
            raise SystemExit(f"original publication note missing for {post['slug']}")
        for needle in ("instagram.com/mxhaib", "linkedin.com/in/mshoaib94", "fiverr.com/mxhoaib", "mxhoaib0@gmail.com"):
            if needle not in page:
                raise SystemExit(f"author box missing {needle} on {post['slug']}")
        destination = ROOT / "blog" / post["slug"] / "index.html"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(page, encoding="utf-8")
        by_slug[post["slug"]] = post
    ordered = sort_posts(list(by_slug.values()))
    update_blog_index(ordered)
    update_home(ordered)
    update_sitemap(ordered)
    update_rss(ordered)
    print(f"built {len(markdown_posts)} markdown posts; index lists {len(ordered)}")
    for post in markdown_posts:
        print(f"{SITE}/blog/{post['slug']}/")


if __name__ == "__main__":
    main()
