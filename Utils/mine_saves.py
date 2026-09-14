"""Mine Suzerain saves for the full Lua variable key universe.

Parses the `variables` string of every save in the Suzerain save dir
(same format logic as Suzerain-Save-Editor Utils/Parser.py) and dumps:
  - per-save: campaign/storyPack/turnNo/version, key count
  - aggregate: every key with observed types + sample values + in-how-many-saves
  - JSON artifacts for further diffing (written to GameDump mining dir)

Usage:
  & "<save-editor>/venv/Scripts/python.exe" Utils/mine_saves.py (from repo root)
"""
import json
import re
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SAVE_DIR = Path(r"C:\Users\GLENN\AppData\LocalLow\Torpor Games\Suzerain")
OUT_DIR = REPO / "GameDump" / "3.1.0.1.175" / "mining"
OUT_DIR.mkdir(parents=True, exist_ok=True)
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


def main():
    saves = sorted(SAVE_DIR.glob("*.json"))
    print(f"saves found: {len(saves)}")
    universe = defaultdict(lambda: {"types": set(), "samples": [], "nsaves": 0, "saves": []})
    per_save = []
    for path in saves:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"SKIP {path.name}: {e}")
            continue
        varstr = data.get("variables", "")
        keys = {}
        for k, raw in PAIR_RE.findall(varstr):
            try:
                keys[k] = coerce(raw)
            except Exception:
                keys[k] = f"<unparsed:{raw[:40]}>"
        meta = {
            "file": path.name,
            "campaign": data.get("campaignName"),
            "storyPack": data.get("currentStoryPack"),
            "turn": data.get("turnNo"),
            "version": data.get("version"),
            "nkeys": len(keys),
        }
        per_save.append(meta)
        print(f"{path.name}: pack={meta['storyPack']} turn={meta['turn']} ver={meta['version']} nkeys={meta['nkeys']}")
        for k, v in keys.items():
            u = universe[k]
            u["types"].add(type(v).__name__)
            u["nsaves"] += 1
            u["saves"].append(path.name)
            if len(u["samples"]) < 3:
                u["samples"].append(v)

    serial = {
        k: {"types": sorted(v["types"]), "samples": v["samples"][:3], "nsaves": v["nsaves"]}
        for k, v in sorted(universe.items())
    }
    (OUT_DIR / "universe.json").write_text(json.dumps(serial, indent=1, default=str), encoding="utf-8")
    (OUT_DIR / "saves.json").write_text(json.dumps(per_save, indent=1, default=str), encoding="utf-8")
    print(f"total unique keys: {len(serial)}")
    prefixes = defaultdict(int)
    for k in serial:
        prefixes[k.split(".")[0] if "." in k else "<noprefix>"] += 1
    print("prefix counts:", dict(sorted(prefixes.items())))


if __name__ == "__main__":
    main()
