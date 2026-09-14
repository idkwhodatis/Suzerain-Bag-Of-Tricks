"""Compare F9 live-dump values vs DB initials (menu-default vs residual-state analysis).

Prerequisite: a BagOfTricks F9 dump in the game UserData dir (see DUMP below).
Writes: GameDump/3.1.0.1.175/mining/menu_deviations.json (gitignored).
Usage: & "<save-editor>/venv/Scripts/python.exe" Utils/live_compare.py
"""
import json
from pathlib import Path

MINING = Path(r"C:\Users\GLENN\Documents\git repos\Suzerain-BagOfTricks\GameDump\3.1.0.1.175\mining")
table = json.loads((MINING / "db_variables.json").read_text(encoding="utf-8"))

DUMP = Path(r"G:\SteamLibrary\steamapps\common\Suzerain\UserData\BagOfTricks\dump_menu_T0_S0_20260914_023045.txt")
live = {}
for ln in DUMP.read_text(encoding="utf-8").splitlines()[1:]:
    p = ln.split("\t")
    if len(p) >= 4 and p[1] == "True":
        live[p[0]] = p[2]

real = []
for k, v in live.items():
    init = (table.get(k) or {}).get("initial")
    if init in (None, ""):
        continue
    try:
        if int(float(init)) != int(v):
            # exclude pure bool-cast pairs
            if not ((init == "False" and v == "0") or (init == "True" and v == "1")):
                real.append((k, init, v))
    except ValueError:
        pass
print(f"real numeric deviations at menu: {len(real)}")
for k, a, b in sorted(real):
    print(f"  {k}: db-init={a} menu-live={b}")
json.dump([{"key": k, "dbInit": a, "menuLive": b} for k, a, b in sorted(real)],
          open(MINING / "menu_deviations.json", "w"), indent=1)
print("wrote mining/menu_deviations.json")
