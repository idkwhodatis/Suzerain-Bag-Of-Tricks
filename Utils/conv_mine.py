"""Mine Variable[".."] references in dialogue conditions + scripts (all conversations).

Prerequisite: GameDump/3.1.0.1.175/db_tree.json (see Utils/db_dump.py).
Writes: GameDump/3.1.0.1.175/mining/conversation_refs.json (gitignored).
Usage: & "<save-editor>/venv/Scripts/python.exe" Utils/conv_mine.py
"""
import json
import re
from collections import defaultdict
from pathlib import Path

REPO = Path(r"C:\Users\GLENN\Documents\git repos\Suzerain-BagOfTricks")
OUT = REPO / "GameDump" / "3.1.0.1.175" / "mining" / "conversation_refs.json"
VAR_RE = re.compile(r'Variable\["([^"]+)"\]')

print("loading...")
db = json.load(open(REPO / "GameDump" / "3.1.0.1.175" / "db_tree.json", encoding="utf-8"))
refs = defaultdict(list)
nentries = 0
for conv in db.get("conversations", []):
    title = ""
    for f in conv.get("fields", []):
        if f.get("title") == "Title":
            title = f.get("value")
            break
    for e in conv.get("dialogueEntries", []):
        nentries += 1
        etitle = ""
        for f in e.get("fields", []):
            if f.get("title") == "Title":
                etitle = str(f.get("value"))[:60]
                break
        for kind, text in (("cond", e.get("conditionsString", "")), ("script", e.get("userScript", ""))):
            if not text:
                continue
            for key in set(VAR_RE.findall(text)):
                refs[key].append({"conv": title, "entry": etitle, "kind": kind,
                                  "snippet": text[:160]})
print(f"entries: {nentries}, referenced keys: {len(refs)}")
json.dump({k: v for k, v in sorted(refs.items())}, open(OUT, "w"), indent=0, default=str)
print(f"wrote {OUT} ({OUT.stat().st_size // 1024}KB)")

targets = ["BaseGame.BlackTuesdayHappened", "BaseGame.Situation_Order_Corruption",
           "RiziaDLC.Authority_Modifier_Retrograde", "RiziaDLC.Energy_Modifier_Retrograde",
           "GameCondition.Turn11_SnO_RumburgWarWin", "GameCondition.Turn11_SnO_RumburgWarLost",
           "BaseGame.RumburgWar_Performance", "BaseGame.GovernmentBudget"]
for t in targets:
    hits = refs.get(t, [])
    print(f"\n== {t}: {len(hits)} refs ==")
    for h in hits[:8]:
        print(f"  [{h['kind']}] {h['conv']} / {h['entry']} :: {h['snippet'][:120]}")
