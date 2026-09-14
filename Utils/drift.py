"""Version drift + globally-static key analysis across all saves.

- Keys added/removed between game versions (migration fossils).
- Keys byte-identical across every save (untaken branches, not dead keys).
- Writes drift.json to the GameDump mining dir.

Usage:
  & "<save-editor>/venv/Scripts/python.exe" Utils/drift.py (from repo root, after mine_saves.py)
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


def load_vars(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return data, {k: v.strip() for k, v in PAIR_RE.findall(data.get("variables", ""))}


def main():
    ver_keys = defaultdict(set)
    key_vals = defaultdict(set)
    key_n = defaultdict(int)
    nsaves = 0
    for p in sorted(SAVE_DIR.glob("*.json")):
        try:
            data, kv = load_vars(p)
        except Exception:
            continue
        nsaves += 1
        ver_keys[data.get("version", "?")].update(kv.keys())
        for k, v in kv.items():
            key_vals[k].add(v[:80])
            key_n[k] += 1
    print(f"saves: {nsaves}, versions: {sorted(ver_keys)}")
    for v, ks in sorted(ver_keys.items()):
        print(f"  {v}: {len(ks)} keys")
    order = ["release_3.0.9-hotfix", "3.1.0.1.137", "3.1.0.1.153"]
    versions = [v for v in order if v in ver_keys]
    oldest, newest = versions[0], versions[-1]
    added = sorted(ver_keys[newest] - ver_keys[oldest])
    removed = sorted(ver_keys[oldest] - ver_keys[newest])
    print(f"added {newest} vs {oldest}: {len(added)}")
    print(f"removed {newest} vs {oldest}: {len(removed)}")
    static_all = sorted(k for k, vs in key_vals.items() if len(vs) == 1 and key_n[k] == nsaves)
    print(f"static-in-every-save: {len(static_all)}")
    (OUT_DIR / "drift.json").write_text(json.dumps(
        {"oldest": oldest, "newest": newest, "added": added,
         "removed": removed, "staticAll": static_all}, indent=1), encoding="utf-8")
    print("wrote drift.json")


if __name__ == "__main__":
    main()
