# -*- coding: utf-8 -*-
"""Add human-readable title="<Book> <ref>" tooltips to every cross-reference
link in the commentary chapters. Operates on current export.json; idempotent.
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

    cbb = {}
    for c in d['chapters']:
        cbb.setdefault(c['book_id'], []).append(c)
    for lst in cbb.values():
        lst.sort(key=lambda c: (c.get('ordering') or 0))
    book_slug = {bid: (config.COMMENTARY_BOOK_SLUGS.get(bid) or slugify(b['title']))
                 for bid, b in books.items()}
    path_to_title = {}
    cid_path = {}
    for bid, lst in cbb.items():
        seen = set()
        for c in lst:
            s = slugify(c['title']) or f"chapter-{c['id']}"
            base, i = s, 2
            while s in seen:
                s = f'{base}-{i}'; i += 1
            seen.add(s)
            path = f"/{book_slug[bid]}/{s}/"
            path_to_title[path] = c['title'].strip()
            cid_path[c['id']] = path

    log = io.open(r'C:\src\cpbi\_titles.log', 'w', encoding='utf-8')
    total = 0
    for cid, c in chapters.items():
        new_html, n = X.add_link_titles(c['text'], path_to_title, c['title'].strip())
        total += n
        if n:
            log.write(f"cid={cid:>3} {c['title']!r}: titled={n}\n")
        if apply:
            chapters[cid]['text'] = new_html
    log.write(f"\nTOTAL titled={total}\n")
    log.close()

    if apply:
        stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        shutil.copy2(EXPORT, EXPORT + f'.bak6-{stamp}')
        with io.open(EXPORT, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        print(f"APPLIED: {total} link titles. Wrote export.json")
    else:
        print(f"DRY RUN: would add {total} link titles. See _titles.log")


if __name__ == "__main__":
    import sys
    main(apply='--apply' in sys.argv)
