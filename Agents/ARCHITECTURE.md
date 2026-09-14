# ARCHITECTURE

## Game (read-only dependency, never committed)

- Location: `G:\SteamLibrary\steamapps\common\Suzerain`
- Unity 6 + IL2CPP: `Suzerain.exe`, `GameAssembly.dll`,
  `Suzerain_Data/il2cpp_data/Metadata/global-metadata.dat`,
  `Suzerain_Data/ScriptingAssemblies.json`, `boot.config`, `app.info`.
- Variable state: PixelCrushers Dialogue System `DialogueLua` over
  `Language.Lua` VM (`LuaTable`/`LuaString`/`LuaNumber`/`LuaBoolean`,
  `LuaInterpreter`). Global table `Variable`; save `variables` string is its
  serialization (`Utils/Parser.py` regex documents the format).

## Loader stack

- MelonLoader (native host for IL2CPP) + Suzerain Modding Kit DLL in
  `Suzerain/Mods/`. SMK provides `Variables`, `GameState`,
  `DecisionManager`, `Events` (e.g. `OnEvaluateStep`, `OnDecisionShow`,
  `OnDecisionFinished`), `SuzerainStoryPackInfo`, vanilla-data helpers,
  and the Ctrl+D debug overlay.
- Prereqs (Windows): VC++ 2015-2019 x64, .NET Desktop Runtime 6.0.x,
  MelonLoader installer pointed at Suzerain, one launch to generate files.
- SMK is beta (`era.release`, either component may break on game updates).
  Never mix with BepInEx/SuzerainUnbound in the same install.

## Repo layout

```text
Agents/                 agent docs (index = Agents.md) + API.md catalog
src/                    MelonMod source (BagOfTricks.csproj,Core,Dump,CheatMenu,Keys; net6.0 x64)
Utils/                  research pipeline scripts + metadump/ tool
GameDump/<gamever>/    GITIGNORED local copies: notes,mining JSON,codestrings
```

## Dump-dir policy

- `GameDump/` is gitignored. Subdir per installed game `version`, e.g.
  `GameDump/3.1.0.1.175/`. Contents: small identifying game files (copied),
  `notes.md` (version stamp + findings log), `mining/` (pipeline JSON),
  `codestrings/ALL.txt` (game-assembly `#US` heap via `Utils/metadump`).
- Large binaries (`GameAssembly.dll`,`global-metadata.dat`,`data.unity3d`)
  are never copied — read in place, SHA256 recorded in `notes.md`.
  MelonLoader dummy assemblies stay in the game dir.
- Regen: create dir, copy small files, run `Utils/` pipeline (see
  RESEARCH.md §7), run `Utils/metadump strings`, distill into `Agents/API.md`.
- Rationale: game files are large, versioned, and copyrighted; keeps the
  repo clean and avoids accidental distribution of decompiled code.
- No per-directory READMEs anywhere: all guidance lives in `Agents/` docs
  (this file + RESEARCH.md + IMPLEMENTATION.md) and the root `README.md`.

## Mod design (v0.1)

- `Core : MelonMod.OnInitializeMelon`: log init, register menu + presets.
- Menu: immediate-mode overlay (Unity IMGUI or SMK overlay hooks);
  search box (prefix filter), typed rows (int field / bool toggle),
  apply-on-confirm, preset buttons (MaxMoney, MaxRizia).
- State access only through `SMK.Variables.Get*/Set`; guard calls by
  `GameState` (story pack / turn) where behavior differs Sordland vs Rizia.
- No raw Harmony patches in v0.1; isolate any future patches behind a flag.
