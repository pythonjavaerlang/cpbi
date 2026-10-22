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


# Reconstruct a verse index from anchors ALREADY present in a chapter's HTML
# (used when re-processing data that was anchored in a previous run).
_MARKER_WITH_ID = re.compile(
    r'<span class="s b"[^>]*id="v(\d{1,3})-(\d{1,3})"[^>]*>\s*'
    r'(\d{1,3}):(\d{1,3})(?:[-–](\d{1,3}))?'
)

def verse_index_from_html(html: str) -> dict:
    idx = {}
    for m in _MARKER_WITH_ID.finditer(html):
        aid = f"v{m.group(1)}-{m.group(2)}"
        c = int(m.group(3)); vs = int(m.group(4))
        ve = int(m.group(5)) if m.group(5) else vs
        if ve < vs:
            vs, ve = ve, vs
        for v in range(vs, ve + 1):
            idx.setdefault((c, v), aid)
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

# A bare verse reference "C:V[-V][part]" with no book abbreviation. We DON'T
# require word boundaries that would include a preceding abbreviation; the
# tokenizer already skips text inside <a>, and _link_text_bare refuses to match
# when the digits are immediately preceded by a book-abbreviation+period.
_BARE_REF = re.compile(
    r'(?P<c>\d{1,3}):(?P<v>\d{1,3})(?P<rng>[-–]\d{1,3})?(?P<part>[абвАБВ]?)'
)
# A book abbreviation + period right before the match means it is an
# abbreviated reference (already linked) -> skip.
_ABBR_TAIL = re.compile(r'[А-ЯІЇЄҐ][А-ЯІЇЄҐа-яіїєґ]{0,6}\.\s?$')


def _same_page_href(cid: int, c: str, v: str):
    """Anchor on the CURRENT page for a bare ref, only if the anchor exists."""
    idx = _VINDEX.get(cid)
    if not idx:
        return None
    try:
        key = (int(c), int(v))
    except ValueError:
        return None
    aid = idx.get(key)
    if aid is None:
        return None
    return f"#{aid}"

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


def link_bare_references(html: str, current_cid: int) -> tuple[str, int]:
    """Wrap bare "C:V" references (no book abbreviation) that resolve to an
    existing anchor on the CURRENT page. Safe to run after link_references:
    text already inside <a> is skipped, so abbreviated links are never touched.
    Returns (html, link_count)."""
    out = []
    in_anchor = False
    in_marker = False
    count = 0

    for tok in _TAG_OR_TEXT.findall(html):
        if tok.startswith('<'):
            low = tok.lower()
            if low.startswith('<a'):
                in_anchor = True
            elif low.startswith('</a'):
                in_anchor = False
            if 'class="s b"' in tok and low.startswith('<span'):
                in_marker = True
            elif low.startswith('</span>') and in_marker:
                in_marker = False
            out.append(tok)
            continue

        if in_anchor or in_marker:
            out.append(tok)
            continue

        new_tok, n = _link_text_bare(tok, current_cid)
        count += n
        out.append(new_tok)

    return ''.join(out), count


def _link_text_bare(text: str, current_cid: int) -> tuple[str, int]:
    count = 0

    def repl(m):
        nonlocal count
        # Skip if immediately preceded by a book abbreviation + period
        # (that is an abbreviated reference, handled elsewhere / already linked).
        if _ABBR_TAIL.search(text[:m.start()]):
            return m.group(0)
        href = _same_page_href(current_cid, m.group('c'), m.group('v'))
        if not href:
            return m.group(0)        # no matching section on this page -> leave
        count += 1
        return f'<a class="xref" href="{href}">{m.group(0)}</a>'

    out = _BARE_REF.sub(repl, text)
    return out, count



# ── Dead-fragment remapping ──────────────────────────────────────────────────
# Some references point at a verse that is not the START of any comment block
# and is not covered by any block range we captured, so the generated #vC-V
# anchor does not exist. Rather than let such a link land at the page top, we
# remap it to the nearest *existing* anchor in the SAME chapter (greatest start
# verse <= the referenced verse), i.e. the comment block that most plausibly
# discusses that verse. If the chapter has no anchors at all, the fragment is
# dropped so the link still reaches the correct page.

_HREF_RE = re.compile(r'(<a class="xref" href=")([^"]*)(">)')


def anchors_of(html: str) -> set:
    """Return the set of anchor ids present in a chapter's HTML."""
    return set(re.findall(r'id="(v\d+-\d+)"', html))


def _chapter_anchor_starts(anchor_set):
    """Map chapter -> sorted list of start-verses that have an anchor."""
    by_ch = {}
    for a in anchor_set:
        mm = re.match(r'v(\d+)-(\d+)$', a)
        if mm:
            by_ch.setdefault(int(mm.group(1)), []).append(int(mm.group(2)))
    for k in by_ch:
        by_ch[k].sort()
    return by_ch


def remap_dead_fragments(html: str, anchors_by_cid_path):
    """Rewrite every xref href whose #fragment is missing on its target page.

    anchors_by_cid_path: dict  path(str) -> (anchor_set, starts_by_chapter)
      where path is the href WITHOUT the fragment (e.g. '/slug/chap/' or '' for
      a same-page link). Returns (html, remapped_count, dropped_count).
    """
    remapped = [0]
    dropped = [0]

    def repl(m):
        pre, href, post = m.group(1), m.group(2), m.group(3)
        if '#' not in href:
            return m.group(0)
        path, frag = href.split('#', 1)
        entry = anchors_by_cid_path.get(path)
        if entry is None:
            return m.group(0)  # unknown page; leave untouched
        anchor_set, starts = entry
        if frag in anchor_set:
            return m.group(0)  # already valid
        # Parse the fragment's chapter/verse.
        fm = re.match(r'v(\d+)-(\d+)$', frag)
        if not fm:
            return m.group(0)
        c, v = int(fm.group(1)), int(fm.group(2))
        cand = [s for s in starts.get(c, []) if s <= v]
        if cand:
            new_frag = f'v{c}-{cand[-1]}'   # nearest preceding block start
            remapped[0] += 1
            return f'{pre}{path}#{new_frag}{post}'
        # No anchor in this chapter: drop the fragment, keep the page link.
        dropped[0] += 1
        return f'{pre}{path}{post}'

    out = _HREF_RE.sub(repl, html)
    return out, remapped[0], dropped[0]



# ── Link title (tooltip) injection ───────────────────────────────────────────
# Add a human-readable title="<Book> <ref text>" to every xref link so hovering
# shows the destination. The book name is derived from the target page; the ref
# text is the link's visible content.

_A_FULL = re.compile(r'<a class="xref" href="([^"]+)"(?P<extra>[^>]*)>(?P<txt>[^<]*)</a>')


def add_link_titles(html: str, path_to_title: dict, current_title: str) -> tuple[str, int]:
    """path_to_title: page path ('/slug/chap/') -> human book title.
    current_title: title of the page we are processing (for same-page '#...').
    Returns (html, count). Idempotent: links that already have title= are left."""
    count = 0

    def repl(m):
        nonlocal count
        if 'title=' in m.group('extra'):
            return m.group(0)                 # already titled
        href = m.group(1)
        txt = m.group('txt')
        path = href.split('#', 1)[0]
        book = current_title if path == '' else path_to_title.get(path)
        if not book:
            return m.group(0)
        # Build a clear tooltip: full book name + the numeric reference portion.
        ref = _ref_numerals(txt)
        title = f'{book} {ref}'.strip() if ref else book
        title = title.replace('"', '&quot;')
        count += 1
        return (f'<a class="xref" href="{href}"{m.group("extra")} '
                f'title="{title}">{txt}</a>')

    out = _A_FULL.sub(repl, html)
    return out, count


def _ref_numerals(txt: str) -> str:
    """Extract the 'C:V[-V][,...]' numeric reference from the visible link text,
    dropping any leading book abbreviation."""
    m = re.search(r'\d{1,3}:\d{1,3}[\d:,\-–абвАБВ\s]*', txt)
    return m.group(0).strip() if m else txt.strip()
