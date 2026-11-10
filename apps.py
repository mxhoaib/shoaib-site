"""Homepage Web Apps / Free Tools section, plus a Tools nav link.

Add another app by appending an object to apps.json (title, description, href),
then rebuild with build.py. This module only fills the homepage block between
<!-- apps:start --> and <!-- apps:end -->, and inserts one nav link after Work.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APPS_START, APPS_END = "<!-- apps:start -->", "<!-- apps:end -->"
NAV_WORK = re.compile(
    r'(<a href="((?:\.\./)*)portfolio/"(?: aria-current=page)?>Work</a>)(?!<a href="\2#web-apps">)'
)


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def load_apps() -> list[dict]:
    apps = json.loads((ROOT / "apps.json").read_text(encoding="utf-8"))
    if not isinstance(apps, list) or not apps:
        raise SystemExit("apps.json must be a non-empty list")
    for app in apps:
        for key in ("title", "description", "href"):
            if not str(app.get(key, "")).strip():
                raise SystemExit(f"apps.json entry missing {key}")
        href = app["href"]
        if not href.startswith("https://"):
            raise SystemExit(f"app href must be https: {href}")
        if "instagram.com/mxhaib" in href.lower():
            raise SystemExit("refusing an instagram.com/mxhaib link")
    return apps


def card(app: dict) -> str:
    return (
        f'<a class="card reveal" href="{esc(app["href"])}" target="_blank" rel="noopener">'
        f'<h3>{esc(app["title"])}</h3><p>{esc(app["description"])}</p>'
        f'<span class="more">Open tool ›</span></a>'
    )


def section_html(apps: list[dict]) -> str:
    cards = "".join(card(app) for app in apps)
    return (
        f'{APPS_START}<section class="sec" id="web-apps"><div class="wrap">'
        f'<p class="eyebrow center reveal">Free Tools</p>'
        f'<h2 class="big center reveal">Web Apps.</h2>'
        f'<div class="grid3">{cards}</div></div></section>{APPS_END}'
    )


def update_home(apps: list[dict]) -> None:
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    block = section_html(apps)
    if APPS_START in text:
        text, n = re.subn(
            re.escape(APPS_START) + ".*?" + re.escape(APPS_END),
            lambda _m: block,
            text,
            count=1,
            flags=re.S,
        )
        if n != 1:
            raise SystemExit("could not replace the homepage web apps section")
    elif "<!-- portfolio:end -->" in text:
        text = text.replace("<!-- portfolio:end -->", "<!-- portfolio:end -->" + block, 1)
    else:
        anchor = '<section class="sec gray"><div class="wrap"><h2 class="big center reveal">Working with clients in four markets.'
        if text.count(anchor) != 1:
            raise SystemExit("could not find the homepage anchor for the web apps section")
        text = text.replace(anchor, block + anchor, 1)
    path.write_text(text, encoding="utf-8")


def add_nav_link() -> None:
    """Insert Tools after Work in every main nav. Idempotent. Skips pages with no nav."""
    for page in ROOT.rglob("*.html"):
        if ".git" in page.parts:
            continue
        text = page.read_text(encoding="utf-8")
        new, n = NAV_WORK.subn(
            lambda m: f'{m.group(1)}<a href="{m.group(2)}#web-apps">Tools</a>',
            text,
            count=1,
        )
        if n and new != text:
            page.write_text(new, encoding="utf-8")
    missing = []
    for page in ROOT.rglob("*.html"):
        if ".git" in page.parts:
            continue
        text = page.read_text(encoding="utf-8")
        if 'aria-label="Main"' not in text:
            continue
        if len(re.findall(r'href="(?:\.\./)*#web-apps">Tools</a>', text)) != 1:
            missing.append(str(page.relative_to(ROOT)))
    if missing:
        raise SystemExit("Tools nav link missing or duplicated on: " + ", ".join(missing))


def apply() -> None:
    apps = load_apps()
    update_home(apps)
    add_nav_link()
    print(f"web apps: {len(apps)} on the homepage, Tools nav link checked")


if __name__ == "__main__":
    apply()
