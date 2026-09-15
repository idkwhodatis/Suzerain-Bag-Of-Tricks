# Suzerain BagOfTricks

Live in-game cheat/research mod for Suzerain (Torpor Games, Steam-only,
Unity 6 + IL2CPP): overlay (F10 or Ctrl+D) to browse + set live variables
with overshoot warnings, grouped modify-together widgets and presets;
Advanced section dumps all catalog keys with runtime values. Catalog +
research in `Agents/`.

## Map

- `Agents/` — all docs (start at `Agents/Agents.md`); `Agents/API.md` is the
  living variable catalog (170 save-editor keys + ~4300 mined extras).
- `src/` — MelonMod source (`BagOfTricks.csproj`,Core,Dump,CheatMenu,Keys,
  Groups,Warnings; net6.0 x64). Build: `dotnet build src -c Release -p:Platform=x64`.
- `Utils/` — research pipeline (`mine→analyze→build_extras→gen_api→
  gen_keys→drift→db/db_table/conv_mine→thresholds/triggers→groups/warnings`,
  plus `validate_api` gate) + `metadump/` metadata enumerator
  (see `Agents/RESEARCH.md`).
- `GameDump/` — gitignored local game copies + mining artifacts.

## Requirements (to use the mod)

- Suzerain 3.1.0.1.175 on Steam, MelonLoader v0.7.3, SMK v2.4 in `Mods/`
  (see `Agents/IMPLEMENTATION.md` P1; game dir untouched by this repo except
  the built `BagOfTricks.dll` PostBuild-copied to `Mods/`).
- In game: Ctrl+D toggles the menu (SMK's own debug overlay opens
  alongside it); Settings section runs the full key dump.

## Installation (alpha 0.1.0-alpha)

> Only ever install mods from sources you trust. Back up your saves first:
> `%LOCALAPPDATA%Low\Torpor Games\Suzerain`.

1. Install prereqs: [VC++ 2015-2019 x64](https://aka.ms/vs/16/release/vc_redist.x64.exe)
   and [.NET Desktop Runtime 6.0.x](https://dotnet.microsoft.com/en-us/download/dotnet/6.0).
2. Install MelonLoader: run [MelonLoader.Installer.exe](https://github.com/LavaGang/MelonLoader.Installer/releases/latest),
   select Suzerain, install. Launch the game once to the main menu, then quit
   (MelonLoader generates its folders on first launch).
3. Install SMK: download `SuzerainModdingKit.dll` from the
   [SMK releases](https://github.com/suzerain-modding/suzerain-modding-kit/releases)
   (v2.4 for game 3.1.0.1.175) into `Suzerain/Mods/`.
4. Install BagOfTricks: copy the built `BagOfTricks.dll` into `Suzerain/Mods/`
   (or `dotnet build src -c Release -p:Platform=x64` — PostBuild copies it).
5. Launch via Steam. Press Ctrl+D: SMK's debug overlay plus the BagOfTricks
   menu appear. Sordland/Rizia pages hold the save-editor-grouped cheats;
   mined extras stay hidden until Experimental is enabled in Settings.
6. To uninstall: delete `BagOfTricks.dll` from `Mods/` (leave everything else).

## Dev requirements (to build + research with `Utils/`)

- dotnet SDK 8+ (`Utils/metadump`, mod builds; net6.0 target).
- save-editor venv python for `Utils/*.py` pipeline scripts.
- UnityPy scratch venv only for the one-shot `Utils/db_dump.py` step.
- VS2022 + MelonLoader VS Wizard optional (CLI build is complete).

## License

MIT — see `LICENSE`. Unofficial community project, not affiliated with
Torpor Games.
