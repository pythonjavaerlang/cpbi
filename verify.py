"""Verify the built static site: tags, OG images, internal links, sitemap."""
from __future__ import annotations

import re
import sys
from pathlib import Path

DIST = Path(__file__).resolve().parent / "dist"

errors = []
pages = list(DIST.rglob("index.html"))
print(f"pages: {len(pages)}")

# 1. Every page must have title, canonical, og:image, og:title, description.
required = ['<title>', 'rel="canonical"', 'property="og:image"', 'property="og:title"', 'name="description"']
missing_tags = 0
for p in pages:
    html = p.read_text(encoding="utf-8")
    for r in required:
        if r not in html:
            missing_tags += 1
            errors.append(f"{p.relative_to(DIST)} missing {r}")
print(f"tag checks: {'OK' if missing_tags == 0 else f'{missing_tags} missing'}")

# 2. Every og:image referenced must exist on disk.
og_refs = set()
for p in pages:
    html = p.read_text(encoding="utf-8")
    for m in re.finditer(r'property="og:image" content="https://cpbi\.info/(og/[^"]+)"', html):
        og_refs.add(m.group(1))
missing_og = [r for r in og_refs if not (DIST / r).exists()]
print(f"og images referenced: {len(og_refs)}, missing files: {len(missing_og)}")
for r in missing_og:
    errors.append(f"missing og file {r}")

# 3. OG images on disk.
og_files = list((DIST / "og").glob("*.jpg"))
print(f"og image files: {len(og_files)}")

# 4. Internal links resolve. Links are relative ("../x/", "./media/..") — resolve
#    them against each page's own directory and confirm the target exists on disk.
def _is_external(link: str) -> bool:
    return link.startswith(("http://", "https://", "//", "mailto:", "tel:", "data:", "#"))


broken = {}
link_re = re.compile(r'(?:href|src)="([^"]+)"')
script_re = re.compile(r"<script\b.*?</script>", re.S | re.I)
for p in pages:
    page_dir = p.parent
    html = p.read_text(encoding="utf-8")
    html_no_js = script_re.sub("", html)  # ignore URLs built inside inline JS
    for m in link_re.finditer(html_no_js):
        link = m.group(1)
        if _is_external(link):
            continue
        if "'+" in link or "+'" in link or "{{" in link:
            continue  # template/JS artifact, not a real URL
        clean = link.split("#")[0].split("?")[0]
        if not clean:
            continue
        target = (page_dir / clean).resolve()
        # directory link (ends with / or no suffix) -> expect index.html inside
        if clean.endswith("/"):
            ok = (target / "index.html").exists()
        elif target.suffix:
            ok = target.exists()
        else:
            ok = (target / "index.html").exists() or target.exists()
        if not ok:
            broken.setdefault(link, []).append(str(p.relative_to(DIST)))
print(f"broken internal links: {len(broken)}")
for link, where in list(broken.items())[:40]:
    errors.append(f"broken link {link} (e.g. in {where[0]})  x{len(where)}")

# 5. sitemap + robots.
sm = DIST / "sitemap.xml"
rb = DIST / "robots.txt"
print(f"sitemap.xml: {'OK' if sm.exists() else 'MISSING'} ; robots.txt: {'OK' if rb.exists() else 'MISSING'}")
if sm.exists():
    locs = re.findall(r"<loc>(.*?)</loc>", sm.read_text(encoding="utf-8"))
    print(f"sitemap urls: {len(locs)}")

# 6. No stray numeric-only top dirs.
stray = [d.name for d in DIST.iterdir() if d.is_dir() and d.name.isdigit()]
if stray:
    errors.append(f"stray numeric dirs: {stray}")
print(f"stray numeric dirs: {stray}")

print("\n=== RESULT ===")
if errors:
    print(f"{len(errors)} issue(s):")
    for e in errors[:60]:
        print("  -", e)
    sys.exit(1)
print("ALL CHECKS PASSED")
