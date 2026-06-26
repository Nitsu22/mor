from __future__ import annotations

from pathlib import Path
import sys


USER_DIC_FILENAME = "mjk-cwj.dic"


def find_bundled_user_dic() -> Path | None:
    for path in _candidate_paths():
        if path.exists():
            return path
    return None


def _candidate_paths() -> list[Path]:
    candidates: list[Path] = []

    frozen_base = getattr(sys, "_MEIPASS", None)
    if frozen_base:
        candidates.append(Path(frozen_base) / "resources" / USER_DIC_FILENAME)

    executable = Path(sys.executable).resolve()
    candidates.extend(
        [
            executable.parent / "resources" / USER_DIC_FILENAME,
            executable.parent.parent / "Resources" / "resources" / USER_DIC_FILENAME,
        ]
    )

    project_root = Path(__file__).resolve().parents[2]
    candidates.append(project_root / "resources" / USER_DIC_FILENAME)
    return _dedupe(candidates)


def _dedupe(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        unique.append(path)
    return unique
