"""Static site configuration: domain, SEO defaults, and the Ukrainian slug map.

The slug map pins stable, human-friendly Ukrainian-transliterated URLs for the
fixed (non-content) pages and the top-level content sections. Content pages
(flatpages, chapters, issues, blog, events) derive their slugs from titles.
"""
from __future__ import annotations

SITE_DOMAIN = "cpbi.info"
BASE_URL = "https://cpbi.info"
SITE_NAME = "Чернівецький Православний Богословський Інститут"
SITE_SHORT = "ЧПБІ"
LANG = "uk"

SEO_DEFAULT_DESCRIPTION = (
    "Вищий навчальний заклад, що готує бакалаврів, магістрів та докторів зі "
    "спеціальності «Православне богослов’я (теологія)». Бібліотека, тлумачення "
    "Святого Письма Старого і Нового Завіту, наукові видання."
)
SEO_DEFAULT_KEYWORDS = (
    "богослів'я, теологія, семінарія, православний інститут, Чернівці, "
    "тлумачення Святого Письма, Старий Завіт, Новий Завіт, духовна освіта"
)

# OG image config (parity with light-fastapi: 1200x630).
OG_WIDTH = 1200
OG_HEIGHT = 630

# Fixed-page slugs (Ukrainian, transliterated). key -> url path (no leading slash
# except root). These override title-derived slugs for stability.
FIXED_PAGES = {
    "home": "",
    "bible": "tlumachennia-sviatoho-pysma",            # TOC of commentary
    "library": "biblioteka",                            # book library index
    "lecture": "video-lektsii",
    "journal": "zhurnal",
    "donate": "pozhertvy",
    "contact": "kontakty",
    "apply": "vstup",
    "school": "pochatkova-shkola",
    "python_course": "kursy-python",
    "journal_subscription": "peredplata-zhurnalu",
    "news": "novyny",
}

# Top-level content section prefixes.
SECTION = {
    "book": "biblioteka",      # /biblioteka/<book-slug>/<chapter-slug>/
    "journal": "zhurnal",      # /zhurnal/<issue-slug>/
    "news": "novyny",          # /novyny/<slug>/
    "event": "podiia",         # /podiia/<slug>/
    "page": "",                # flatpages mount at root: /<flatpage-slug>/
}

# Stable top-level slugs for the two commentary books (requested in the menu).
COMMENTARY_BOOK_SLUGS = {
    1: "tlumachennia-novoho-zavitu",   # New Testament
    21: "tlumachennia-staroho-zavitu",  # Old Testament
}

# Flatpage URL (/foo/) is already a clean latin slug; reuse it as the static slug
# by stripping slashes. A few have odd nested urls we normalise in build.py.

GA_MEASUREMENT_ID = "UA-141017197-1"
FB_PIXEL_ID = "1099366943578344"
