"""Condense conversation_refs.json into per-key trigger summaries + role tags.

Roles (evidence-based, from dialogue write/read sites + campaign variance):
  store   — read and written across content (core state variable)
  trigger — set in <=2 fragments, read by branches (one-shot event flag)
  lever   — Decision_/Policy_/Promise_/Enable_/Bill_ enactment flag read later
  mirror  — no content refs but varies in saves (engine-written display copy)
  gate    — read by branches, never written in content (engine input)
  record  — written in content, never branched on (outcome log)
  const   — no refs, static, clamp-like name (Min/Max/Threshold sentinel)
  dormant — no refs and static in saves (rare-branch or dead)

Writes: GameDump/3.1.0.1.175/mining/triggers.json (gitignored):
  {key: {nwrites, nconds, nconvs, writes:[conv/entry], conds:[conv], role}}
Capped small; consumed by Utils/gen_api.py.
Usage: & "<save-editor>/venv/Scripts/python.exe" Utils/build_triggers.py
"""
import json
from collections import Counter
from pathlib import Path

MINING = Path(__file__).resolve().parent.parent / "GameDump" / "3.1.0.1.175" / "mining"
REFS = json.loads((MINING / "conversation_refs.json").read_text(encoding="utf-8"))
ANA = json.loads((MINING / "analysis.json").read_text(encoding="utf-8"))
VARYING = set(ANA["campaigns"]["sordland_3.1.0.1.153"]["allVarying"]) | set(
    ANA["campaigns"]["rizia_3.1.0.1.137"]["allVarying"])


ENACT = ("Decision_", "Policy_", "Promise_", "Enable_", "Bill_")


def role(key, nw, nc):
    if nw == 0 and nc == 0:
        if key in VARYING:
            return "mirror"
        if key.endswith(("_Max", "_Min")) or "Threshold" in key:
            return "const"
        return "dormant"
    if nw == 0:
        return "gate"
    if nc == 0:
        return "record"
    if any(s in key for s in ENACT):
        return "lever"
    if nw <= 2:
        return "trigger"
    return "store"


out = {}
for key, hits in REFS.items():
    wr = [(h["conv"], h["entry"]) for h in hits if h["kind"] == "script"]
    co = Counter(h["conv"] for h in hits if h["kind"] == "cond")
    nw, nc = len(wr), sum(co.values())
    out[key] = {"nwrites": nw, "nconds": nc,
                "nconvs": len({h["conv"] for h in hits}),
                "writes": [f"{c}/{e}" for c, e in wr[:5]],
                "condConvs": [f"{c}({n})" for c, n in co.most_common(5)],
                "role": role(key, nw, nc)}
from collections import Counter as C2
UNI = json.loads((MINING / "universe.json").read_text(encoding="utf-8"))
for key in UNI:
    if key not in out:
        out[key] = {"nwrites": 0, "nconds": 0, "nconvs": 0, "writes": [],
                    "condConvs": [], "role": role(key, 0, 0)}
json.dump(out, open(MINING / "triggers.json", "w"), indent=0)
print(f"triggers for {len(out)} keys; roles: {dict(C2(v['role'] for v in out.values()).most_common())}")
