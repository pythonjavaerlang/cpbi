# coding=utf-8
"""Nominatim geocoder with on-disk cache and polite rate-limiting.

Usage:
    from geocode import geocode
    lat, lon = geocode("Egypt")

Respects the OSM Nominatim usage policy: max 1 request/second, a descriptive
User-Agent, and results cached to content/geocode_cache.json so repeated builds
never re-hit the API.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "content" / "geocode_cache.json"
USER_AGENT = "cpbi-static-maps/1.0 (biblical commentary; contact: support@cpbi.info)"
_MIN_INTERVAL = 1.1  # seconds between requests (Nominatim policy: <= 1 req/s)

_last_request = [0.0]


def _load_cache() -> dict:
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def _save_cache(cache: dict) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")


_cache = _load_cache()


def geocode(query: str) -> tuple[float, float] | None:
    """Return (lat, lon) for a query string, or None. Cached on disk."""
    key = query.strip().lower()
    if key in _cache:
        v = _cache[key]
        return (v[0], v[1]) if v else None

    # Rate limit.
    wait = _MIN_INTERVAL - (time.time() - _last_request[0])
    if wait > 0:
        time.sleep(wait)

    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": query, "format": "json", "limit": 1}
    )
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8"))
        _last_request[0] = time.time()
    except Exception as e:  # pragma: no cover
        print(f"  geocode error for {query!r}: {e}")
        return None

    if data:
        lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
        _cache[key] = [lat, lon]
        _save_cache(_cache)
        return lat, lon
    _cache[key] = None
    _save_cache(_cache)
    return None
