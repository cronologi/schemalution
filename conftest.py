from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Ensure src/ layouts are importable when running tests from the repo root.
for src_path in sorted(ROOT.glob("packages/*/src")):
    src_str = str(src_path)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)
