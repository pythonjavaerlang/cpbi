"""Ukrainian-aware slugification (Cyrillic -> Latin transliteration).

Produces clean, URL-safe, lowercase hyphenated slugs from Ukrainian text,
following the Ukrainian National transliteration table (close enough for URLs).
"""
from __future__ import annotations

import re

# Ukrainian National transliteration (2010). Lowercase keys; we lowercase first.
_UK_MAP = {
    "а": "a", "б": "b", "в": "v", "г": "h", "ґ": "g", "д": "d", "е": "e",
    "є": "ie", "ж": "zh", "з": "z", "и": "y", "і": "i", "ї": "i", "й": "i",
    "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r",
    "с": "s", "т": "t", "у": "u", "ф": "f", "х": "kh", "ц": "ts", "ч": "ch",
    "ш": "sh", "щ": "shch", "ь": "", "ю": "iu", "я": "ia", "'": "", "’": "",
    "ъ": "", "ы": "y", "э": "e", "ё": "e",
}


def translit(text: str) -> str:
    out = []
    for ch in text.lower():
        out.append(_UK_MAP.get(ch, ch))
    return "".join(out)


def slugify(text: str, max_len: int = 80) -> str:
    """Return a clean latin slug for Ukrainian or latin input."""
    if not text:
        return ""
    s = translit(text.strip())
    # keep ascii letters/digits, turn everything else into hyphens
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    if len(s) > max_len:
        s = s[:max_len].rsplit("-", 1)[0]
    return s or "page"
