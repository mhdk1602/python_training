"""Validate that every notebook in the repo is well-formed.

Checks JSON parseability, nbformat structure, and (as warnings only)
the chapter naming convention. Run from the repo root:

    python3 scripts/validate_notebooks.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME_PATTERN = re.compile(r"^\d+\.\d+(\.\d+)? .+\.ipynb$|^bonus", re.IGNORECASE)

errors = []
warnings = []
count = 0

for path in sorted(ROOT.glob("notebooks/**/*.ipynb")):
    if ".ipynb_checkpoints" in path.parts or ".venv" in str(path):
        continue
    count += 1
    rel = path.relative_to(ROOT)

    try:
        nb = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        errors.append(f"{rel}: not parseable JSON ({exc})")
        continue

    if "cells" not in nb or not isinstance(nb["cells"], list):
        errors.append(f"{rel}: missing or invalid 'cells' list")
        continue
    if "nbformat" not in nb:
        errors.append(f"{rel}: missing 'nbformat' version")
        continue

    for i, cell in enumerate(nb["cells"]):
        if cell.get("cell_type") not in ("code", "markdown", "raw"):
            errors.append(f"{rel}: cell {i} has invalid cell_type {cell.get('cell_type')!r}")
        if "source" not in cell:
            errors.append(f"{rel}: cell {i} has no source")

    if not NAME_PATTERN.match(path.name):
        warnings.append(f"{rel}: name does not follow '{{chapter}}.{{section}} Topic.ipynb'")

print(f"checked {count} notebooks")
for w in warnings:
    print(f"warning: {w}")
if errors:
    for e in errors:
        print(f"ERROR: {e}")
    sys.exit(1)
print("all notebooks well-formed")
