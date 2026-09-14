"""Extract DialogueDB variable table: name/type/initial/description per variable.

Prerequisite: GameDump/3.1.0.1.175/db_tree.json (see Utils/db_dump.py).
Writes: GameDump/3.1.0.1.175/mining/db_variables.json (gitignored).
Usage: & "<save-editor>/venv/Scripts/python.exe" Utils/db_table.py
"""
import ast
import json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MINING = REPO / "GameDump" / "3.1.0.1.175" / "mining"
DB = REPO / "GameDump" / "3.1.0.1.175" / "db_tree.json"
CONSTS = Path(r"C:\Users\GLENN\Documents\git repos\Suzerain-Save-Editor\Utils\Consts.py")
print("loading...")
db = json.loads(DB.read_text(encoding="utf-8"))
variables = db["variables"]

# one full entry
for v in variables:
    names = [f for f in v["fields"] if f.get("title") == "Name"]
    if names and names[0].get("value") == "BaseGame.GovernmentBudget":
        print("GOVBUDGET FULL:", json.dumps(v, default=str))
        break

table = {}
for v in variables:
    d = {f.get("title"): f.get("value") for f in v["fields"]}
    name = d.get("Name")
    if name:
        table[name] = {"type": d.get("Type"), "initial": d.get("Initial Value"),
                       "desc": d.get("Description"), "id": v.get("id")}
print(f"\ntable: {len(table)} named variables")
print("types:", Counter(v["type"] for v in table.values()).most_common(10))
ndesc = sum(1 for v in table.values() if v["desc"])
print(f"with Description: {ndesc}/{len(table)}")
for k in ("BaseGame.GovernmentBudget", "RiziaDLC.Resources_Budget", "BaseGame.Agnolia_Alliance"):
    print(f"{k}: {table.get(k)}")

tree = ast.parse(CONSTS.read_text(encoding="utf-8"))
ns = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        try:
            ns[node.targets[0].id] = ast.literal_eval(node.value)
        except Exception:
            pass
maps = set(ns["FIELD_MAP_SORDLAND"].values()) | set(ns["FIELD_MAP_RIZIA"].values())
print(f"\nFIELD_MAP in DB: {len(set(maps) & set(table))}/170")
print("missing:", sorted(set(maps) - set(table))[:20])
uni = json.loads((MINING / "universe.json").read_text(encoding="utf-8"))
print(f"\nDB names never in saves: {len(set(table) - set(uni))}")
only = sorted(set(table) - set(uni))
for k in only[:30]:
    print(f"  DB-ONLY: {k} ({table[k]['type']})")
json.dump(only, open(MINING / "db_only.json", "w"), indent=0)
print("wrote mining/db_only.json")
json.dump(table, open(MINING / "db_variables.json", "w"), indent=0, default=str)
print("\nwrote mining/db_variables.json")
