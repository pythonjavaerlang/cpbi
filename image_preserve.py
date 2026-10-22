# -*- coding: utf-8 -*-
"""Preserve images from an existing chapter's HTML when its body text is
regenerated from a .docx.

Strategy
--------
Old chapters embed <img> inside small wrappers (<center>, <p>, or a sized
<span>). Each image sits next to a short caption or a specific verse marker.
We:
  1. Extract every image occurrence as a normalised standalone block
     (<p class="imgblock">...</p>) together with:
       - the *caption* text that immediately follows the image (if any), and
       - a *preceding* text anchor (tail of the paragraph just before it).
  2. After the docx is converted to new HTML, we locate the best insertion
     point by matching the caption (preferred) or preceding anchor text against
     the new paragraphs, and splice the image block in at that point.
  3. Any image whose anchors cannot be confidently matched is appended at the
     end under an "Ілюстрації" divider so nothing is ever lost.
"""
from __future__ import annotations

import re
import html as _html

IMG_RE = re.compile(r'<img\b[^>]*>', re.I)
TAG_RE = re.compile(r'<[^>]+>')
WS_RE = re.compile(r'\s+')


def _text_of(fragment: str) -> str:
    t = TAG_RE.sub(' ', fragment)
    t = _html.unescape(t)
    t = WS_RE.sub(' ', t).strip()
    return t


def _norm(t: str) -> str:
    t = _html.unescape(t or '')
    t = TAG_RE.sub(' ', t)
    t = WS_RE.sub(' ', t).strip().lower()
    return t


# A paragraph (top-level <p>...</p>) or a <center>...</center> block.
PARA_SPLIT_RE = re.compile(r'(<center\b.*?</center>|<p\b.*?</p>)', re.I | re.S)


def extract_images(old_html: str):
    """Return a list of dicts: {block, caption, before} for each image, in order.

    `block`   - normalised HTML to re-insert (keeps original <img> attributes).
    `caption` - normalised text of the paragraph/span right after the image.
    `before`  - normalised tail text of content right before the image.
    """
    results = []
    # Work on a linear scan: find each <img>, then look outward for the nearest
    # caption (following visible text) and preceding visible text.
    for m in IMG_RE.finditer(old_html):
        img_tag = m.group(0)
        # Normalise the img tag: keep src/alt/title/width/height, self-close.
        src = re.search(r'src="([^"]*)"', img_tag)
        if not src:
            continue
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', img_tag))
        style = ''
        # Preserve sizing if present as style on the tag.
        mstyle = re.search(r'style="([^"]*)"', img_tag)
        if mstyle:
            style = f' style="{mstyle.group(1)}"'
        a = []
        for k in ('src', 'alt', 'title'):
            if k in attrs:
                a.append(f'{k}="{attrs[k]}"')
        norm_img = f'<img {" ".join(a)}{style} loading="lazy"/>'
        block = (f'<p class="p pc imgblock" style="text-align:center;margin:12pt 0;">'
                 f'{norm_img}</p>')

        # Following caption: next ~200 chars of visible text after the image's
        # enclosing block.
        after_region = old_html[m.end(): m.end() + 1200]
        caption = ''
        for pm in PARA_SPLIT_RE.finditer(after_region):
            txt = _text_of(pm.group(1))
            if txt:
                caption = txt
                break

        # Preceding anchor: last visible text in the ~1500 chars before.
        before_region = old_html[max(0, m.start() - 2000): m.start()]
        before = ''
        blocks = PARA_SPLIT_RE.findall(before_region)
        for pm in reversed(blocks):
            txt = _text_of(pm)
            if txt:
                before = txt
                break

        results.append({
            'block': block,
            'caption': _norm(caption),
            'before': _norm(before),
            'src': src.group(1),
        })
    return results


def _split_new_paragraphs(new_html: str):
    """Split converted HTML into a list of top-level <p>/<table> blocks."""
    parts = re.split(r'(?<=</p>)\n|(?<=</table>)\n', new_html)
    return [p for p in parts if p.strip()]


def _best_index(blocks, needle, used):
    """Return index of the block whose text best matches `needle`."""
    if not needle:
        return None
    # Try: a block whose normalised text contains, or is contained by, needle.
    needle_short = needle[:60]
    best = None
    for i, b in enumerate(blocks):
        if i in used:
            continue
        bt = _norm(b)
        if not bt:
            continue
        if needle_short and needle_short in bt:
            return i
        if bt[:60] and bt[:60] in needle:
            best = i
    return best


def reinsert_images(new_html: str, images):
    """Insert each image block into new_html near its caption/before anchor.
    Returns (html, placed_count, total_count)."""
    if not images:
        return new_html, 0, 0
    blocks = _split_new_paragraphs(new_html)
    used = set()
    # Map image -> insertion position (index into blocks, insert AFTER it).
    placements = []  # (pos, block_html)
    unplaced = []
    for img in images:
        pos = None
        mode = None
        # Prefer matching the caption: image goes BEFORE the caption paragraph.
        idx = _best_index(blocks, img['caption'], used)
        if idx is not None:
            pos = idx            # insert before caption
            mode = 'before_caption'
        else:
            idx = _best_index(blocks, img['before'], used)
            if idx is not None:
                pos = idx + 1    # insert after the preceding paragraph
                mode = 'after_before'
        if pos is None:
            unplaced.append(img)
            continue
        used.add(idx)
        placements.append((pos, img['block']))

    placed = len(placements)
    # Apply placements from the end so indices stay valid.
    placements.sort(key=lambda x: x[0], reverse=True)
    for pos, blk in placements:
        pos = max(0, min(pos, len(blocks)))
        blocks.insert(pos, blk)

    result = "\n".join(blocks)
    if unplaced:
        result += ('\n<p class="pe"><span class="s"></span></p>'
                   '\n<p class="p pc"><span class="s b">Ілюстрації</span></p>')
        for img in unplaced:
            result += "\n" + img['block']

    return result, placed, len(images)
