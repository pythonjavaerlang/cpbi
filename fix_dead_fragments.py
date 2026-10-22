# -*- coding: utf-8 -*-
"""Fix dead #fragments in cross-reference links: remap each href whose target
anchor does not exist to the nearest existing anchor in the same chapter (or
drop the fragment if the target page has none). Operates on current export.json.
Backs up before writing.
"""
import json, io, shutil, datetime, re
import config
from slugs import slugify
import xref_links as X

EXPORT = r'C:\src\cpbi\content\export.json'


def main(apply=False):
    d = json.load(open(EXPORT, encoding='utf-8'))
    books = {b['id']: b for b in d['books']}
    chapters = {c['id']: c for c in d['chapters']}

    # Build path -> cid and anchors per page (same as build.py slugging).
    cbb = {}
    for c in d['chapters']:
        cbb.setdefault(c['book_id'], []).append(c)
    for lst in cbb.values():
        lst.sort(key=lambda c: (c.get('ordering') or 0))
    book_slug = {bid: (config.COMMENTARY_BOOK_SLUGS.get(bid) or slugify(b['title']))
                 for bid, b in books.items()}
    path_cid = {}
    for bid, lst in cbb.items():
        seen = set()
        for c in lst:
            s = slugify(c['title']) or f"chapter-{c['id']}"
            base, i = s, 2
            while s in seen:
                s = f'{base}-{i}'; i += 1
            seen.add(s)
            path_cid[f"/{book_slug[bid]}/{s}/"] = c['id']

    # Precompute anchors + chapter-start map for each page path.
    page_info = {}
    for path, cid in path_cid.items():
        aset = X.anchors_of(chapters[cid]['text'])
        page_info[path] = (aset, X._chapter_anchor_starts(aset))

    log = io.open(r'C:\src\cpbi\_remap.log', 'w', encoding='utf-8')
    total_remapped = total_dropped = 0
    for cid, c in chapters.items():
        if cid not in chapters:
            continue
        # Same-page links (href begins with just '#') use this chapter's anchors.
        own_path = next((p for p, cc in path_cid.items() if cc == cid), None)
        info = dict(page_info)
        if own_path:
            info[''] = page_info[own_path]   # map empty path to own page
        new_html, rem, drop = X.remap_dead_fragments(c['text'], info)
        total_remapped += rem
        total_dropped += drop
        if rem or drop:
            log.write(f"cid={cid:>3} {c['title']!r}: remapped={rem} dropped={drop}\n")
        if apply:
            chapters[cid]['text'] = new_html
    log.write(f"\nTOTAL remapped={total_remapped} dropped={total_dropped}\n")
    log.close()

    if apply:
        stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        shutil.copy2(EXPORT, EXPORT + f'.bak5-{stamp}')
        with io.open(EXPORT, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        print(f"APPLIED: remapped {total_remapped}, dropped {total_dropped}. Wrote export.json")
    else:
        print(f"DRY RUN: would remap {total_remapped}, drop {total_dropped}. See _remap.log")


if __name__ == "__main__":
    import sys
    main(apply='--apply' in sys.argv)
