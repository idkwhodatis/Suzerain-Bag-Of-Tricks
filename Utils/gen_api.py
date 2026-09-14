"""Generate ../Agents/API.md variable catalog from Suzerain-Save-Editor Utils/Consts.py.

Usage (pwsh, from repo root):
  & "<save-editor>/venv/Scripts/python.exe" Utils/gen_api.py \
      --src "C:/Users/GLENN/Documents/git repos/Suzerain-Save-Editor/Utils/Consts.py"

Output: <repo>/API.md (UTF-8). Do not hand-edit the tables in API.md;
re-run this script after editing the source maps (Consts.py) or the mined
extras (Utils/api_extras.json).
"""
import argparse
import ast
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_SRC = Path(r"C:\Users\GLENN\Documents\git repos\Suzerain-Save-Editor\Utils\Consts.py")


def load_consts(src: Path) -> dict:
    tree = ast.parse(src.read_text(encoding="utf-8"))
    ns = {}
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            try:
                ns[node.targets[0].id] = ast.literal_eval(node.value)
            except Exception:
                pass  # non-literal (e.g. STORY_PACK references) — skip
    return ns


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(DEFAULT_SRC))
    ap.add_argument("--dst", default=str(REPO / "Agents" / "API.md"))
    args = ap.parse_args()

    ns = load_consts(Path(args.src))
    packs = [
        ("Sordland", ns["FIELD_MAP_SORDLAND"], ns["GROUP_SORDLAND"], "sordland"),
        ("Rizia", ns["FIELD_MAP_RIZIA"], ns["GROUP_RIZIA"], "rizia"),
    ]
    extras = {"sections": []}
    if (REPO / "Utils" / "api_extras.json").exists():
        extras = json.loads((REPO / "Utils" / "api_extras.json").read_text(encoding="utf-8"))

    def render_extras_section(sec):
        out.append(f"### {sec['title']}")
        out.append("")
        out.append(sec["intro"])
        out.append("")
        cols = sec["columns"]
        out.append("| " + " | ".join(cols) + " |")
        out.append("|" + "|".join(["---"] * len(cols)) + "|")
        for row in sec["rows"]:
            cells = [f"`{c}`" if i == 0 else str(c) for i, c in enumerate(row)]
            if len(cells) > 1:
                cells[1] = cells[1] + db_note(row[0]) + trig_note(row[0])
            out.append("| " + " | ".join(cells) + " |")
        out.append("")

    out = []
    out.append("# API \u2014 Suzerain variable catalog")
    out.append("")
    out.append("What each live/save variable key does. Keys are the in-game Lua variable")
    out.append("names (`BaseGame.*`, `RiziaDLC.*`, \u2026); `Field` is the friendly name used")
    out.append("by `Suzerain-Save-Editor` and (planned) `BagOfTricks` presets.")
    out.append("")
    out.append("> Source: `Suzerain-Save-Editor/Utils/Consts.py` (auto-generated \u2014 do not")
    out.append("> hand-edit tables; re-run `Utils/gen_api.py` after changing the source).")
    out.append("> Status: UNCONFIRMED against live game \u2014 save-editor maps are")
    out.append("> ~1yr old and mined saves are .153/.137-era while installed game is")
    out.append("> 3.1.0.1.175. Confirm each key live via `Agents/RESEARCH.md` before")
    out.append("> relying on it. Installed game: 3.1.0.1.175 (Steam build 23568265).")
    out.append("> Mechanism CONFIRMED against .175 dummy assemblies: `DialogueLua`.")
    out.append("> `GetVariable`/`SetVariable`, `LuaTable.Dict`, `LuaNumber.Number: double`.")
    out.append("")
    out.append("Legend: `_field` (leading underscore) = internal/derived flag, not a")
    out.append("direct HUD stat. `\u2014` in Key = composite UI field (see")
    out.append("`Models/Sordland.py` / `Models/Rizia.py` in save-editor), not a raw key.")
    out.append("Roles (from dialogue write/read sites + campaign variance): `store` = core")
    out.append("read-write state; `trigger` = one-shot event flag; `lever` = enactment flag;")
    out.append("`mirror` = engine-written, varies; `gate` = read-only branch input;")
    out.append("`record` = written, never branched on; `const` = static clamp/sentinel;")
    out.append("`dormant` = static, unreferenced (rare-branch or dead).")
    out.append("")

    togroups = []
    groups_path = REPO / "Utils" / "groups.json"
    if groups_path.exists():
        togroups = json.loads(groups_path.read_text(encoding="utf-8"))["groups"]
    group_of = {}
    for g in togroups:
        members = list(g.get("members", []))
        for opts in g.get("options", {}).values():
            members += opts
        for k in members:
            group_of.setdefault(k, []).append(g["name"] + "(" + g["kind"] + ")")

    def group_note(key):
        gs = group_of.get(key)
        return " Group:" + ",".join(gs) if gs else ""
    db_path = REPO / "GameDump" / "3.1.0.1.175" / "mining" / "db_variables.json"
    db = json.loads(db_path.read_text(encoding="utf-8")) if db_path.exists() else {}
    n_db = 0
    trig_path = REPO / "GameDump" / "3.1.0.1.175" / "mining" / "triggers.json"
    trig = json.loads(trig_path.read_text(encoding="utf-8")) if trig_path.exists() else {}
    n_trig = 0

    def clean(s):
        return str(s).replace("|", "/").replace("\n", " ")

    def db_note(key):
        nonlocal n_db
        e = db.get(key)
        if not e:
            return ""
        n_db += 1
        parts = []
        if e.get("desc"):
            parts.append(clean(e["desc"]))
        if e.get("initial") not in (None, ""):
            parts.append("init " + clean(e["initial"]))
        return " DB: " + "; ".join(parts) if parts else ""

    def trig_note(key):
        nonlocal n_trig
        t = trig.get(key)
        if not t:
            return ""
        n_trig += 1
        bits = [f"{t['nwrites']}W/{t['nconds']}C"]
        if t["writes"]:
            bits.append("set:" + clean(t["writes"][0]))
        if t["condConvs"]:
            bits.append("gates:" + clean(t["condConvs"][0]))
        role = t.get("role", "")
        prefix = f" Role:{role}; " if role else " "
        if t["nwrites"] == 0 and t["nconds"] == 0:
            return prefix + "no content refs"
        return prefix + "Trig: " + ", ".join(bits)

    n_extra = 0
    for pack_name, field_map, groups, slug in packs:
        out.append(f"## {pack_name}")
        out.append("")
        referenced = set()
        for group_name, fields in groups.items():
            out.append(f"### {pack_name} \u2014 {group_name}")
            out.append("")
            out.append("| Field | Key | Notes |")
            out.append("|---|---|---|")
            for field in fields:
                referenced.add(field)
                key = field_map.get(field, "\u2014")
                if key == "\u2014":
                    notes = "composite/derived"
                else:
                    notes = "internal flag" if field.startswith("_") else ""
                    notes += db_note(key) + trig_note(key) + group_note(key)
                out.append(f"| `{field}` | `{key}` | {notes} |")
            out.append("")
        ungrouped = [(f, k) for f, k in field_map.items() if f not in referenced]
        if ungrouped:
            out.append(f"### {pack_name} \u2014 Ungrouped (in map, no UI group)")
            out.append("")
            out.append("| Field | Key | Notes |")
            out.append("|---|---|---|")
            for field, key in ungrouped:
                notes = "internal flag" if field.startswith("_") else ""
                notes += db_note(key) + trig_note(key) + group_note(key)
                out.append(f"| `{field}` | `{key}` | {notes} |")
            out.append("")
        for sec in extras["sections"]:
            if sec.get("pack") == slug:
                render_extras_section(sec)
                n_extra += len(sec["rows"])

    out.append("## Shared reference (cross-pack, not in save-editor maps)")
    out.append("")
    out.append("Mined extras that span story packs or belong to no pack: story gates, world mirrors, vote counters, war setup, decree UI, database-only keys.")
    out.append("")
    for sec in extras["sections"]:
        if not sec.get("pack"):
            render_extras_section(sec)
            n_extra += len(sec["rows"])

    out.append("## Modify-together groups (save-editor semantics)")
    out.append("")
    out.append("Keys that share one purpose and must be edited together. Kinds: `and` = setter writes all members to one value (getter is AND); `exclusive` = setter clears the group then sets one option; `inverse` = pair kept opposite; `compensating` = setting the total delta-adjusts the base — edit both.")
    out.append("")
    out.append("| Group | Kind | Members / Options |")
    out.append("|---|---|---|")
    for g in togroups:
        if "options" in g:
            members = "; ".join(f"{o}=[{', '.join(ks) if ks else 'none'}]" for o, ks in g["options"].items())
        else:
            members = ", ".join(f"`{k}`" for k in g["members"])
        out.append(f"| `{g['name']}` | {g['kind']} | {clean(g.get('effect', ''))}: {members} |")
    out.append("")

    out.append("## Known mapping issues (save-editor, to verify live)")
    out.append("")
    out.append("| # | Issue | Evidence |")
    out.append("|---|---|---|")
    out.append("| 1 | `resourcesAuthorityMax` maps to `Rizia_HUDStat_Budget_Max` and `resourcesBudgetMax` maps to `Rizia_HUDStat_Authority_Max` — looks swapped: cap keys read Budget_Max=20,Authority_Max=15,Energy_Max=15 while natural T1 resources are Budget 8,Authority 6,Energy 11 (each under its same-named cap) | All Rizia saves, 2026-09-14; edited saves hit 99 on all three so caps don't hard-clamp — live-confirm |")
    out.append("| 2 | `*_Min` clamp keys missing from maps (`Sordland_HUDStat_GovernmentBudget_Min=-20`, `PersonalWealth_Min=0`, Rizia `Authority/Budget/Energy_Min=0`) | Rizia T1 + Sordland saves, 2026-09-14 |")
    out.append("| 3 | `GROUP_SORDLAND` Anti Cheat lists `blackTuesday` but map key is `_blackTuesday`; same for `superpowerTradeWar`/`_superpowerTradeWar`, `employment`, `trade`, `tax`, `transportation`, `tourism` (composite/model fields, see `Models/Sordland.py`) | `Consts.py` GROUP vs FIELD_MAP diff |")
    out.append("")

    out.append("## Changelog")
    out.append("")
    out.append("| Date | Game ver | Change |")
    out.append("|---|---|---|")
    out.append("| 2026-09-14 | 3.1.0.1.153 | Seeded from save-editor `Consts.py` (ABOUT v0.2.2 era); version stamped from live save. |")
    out.append("| 2026-09-14 | 3.1.0.1.175 | DialogueDB descriptions + initials merged (`Suzerain.asset`,12828 vars,646 described); installed game corrected to .175. |")
    out.append("| 2026-09-14 | 3.1.0.1.175 | Extras reorganized save-editor-style: themed subgroups under each pack (Money,Economy,Opinion,Votes,Factions,Decrees,Diplomacy,Military,Law,Decisions,Situations,Story,Characters,Other) + shared appendices. |")
    out.append("")

    dst = Path(args.dst)
    dst.write_text("\n".join(out), encoding="utf-8")
    n_keys = sum(len(m) for _, m, _, _ in packs)
    print(f"wrote {dst} ({n_keys} mapped keys, {n_extra} extras, {n_db} db-annotated, {n_trig} trig-annotated)")

    # Self-check: every key in the maps appears in the output exactly once.
    text = dst.read_text(encoding="utf-8")
    missing = [
        k for _, m, _, _ in packs for k in m.values() if f"`{k}`" not in text
    ]
    missing += [
        r[0] for s in extras["sections"] for r in s["rows"]
        if f"`{r[0]}`" not in text
    ]
    for g in togroups:
        members = list(g.get("members", []))
        for opts in g.get("options", {}).values():
            members += opts
        for k in members:
            if f"`{k}`" not in text:
                missing.append(f"group-member:{k}")
    if missing:
        raise SystemExit(f"MISSING KEYS: {missing}")
    print("self-check ok: all mapped + extras keys present")


if __name__ == "__main__":
    main()
