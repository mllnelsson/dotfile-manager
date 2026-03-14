from pathlib import Path

import pytest

from dotfile_manager.errors import LocalPathNotFoundError
from dotfile_manager.local_paths import LOCAL_PATH_MAP, resolve_local_path
from dotfile_manager.registry.model import DotfileEntry, DotfileType


def test_local_path_map_has_all_types() -> None:
    for dt in DotfileType:
        assert dt in LOCAL_PATH_MAP, f"Missing mapping for {dt}"


def test_resolve_local_path_returns_path() -> None:
    entry = DotfileEntry(
        name="nvim", source_path=Path("nvim"), file_type=DotfileType.NVIM, is_dir=True
    )
    path = resolve_local_path(entry)
    assert isinstance(path, Path)
    assert "nvim" in str(path)


def test_resolve_local_path_unknown_type(monkeypatch: pytest.MonkeyPatch) -> None:
    from dotfile_manager import local_paths

    entry = DotfileEntry(
        name="x", source_path=Path("x"), file_type=DotfileType.ZSH, is_dir=False
    )
    # Temporarily remove mapping
    original = local_paths.LOCAL_PATH_MAP.copy()
    local_paths.LOCAL_PATH_MAP.clear()
    with pytest.raises(LocalPathNotFoundError):
        resolve_local_path(entry)
    local_paths.LOCAL_PATH_MAP.update(original)
