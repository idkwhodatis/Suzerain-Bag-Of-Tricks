"""Persist per-key condition stats + numeric thresholds to mining/thresholds.json.

Prerequisite: mining/conversation_refs.json (see Utils/conv_mine.py).
Usage: & "<save-editor>/venv/Scripts/python.exe" Utils/save_thresholds.py
"""
import ast
import json
import re
from pathlib import Path

REPO = Path(r"C:\Users\GLENN\Documents\git repos\Suzerain-BagOfTricks")
MINING = REPO / "GameDump" / "3.1.0.1.175" / "mining"
REFS = json.loads((MINING / "conversation_refs.json").read_text(encoding="utf-8"))
CONSTS = Path(r"C:\Users\GLENN\Documents\git repos\Suzerain-Save-Editor\Utils\Consts.py")
tree = ast.parse(CONSTS.read_text(encoding="utf-8"))
ns = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        try:
            ns[node.targets[0].id] = ast.literal_eval(node.value)
        except Exception:
            pass
maps = set(ns["FIELD_MAP_SORDLAND"].values()) | set(ns["FIELD_MAP_RIZIA"].values())
CMP_RE = re.compile(r'Variable\["([^"]+)"\]\s*(>=|<=|==|~=|>|<)\s*(-?\d+(?:\.\d+)?)')

out = {}
for key in sorted(maps):
    conds = [h for h in REFS.get(key, []) if h["kind"] == "cond"]
    scripts = sum(1 for h in REFS.get(key, []) if h["kind"] == "script")
    convs = sorted({h["conv"] for h in REFS.get(key, [])})
    thresh = {}
    for h in conds:
        for m in CMP_RE.finditer(h["snippet"]):
            if m.group(1) == key:
                thresh.setdefault(m.group(2), set()).add(m.group(3))
    out[key] = {"conds": len(conds), "writes": scripts, "convs": len(convs),
                "thresholds": {op: sorted(v, key=float) for op, v in thresh.items()}}
json.dump(out, open(MINING / "thresholds.json", "w"), indent=1)
n_thr = sum(1 for v in out.values() if v["thresholds"])
n_ref = sum(1 for v in out.values() if v["conds"] or v["writes"])
print(f"mapped keys with any refs: {n_ref}/170, with numeric thresholds: {n_thr}/170")
print("wrote mining/thresholds.json")
