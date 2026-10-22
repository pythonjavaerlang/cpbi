"""CPBI static site generator.

Reads the exported content bundle (content/export.json), renders every page to
dist/ as static HTML with clean Ukrainian slugs, per-page SEO + Open Graph tags,
generates a Ukrainian OG image per page, and emits sitemap.xml + robots.txt.

Usage:  python build.py
"""
from __future__ import annotations

import datetime
import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

import config
from og_image import generate_og_image
from seo import SeoMeta, seo_head, organization_schema, website_schema, article_schema
from slugs import slugify
from book_descriptions import description_for

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content" / "export.json"
DIST = ROOT / "dist"
TEMPLATES = ROOT / "templates"
MEDIA_URL = "/media/"

# ── Jinja env ───────────────────────────────────────────────────────────────
env = Environment(
    loader=FileSystemLoader(str(TEMPLATES)),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)
env.globals.update(
    seo_head=seo_head,
    site_name=config.SITE_NAME,
    media_url=MEDIA_URL,
    fixed=config.FIXED_PAGES,
    section=config.SECTION,
    ga_id=config.GA_MEASUREMENT_ID,
    ot_slug=config.COMMENTARY_BOOK_SLUGS[21],
    nt_slug=config.COMMENTARY_BOOK_SLUGS[1],
)

_pages_for_sitemap: list[str] = []

# Chapter title -> generated map scene (see make_maps.py). The image is shown at
# the top of the chapter reader when present.
CHAPTER_MAPS = {
    "Книга Єремії": "jeremiah-egypt",
    "Вихід": "exodus",
    "Ісуса Навина": "conquest-canaan",
    "Книга Суддів": "conquest-canaan",
    "I Царів": "divided-kingdom",
    "II Царів": "divided-kingdom",
    "Даниїла": "exile-mesopotamia",
    "Книга Єзекиїла": "exile-mesopotamia",
    "Езри": "exile-mesopotamia",
    "Книга Неємії": "exile-mesopotamia",
    "Естери": "exile-mesopotamia",
    "Одкровення": "seven-churches",
    # Pauline epistles share the «міста послань Павла» map.
    "Послання  до  Римлян": "paul-regions",
    "Перше Послання до Корінтян": "paul-regions",
    "Друге Послання до Корінтян": "paul-regions",
    "Послання до Галатів": "paul-regions",
    "Послання  до Ефесян": "paul-regions",
    "Послання до Филип’ян": "paul-regions",
    "Послання  до Колосян": "paul-regions",
    "Перше Послання до Солунян": "paul-regions",
    "Друге Послання до Солунян": "paul-regions",
    "Перше Послання  до Тимотея": "paul-regions",
    "Друге Послання  до Тимотея": "paul-regions",
    "Послання  до Тита": "paul-regions",
    "Послання до Євреїв": "paul-regions",
}


def _chapter_map(title):
    import re as _re
    key = _re.sub(r"\s+", " ", (title or "").strip())
    norm_maps = {_re.sub(r"\s+", " ", k): v for k, v in CHAPTER_MAPS.items()}
    scene = norm_maps.get(key)
    return f"/media/maps/{scene}.png" if scene else None


def load_bundle() -> dict:
    with open(CONTENT, encoding="utf-8") as f:
        return json.load(f)


def canonical(path: str) -> str:
    path = "/" + path.strip("/")
    if path != "/":
        path += "/"
    return f"{config.BASE_URL}{path}"


import re as _re_rel

# Rewrite root-relative href/src ("/foo") to a path relative to the current
# page's depth, so the site works at any base (domain root, subpath, or file://)
# and never leaks the build directory into URLs. Absolute (http/https/mailto/
# tel/#/data:) and protocol-relative (//) URLs are left untouched.
_REL_ATTR_RE = _re_rel.compile(r'(\b(?:href|src)=")(/(?!/)[^"]*)(")')


def _relativise(html: str, depth: int) -> str:
    prefix = "../" * depth if depth > 0 else "./"

    def repl(m):
        attr, url, end = m.group(1), m.group(2), m.group(3)
        # url starts with a single "/"; strip it and prepend the relative prefix.
        return f"{attr}{prefix}{url[1:]}{end}"

    return _REL_ATTR_RE.sub(repl, html)


def write_page(out_path: str, html: str, *, sitemap: bool = True) -> None:
    """out_path is a site path like 'history' or '' (home) or 'biblioteka/x/y'."""
    rel = out_path.strip("/")
    depth = len([p for p in rel.split("/") if p]) if rel else 0
    html = _relativise(html, depth)
    target = DIST / rel / "index.html" if rel else DIST / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    if sitemap:
        _pages_for_sitemap.append(canonical(out_path))


def make_meta(slug: str, title: str, description: str, *, og_type="website",
              subtitle="", structured=None) -> SeoMeta:
    og_rel = generate_og_image(slug or "index", title, DIST, subtitle=subtitle)
    return SeoMeta(
        title=f"{title} — {config.SITE_NAME}" if title and slug else (title or config.SITE_NAME),
        description=description or config.SEO_DEFAULT_DESCRIPTION,
        canonical_url=canonical(slug),
        og_image="/" + og_rel,
        og_image_alt=title,
        og_type=og_type,
        structured_data=structured or [],
    )


def strip_html(text: str, limit: int = 160) -> str:
    import re
    t = re.sub(r"<[^>]+>", " ", text or "")
    t = re.sub(r"&[a-z]+;", " ", t)
    t = " ".join(t.split())
    return (t[: limit - 1] + "\u2026") if len(t) > limit else t


# ── Flatpage slug normalisation ───────────────────────────────────────────────
def flatpage_slug(url: str, title: str = "") -> str:
    """Convert a Django flatpage url (/history/ or /cpbi.info/library/foo/) to a
    clean single-segment slug. Numeric-only segments fall back to the title."""
    parts = [p for p in url.strip("/").split("/") if p and p != "cpbi.info"]
    if not parts:
        return slugify(title) or "page"
    seg = parts[-1]
    if seg.isdigit():
        return slugify(title) or f"page-{seg}"
    return slugify(seg)


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    bundle = load_bundle()

    # Index books/chapters.
    books = {b["id"]: b for b in bundle["books"]}
    chapters_by_book: dict[int, list] = {}
    for ch in bundle["chapters"]:
        chapters_by_book.setdefault(ch["book_id"], []).append(ch)
    for lst in chapters_by_book.values():
        lst.sort(key=lambda c: (c.get("ordering") or 0))

    # Compute slugs.
    book_slug = {}
    for bid, b in books.items():
        book_slug[bid] = config.COMMENTARY_BOOK_SLUGS.get(bid) or slugify(b["title"])
    chapter_slug = {}
    for bid, lst in chapters_by_book.items():
        seen = set()
        for ch in lst:
            s = slugify(ch["title"]) or f"chapter-{ch['id']}"
            base = s
            i = 2
            while s in seen:
                s = f"{base}-{i}"
                i += 1
            seen.add(s)
            chapter_slug[ch["id"]] = s

    # ── Home ──────────────────────────────────────────────────────────────────
    latest_news = None
    if bundle["blog"]:
        b0 = bundle["blog"][0]
        latest_news = {"slug": slugify(b0["title"]) or b0["slug"], "title": b0["title"]}
    meta = make_meta("", config.SITE_NAME, config.SEO_DEFAULT_DESCRIPTION,
                     structured=[organization_schema(), website_schema()])
    write_page("", env.get_template("home.html").render(meta=meta, latest_news=latest_news))

    # ── Flatpages (mount at root) ──────────────────────────────────────────────
    for fp in bundle["flatpages"]:
        slug = flatpage_slug(fp["url"], fp["title"])
        desc = strip_html(fp["content"]) or fp["title"]
        meta = make_meta(slug, fp["title"], desc, og_type="article")
        html = env.get_template("flatpage.html").render(
            meta=meta, page_slug=slug, page_title=fp["title"], page_content=fp["content"],
        )
        write_page(slug, html)

    # ── Commentary TOC (bible) ─────────────────────────────────────────────────
    commentary_books = []
    for bid, b in books.items():
        if not b.get("is_commentary"):
            continue
        commentary_books.append({
            "slug": book_slug[bid],
            "title": b["title"],
            "chapters": [
                {"slug": chapter_slug[ch["id"]], "title": ch["title"]}
                for ch in chapters_by_book.get(bid, [])
            ],
        })
    commentary_books.sort(key=lambda x: x["slug"])
    meta = make_meta(config.FIXED_PAGES["bible"],
                     "Тлумачення Святого Письма Старого і Нового Завіту",
                     "Тлумачення Святого Письма українською мовою — Старий і Новий Завіт.")
    write_page(config.FIXED_PAGES["bible"],
               env.get_template("bible.html").render(meta=meta, commentary_books=commentary_books))

    # ── Library index ──────────────────────────────────────────────────────────
    lib_books = []
    for bid, b in books.items():
        chs = chapters_by_book.get(bid, [])
        if not chs:
            continue
        lib_books.append({
            "slug": book_slug[bid],
            "title": b["title"],
            "short_description": b.get("short_description") or "",
            "first_chapter_slug": chapter_slug[chs[0]["id"]],
        })
    lib_books.sort(key=lambda x: x["title"])
    meta = make_meta(config.FIXED_PAGES["library"], "Бібліотека",
                     "Бібліотека Чернівецького православного богословського інституту.")
    write_page(config.FIXED_PAGES["library"],
               env.get_template("library.html").render(meta=meta, books=lib_books))

    # ── Book chapters ───────────────────────────────────────────────────────────
    for bid, b in books.items():
        chs = chapters_by_book.get(bid, [])
        bslug = book_slug[bid]
        contents = [{"slug": chapter_slug[c["id"]], "title": c["title"]} for c in chs]
        for i, ch in enumerate(chs):
            cslug = chapter_slug[ch["id"]]
            path = f"{bslug}/{cslug}"
            prev_url = f"/{bslug}/{chapter_slug[chs[i-1]['id']]}/" if i > 0 else None
            next_url = f"/{bslug}/{chapter_slug[chs[i+1]['id']]}/" if i < len(chs) - 1 else None
            desc = description_for(ch["title"]) or strip_html(ch["text"]) or f"{b['title']} — {ch['title']}"
            meta = make_meta(path, ch["title"], desc, og_type="article",
                             subtitle=b["title"],
                             structured=[article_schema(
                                 ch["title"], desc, canonical(path),
                                 section=b["title"])])
            html = env.get_template("chapter.html").render(
                meta=meta,
                chapter={"title": ch["title"], "text": ch["text"], "css": ch.get("css"), "description": description_for(ch["title"])},
                book={"slug": bslug, "title": b["title"],
                      "short_description": b.get("short_description") or ""},
                contents=contents,
                prev_url=prev_url, next_url=next_url,
                prev_title=chs[i-1]["title"] if i > 0 else "",
                next_title=chs[i+1]["title"] if i < len(chs) - 1 else "",
                chapter_map=_chapter_map(ch["title"]),
            )
            write_page(path, html)

        # Book root page = first chapter content (parity with Django BookView).
        if chs:
            ch = chs[0]
            cslug = chapter_slug[ch["id"]]
            next_url = f"/{bslug}/{chapter_slug[chs[1]['id']]}/" if len(chs) > 1 else None
            desc = description_for(ch["title"]) or strip_html(ch["text"]) or f"{b['title']} — {ch['title']}"
            meta = make_meta(bslug, b["title"], desc, og_type="article", subtitle=b["title"],
                             structured=[article_schema(
                                 b["title"], desc, canonical(bslug),
                                 section=b["title"])])
            html = env.get_template("chapter.html").render(
                meta=meta,
                chapter={"title": ch["title"], "text": ch["text"], "css": ch.get("css"), "description": description_for(ch["title"])},
                book={"slug": bslug, "title": b["title"],
                      "short_description": b.get("short_description") or ""},
                contents=contents,
                prev_url=None, next_url=next_url,
                prev_title="", next_title=chs[1]["title"] if len(chs) > 1 else "",
                chapter_map=_chapter_map(ch["title"]),
            )
            write_page(bslug, html)

    # ── Journal + issues ────────────────────────────────────────────────────────
    issues = bundle["issues"]
    issue_slug = {}
    seen = set()
    for it in issues:
        s = slugify(it["title"]) or f"issue-{it['id']}"
        base, i = s, 2
        while s in seen:
            s = f"{base}-{i}"; i += 1
        seen.add(s); issue_slug[it["id"]] = s
    journal = bundle["journals"][0] if bundle["journals"] else None
    if journal:
        jmeta = make_meta(config.FIXED_PAGES["journal"], journal["title"],
                          strip_html(journal.get("short_description") or "") or journal["title"])
        write_page(config.FIXED_PAGES["journal"], env.get_template("journal.html").render(
            meta=jmeta, journal=journal,
            issues=[{"slug": issue_slug[i["id"]], "title": i["title"]} for i in issues],
        ))
        contents = [{"slug": issue_slug[i["id"]], "title": i["title"]} for i in issues]
        for idx, it in enumerate(issues):
            s = issue_slug[it["id"]]
            path = f"{config.SECTION['journal']}/{s}"
            prev_url = f"/{config.SECTION['journal']}/{issue_slug[issues[idx-1]['id']]}/" if idx > 0 else None
            next_url = f"/{config.SECTION['journal']}/{issue_slug[issues[idx+1]['id']]}/" if idx < len(issues)-1 else None
            meta = make_meta(path, it["title"], strip_html(it["text"]) or it["title"],
                             og_type="article", subtitle=journal["title"])
            html = env.get_template("journal_issue.html").render(
                meta=meta, issue={"title": it["title"], "text": it["text"], "css": it.get("css")},
                contents=contents, prev_url=prev_url, next_url=next_url,
                prev_title=issues[idx-1]["title"] if idx > 0 else "",
                next_title=issues[idx+1]["title"] if idx < len(issues)-1 else "",
            )
            write_page(path, html)

    # ── Blog ─────────────────────────────────────────────────────────────────────
    blog = bundle["blog"]
    blog_slug = {}
    for e in blog:
        blog_slug[e["id"]] = slugify(e["title"]) or e["slug"]
    bmeta = make_meta(config.FIXED_PAGES["news"], "Новини", "Новини та оголошення " + config.SITE_NAME)
    write_page(config.FIXED_PAGES["news"], env.get_template("blog_list.html").render(
        meta=bmeta,
        entries=[{"slug": blog_slug[e["id"]], "title": e["title"],
                  "announcement": e.get("announcement") or "",
                  "date": (e.get("created") or "")[:10]} for e in blog],
    ))
    for e in blog:
        s = blog_slug[e["id"]]
        path = f"{config.SECTION['news']}/{s}"
        meta = make_meta(path, e["title"], strip_html(e.get("body") or "") or e["title"], og_type="article")
        html = env.get_template("blog_entry.html").render(
            meta=meta, entry={"title": e["title"], "body": e.get("body") or "",
                              "date": (e.get("created") or "")[:10]},
        )
        write_page(path, html)

    # ── Events ─────────────────────────────────────────────────────────────────
    for ev in bundle["events"]:
        s = ev.get("slug") or slugify(ev.get("summary") or f"event-{ev['id']}")
        s = slugify(s)
        path = f"{config.SECTION['event']}/{s}"
        title = ev.get("summary") or "Подія"
        meta = make_meta(path, title, strip_html(ev.get("desc") or "") or title, og_type="article")
        html = env.get_template("event.html").render(
            meta=meta, event={"slug": s, "summary": title, "desc": ev.get("desc") or ""},
        )
        write_page(path, html)

    # ── Lecture / donate / contact / apply / school / journal subscription ──────
    meta = make_meta(config.FIXED_PAGES["lecture"], "Відео-лекції",
                     "Відео-лекції Чернівецького православного богословського інституту.")
    write_page(config.FIXED_PAGES["lecture"], env.get_template("lecture.html").render(meta=meta))

    meta = make_meta(config.FIXED_PAGES["donate"], "Доброчинцям",
                     "Підтримайте Чернівецький православний богословський інститут пожертвою.")
    write_page(config.FIXED_PAGES["donate"], env.get_template("donate.html").render(meta=meta))

    # Tally form pages (form ids to be filled after import).
    form_pages = [
        (config.FIXED_PAGES["contact"], "Зв'язатися з нами",
         "Напишіть нам — ми відповімо якнайшвидше.", "labN0v",
         "Контакти " + config.SITE_NAME),
        (config.FIXED_PAGES["apply"], "Вступ — подання заяви",
         "Заповніть форму вступу до інституту.", "dbWYZK",
         "Вступ до " + config.SITE_NAME),
        (config.FIXED_PAGES["school"], "Початкова школа — заява",
         "Заповніть форму для вступу до початкової школи.", "OQDAjg",
         "Початкова школа при ЧПБІ"),
        (config.FIXED_PAGES["journal_subscription"], "Передплата журналу",
         "Оформіть передплату науково-богословського журналу «Світильник».",
         "RWGzZj", "Передплата журналу «Світильник»"),
    ]
    for slug, title, intro, form_id, desc in form_pages:
        meta = make_meta(slug, title, desc)
        html = env.get_template("form_page.html").render(
            meta=meta, page_slug=slug, page_title=title, intro=intro, tally_form_id=form_id,
        )
        write_page(slug, html)

    # ── sitemap.xml + robots.txt ────────────────────────────────────────────────
    copy_media()
    write_pages_files()
    write_sitemap()
    write_robots()

    print(f"Built {len(_pages_for_sitemap)} pages into {DIST}")


def copy_media():
    """Copy the bundled media assets (assets/media + generated assets/maps) into
    dist/media so the published site is fully self-contained — no dependency on
    any external tree. Everything the pages reference lives in the repo."""
    dst_root = DIST / "media"
    bundled = ROOT / "assets" / "media"
    if bundled.exists():
        shutil.copytree(bundled, dst_root, dirs_exist_ok=True)
    # Generated biblical maps (assets/maps -> dist/media/maps).
    maps_src = ROOT / "assets" / "maps"
    if maps_src.exists():
        shutil.copytree(maps_src, dst_root / "maps", dirs_exist_ok=True)


def write_pages_files():
    """GitHub Pages: disable Jekyll processing and set the custom domain."""
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    (DIST / "CNAME").write_text(config.SITE_DOMAIN + "\n", encoding="utf-8")


def write_sitemap():
    today = datetime.date.today().isoformat()
    urls = "\n".join(
        f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>" for u in sorted(set(_pages_for_sitemap))
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n"
    )
    (DIST / "sitemap.xml").write_text(xml, encoding="utf-8")


def write_robots():
    txt = (
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {config.BASE_URL}/sitemap.xml\n"
    )
    (DIST / "robots.txt").write_text(txt, encoding="utf-8")


if __name__ == "__main__":
    build()
