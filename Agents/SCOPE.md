# SCOPE — BagOfTricks v0.1

## In scope

1. **Live cheat menu** (MelonMod overlay)
   - Browse/search live variables by prefix (`BaseGame.`, `RiziaDLC.`,
     `GameCondition.`, `BaseGameIsolated.`, `BaseGameSupport.`).
   - Get/set int + bool at minimum (float/string if trivial via SMK API).
   - Presets: MaxMoney (Sordland budget/wealth to `*_Max`, mirrors
     `Parser.maxMoney` in save-editor), MaxRizia (budget/authority/energy).
   - Read-only safe by default: edits only on explicit user action.

2. **Variable research catalog**
   - `Agents/API.md`: key, friendly field, effect/group, per UI group.
   - Seed from save-editor `FIELD_MAP_SORDLAND` / `FIELD_MAP_RIZIA`;
     extend with keys discovered via dump + in-game overlay.
   - Unknown-key log from play sessions feeds the catalog.

## Out of scope (v0.1)

- Custom story content (decisions/bills/reports) via SMK fragment APIs.
- Save-file editing (save-editor already covers that; refresh it separately).
- BepInEx / SuzerainUnbound support (incompatible with MelonLoader/SMK).
- macOS support (SMK: Windows + Linux/Proton only, Steam only).
- Asset mods, localization, multiplayer/cloud-save features.

## Acceptance criteria

- Fresh checkout + doc steps → Release DLL in `Suzerain/Mods/` → F10
  overlay opens in-game, lists live vars, set + preset actions visibly change
  HUD/state; F9 dump writes all catalog keys with live values.
- `API.md` covers at least the save-editor key set with
  types confirmed against the pinned game version.
- Repo contains zero game binaries / decompiled game code (`GameDump/`
  gitignored, verified via `git status`).
