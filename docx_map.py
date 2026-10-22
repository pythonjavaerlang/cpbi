# -*- coding: utf-8 -*-
"""Explicit mapping: docx filename -> chapter id in export.json.
Chapters belong to book 1 (New Testament) and book 21 (Old Testament).
Book 22 (Greek course) is NOT covered by theology docx files.
"""

# chapter id -> docx filename (basename). None means "no docx / skip".
CHAPTER_DOCX = {
    # ---- New Testament (book 1) ----
    24: "ЄВАНГЕЛІЄ ВІД МАТФЕЯ.docx",            # Євангеліє від Матея
    25: "ЄВАНГЕЛІЄ ВІД МАРКА.docx",             # Євангеліє від Марка
    22: "ЄВАНГЕЛІЄ ВІД ЛУКИ.docx",              # Євангеліє від Луки
    23: "ЄВАНГЕЛІЯ ВІД ІОАННА.docx",            # Євангеліє від Йоана
    19: "ДІЯННЯ СВЯТИХ АПОСТОЛІВ.docx",         # Діяння Апостолів
    32: "СОБОРНЕ ПОСЛАННЯ АПОСТОЛА ЯКОВА.docx", # Послання Якова
    9:  "1 ПОСЛАННЯ АПОСТОЛА ПЕТРА.docx",       # Перше Послання Петра
    13: "2 ПОСЛАННЯ АПОСТОЛА ПЕТРА.docx",       # Друге Послання Петра
    6:  "1 ПОСЛАННЯ АПОСТОЛА ІОАННА.docx",      # Перше Послання Йоана
    7:  "2 ПОСЛАННЯ АПОСТОЛА ІОАННА.docx",      # Друге Послання Йоана
    16: "3 ПОСЛАННЯ АПОСТОЛА ІОАННА.docx",      # Третє Послання Йоана
    31: "ТЛУМАЧЕННЯ СОБОРНОГО ПОСЛАННЯ СВЯТОГО АПОСТОЛА ЮДИ.docx",  # Послання Юди
    27: "ТЛУМАЧЕННЯ ПОСЛАННЯ СВЯТОГО АПОСТОЛА ПАВЛА ДО РИМЛЯН .docx",  # до Римлян
    8:  "ТЛУМАЧЕННЯ ПЕРШОГО ПОСЛАННЯ СВЯТОГО АПОСТОЛА ПАВЛА ДО КОРІНФЯН.docx",  # 1 Корінтян
    12: "ТЛУМАЧЕННЯ ДРУГОГО ПОСЛАННЯ СВЯТОГО АПОСТОЛА ПАВЛА ДО КОРІНФЯН.docx",  # 2 Корінтян
    18: "ТЛУМАЧЕННЯ ПОСЛАННЯ СВЯТОГО АПОСТОЛА ПАВЛА ГАЛАТАМ .docx",  # Галатів
    20: "ТЛУМАЧЕННЯ ПОСЛАННЯ СВЯТОГО АПОСТОЛА ПАВЛА ЕФЕСЯНАМ .docx", # Ефесян
    30: "ТЛУМАЧЕННЯ ПОСЛАННЯ ФИЛИП’ЯНАМ.docx",  # Филип'ян
    21: "ТЛУМАЧЕННЯ ПОСЛАННЯ КОЛОСЯНАМ.docx",   # Колосян  (chapter id 21, book 1)
    10: "ТЛУМАЧЕННЯ ПЕРШОГО ПОСЛАННЯ СВЯТОГО АПОСТОЛА ПАВЛА ДО СОЛУНЯН.docx",  # 1 Солунян
    14: "ТЛУМАЧЕННЯ ДРУГОГО ПОСЛАННЯ  СОЛУНЯН.docx",  # 2 Солунян
    11: "ТЛУМАЧЕННЯ ПЕРШОГО ТИМОФІЯ.docx",      # 1 Тимотея
    15: "ТЛУМАЧЕННЯ ДРУГОГО ТИМОФІЯ.docx",      # 2 Тимотея
    28: "ТЛУМАЧЕННЯ ТИТА.docx",                 # Тита
    29: "ТЛУМАЧЕННЯ ФИЛИМОНА.docx",             # Филимона
    17: "ТЛУМАЧЕННЯ ПОСЛАННЯ ДО ЄВРЕЇВ.docx",   # Євреїв
    26: "ТЛУМАЧЕННЯ ОДКРОВЕННЯ .docx",          # Одкровення
    92: "ТЛУМАЧЕННЯ КНИГИ АМОСА.docx",          # Книга Амоса (note: book 1 ord 31)
    # ---- Old Testament (book 21) ----
    42: "ТЛУМАЧЕННЯ КНИГИ БУТТЯ.docx",          # Буття
    43: "ТЛУМАЧЕННЯ КНИГИ ВИХІД.docx",          # Вихід
    65: "ТЛУМАЧЕННЯ КНИГИ ЛЕВИТ.docx",          # Левіт
    66: "ТЛУМАЧЕННЯ КНИГИ ЧИСЛА.docx",          # Числа
    67: "ТЛУМАЧЕННЯ КНИГИ ВТОРОЗАКОННЯ.docx",   # Второзаконня
    68: "ТЛУМАЧЕННЯ КНИГИ ІСУСА НАВИНА .docx",  # Ісуса Навина
    69: "ТЛУМАЧЕННЯ КНИГИ СУДДІВ.docx",         # Книга Суддів
    70: "ТЛУМАЧЕННЯ КНИГИ РУФІ.docx",           # Рута
    71: "ТЛУМАЧЕННЯ ПЕРШОЇ КНИГИ ЦАРСТВ (ПЕРША КНИГА САМУЇЛА).docx",  # I Самуїла
    72: "ТЛУМАЧЕННЯ ДРУГОЇ КНИГИ ЦАРСТВ (ДРУГАКНИГА САМУЇЛА).docx",   # II Самуїла
    73: "ТЛУМАЧЕННЯ ТРЕТЬОЇ КНИГИ ЦАРСТВ (ПЕРША КНИГА ЦАРІВ).docx",   # I Царів
    74: "ТЛУМАЧЕННЯ ЧЕТВЕРТОЇ КНИГИ ЦАРСТВ.docx",                     # II Царів
    75: "ТЛУМАЧЕННЯ ПЕРШОЇ КНИГИ ПАРАЛИПОМЕНОН.docx",  # I Хронік
    76: "ТЛУМАЧЕННЯ ДРУГОЇ КНИГИ ПАРАЛИПОМЕНОН.docx",  # II Хронік
    77: "ТЛУМАЧЕННЯ ПЕРШОЇ КНИГИ ЕЗДРИ.docx",   # Езри
    81: "ТЛУМАЧЕННЯ КНИГИ НЕЄМІЇ.docx",         # Неємії
    82: "ТЛУМАЧЕННЯ КНИГИ ЕСФИРІ .docx",        # Естери
    83: "ТЛУМАЧЕННЯ КНИГИ ІОВА.docx",           # Іов
    80: None,                                   # Книга Псалмів -> only .pages, skip
    78: "ТЛУМАЧЕННЯ КНИГИ ПРИТЧІ СОЛОМОНА.docx",# Приповідок
    79: "ТЛУМАЧЕННЯ КНИГИ ЕККЛЕЗІАСТА.docx",    # Проповідника
    84: "ТЛУМАЧЕННЯ КНИГИ ПІСНІ ПІСЕНЬ.docx",   # Пісень
    85: "ТЛУМАЧЕННЯ КНИГИ ІСАЇ .docx",          # Ісаї
    86: "ТЛУМАЧЕННЯ КНИГИ ЄРЕМІЇ .docx",        # Єремії
    87: "ТЛУМАЧЕННЯ ПЛАЧ ЄРЕМІЇ.docx",          # Плач Єремії
    88: "ТЛУМАЧЕННЯ КНИГИ ЄЗИКЕЇЛЯ.docx",       # Єзекиїла
    89: "ТЛУМАЧЕННЯ КНИГИ ДАНИЇЛА.docx",        # Даниїла
    90: "ТЛУМАЧЕННЯ КНИГИ ОСІЇ.docx",           # Осії
    91: "ТЛУМАЧЕННЯ КНИГИ ІОЇЛЯ.docx",          # Йоіла
    93: "ТЛУМАЧЕННЯ КНИГИ АВДІЯ.docx",          # Авдія
    94: "ТЛУМАЧЕННЯ КНИГИ ІОНИ.docx",           # Йони
    95: "ТЛУМАЧЕННЯ КНИГИ МИХЕЯ.docx",          # Міхея
    96: "ТЛУМАЧЕННЯ КНИГИ НАУМА.docx",          # Наума
    97: "ТЛУМАЧЕННЯ КНИГИ АВВАКУМА.docx",       # Авакума
    98: "ТЛУМАЧЕННЯ КНИГИ СОФОНІЇ.docx",        # Софонії
    99: "ТЛУМАЧЕННЯ КНИГИ АГГЕЯ.docx",          # Аггея
    100:"ТЛУМАЧЕННЯ КНИГИ ЗАХАРІЇ.docx",        # Захарії
    101:"ТЛУМАЧЕННЯ КНИГИ МАЛАХІЇ.docx",        # Малахії
}

import os as _os, unicodedata as _ud

DOCX_DIR = r'C:\src\ex\theology'


def resolve_path(fn):
    """Return the real on-disk path for a mapped filename, matching across
    Unicode NFC/NFD normalization differences (macOS stores NFD)."""
    if fn is None:
        return None
    target = _ud.normalize('NFC', fn)
    for real in _os.listdir(DOCX_DIR):
        if _ud.normalize('NFC', real) == target:
            return _os.path.join(DOCX_DIR, real)
    return None


if __name__ == "__main__":
    import json, os, io
    d = json.load(open(r'C:\src\cpbi\content\export.json', encoding='utf-8'))
    chapters = {c['id']: c for c in d['chapters']}
    docx_dir = r'C:\src\ex\theology'
    existing = {_ud.normalize('NFC', f) for f in os.listdir(docx_dir)}
    out = io.open(r'C:\src\cpbi\_map_check.txt', 'w', encoding='utf-8')

    # content chapters that need coverage = books 1 and 21
    content_ids = [c['id'] for c in d['chapters'] if c['book_id'] in (1, 21)]
    out.write(f"Content chapters (books 1,21): {len(content_ids)}\n")
    out.write(f"Mapped chapters: {len(CHAPTER_DOCX)}\n\n")

    out.write("UNMAPPED content chapters:\n")
    for cid in content_ids:
        if cid not in CHAPTER_DOCX:
            out.write(f"  {cid} {chapters[cid]['title']!r}\n")

    out.write("\nMISSING docx files on disk:\n")
    used = set()
    for cid, fn in CHAPTER_DOCX.items():
        if fn is None:
            out.write(f"  (skip) chapter {cid} {chapters[cid]['title']!r}\n")
            continue
        nfc = _ud.normalize('NFC', fn)
        used.add(nfc)
        if nfc not in existing:
            out.write(f"  !! {fn}  (for chapter {cid} {chapters[cid]['title']!r})\n")

    out.write("\nUNUSED docx files on disk (not mapped):\n")
    for fn in sorted(existing):
        if fn.lower().endswith('.docx') and fn not in used:
            out.write(f"  {fn}\n")
    out.close()
    print('done')
