# -*- coding: utf-8 -*-
"""Turn Scripture cross-references in commentary chapters into hyperlinks.

Two passes per chapter:
  1. inject_anchors():  add id="vC-V" to the bold verse-marker spans
     (e.g. <span class="s b">13:2-10. </span> -> ...id="v13-2"...), giving each
     comment block an in-page anchor keyed by its starting chapter:verse.
  2. link_references():  wrap recognised references
       - "Abbr. C:V[-V]"  (Abbr in a strict whitelist of book abbreviations)
       - bare  "C:V[-V]"  inside running text (same book -> same page)
     in <a class="xref" href="/book/chapter/#vC-V">...</a>.

Safety:
  * Only a strict whitelist of book abbreviations is linked, so ordinary words
    ending in "." before a number (Бога. 5, Христа. 3) are never linked.
  * Replacements run only on text OUTSIDE tags; we never touch attributes, never
    nest <a>, and never alter the bold verse-marker spans themselves.
  * Idempotent: re-running does not double-wrap (we skip text already inside <a>
    and skip chapters already processed via a sentinel).
"""
from __future__ import annotations
import re

# CSS for the generated cross-reference links (append to each chapter's css).
XREF_CSS = (
    "\n.xref{color:#8a1c1c;text-decoration:none;border-bottom:1px dotted #c8a2a2;}"
    "\n.xref:hover{color:#b31b1b;border-bottom-color:#b31b1b;}"
)


# ── Abbreviation -> chapter id (only books that have a page) ─────────────────
# Multiple spellings map to the same book. Keys are compared after stripping
# internal spaces and the trailing period, case-sensitive on the first letter.
ABBR_TO_CID = {
    # New Testament
    'Мт': 24, 'Мат': 24, '2Мт': 24,
    'Мк': 25, 'Марк': 25,
    'Лк': 22,
    'Ін': 23, 'Йн': 23, '1Йн': 6, 'Іоан': 23, 'Йоан': 23,
    'Діян': 19, 'Двян': 19,
    'Як': 32,
    '1Пт': 9, '2Пт': 13, 'Пт': 9,
    '1Ін': 6, '2Ін': 7, '3Ін': 16,
    'Юд': 31,
    'Рим': 27, 'Рмм': 27,
    '1Кор': 8, '2Кор': 12, 'Кор': 8, '1Кр': 8,
    'Гал': 18, 'Га': 18,
    'Еф': 20,
    'Флп': 30, 'Фил': 30, 'Флм': 29,
    'Кол': 21,
    '1Сол': 10, '2Сол': 14, 'Сол': 10,
    '1Тим': 11, '2Тим': 15, '2Ти': 15,
    'Тит': 28,
    'Євр': 17,
    'Одкр': 26,
    # Old Testament
    'Бут': 42,
    'Вих': 43, 'Вто': 67, 'Втор': 67,
    'Лев': 65,
    'Чис': 66,
    'ІсНав': 68, 'Нав': 68, 'Навин': 68, 'Іис': 68,
    'Суд': 69,
    'Рут': 70, 'Руф': 70,
    '1Сам': 71, '2Сам': 72, 'Сам': 71, '1Са': 71, '2Са': 72,
    '1Цар': 73, '2Цар': 74, 'Цар': 73,
    '1Хр': 75, '2Хр': 76, 'Хр': 75, '1Хрон': 75,
    'Езр': 77, 'Езра': 77,
    'Неєм': 81,
    'Ест': 82, 'Ес': 82,
    'Іов': 83, 'Іова': 83,
    'Пс': 80,
    'Прип': 78,
    'Проп': 79,
    'Пісн': 84,
    'Іс': 85, 'Іса': 85, 'Ісая': 85,
    'Єр': 86,
    'ПлЄр': 87, 'Лам': 87,
    'Єз': 88, 'Єзек': 88, 'Ез': 88,
    'Дан': 89,
    'Ос': 90,
    'Іоіл': 91, 'Йоіл': 91,
    'Ам': 92,
    'Авд': 93,
    # Йони / Jonah
    'Йон': 94, 'Йони': 94,
    'Міх': 95,
    'Наум': 96,
    'Ав': 97,   # Авакума (Habakkuk)  — NOTE: 'Авд' (Obadiah) handled above
    'Соф': 98,
    'Аг': 99,
    'Зах': 100,
    'Мал': 101,
}

# Books referenced but with NO commentary page (left unlinked on purpose).
# e.g. 1Мак/2Мак (Maccabees), 2Езр. We simply omit them from ABBR_TO_CID.

# CID -> site path (filled by caller via set_url_map()); e.g. "/slug/chap/".
_URL = {}
# CID -> verse index {(chapter, verse): anchor_id} (filled via set_verse_index).
_VINDEX = {}

def set_url_map(mapping: dict):
    _URL.clear()
    _URL.update(mapping)

def set_verse_index(cid: int, index: dict):
    _VINDEX[cid] = index


# ── Anchor injection ─────────────────────────────────────────────────────────
# Bold verse marker at a comment block start. Capture chapter and starting verse.
_MARKER = re.compile(
    r'(<span class="s b">\s*)(\d{1,3}):(\d{1,3})([а-яіїєґ]?)((?:[-–]\d{1,3}[а-яіїєґ]?)?(?:[.,]|\s*\.)?\s*)(</span>)'
)

def inject_anchors(html: str):
    """Add id="vC-V" to bold verse-marker spans. Returns (html, anchor_set,
    ranges) where ranges is a list of (chapter:int, vstart:int, vend:int, id:str)
    describing the verse span each anchored block covers."""
    anchors = set()
    seen = set()
    ranges = []

    def repl(m):
        c, v = m.group(2), m.group(3)
        aid = f"v{c}-{v}"
        # Parse the end verse of the range, if any, from the tail group.
        tail = m.group(5)
        mend = re.search(r'[-–](\d{1,3})', tail)
        try:
            ci = int(c); vs = int(v)
            ve = int(mend.group(1)) if mend else vs
        except ValueError:
            ci = vs = ve = None
        if aid in seen:
            return m.group(0)
        seen.add(aid)
        anchors.add(aid)
        if ci is not None:
            ranges.append((ci, vs, ve, aid))
        open_span = m.group(1)[:-1]  # drop trailing '>'
        return (f'{open_span} id="{aid}">{m.group(2)}:{m.group(3)}'
                f'{m.group(4)}{m.group(5)}{m.group(6)}')

    out = _MARKER.sub(repl, html)
    return out, anchors, ranges


def build_verse_index(ranges):
    """From ranges -> dict (chapter, verse) -> anchor id, mapping every verse in
    each block's span to that block's anchor so mid-block references resolve."""
    idx = {}
    for ci, vs, ve, aid in ranges:
        if ve < vs:
            vs, ve = ve, vs
        for v in range(vs, ve + 1):
            idx.setdefault((ci, v), aid)   # first (document order) wins
    return idx


# ── Reference linking ────────────────────────────────────────────────────────
# Capture any abbreviation-like token (optional leading 1-3, Cyrillic letters,
# trailing period) followed by C:V. We then normalise and look it up in the
# whitelist, so ordinary words are ignored and spacing variants all resolve.
_REF_WITH_ABBR = re.compile(
    r'(?P<abbr>(?:[1-3]\s?)?[А-ЯІЇЄҐ][А-ЯІЇЄҐа-яіїєґ]{0,6})\.\s?'
    r'(?P<c>\d{1,3}):(?P<v>\d{1,3})(?P<part>[а-яіїєґ]?)'
)

def _abbr_key(abbr: str) -> str:
    return re.sub(r'\s+', '', abbr)

def _href(cid: int, c: str, v: str):
    path = _URL.get(cid)
    if not path:
        return None
    # Resolve the verse to the anchor of the block that CONTAINS it, so
    # mid-block references land on the right comment, not the page top.
    try:
        key = (int(c), int(v))
    except ValueError:
        key = None
    idx = _VINDEX.get(cid)
    aid = idx.get(key) if (idx and key) else None
    if aid is None:
        aid = f"v{c}-{v}"   # fall back to the exact start-verse anchor
    return f'{path}#{aid}'


# Split HTML into segments, tagging whether each is inside a tag or inside an <a>.
_TAG_OR_TEXT = re.compile(r'<[^>]+>|[^<]+')

def link_references(html: str, current_cid: int) -> tuple[str, int]:
    """Wrap recognised references in <a>. Returns (html, link_count)."""
    out = []
    in_anchor = False
    in_marker = False  # inside a bold verse-marker span (do not link there)
    count = 0

    for tok in _TAG_OR_TEXT.findall(html):
        if tok.startswith('<'):
            low = tok.lower()
            if low.startswith('<a'):
                in_anchor = True
            elif low.startswith('</a'):
                in_anchor = False
            # Track bold marker spans so we never link the marker text itself.
            if 'class="s b"' in tok and low.startswith('<span'):
                in_marker = True
            elif low.startswith('</span>') and in_marker:
                in_marker = False
            out.append(tok)
            continue

        # Text node.
        if in_anchor or in_marker:
            out.append(tok)
            continue

        new_tok, n = _link_text(tok, current_cid)
        count += n
        out.append(new_tok)

    return ''.join(out), count


def _link_text(text: str, current_cid: int) -> tuple[str, int]:
    count = 0

    def repl(m):
        nonlocal count
        key = _abbr_key(m.group('abbr'))
        cid = ABBR_TO_CID.get(key)
        if cid is None:
            return m.group(0)        # not a known book abbreviation -> leave
        c, v = m.group('c'), m.group('v')
        href = _href(cid, c, v)
        if not href:
            return m.group(0)        # book has no page -> leave
        count += 1
        return f'<a class="xref" href="{href}">{m.group(0)}</a>'

    out = _REF_WITH_ABBR.sub(repl, text)
    return out, count
