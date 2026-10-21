# coding=utf-8
"""Curated gazetteer of biblical places with known coordinates.

Each entry maps a canonical key to:
  ua:      Ukrainian label (ancient name) to render on the map
  modern:  modern place / Nominatim query hint (for reference / fallback)
  lat,lon: decimal degrees (WGS84)

Coordinates are well-established identifications of ancient sites (e.g.
Tahpanhes ≈ Tell Defenneh, Noph = Memphis, On = Heliopolis). Using a fixed
table avoids Nominatim returning the wrong modern place for ancient-only names
and keeps the build reproducible/offline.
"""
from __future__ import annotations

# key: (ua_label, modern_hint, lat, lon)
PLACES = {
    # — Egypt / Exodus & Jeremiah-in-Egypt cluster —
    "egypt":        ("Єгипет", "Egypt", 26.8206, 30.8025),
    "noph":         ("Ноф (Мемфіс)", "Memphis, Egypt", 29.8447, 31.2506),
    "memphis":      ("Мемфіс", "Memphis, Egypt", 29.8447, 31.2506),
    "tahpanhes":    ("Тахпанхес (Телль-Дефенне)", "Tell Defenneh, Egypt", 30.8667, 32.1667),
    "migdol":       ("Мігдол", "Tell el-Her, Egypt", 31.0333, 32.4167),
    "on":           ("Он (Геліополіс)", "Heliopolis, Cairo", 30.1292, 31.2894),
    "heliopolis":   ("Геліополіс", "Heliopolis, Cairo", 30.1292, 31.2894),
    "pathros":      ("Патрос (Верхній Єгипет)", "Thebes, Luxor, Egypt", 25.6872, 32.6396),
    "goshen":       ("Гошен", "Faqus, Egypt", 30.7281, 31.7967),
    "pithom":       ("Пітом", "Tell el-Maskhuta, Egypt", 30.5500, 32.1000),
    "rameses":      ("Рамесес", "Qantir, Egypt", 30.8000, 31.8333),
    "nile":         ("Ніл", "Nile River", 27.0000, 31.0000),
    "red_sea":      ("Червоне море", "Red Sea", 27.0000, 34.5000),

    # — Mesopotamia / exile cluster —
    "babylon":      ("Вавилон", "Babylon, Iraq", 32.5355, 44.4209),
    "nineveh":      ("Ніневія", "Nineveh, Mosul, Iraq", 36.3597, 43.1528),
    "ur":           ("Ур Халдейський", "Ur, Iraq", 30.9626, 46.1030),
    "susa":         ("Сузи (Шушан)", "Susa, Iran", 32.1897, 48.2578),
    "haran":        ("Харан", "Harran, Turkey", 36.8639, 39.0306),
    "euphrates":    ("Євфрат", "Euphrates River", 34.0000, 42.0000),
    "tigris":       ("Тигр", "Tigris River", 35.0000, 43.5000),
    "ecbatana":     ("Екбатана", "Hamadan, Iran", 34.7983, 48.5148),
    "persepolis":   ("Персеполь", "Persepolis, Iran", 29.9356, 52.8906),

    # — Levant / Israel & Judah —
    "jerusalem":    ("Єрусалим", "Jerusalem", 31.7767, 35.2345),
    "bethlehem":    ("Віфлеєм", "Bethlehem", 31.7054, 35.2024),
    "hebron":       ("Хеврон", "Hebron", 31.5326, 35.0998),
    "jericho":      ("Єрихон", "Jericho", 31.8611, 35.4444),
    "samaria":      ("Самарія", "Sebastia, Nablus", 32.2767, 35.1903),
    "shechem":      ("Сихем", "Nablus", 32.2211, 35.2544),
    "shiloh":       ("Сило", "Shiloh, West Bank", 32.0556, 35.2897),
    "bethel":       ("Вефіль", "Beitin, West Bank", 31.9303, 35.2256),
    "gibeon":       ("Гаваон", "Al Jib, Jerusalem", 31.8464, 35.1836),
    "ai":           ("Гай", "Et-Tell, West Bank", 31.9170, 35.2600),
    "nazareth":     ("Назарет", "Nazareth", 32.7019, 35.2978),
    "capernaum":    ("Капернаум", "Capernaum", 32.8808, 35.5753),
    "cana":         ("Кана Галілейська", "Kafr Kanna", 32.7475, 35.3419),
    "bethsaida":    ("Віфсаїда", "Bethsaida, Israel", 32.9100, 35.6306),
    "tiberias":     ("Тиверіада", "Tiberias", 32.7922, 35.5312),
    "sea_galilee":  ("Галілейське море", "Sea of Galilee", 32.8000, 35.5833),
    "jordan":       ("Йордан", "Jordan River", 32.3000, 35.5700),
    "dead_sea":     ("Мертве море", "Dead Sea", 31.5000, 35.5000),
    "beersheba":    ("Беер-Шева", "Beersheba", 31.2518, 34.7913),
    "jezreel":      ("Ізреель", "Jezreel Valley", 32.5586, 35.3292),
    "carmel":       ("Кармил", "Mount Carmel, Haifa", 32.7333, 35.0500),
    "mount_tabor":  ("Гора Фавор", "Mount Tabor, Israel", 32.6870, 35.3903),
    "mount_sinai":  ("Гора Синай", "Mount Sinai, Egypt", 28.5392, 33.9750),
    "mount_horeb":  ("Гора Хорив", "Mount Sinai, Egypt", 28.5392, 33.9750),
    "mount_nebo":   ("Гора Нево", "Mount Nebo, Jordan", 31.7681, 35.7256),
    "olivet":       ("Оливна гора", "Mount of Olives, Jerusalem", 31.7784, 35.2456),
    "dan":          ("Дан", "Tel Dan, Israel", 33.2486, 35.6525),

    # — Phoenicia / Syria —
    "tyre":         ("Тир", "Tyre, Lebanon", 33.2705, 35.2038),
    "sidon":        ("Сидон", "Sidon, Lebanon", 33.5606, 35.3756),
    "damascus":     ("Дамаск", "Damascus", 33.5138, 36.2765),
    "antioch":      ("Антіохія", "Antakya, Turkey", 36.2058, 36.1614),

    # — Transjordan / neighbours —
    "moab":         ("Моав", "Madaba, Jordan", 31.4500, 35.7500),
    "edom":         ("Едом", "Petra, Jordan", 30.3285, 35.4444),
    "ammon":        ("Аммон", "Amman, Jordan", 31.9539, 35.9106),
    "midian":       ("Мадіам", "Tabuk, Saudi Arabia", 28.3833, 36.5833),

    # — Asia Minor / Greece / Rome (NT epistles, Revelation) —
    "ephesus":      ("Ефес", "Selcuk, Turkey", 37.9497, 27.3639),
    "corinth":      ("Корінт", "Corinth, Greece", 37.9061, 22.8781),
    "athens":       ("Афіни", "Athens, Greece", 37.9838, 23.7275),
    "thessalonica": ("Солунь", "Thessaloniki, Greece", 40.6401, 22.9444),
    "philippi":     ("Філіппи", "Philippi, Greece", 41.0136, 24.2869),
    "rome":         ("Рим", "Rome, Italy", 41.9028, 12.4964),
    "colossae":     ("Колоси", "Honaz, Turkey", 37.7906, 29.2611),
    "galatia":      ("Галатія", "Ankara, Turkey", 39.9334, 32.8597),
    "iconium":      ("Іконія", "Konya, Turkey", 37.8714, 32.4846),
    "lystra":       ("Листра", "Hatunsaray, Turkey", 37.5800, 32.2800),
    "derbe":        ("Дервія", "Karaman, Turkey", 37.1814, 33.2156),
    "cyprus":       ("Кіпр", "Cyprus", 35.1264, 33.4299),
    "crete":        ("Крит", "Crete, Greece", 35.2401, 24.8093),
    "malta":        ("Мальта (Меліта)", "Malta", 35.9375, 14.3754),
    "patmos":       ("Патмос", "Patmos, Greece", 37.3089, 26.5467),
    "smyrna":       ("Смирна", "Izmir, Turkey", 38.4237, 27.1428),
    "pergamum":     ("Пергам", "Bergama, Turkey", 39.1319, 27.1817),
    "thyatira":     ("Тіятира", "Akhisar, Turkey", 38.9192, 27.8408),
    "sardis":       ("Сарди", "Sart, Turkey", 38.4883, 28.0400),
    "philadelphia": ("Філадельфія", "Alasehir, Turkey", 38.3486, 28.5189),
    "laodicea":     ("Лаодикія", "Denizli, Turkey", 37.8361, 29.1075),
}
