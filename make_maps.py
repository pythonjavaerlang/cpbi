# coding=utf-8
"""Generate historical biblical maps for the commentary.

For each named scene (a set of places from the curated gazetteer), render a
modern OSM base map with staticmap, then overlay markers and ANCIENT Ukrainian
place-name labels with Pillow. Optionally draw a route (ordered polyline).

Places not in the gazetteer can be resolved via Nominatim (geocode.py), but the
built-in table already covers the ancient sites that modern maps mislabel
(Tahpanhes, Noph/Memphis, Migdol, Pathros, On/Heliopolis, ...).

Output: dist/og/maps/<scene>.png  (also usable as in-page images).
"""
from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from staticmap import StaticMap, CircleMarker, Line
from staticmap.staticmap import _lon_to_x, _lat_to_y

from biblical_places import PLACES
from geocode import geocode

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "maps"
WIDTH, HEIGHT = 1200, 800

_FONTS = ROOT / "assets" / "fonts"
_FONT_CANDIDATES = [
    str(_FONTS / "arialbd.ttf"),
    str(ROOT / "assets" / "media" / "fonts" / "Georgia.ttf"),
    "C:/Windows/Fonts/arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

MARKER_COLOR = "#B22222"
ROUTE_COLOR = "#1E4E8C"


# Scene = (title, [place keys...], draw_route?)
SCENES = {
    "jeremiah-egypt": (
        "Втеча юдеїв до Єгипту (Книга Єремії)",
        ["jerusalem", "tahpanhes", "migdol", "noph", "pathros", "on", "nile"],
        True,
    ),
    "exodus": (
        "Вихід з Єгипту",
        ["rameses", "pithom", "goshen", "red_sea", "mount_sinai", "mount_nebo", "jericho"],
        True,
    ),
    "divided-kingdom": (
        "Розділене царство: Ізраїль та Юдея",
        ["dan", "samaria", "jezreel", "carmel", "shechem", "bethel", "jerusalem",
         "bethlehem", "hebron", "beersheba"],
        False,
    ),
    "exile-mesopotamia": (
        "Вавилонський полон і Перська імперія",
        ["jerusalem", "damascus", "haran", "nineveh", "babylon", "ur", "susa",
         "ecbatana", "persepolis"],
        False,
    ),
    "conquest-canaan": (
        "Завоювання Ханаану (Ісуса Навина)",
        ["jericho", "ai", "gibeon", "shechem", "shiloh", "bethel", "hebron",
         "jerusalem", "beersheba", "dan"],
        False,
    ),
    "seven-churches": (
        "Сім церков Одкровення",
        ["ephesus", "smyrna", "pergamum", "thyatira", "sardis", "philadelphia",
         "laodicea", "patmos"],
        False,
    ),
    "paul-regions": (
        "Міста послань апостола Павла",
        ["rome", "corinth", "athens", "thessalonica", "philippi", "ephesus",
         "colossae", "galatia", "antioch", "jerusalem", "crete", "malta"],
        False,
    ),
}


def _font(size):
    for c in _FONT_CANDIDATES:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _resolve(keys):
    """Return [(ua_label, lat, lon), ...] for the given gazetteer keys."""
    pts = []
    for k in keys:
        if k in PLACES:
            ua, hint, lat, lon = PLACES[k]
            pts.append((ua, lat, lon))
        else:
            r = geocode(k)
            if r:
                pts.append((k, r[0], r[1]))
    return pts


def generate_scene(name, title, keys, route=False):
    pts = _resolve(keys)
    if not pts:
        print(f"  [{name}] no points resolved")
        return None

    m = StaticMap(WIDTH, HEIGHT, url_template="https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
    if route and len(pts) > 1:
        coords = [(lon, lat) for _, lat, lon in pts]
        m.add_line(Line(coords, ROUTE_COLOR, 3))
    for _, lat, lon in pts:
        m.add_marker(CircleMarker((lon, lat), "white", 18))
        m.add_marker(CircleMarker((lon, lat), MARKER_COLOR, 12))

    image = m.render()  # PIL Image, auto-fitted to markers

    # Overlay labels + title.
    draw = ImageDraw.Draw(image)
    label_font = _font(22)
    title_font = _font(30)

    # Title banner.
    tw = draw.textlength(title, font=title_font)
    draw.rectangle([0, 0, WIDTH, 50], fill=(11, 42, 74))
    draw.text(((WIDTH - tw) / 2, 10), title, font=title_font, fill="white")

    # Project lat/lon -> pixel using staticmap internals for label placement.
    for ua, lat, lon in pts:
        x = m._x_to_px(_lon_to_x(lon, m.zoom))
        y = m._y_to_px(_lat_to_y(lat, m.zoom))
        # text with a light halo for readability
        tx, ty = x + 14, y - 10
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                draw.text((tx + dx, ty + dy), ua, font=label_font, fill="white")
        draw.text((tx, ty), ua, font=label_font, fill=(20, 20, 20))

    OUT.mkdir(parents=True, exist_ok=True)
    dst = OUT / f"{name}.png"
    image.save(dst, "PNG", optimize=True)
    print(f"  [{name}] {len(pts)} places -> {dst.relative_to(ROOT)}")
    return dst


def main():
    print("Generating biblical maps...")
    for name, (title, keys, route) in SCENES.items():
        generate_scene(name, title, keys, route)


if __name__ == "__main__":
    main()
