"""Nothing this project writes may fill the disk."""
import pytest

from abductive.disk import DiskFull, ensure_room


def test_enough_room_passes_and_too_little_stops_the_run(tmp_path):
    ensure_room(tmp_path, min_free_gb=0, free=lambda p: 50 * 2**30)
    with pytest.raises(DiskFull):
        ensure_room(tmp_path, min_free_gb=20, free=lambda p: 19 * 2**30)
