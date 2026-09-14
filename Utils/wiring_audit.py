"""Wiring audit: every save-editor GROUP field verified against game logic.

For each GROUP field: resolve Lua key(s) via FIELD_MAP (+ groups.json pair
expansion), then verdict per key from dialogue refs (triggers.json), live
menu presence (livedump_analysis.json), DB presence (db_variables.json),
save variance (analysis.json).
Verdicts: WIRED-content / WIRED-engine / DORMANT / STALE / MISMATCH.
Writes: GameDump/3.1.0.1.175/mining/wiring_audit.json (gitignored).
Usage: & "<save-editor>/venv/Scripts/python.exe" Utils/wiring_audit.py
"""
import ast
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
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
MAPS = {**ns["FIELD_MAP_SORDLAND"], **ns["FIELD_MAP_RIZIA"]}
GROUPS = {"sordland": {"field_map": ns["FIELD_MAP_SORDLAND"], "group": ns["GROUP_SORDLAND"]},
          "rizia": {"field_map": ns["FIELD_MAP_RIZIA"], "group": ns["GROUP_RIZIA"]}}
COMPOSITES = {
    "blackTuesday": ["_blackTuesday", "_marketsCrash"],
    "superpowerTradeWar": ["_superpowerTradeWar", "_globalTradeWar"],
    "employment": ["_highEmployment", "_unemploymentCrisis"],
    "trade": ["_increasedTrade", "_decreasedTrade"],
    "tax": ["_taxEfficientEconomy", "_taxAvoidance", "_taxEvasion"],
    "transportation": ["_improvedTransportation", "_weakTransportation"],
    "tourism": ["_tourismBooming", "_tourismAverage", "_tourismDeclining"],
    "situationAgnland": ["_agnlandMajorFishExport", "_agnlandEconomicStabilisation", "_agnlandLackInvestment"],
    "situationBergia": ["_bergiaMajorAgriculturalZone", "_bergiaEconomicStabilisation", "_bergiaEconomicDownturn"],
    "situationGruni": ["_gruniLightTowerRegion", "_gruniMaintainingGrowth", "_gruniLaggingBehind"],
    "situationLorren": ["_lorrenProductionAndTradeCenter", "_lorrenEconomicStabilisation", "_lorrenRustBelt"],
    "deanaLoved": ["_deanaLoved", "_deanaOpinion"],
    "ewaldOpinion": ["_ewaldDiscontent", "_ewaldNeutral", "_ewaldFriendly"],
    "partyElectionResult": ["_partyElectionWon", "_partyElectionLost", "_partyElectionNewParty"],
    "sordishRadioTVCouncilStatus": ["_sordishRadioTVCouncil", "_sordishRadioTVCouncilControlled", "_sordishRadioTVCouncilIndependent"],
    "operationBearTrap": ["_wehlenDefendBorder", "_wehlenJointOperation"],
    "agnoliaTradeDeal": ["_agnoliaTradeDeal", "_agnoliaTrade"],
    "agnoliaAlliance": ["_agnoliaAlliance", "_policyAgnoliaAlliance"],
    "wehlenTradeDeal": ["_wehlenTradeDeal", "_wehlenTrade"],
    "wehlenAlliance": [],
    "lespiaAlliance": ["_lespiaAlliance", "_policyLespiaAlliance"],
    "valgslandAlliance": ["_valgslandAlliance", "_policyValgslandAlliance"],
    "ATO": ["_ATO", "_ATOArea"],
    "CSP": ["_CSP", "_CSPArea"],
    "modernisedArmy": ["_modernisedArmy", "_modernisationArmy"],
    "expandedArmy": ["_expandedArmy", "_expansionArmy"],
    "modernisedNavy": ["_modernisedNavy", "_modernisationNavy"],
    "expandedNavy": ["_expandedNavy", "_expansionNavy"],
    "modernisedAirForce": ["_modernisedAirForce", "_modernisationAirForce"],
    "expandedAirForce": ["_expandedAirForce", "_expansionAirForce"],
    "rumburgWarWin": ["_SnORumburgWarWin", "_SnORumburgWarLost"],
    "courtStatus": ["_courtBacklog", "_efficientJusticeSystem"],
    "womenRights": ["_limitedWomenRights", "_averageWomenRights", "_excellentWomenRights"],
    "corruption": ["_corruption", "_corruptionTackled"],
    "crime": ["_organisedCrime", "_organisedCrimeContained"],
    "vesordRumbergNavy": ["_vesordRumburgNavyInferior", "_vesordRumburgNavySuperior"],
}
TOG = json.loads((REPO / "Utils" / "groups.json").read_text(encoding="utf-8"))["groups"]
PAIR_OF = {}
for g in TOG:
    mem = list(g.get("members", []))
    for opts in g.get("options", {}).values():
        mem += opts
    for k in mem:
        PAIR_OF.setdefault(k, []).append(g["name"])
TRIG = json.loads((MINING / "triggers.json").read_text(encoding="utf-8"))
DB = json.loads((MINING / "db_variables.json").read_text(encoding="utf-8"))
ANA = json.loads((MINING / "analysis.json").read_text(encoding="utf-8"))
VARY = set(ANA["campaigns"]["sordland_3.1.0.1.153"]["allVarying"]) | set(
    ANA["campaigns"]["rizia_3.1.0.1.137"]["allVarying"])
ABSENT = set(json.loads((MINING.parent / "livedump_analysis.json").read_text(encoding="utf-8"))["absent"])


def verdict(key):
    if key.startswith("MISSING-FIELD_MAP:"):
        return "MISMATCH"
    t = TRIG.get(key, {})
    if t.get("nwrites", 0) + t.get("nconds", 0) > 0:
        return "WIRED-content"
    if key not in DB:
        return "STALE"
    if key not in VARY and key in ABSENT:
        return "DORMANT"
    return "WIRED-engine"


out = {}
for pack, spec in GROUPS.items():
    out[pack] = {}
    for group, fields in spec["group"].items():
        rows = []
        for f in fields:
            members = set()
            if f in MAPS:
                members.add(MAPS[f])
            elif "_" + f in MAPS:
                members.add(MAPS["_" + f])
            for m in COMPOSITES.get(f, []):
                if m in MAPS:
                    members.add(MAPS[m])
                else:
                    members.add("MISSING-FIELD_MAP:" + m)
            if not members:
                rows.append({"field": f, "keys": [], "verdicts": ["MISMATCH-no-FIELD_MAP-entry"]})
                continue
            for g in TOG:
                gm = list(g.get("members", [])) + [x for o in g.get("options", {}).values() for x in o]
                if members & set(gm):
                    members.update(gm)
            members = sorted(members)
            rows.append({"field": f, "keys": members, "verdicts": [verdict(k) for k in members]})
        out[pack][group] = rows

json.dump(out, open(MINING / "wiring_audit.json", "w"), indent=1)
from collections import Counter
c = Counter()
bad = []
for pack, gs in out.items():
    for group, rows in gs.items():
        for r in rows:
            for k, v in zip(r["keys"], r["verdicts"]):
                c[v] += 1
                if v in ("STALE", "DORMANT", "MISMATCH-no-FIELD_MAP-entry"):
                    bad.append((pack, group, r["field"], k, v))
print("verdicts:", dict(c.most_common()))
print(f"flagged: {len(bad)}")
for b in bad:
    print("  ", b)
print("wrote mining/wiring_audit.json")
