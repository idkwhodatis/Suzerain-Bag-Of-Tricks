# Suzerain BagOfTricks — Agent Index

Read this file first. Detailed topics live in sibling files; this index is the
entry point, not a duplicate of them.

- `SCOPE.md` — what v0.1 is / is not (live cheat menu + variable research).
- `ARCHITECTURE.md` — game + loader + repo layout + dump-dir policy.
- `IMPLEMENTATION.md` — phased build order (P0 scaffold → P1 verify+dumps → P2 mod).
- `RESEARCH.md` — decompile + variable-catalog workflow (Cpp2IL, SMK overlay).

`API.md` (this folder) is the living variable catalog (what each key does);
`Utils/gen_api.py` regenerates it from save-editor maps.

## What it is

Live in-game cheat/research mod for Suzerain (Torpor Games, Steam-only).
v0.1: in-game overlay to browse + set live `BaseGame.*` / `RiziaDLC.*`
variables, plus a per-version researched variable catalog. Reuses key maps
from `Suzerain-Save-Editor`. Does not edit saves on disk.

## Ground facts (verified 2026-09-14)

- Game install: `G:\SteamLibrary\steamapps\common\Suzerain`
- Unity 6 + IL2CPP: `GameAssembly.dll` (~75MB), no `Managed/` folder,
  `Suzerain_Data/il2cpp_data/Metadata/global-metadata.dat` (~17MB).
  Assembly list in `Suzerain_Data/ScriptingAssemblies.json`
  (`Assembly-CSharp.dll`, etc. — metadata names only, compiled to native).
- Consequence: plain Unity Mod Manager Mono/Assembly path does not apply.
  Stack is **MelonLoader + Suzerain Modding Kit (SMK, beta)**.
- Reference repo: `C:\Users\GLENN\Documents\git repos\Suzerain-Save-Editor`
  (`Utils/Consts.py` FIELD_MAP_*, `Utils/Parser.py` variables-string regex).
- Data model: PixelCrushers Dialogue System + `Language.Lua` VM; globals in
  `Variable` LuaTable (`LuaString` → `LuaNumber`/`LuaBoolean`/`LuaString`);
  ~428 numeric vars in a typical campaign.
- Toolchain present: `dotnet` SDKs incl. 6.0.x (matches MelonLoader .NET 6
  requirement). IDE: Visual Studio 2022+.

## Conventions for agents

- C# (.NET 6, x64). VS2022 + ".NET desktop development" + MelonLoader VS
  Wizard template. Debug = dev, Release = publish.
- All game-copy / decompiler output goes under `GameDump/<gamever>/`
  (gitignored, local-only). Never commit game binaries or full decompiled
  sources. Commit only: our code, Utils, src, and `API.md`.
- Game version = save `version` field + Steam build (e.g. `3.1.0.1.153`).
  Pin SMK + game version in docs; both SMK `era.release` components may break.
- Back up saves before in-game tests:
  `%LOCALAPPDATA%Low\Torpor Games\Suzerain`.
- SMK install check: launch to main menu, Ctrl+D shows debug overlay
  ("GameFlowManager not loaded!" in menu is normal).
- Keep docs DRY: index here,details in topic files. Update the topic file,
  not this one,when behavior changes.

## Programming Guardrails

### Format Guideline

* Ignore all non-needed spaces,such as after colon,comma,or any space that will not break compile and run.
* Spaces for the previous rule are exempt for code block indentation. Use strict indentation in code blocks,like Python. Use 4 spaces for indentation.
* Use `UpperPascalCase` for classes and filenames.
* Use `lowerPascalCase` for variables,functions,and methods when possible.
* For terms like `CPU`,`ID`,`API`,`URL`,`HTTP`,`JSON`,keep the acronym fully capitalized when possible.
* Keep formatting consistent with nearby code when modifying existing files.

### Naming

Prefer names that describe product concepts clearly.

Good:

```text
ProfileMemory
PersonalityTrait
CandidateMemory
DailyRecommendation
AssessmentResult
ProfileSeed
RecommendationFeedback
CoreConnection
CoreCapability
CoreHealth
BotAdapter
IntegrationPlugin
AdminDashboard
AdminSettings
ServerSettings
```

Avoid vague names:

```text
Data
Info
Thing
Manager
Helper
Stuff
```

### Function behavior

Functions should do one clear thing.

Prefer small,composable functions over large mixed-responsibility functions.

Avoid functions that both:

* generate AI output
* mutate profile memory
* update personality traits
* write recommendation feedback
* render UI
