# -*- coding: utf-8 -*-
"""Apply cross-reference hyperlinks to content/export.json.

Phase A: inject verse anchors into every commentary chapter and build each
         book's verse->anchor index.
Phase B: with all indices known, wrap recognised references in <a> links
         (a chapter may link to anchors on other chapters' pages).
Also appends the .xref style to each chapter's css.

Backs up export.json before writing.
"""
import json, io, shutil, datetime, re
import config
from slugs import slugify
import docx_map
import xref_links as X

EXPORT = r'C:\src\cpbi\content\export.json'


def compute_url_map(d):
    books = {b['id']: b for b in d['books']}
    cbb = {}
    for ch in d['chapters']:
        cbb.setdefault(ch['book_id'], []).append(ch)
    for lst in cbb.values():
        lst.sort(key=lambda c: (c.get('ordering') or 0))
    book_slug = {bid: (config.COMMENTARY_BOOK_SLUGS.get(bid) or slugify(b['title']))
                 for bid, b in books.items()}
    url_map = {}
    for bid, lst in cbb.items():
        seen = set()
        for ch in lst:
            s = slugify(ch['title']) or f"chapter-{ch['id']}"
            base, i = s, 2
            while s in seen:
                s = f'{base}-{i}'; i += 1
            seen.add(s)
            url_map[ch['id']] = f"/{book_slug[bid]}/{s}/"
    return url_map


def main(apply=False):
    d = json.load(open(EXPORT, encoding='utf-8'))
    chapters = {c['id']: c for c in d['chapters']}
    converted = [cid for cid, fn in docx_map.CHAPTER_DOCX.items() if fn]

    url_map = compute_url_map(d)
    X.set_url_map(url_map)

    log = io.open(r'C:\src\cpbi\_xref_apply.log', 'w', encoding='utf-8')

    # Phase A: anchors + verse indices.
    anchored = {}
    total_anchors = 0
    for cid in converted:
        html2, anchors, ranges = X.inject_anchors(chapters[cid]['text'])
        anchored[cid] = html2
        X.set_verse_index(cid, X.build_verse_index(ranges))
        total_anchors += len(anchors)

    # Phase B: link references.
    total_links = 0
    nested_total = 0
    for cid in converted:
        linked, n = X.link_references(anchored[cid], cid)
        nested = len(re.findall(r'<a\b[^>]*>(?:(?!</a>).)*<a\b', linked, re.S))
        nested_total += nested
        total_links += n
        css = chapters[cid].get('css') or ''
        if 'xref' not in css:
            css = css + X.XREF_CSS
        if apply:
            chapters[cid]['text'] = linked
            chapters[cid]['css'] = css
        log.write(f"cid={cid:>3} {chapters[cid]['title']!r}: links={n} nested={nested}\n")

    log.write(f"\nTOTAL anchors={total_anchors} links={total_links} nested_total={nested_total}\n")
    log.close()

    if nested_total:
        print(f"ABORT: {nested_total} nested <a> detected; not writing.")
        return False

    if apply:
        stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        shutil.copy2(EXPORT, EXPORT + f'.bak3-{stamp}')
        with io.open(EXPORT, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        print(f"APPLIED: {total_links} links, {total_anchors} anchors. Wrote export.json")
    else:
        print(f"DRY RUN: would create {total_links} links, {total_anchors} anchors. See _xref_apply.log")
    return True


if __name__ == "__main__":
    import sys
    main(apply='--apply' in sys.argv)
