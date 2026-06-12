"""Check that local href/src targets in the GitHub Pages HTML files exist.

External URLs are not fetched; this only guards against broken
file references inside the repo. Run from the repo root:

    python3 scripts/check_site_links.py
"""

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
ATTR_PATTERN = re.compile(r"""(?:href|src)=["']([^"']+)["']""")

errors = []
checked = 0

for page in sorted(ROOT.glob("*.html")):
    text = page.read_text(encoding="utf-8")
    for target in ATTR_PATTERN.findall(text):
        parsed = urlparse(target)
        if parsed.scheme or target.startswith(("#", "mailto:", "//")):
            continue
        local = unquote(parsed.path)
        if not local:
            continue
        checked += 1
        if not (ROOT / local).exists():
            errors.append(f"{page.name}: missing local target '{target}'")

print(f"checked {checked} local references across {len(list(ROOT.glob('*.html')))} pages")
if errors:
    for e in errors:
        print(f"ERROR: {e}")
    sys.exit(1)
print("all local site links resolve")
