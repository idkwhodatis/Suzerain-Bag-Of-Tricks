# Suzerain BagOfTricks

Live in-game cheat/research mod for Suzerain (Torpor Games, Steam-only,
Unity 6 + IL2CPP): F10 overlay to browse + set live variables, F9 to dump
all catalog keys with runtime values. Catalog + research in `Agents/`.

## Map

- `Agents/` — all docs (start at `Agents/Agents.md`); `Agents/API.md` is the
  living variable catalog (170 save-editor keys + 2272 mined extras).
- `src/` — MelonMod source (`BagOfTricks.csproj`,Core,Dump,CheatMenu,Keys;
  net6.0 x64). Build: `dotnet build src -c Release -p:Platform=x64`.
- `Utils/` — research pipeline (`mine→analyze→build_extras→gen_api→
  gen_keys→drift`) + `metadump/` metadata enumerator (see `Agents/RESEARCH.md`).
- `GameDump/` — gitignored local game copies + mining artifacts.

## Requirements

- Suzerain 3.1.0.1.175 on Steam, MelonLoader v0.7.3, SMK v2.4 in `Mods/`
  (see `Agents/IMPLEMENTATION.md` P1; game dir untouched by this repo except
  the built `BagOfTricks.dll` PostBuild-copied to `Mods/`).
- dotnet SDK 8+ for `Utils/metadump`; save-editor venv python for `Utils/*.py`.

## License

MIT — see `LICENSE`. Unofficial community project, not affiliated with
Torpor Games.
