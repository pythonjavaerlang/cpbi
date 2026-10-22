# -*- coding: utf-8 -*-
"""Add same-page hyperlinks for BARE verse references (e.g. 40:34-38) in the
commentary chapters. Operates on the current content/export.json (which already
contains verse anchors and abbreviated-reference links from apply_xref.py).

For each chapter we rebuild its verse index from the anchors already present,
then wrap bare C:V references that resolve to an existing section on that same
page. Idempotent: text already inside <a> (abbreviated links or previously
linked bare refs) is skipped.

Backs up export.json before writing.
"""
import json, io, shutil, datetime, re
import docx_map
import xref_links as X

EXPORT = r'C:\src\cpbi\content\export.json'


def main(apply=False):
    d = json.load(open(EXPORT, encoding='utf-8'))
    chapters = {c['id']: c for c in d['chapters']}
    converted = [cid for cid, fn in docx_map.CHAPTER_DOCX.items() if fn]

    log = io.open(r'C:\src\cpbi\_bare_apply.log', 'w', encoding='utf-8')
    total = 0
    nested_total = 0
    for cid in converted:
        htmltext = chapters[cid]['text']
        idx = X.verse_index_from_html(htmltext)
        X.set_verse_index(cid, idx)
        linked, n = X.link_bare_references(htmltext, cid)
        nested = len(re.findall(r'<a\b[^>]*>(?:(?!</a>).)*<a\b', linked, re.S))
        nested_total += nested
        total += n
        if apply:
            chapters[cid]['text'] = linked
        log.write(f"cid={cid:>3} {chapters[cid]['title']!r}: bare_links={n} nested={nested} idx={len(idx)}\n")
    log.write(f"\nTOTAL bare links={total} nested_total={nested_total}\n")
    log.close()

    if nested_total:
        print(f"ABORT: {nested_total} nested <a> detected; not writing.")
        return False

    if apply:
        stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        shutil.copy2(EXPORT, EXPORT + f'.bak4-{stamp}')
        with io.open(EXPORT, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        print(f"APPLIED: {total} bare links. Wrote export.json")
    else:
        print(f"DRY RUN: would add {total} bare links. See _bare_apply.log")
    return True


if __name__ == "__main__":
    import sys
    main(apply='--apply' in sys.argv)
