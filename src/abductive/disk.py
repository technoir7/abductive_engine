"""A floor under the disk's free space: the downloads, the reading and the
embeddings stop rather than fill it (the user's request, 2026-10-26)."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Callable

MIN_FREE_GB = 20


class DiskFull(RuntimeError):
    pass


def ensure_room(path: Path, min_free_gb: float = MIN_FREE_GB,
                free: Callable[[Path], int] = lambda p: shutil.disk_usage(p).free) -> None:
    left = free(path) / 2**30
    if left < min_free_gb:
        raise DiskFull(f"{left:.1f} GB free, under the {min_free_gb} GB floor: stopping")
