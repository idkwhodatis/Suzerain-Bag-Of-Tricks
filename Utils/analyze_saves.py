"""Variance + coverage analysis over mined saves.

- Checks every FIELD_MAP key (Consts.py) exists in the save universe.
- Tracks value changes across two full campaigns:
    Sordland 3.1.0.1.153 turns 1-11 (TurnSave_28/29-03-2026_*)
    Rizia    3.1.0.1.137 turns 1-11 (TurnSave_12-09-2025_*)
- Lists GameCondition.* keys, *HUDStat*/*Max* keys, SharedSupport.* keys.
- Writes analysis.json to the GameDump mining dir.

Usage:
  & "<save-editor>/venv/Scripts/python.exe" Utils/analyze_saves.py (from repo root, after mine_saves.py)
"""
import ast
import json
import re
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HERE = REPO / "GameDump" / "3.1.0.1.175" / "mining"
SAVE_DIR = Path(r"C:\Users\GLENN\AppData\LocalLow\Torpor Games\Suzerain")
CONSTS = Path(r"C:\Users\GLENN\Documents\git repos\Suzerain-Save-Editor\Utils\Consts.py")
PAIR_RE = re.compile(r'\["([^"]+)"\]=("(?:(?:\\.|[^"\\])*)"|[^,}]+)')
INT_RE = re.compile(r"[+-]?\d+$")
FLOAT_RE = re.compile(r"[+-]?\d+\.\d+$")
EXP_RE = re.compile(r'^"?([+-]?(?:\d+(?:\.\d*)?|\.\d+)[eE][+-]?\d+)"?$')


def coerce(raw):
    v = raw.strip()
    if v == "true":
        return True
    if v == "false":
        return False
    if INT_RE.fullmatch(v):
        return int(v)
    if FLOAT_RE.fullmatch(v):
        return float(v)
    m = EXP_RE.fullmatch(v)
    if m:
        return int(float(m.group(1)))
    return v.replace('"', "")


def load_vars(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k: coerce(r) for k, r in PAIR_RE.findall(data.get("variables", ""))}


def campaign(prefix_date, pack):
    files = sorted(SAVE_DIR.glob(f"TurnSave_{prefix_date}_*.json"))
    seq = []
    for p in files:
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("currentStoryPack") == pack:
            seq.append((d.get("turnNo"), p))
    return [p for _, p in sorted(seq)]


def main():
    tree = ast.parse(CONSTS.read_text(encoding="utf-8"))
    ns = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                ns[node.targets[0].id] = ast.literal_eval(node.value)
            except Exception:
                pass
    field_keys = set(ns["FIELD_MAP_SORDLAND"].values()) | set(ns["FIELD_MAP_RIZIA"].values())

    universe = {k: v for k, v in json.loads((HERE / "universe.json").read_text(encoding="utf-8")).items()}
    missing = sorted(k for k in field_keys if k not in universe)
    print(f"FIELD_MAP keys: {len(field_keys)}, missing from saves: {len(missing)}")
    for k in missing:
        print(f"  MISSING: {k}")

    result = {"fieldMapMissing": missing, "campaigns": {}}
    for name, files in [
        ("sordland_3.1.0.1.153", campaign("28-03-2026", "StoryPack_Main") + campaign("29-03-2026", "StoryPack_Main")),
        ("rizia_3.1.0.1.137", campaign("12-09-2025", "StoryPack_Rizia")),
    ]:
        print(f"\n== {name}: {len(files)} saves ==")
        snaps = [load_vars(p) for p in files]
        keys = set().union(*[set(s) for s in snaps])
        varying, static = {}, 0
        for k in keys:
            vals = [repr(s.get(k, "<absent>")) for s in snaps]
            if len(set(vals)) > 1:
                varying[k] = vals
            else:
                static += 1
        print(f"keys: {len(keys)}, varying across turns: {len(varying)}, static: {static}")
        pre = defaultdict(int)
        for k in varying:
            pre[k.split(".")[0]] += 1
        print("varying by prefix:", dict(sorted(pre.items())))
        # crucial-looking varying keys: HUD stats, resources, opinion, economy, war, conditions
        interesting = sorted(
            k for k in varying
            if re.search(r"HUDStat|_Max$|Resources_|Opinion|Economy|War|Budget|Authority|Energy|Wealth|Unrest|Vote|Alliance|TradeDeal|Corruption|Crime", k)
            and "Support" not in k and "Isolated" not in k
        )
        print(f"crucial-candidate varying keys: {len(interesting)}")
        result["campaigns"][name] = {
            "nsaves": len(files),
            "nkeys": len(keys),
            "nvarying": len(varying),
            "varyingPrefixes": dict(sorted(pre.items())),
            "crucialCandidates": {k: varying[k] for k in interesting},
            "allVarying": sorted(varying),
        }

    gamecond = sorted(k for k in universe if k.startswith("GameCondition."))
    print(f"\nGameCondition keys: {len(gamecond)}")
    result["gameCondition"] = gamecond
    shared = sorted(k for k in universe if k.startswith("SharedSupport."))
    print(f"SharedSupport keys: {len(shared)}")
    result["sharedSupport"] = shared
    hudmax = sorted(k for k in universe if "HUDStat" in k or k.endswith("_Max"))
    print(f"HUDStat/_Max keys: {len(hudmax)}")
    result["hudStatMax"] = hudmax

    (HERE / "analysis.json").write_text(json.dumps(result, indent=1, default=str), encoding="utf-8")
    print("\nwrote analysis.json")


if __name__ == "__main__":
    main()
