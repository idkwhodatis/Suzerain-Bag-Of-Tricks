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
             "Dinner", "TBD"}
TURN_SEG = {"Turn01", "Turn02", "Turn03", "Turn04", "Turn05", "Turn06",
            "Turn07", "Turn08", "Turn09", "Turn10", "Turn11"}
HUB_JUNK = {"TalkWith", "HouseGathering_Default_Conversation", "Listened",
            "_Hub_Option", "EPA_Hub_", "Debate_Enable_", "VictoryDay_ChoiceHub_",
            "BergiaMeetingJPA_", "BludishRightsMeeting_", "HealthBudget_", "FCAnrica"}
STATIC_DENY = {"Turn01", "Turn02", "Turn03", "Turn04", "Turn05", "Turn06",
               "Turn07", "Turn08", "Turn09", "Turn10", "Turn11",
               "Dinner", "TBD"}
STATIC_JUNK = {"BaseGame.NewVariable", "RiziaDLCSupport.NewVariable_01",
               "RiziaDLC.sds", "BaseGameSupport.Jou",
               "BaseGame.Shown_MiddleFinger_ToQueen",
               "RiziaDLC.Shown_MiddleFinger_ToQueen",
               "BaseGame.Summary_Title", "RiziaDLC.Summary_Title"}


def seg_of(key):
    return key.split(".")[1].split("_")[0] if "." in key else ""


THEME_ORDER = ["Money & Resources", "Economy", "Opinion & Relations",
               "Votes & Reform", "Factions", "Decrees & Bills",
               "Diplomacy & Foreign Policy", "Military & War", "Law & Order",
               "Decisions & Enactments", "Situations", "Story & Endings",
               "Characters & Houses", "Other"]

SEG_THEME = {
    "Resources": "Money & Resources", "ResourcesExtra": "Money & Resources",
    "Budget": "Money & Resources", "Authority": "Money & Resources",
    "Energy": "Money & Resources", "PersonalWealth": "Money & Resources",
    "GovernmentBudget": "Money & Resources",
    "ModifierCountryStat": "Money & Resources",
    "Sordland": "Money & Resources",
    "Economy": "Economy", "EconomyAction": "Economy",
    "EconomicDirection": "Economy", "EconomicReliance": "Economy",
    "Gasom": "Economy", "MITZ": "Economy",
    "Rizia": "Money & Resources",
    "Relations": "Opinion & Relations", "Country": "Opinion & Relations",
    "Reform": "Votes & Reform", "Amendment": "Votes & Reform",
    "Council": "Votes & Reform", "HouseOfDelegates": "Votes & Reform",
    "HouseElections": "Votes & Reform", "HODElection": "Votes & Reform",
    "RNCElection": "Votes & Reform", "RPPElection": "Votes & Reform",
    "Faction": "Factions",
    "Bill": "Decrees & Bills", "Decrees": "Decrees & Bills",
    "RoyalDecrees": "Decrees & Bills",
    "Diplomacy": "Diplomacy & Foreign Policy",
    "CountryRelation": "Diplomacy & Foreign Policy",
    "Army": "Military & War",
    "Manpower": "Military & War", "Equipment": "Military & War",
    "Tank": "Military & War", "Ship": "Military & War",
    "Submarines": "Military & War", "BomberPlane": "Military & War",
    "FighterPlane": "Military & War",
    "Law": "Law & Order", "Order": "Law & Order", "Security": "Law & Order",
    "LeakedScandal": "Law & Order", "Leaker": "Law & Order",
    "Executions": "Law & Order", "Incident": "Law & Order",
    "Sabotage": "Law & Order", "RescueSpy": "Law & Order",
    "Decision": "Decisions & Enactments", "Enable": "Decisions & Enactments",
    "Promise": "Decisions & Enactments", "Policy": "Decisions & Enactments",
    "Focus": "Decisions & Enactments", "Decisions": "Decisions & Enactments",
    "BFF": "Factions", "NewParty": "Votes & Reform",
    "JoinParty": "Votes & Reform", "CouncilPetition": "Votes & Reform",
    "BergiaSpecialZone": "Decrees & Bills",
    "Production": "Military & War", "Hubertus": "Characters & Houses",
    "ReparationsAccepted": "Diplomacy & Foreign Policy",
    "Protests": "Situations",
    "Situation": "Situations", "Unrest": "Situations", "NoUnrest": "Situations",
    "Ending": "Story & Endings", "Epilogue": "Story & Endings",
    "Prologue": "Story & Endings",
    "Retirement": "Story & Endings", "Exile": "Story & Endings",
    "Resigned": "Story & Endings", "Joined": "Story & Endings",
    "Prologue": "Story & Endings", "Coup": "Story & Endings",
    "LateGameCoup": "Story & Endings", "NewGov": "Story & Endings",
    "Birthday": "Story & Endings", "BirthdayGathering": "Story & Endings",
    "Theocracy": "Story & Endings", "Successor": "Story & Endings",
    "Title": "Story & Endings", "Coronation": "Story & Endings",
    "Path": "Story & Endings", "NatDes": "Story & Endings",
    "Revolution": "Story & Endings", "Marriage": "Story & Endings",
    "Vina": "Characters & Houses", "Lucita": "Characters & Houses",
    "Hugo": "Characters & Houses", "Manus": "Characters & Houses",
    "Axel": "Characters & Houses", "Rico": "Characters & Houses",
    "Sal": "Characters & Houses", "Titus": "Characters & Houses",
    "Pabel": "Characters & Houses", "Angelica": "Characters & Houses",
    "Carlos": "Characters & Houses", "Daria": "Characters & Houses",
    "Estela": "Characters & Houses", "Leona": "Characters & Houses",
    "Adarfo": "Characters & Houses", "BrunoDog": "Characters & Houses",
    "Archetype": "Characters & Houses", "Marcel": "Characters & Houses",
    "Petr": "Characters & Houses", "Soll": "Characters & Houses",
    "TarquinSoll": "Characters & Houses", "Rusty": "Characters & Houses",
    "Taddeus": "Characters & Houses", "Son": "Characters & Houses",
}

SUB_RULES = [
    ("Alliance", "Diplomacy & Foreign Policy"),
    ("TradeDeal", "Diplomacy & Foreign Policy"),
    ("Sanction", "Diplomacy & Foreign Policy"),
    ("Pipeline", "Diplomacy & Foreign Policy"),
    ("Opinion", "Opinion & Relations"),
    ("Vote", "Votes & Reform"),
    ("Election", "Votes & Reform"),
    ("Corruption", "Law & Order"),
    ("Crime", "Law & Order"),
    ("USP", "Factions"), ("NFP", "Factions"), ("PFJP", "Factions"),
    ("Oligarch", "Factions"), ("OldGuard", "Factions"),
    ("Reformist", "Factions"),
    ("Policy_Economy", "Economy"), ("Economy", "Economy"),
    ("Trade", "Economy"),
    ("Policy_Diplomacy", "Diplomacy & Foreign Policy"),
    ("Policy_Law", "Law & Order"), ("Policy_Order", "Law & Order"),
    ("Policy_Military", "Military & War"),
    ("Defence", "Military & War"), ("Offence", "Military & War"),
    ("Blitzkrieg", "Military & War"), ("Pincer", "Military & War"),
    ("Military", "Military & War"), ("War", "Military & War"),
    ("Vina", "Characters & Houses"),
    ("Pales", "Diplomacy & Foreign Policy"),
    ("Morella", "Diplomacy & Foreign Policy"),
    ("Zille", "Diplomacy & Foreign Policy"),
    ("Derdia", "Diplomacy & Foreign Policy"),
    ("Agnolia", "Diplomacy & Foreign Policy"),
    ("Wehlen", "Diplomacy & Foreign Policy"),
    ("Lespia", "Diplomacy & Foreign Policy"),
    ("Valgsland", "Diplomacy & Foreign Policy"),
    ("Rumburg", "Diplomacy & Foreign Policy"),
    ("ATO", "Diplomacy & Foreign Policy"),
    ("CSP", "Diplomacy & Foreign Policy"),
    ("Coup", "Story & Endings"),
    ("Revolution", "Story & Endings"),
]


def theme_of(key):
    for sub, theme in SUB_RULES:
        if sub in key:
            return theme
    return SEG_THEME.get(seg_of(key), "Other")




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
            elif seg_of(k) not in STATIC_DENY and k not in STATIC_JUNK:
                types = "/".join(uni[k]["types"])
                samp = uni[k]["samples"][0] if uni[k]["samples"] else "?"
                note = f"static ({types}={samp!r}, n={uni[k]['nsaves']} saves); outcome record — set before the scene or edit saves"
                static.append([k, note])
        return live, static

    for title, prefix, vset, cands, camp, slug in [
        ("Sordland", "BaseGame", set_s, cand_s, "Sordland 3.1.0.1.153", "sordland"),
        ("Rizia", "RiziaDLC", set_r, cand_r, "Rizia 3.1.0.1.137", "rizia"),
    ]:
        live, static = core_extras(prefix, vset, cands, camp)
        buckets = {t: [] for t in THEME_ORDER}
        for k, note in live + static:
            buckets[theme_of(k)].append([k, note])
        for theme in THEME_ORDER:
            rows = buckets[theme]
            if not rows:
                continue
            sections.append({"title": f"{title} — {theme}",
                             "pack": slug,
                             "intro": f"`{prefix}.*` keys not in save-editor maps, grouped by theme. Evidence notes preserve live-vs-static provenance from save mining.",
                             "columns": ["Key", "Evidence"], "rows": rows})

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

    vote_rows = []
    for k in sorted(uni):
        if "Isolated." in k and re.search(r"Vote|Petition|Count|Election", k):
            types = "/".join(uni[k]["types"])
            samp = uni[k]["samples"][0] if uni[k]["samples"] else "?"
            vote_rows.append([k, f"vote-counter flag ({types}={samp!r}); election-rigging candidate"])
    sections.append({"title": "Vote counters (Isolated, election-rigging candidates)",
                     "intro": "Per-bloc vote counters and petition counts normally accumulated during election fragments. Setting them pre-results rigs the outcome.",
                     "columns": ["Key", "Evidence"], "rows": vote_rows})

    war_rows = []
    for k in sorted(uni):
        if k.startswith("RiziaDLCSetup.War_"):
            types = "/".join(uni[k]["types"])
            samp = uni[k]["samples"][0] if uni[k]["samples"] else "?"
            war_rows.append([k, f"war deployment override ({types}={samp!r}); pre-war setup lever"])
    sections.append({"title": "War setup overrides (RiziaDLCSetup.War_*)",
                     "intro": "Deployment overrides consumed by the war system. Set before war fragments.",
                     "columns": ["Key", "Evidence"], "rows": war_rows})

    pp_rows = []
    for k in sorted(uni):
        if k.startswith("BaseGameUI.PresidentialPower_"):
            types = "/".join(uni[k]["types"])
            samp = uni[k]["samples"][0] if uni[k]["samples"] else "?"
            pp_rows.append([k, f"presidential-decree availability condition ({types}={samp!r})"])
    sections.append({"title": "Decree availability (BaseGameUI.PresidentialPower_*)",
                     "intro": "Conditions gating presidential-decree options in the UI. Flip to unlock decrees.",
                     "columns": ["Key", "Evidence"], "rows": pp_rows})

    for pack_title, iso_prefix, slug in [("Sordland", "BaseGameIsolated", "sordland"),
                                         ("Rizia", "RiziaDLCIsolated", "rizia")]:
        iso_rows = []
        for k in sorted(uni):
            if not k.startswith(iso_prefix + "."):
                continue
            if seg_of(k) in TURN_SEG:
                continue
            if any(j in k for j in HUB_JUNK):
                continue
            if re.search(r"Vote|Voting|Petition|Count|Election|DraftHub", k):
                continue
            types = "/".join(uni[k]["types"])
            samp = uni[k]["samples"][0] if uni[k]["samples"] else "?"
            iso_rows.append([k, f"story-path flag ({types}={samp!r}, n={uni[k]['nsaves']} saves); hub-navigation excluded"])
        sections.append({"title": f"{pack_title} story-path flags ({iso_prefix}, no hub-nav)",
                         "pack": slug,
                         "intro": f"`{iso_prefix}.*` choice/outcome records: reform intentions, investigations, coup/revolution paths, endings. Turn-beat micro-flags, hub-navigation and vote counters excluded (see gating/vote sections).",
                         "columns": ["Key", "Evidence"], "rows": iso_rows})

    con_rows = []
    for k in sorted(uni):
        if ".Reports_Construction_" in k:
            types = "/".join(uni[k]["types"])
            samp = uni[k]["samples"][0] if uni[k]["samples"] else "?"
            con_rows.append([k, f"construction project state ({types}={samp!r}); project-progress lever"])
    sections.append({"title": "Rizia construction reports (Reports_Construction_*)",
                     "pack": "rizia",
                     "intro": "Per-project construction completion states. Flip to fast-track projects.",
                     "columns": ["Key", "Evidence"], "rows": con_rows})

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
