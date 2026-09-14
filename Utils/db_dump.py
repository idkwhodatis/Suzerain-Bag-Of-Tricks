"""Dump Suzerain.asset DialogueDatabase typetree to GameDump (gitignored).

Requires UnityPy (pip install UnityPy; any venv, e.g. TEMP scratch env).
The bundle filename hash changes per game build — update BUNDLE after updates.
Writes: GameDump/3.1.0.1.175/db_tree.json (~300MB, transient working copy).

Usage:
  upyenv-python Utils/db_dump.py
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUNDLE = (r"G:\SteamLibrary\steamapps\common\Suzerain\Suzerain_Data\StreamingAssets\aa"
          r"\StandaloneWindows64\database_assets_all_2c5c6df453acd4d096b216389ddafa9b.bundle")

import UnityPy

env = UnityPy.load(BUNDLE)
for o in env.objects:
    if o.type.name == "MonoBehaviour":
        print(f"container={o.container}")
        tree = o.read_typetree()
        print(f"typetree keys: {list(tree.keys())[:20]}")
        dst = REPO / "GameDump" / "3.1.0.1.175" / "db_tree.json"
        dst.write_text(json.dumps(tree, default=str), encoding="utf-8")
        print(f"wrote {dst} ({dst.stat().st_size // 1024 // 1024}MB)")
        break
