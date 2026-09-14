"""Validate Agents/API.md table structure: column counts, stray pipes, markers.

Usage: & "<save-editor>/venv/Scripts/python.exe" Utils/validate_api.py
Run after every Utils/gen_api.py regen; fails loud on malformed rows.
"""
from pathlib import Path

lines = Path(r"C:\Users\GLENN\Documents\git repos\Suzerain-BagOfTricks\Agents\API.md").read_text(encoding="utf-8").splitlines()
bad = []
nrows = 0
expected = 0
for i, ln in enumerate(lines, 1):
    if ln.startswith("|"):
        nrows += 1
        # separator rows look like |---|---|
        if set(ln.strip("|").replace(" ", "")) <= set("|-:"):
            continue
        cells = ln.split("|")
        if "| Field |" in ln or "| Key |" in ln or "| Change |" in ln or "| # |" in ln:
            expected = len(cells)
            continue
        if len(cells) != expected:
            bad.append((i, ln[:160]))
print(f"table rows: {nrows}, malformed: {len(bad)}")
for i, ln in bad[:15]:
    print(f"  L{i}: {ln}")
for marker in ("TBD", "TODO", "FIXME", "game-dump", "tools/"):
    hits = [(i + 1) for i, ln in enumerate(lines) if marker in ln]
    if hits:
        print(f"marker {marker!r}: lines {hits[:8]}")
