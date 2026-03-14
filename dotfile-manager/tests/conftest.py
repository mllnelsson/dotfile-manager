from pathlib import Path

import pytest

from dotfile_manager.registry.model import DotfileEntry, DotfileType


@pytest.fixture()
def file_entry(tmp_path: Path) -> DotfileEntry:
    return DotfileEntry(
        name="test_file",
        source_path=Path("test_file.txt"),
        file_type=DotfileType.ZSH,
        is_dir=False,
    )


@pytest.fixture()
def dir_entry(tmp_path: Path) -> DotfileEntry:
    return DotfileEntry(
        name="test_dir",
        source_path=Path("test_dir"),
        file_type=DotfileType.NVIM,
        is_dir=True,
    )


@pytest.fixture()
def source_file(tmp_path: Path) -> Path:
    f = tmp_path / "source.txt"
    f.write_text("line1\nline2\nline3\n")
    return f


@pytest.fixture()
def local_file(tmp_path: Path) -> Path:
    f = tmp_path / "local.txt"
    f.write_text("line1\nline2 modified\nline3\nnew line\n")
    return f
