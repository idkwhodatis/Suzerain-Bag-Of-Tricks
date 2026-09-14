"""Build repo Utils/api_extras.json from mined save analysis.

Selection (cheat/content-modding relevant, scene-mirror bulk excluded):
- Varying BaseGame.*/RiziaDLC.* across a full campaign, minus scene segments
  (Turn01-11, Prologue, Dinner, TBD) — these provably change during play.
- Static BaseGame.*/RiziaDLC.* only from cheat-relevant segments
  (resources, policy, economy, endings, unrest, war, ...).
- All GameCondition.* (story-gate IDs) and SharedSupport.* (codex/news mirrors).
- FIELD_MAP keys excluded (already in curated API.md tables).

Usage:
  & "<save-editor>/venv/Scripts/python.exe" Utils/build_extras.py (from repo root, after analyze_saves.py)
Writes: <repo>/Utils/api_extras.json
"""
import ast
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HERE = REPO / "GameDump" / "3.1.0.1.175" / "mining"
CONSTS = Path(r"C:\Users\GLENN\Documents\git repos\Suzerain-Save-Editor\Utils\Consts.py")

SCENE_SEG = {"Turn01", "Turn02", "Turn03", "Turn04", "Turn05", "Turn06",
             "Turn07", "Turn08", "Turn09", "Turn10", "Turn11",
             "Prologue", "Dinner", "TBD"}
STATIC_SEG = {"Resources", "ResourcesExtra", "Budget", "Authority", "Energy",
              "Country", "CountryRelation", "Diplomacy", "Economy",
              "EconomyAction", "EconomicDirection", "Policy", "Enable",
              "Ending", "Epilogue", "Unrest", "NoUnrest", "War", "RumburgWar",
              "Rumburg", "RumburgIncident", "Army", "MITZ", "Focus",
              "RoyalDecrees", "Decrees", "ModifierCountryStat", "Win",
              "Reform", "Faction", "Promise", "Bill", "Election",
              "Retirement", "Exile", "Resigned", "Joined", "BFF",
              "Amendment", "LivingStandard", "Pandemic", "SecretState",
              "Oligarchs", "HeartOfSordland", "SordlandArmySize",
              "VetoedBillCount", "SignedBillCount", "GovernmentBudget",
              "PersonalWealth", "Public", "TradeAmount", "EconomicReliance",
              "Corruption", "Panel", "PersonalValue", "Trait", "Manpower",
              "Equipment", "Military", "GRACETrade", "HouseElections",
              "HODElection", "RNCElection", "RPPElection", "NationalizeRRG",
              "RRG", "PowerProjection", "Security", "FinancialAid",
              "SpecialZone", "BergiaSpecialZone", "ChiefJustice",
              "CurrentSpeaker", "SordishStateCorporation", "Gasom",
              "SuperpowerVisit", "Agnolia", "Wehlen", "Lespia", "Valgsland",
              "Arcasia", "ErsenCase", "LeakedScandal", "Leaker", "Media",
              "Petr", "Lucian", "Marcel", "NFPLeader", "PFJPLeader"}


def seg_of(key):
    return key.split(".")[1].split("_")[0] if "." in key else ""


def main():
    tree = ast.parse(CONSTS.read_text(encoding="utf-8"))
    ns = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                ns[node.targets[0].id] = ast.literal_eval(node.value)
            except Exception:
                pass
    in_maps = set(ns["FIELD_MAP_SORDLAND"].values()) | set(ns["FIELD_MAP_RIZIA"].values())

    uni = json.loads((HERE / "universe.json").read_text(encoding="utf-8"))
    ana = json.loads((HERE / "analysis.json").read_text(encoding="utf-8"))
    camps = ana["campaigns"]
    vary_s = camps["sordland_3.1.0.1.153"]
    vary_r = camps["rizia_3.1.0.1.137"]
    cand_s = vary_s["crucialCandidates"]
    cand_r = vary_r["crucialCandidates"]
    set_s, set_r = set(vary_s["allVarying"]), set(vary_r["allVarying"])

    sections = []

    def core_extras(ns_prefix, vset, cands, camp):
        live, static = [], []
        for k in sorted(uni):
            if not k.startswith(ns_prefix + ".") or k in in_maps:
                continue
            if k in vset:
                if seg_of(k) in SCENE_SEG:
                    continue
                if k in cands:
                    vals = cands[k]
                    note = f"value moves {vals[0]}->{vals[-1]} over T1-T11 ({camp}); effect unconfirmed"
                else:
                    note = f"flips during {camp} campaign; effect unconfirmed"
                live.append([k, note])
            elif seg_of(k) in STATIC_SEG:
                types = "/".join(uni[k]["types"])
                samp = uni[k]["samples"][0] if uni[k]["samples"] else "?"
                note = f"static ({types}={samp!r}, n={uni[k]['nsaves']} saves); lever unconfirmed"
                static.append([k, note])
        return live, static

    for title, prefix, vset, cands, camp in [
        ("Sordland", "BaseGame", set_s, cand_s, "Sordland 3.1.0.1.153"),
        ("Rizia", "RiziaDLC", set_r, cand_r, "Rizia 3.1.0.1.137"),
    ]:
        live, static = core_extras(prefix, vset, cands, camp)
        sections.append({"title": f"{title} — live extras (vary across campaign)",
                         "intro": f"`{prefix}.*` keys observed changing turn-to-turn and not in save-editor maps. Scene-beat flags (`TurnNN`, `Prologue`) excluded — see story-gating section.",
                         "columns": ["Key", "Evidence"], "rows": live})
        sections.append({"title": f"{title} — static state (cheat-relevant segments)",
                         "intro": f"`{prefix}.*` keys constant across mined campaigns but in cheat-relevant areas (resources, policy, endings, unrest, war). Scene-outcome flags excluded.",
                         "columns": ["Key", "Evidence"], "rows": static})

    gc_rows = []
    for k in sorted(k for k in uni if k.startswith("GameCondition.")):
        mark = "flips mid-campaign" if (k in set_s or k in set_r) else "static"
        gc_rows.append([k, f"story-gate flag ({mark}); true once beat available/completed — effect unconfirmed"])
    sections.append({"title": "Story gating — GameCondition.*",
                     "intro": "Scene/beat availability flags. Useful for content modding and diagnosing stuck beats; not cheat levers.",
                     "columns": ["Key", "Evidence"], "rows": gc_rows})

    sh_rows = []
    for k in sorted(k for k in uni if k.startswith("SharedSupport.")):
        if ".Codex_" in k:
            note = "codex unlock flag (collectible cheat candidate)"
        elif ".News_" in k:
            note = "news/world-state mirror (read-only effect)"
        else:
            note = "shared world-state flag"
        sh_rows.append([k, note])
    sections.append({"title": "World mirrors — SharedSupport.*",
                     "intro": "Cross-pack codex unlocks and global news flags. Mirrors of consequences, not levers (except codex completion).",
                     "columns": ["Key", "Evidence"], "rows": sh_rows})

    only_path = HERE / "db_only.json"
    if only_path.exists():
        only = json.loads(only_path.read_text(encoding="utf-8"))
        dbt = json.loads((HERE / "db_variables.json").read_text(encoding="utf-8")) if (HERE / "db_variables.json").exists() else {}
        dbo_rows = []
        for k in sorted(only):
            e = dbt.get(k, {})
            note = "in current DB, never in saves (unencountered branch content)"
            if e.get("desc"):
                note += "; " + e["desc"]
            if e.get("initial") not in (None, ""):
                note += f" (init {e['initial']})"
            dbo_rows.append([k, note])
        sections.append({"title": "Database-only (never observed in saves)",
                         "intro": "Keys present in the current content database but in none of the 71 mined saves: alternate-branch outcomes (mostly Rizia Turn10 variants) and pre-unlocked codex lore.",
                         "columns": ["Key", "Evidence"], "rows": dbo_rows})

    total = sum(len(s["rows"]) for s in sections)
    out = {"source": "mined saves 2026-09-14 (71 saves, 12949 keys); generator: Utils/build_extras.py",
           "sections": sections}
    dst = REPO / "Utils" / "api_extras.json"
    dst.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"wrote {dst}: {len(sections)} sections, {total} rows")
    for s in sections:
        print(f"  {s['title']}: {len(s['rows'])}")


if __name__ == "__main__":
    main()
