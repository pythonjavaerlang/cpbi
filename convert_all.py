# -*- coding: utf-8 -*-
"""Rewrite content/export.json: replace each mapped chapter's `text` with HTML
converted from its .docx, re-inserting the images that were present in the old
HTML. Also set each chapter's `css` to the shared generated class block.

Creates a timestamped backup of export.json before writing.
"""
import json, io, os, shutil, datetime

import docx_map
import docx_to_html
import image_preserve

EXPORT = r'C:\src\cpbi\content\export.json'


def main(apply=False):
    d = json.load(open(EXPORT, encoding='utf-8'))
    chapters = {c['id']: c for c in d['chapters']}

    log = io.open(r'C:\src\cpbi\_convert_all.log', 'w', encoding='utf-8')
    total_old = total_new = 0
    converted = 0
    img_lost_any = False

    for cid, fn in sorted(docx_map.CHAPTER_DOCX.items()):
        c = chapters.get(cid)
        if c is None:
            log.write(f"cid={cid}: NOT IN EXPORT (skip)\n")
            continue
        path = docx_map.resolve_path(fn)
        if not path:
            log.write(f"cid={cid} {c['title']!r}: NO DOCX (skip)\n")
            continue

        old = c['text']
        old_srcs = [image_preserve.re.search(r'src="([^"]*)"', t).group(1)
                    for t in image_preserve.IMG_RE.findall(old)]

        body = docx_to_html.convert(path)
        imgs = image_preserve.extract_images(old)
        new_html, placed, total = image_preserve.reinsert_images(body, imgs)

        new_srcs = [image_preserve.re.search(r'src="([^"]*)"', t).group(1)
                    for t in image_preserve.IMG_RE.findall(new_html)]
        missing = set(old_srcs) - set(new_srcs)
        if missing:
            img_lost_any = True

        if apply:
            c['text'] = new_html
            c['css'] = docx_to_html.CSS

        converted += 1
        total_old += len(old)
        total_new += len(new_html)
        log.write(
            f"cid={cid:>3} {c['title']!r}\n"
            f"      old_len={len(old)} new_len={len(new_html)} "
            f"imgs old={len(old_srcs)} placed_inline={placed} kept={len(new_srcs)} "
            f"MISSING={sorted(missing)}\n")

    log.write(f"\nConverted {converted} chapters. "
              f"total_old={total_old} total_new={total_new}\n")
    log.write(f"ANY_IMAGE_LOST={img_lost_any}\n")
    log.close()

    if apply:
        stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        backup = EXPORT + f'.bak-{stamp}'
        shutil.copy2(EXPORT, backup)
        with io.open(EXPORT, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        print(f"WROTE export.json (backup: {os.path.basename(backup)})")
    else:
        print("DRY RUN (no write). See _convert_all.log")

    return img_lost_any


if __name__ == "__main__":
    import sys
    apply = '--apply' in sys.argv
    lost = main(apply=apply)
    print("ANY_IMAGE_LOST =", lost)
