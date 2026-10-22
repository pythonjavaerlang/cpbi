# -*- coding: utf-8 -*-
"""Apply high-confidence cross-reference corrections to content/export.json.

Each entry: (chapter_id, old_substring, new_substring, rationale).
Every old_substring was verified to occur exactly once in that chapter's raw
HTML and to sit within a single <span>, so replacement is surgical. The fixes
are limited to cases where the surrounding context unambiguously determines the
correction (a colon used where a semicolon/dash separates two complete
references, or a Latin letter standing in for a digit).

Ambiguous cases (reported, NOT changed) are listed at the bottom.
"""
import json, io, shutil, datetime

EXPORT = r'C:\src\cpbi\content\export.json'

FIXES = [
    # OCR: Latin 'l' used as digit '1'. Parent outline is (2:1-8) split into
    # 2:1-4а and 2:4б-8а, so this is unambiguously 2:1-4а.
    (81, '(2:l-4', '(2:1-4', "OCR: Latin l -> digit 1 (parent section 2:1-8)"),

    # Colon used as separator between two complete references; the surrounding
    # list uses ';'. 2:38 ; 10:34 ; 13:38 ; 26:18.
    (19, '(див. 2:38: 10:34; 13:38; 26:18)', '(див. 2:38; 10:34; 13:38; 26:18)',
     "colon->semicolon between refs (list uses ;)"),

    # Two distinct Matthew refs: 4:5 and 27:53 (both call Jerusalem 'holy city').
    (24, '(Мт. 4:5: 27:53)', '(Мт. 4:5; 27:53)',
     "colon->semicolon between two Matthew refs"),

    # Daniel: 9:20-27 and 10:1-12:5 are separate visions in a ';'-list.
    (89, '(част. 7; 8; 9:20-27: 10:1-12:5)', '(част. 7; 8; 9:20-27; 10:1-12:5)',
     "colon->semicolon between refs (list uses ;)"),

    # I Kings: two battle passages 20:26-43 and 22:1-38.
    (73, '(див. 20:26-43: 22:1-38)', '(див. 20:26-43; 22:1-38)',
     "colon->semicolon between two refs"),

    # John: 1:47 ; 2:24-25 ; 6:15, 61 (list uses ;).
    (23, '(див. 1:47; 2:24-25: 6:15, 61)', '(див. 1:47; 2:24-25; 6:15, 61)',
     "colon->semicolon between refs (list uses ;)"),

    # Exodus census/ransom passage is 30:11-16 (single passage).
    (74, '(див. Вихід 30:11:16)', '(див. Вихід 30:11-16)',
     "double colon -> dash: Exodus 30:11-16 is one passage (census ransom)"),

    # Isaiah comparison list: 1:5 ; 53:5, 8 ; 59:13.
    (85, 'порівняння: 1:5: 53:5, 8: 59:13)', 'порівняння: 1:5; 53:5, 8; 59:13)',
     "colon->semicolon between refs (comparison list uses ;)"),
    # Isaiah list: ...21; 35:2 ; 46:13; ...
    (85, 'вірш 21; 35:2: 46:13;', 'вірш 21; 35:2; 46:13;',
     "colon->semicolon between refs (list uses ;)"),
    # Ezekiel refs: 16:60 ; 37:26 (list uses ;).
    (85, '16:60: 37:26; Євреям 13:20)', '16:60; 37:26; Євреям 13:20)',
     "colon->semicolon between refs (list uses ;)"),
    # Isaiah: 41:8, 14 ; 42:24 (list uses ;).
    (85, '41:8, 14:42:24;', '41:8, 14; 42:24;',
     "colon->semicolon between refs (list uses ;)"),
    # Isaiah: 45:12, 18 ; 48:13 (list uses ;).
    (85, '45:12, 18:48:13;', '45:12, 18; 48:13;',
     "colon->semicolon between refs (list uses ;)"),
]

# Intentionally NOT changed (reported for human review): format clearly broken
# but the intended verse numbers cannot be determined from context with
# confidence, so auto-fixing risks citing the wrong verses.
AMBIGUOUS = [
    (19, '18:19-21, 24:19:41', "'24:19:41' malformed; Acts 18 context; intended numbers unclear"),
    (85, 'Єзекиїла 16:46, 48-49: 55:56', "'55:56' invalid for Ezekiel (48 ch); likely ch.16 vv.55,56 but uncertain"),
    (90, '(1:2б; 22:3:5)', "'22:3:5' malformed; Hosea has 14 chapters; intended ref unclear"),
]


def main(apply=False):
    d = json.load(open(EXPORT, encoding='utf-8'))
    chapters = {c['id']: c for c in d['chapters']}
    log = io.open(r'C:\src\cpbi\_fix_refs.log', 'w', encoding='utf-8')

    ok = True
    for cid, old, new, why in FIXES:
        c = chapters[cid]
        n = c['text'].count(old)
        if n != 1:
            ok = False
            log.write(f"!! cid={cid}: expected 1 occurrence of {old!r}, found {n} — SKIP\n")
            continue
        if apply:
            c['text'] = c['text'].replace(old, new)
        log.write(f"OK cid={cid:>3}: {old!r} -> {new!r}   [{why}]\n")

    log.write("\n--- AMBIGUOUS (left unchanged, needs human review) ---\n")
    for cid, token, why in AMBIGUOUS:
        present = chapters[cid]['text'].count(token)
        log.write(f"   cid={cid} {token!r} (found={present}) :: {why}\n")
    log.close()

    if apply and ok:
        stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        shutil.copy2(EXPORT, EXPORT + f'.bak2-{stamp}')
        with io.open(EXPORT, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        print("APPLIED fixes and wrote export.json")
    elif apply and not ok:
        print("ABORTED: a target string was not unique; nothing written.")
    else:
        print("DRY RUN. See _fix_refs.log")
    return ok


if __name__ == "__main__":
    import sys
    main(apply='--apply' in sys.argv)
