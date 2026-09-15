"""Deep dedup audit: extras rows vs mapped keys, groups, other sections.

Fails loud (exit 1) on mapped/extras overlap or cross-section duplicates.
Usage: & "<save-editor>/venv/Scripts/python.exe" Utils/dedup_audit.py
"""
import ast
import json
import re
from collections import defaultdict
from pathlib import Path

REPO = Path(r"C:\Users\GLENN\Documents\git repos\Suzerain-BagOfTricks")
MINING = REPO / "GameDump" / "3.1.0.1.175" / "mining"
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
ex = json.loads((REPO / "Utils" / "api_extras.json").read_text(encoding="utf-8"))
sec_of = defaultdict(list)
for s in ex["sections"]:
    for r in s["rows"]:
        sec_of[r[0]].append(s["title"])
print(f"sections: {len(ex['sections'])}, rows: {sum(len(s['rows']) for s in ex['sections'])}")
print(f"mapped keys also in extras: {sorted(set(maps) & set(sec_of))}")
multi = {k: v for k, v in sec_of.items() if len(v) > 1}
print(f"keys in 2+ extras sections: {len(multi)}")
for k, v in sorted(multi.items())[:30]:
    print(f"  {k}: {v}")

TOG = json.loads((REPO / "Utils" / "groups.json").read_text(encoding="utf-8"))["groups"]
gmem = set()
for g in TOG:
    gmem.update(g.get("members", []))
    for o in g.get("options", {}).values():
        gmem.update(o)
print(f"\ngroup members also extras rows: {sorted(set(gmem) & set(sec_of))[:20]}")
print(f"group members NOT in maps+extras: {sorted(set(gmem) - maps - set(sec_of))[:20]}")

print("\n== same-beat pairs (TurnNN + slug in both GameCondition and scene flags) ==")
beats = defaultdict(set)
for k in list(maps) + list(sec_of):
    m = re.match(r"(?:BaseGameIsolated|BaseGameSupport|RiziaDLCIsolated|RiziaDLCSupport|GameCondition)\.(Turn\d+)_(\w+)", k)
    if not m:
        m = re.match(r"(?:BaseGame|RiziaDLC)\.(Turn\d+)_(\w+)", k)
    if m:
        beats[(m.group(1), m.group(2)[:28])].add(k)
n = sum(1 for v in beats.values() if len(v) > 1)
print(f"beats with 2+ keys: {n}")
shown = 0
for k in sorted(beats):
    if len(beats[k]) > 1 and shown < 15:
        print(f"  {k[0]}/{k[1]}: {sorted(beats[k])}")
        shown += 1
json.dump({"multi": multi}, open(MINING / "dedup_audit.json", "w"), indent=1)
print("wrote mining/dedup_audit.json")
import sys
bad = sorted(set(maps) & set(sec_of)) + sorted(multi)
if bad:
    print(f"DEDUP FAIL: {len(bad)} overlaps")
    sys.exit(1)
print("dedup ok: no overlaps")
