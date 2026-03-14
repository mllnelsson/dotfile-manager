from pathlib import Path

import pytest

from dotfile_manager.registry.model import DotfileEntry


@pytest.fixture()
def file_entry() -> DotfileEntry:
    return DotfileEntry(
        name="zsh",
        source_path=Path("zsh/.zshrc"),
        local_path=Path(".zshrc"),
    )


@pytest.fixture()
def dir_entry() -> DotfileEntry:
    return DotfileEntry(
        name="nvim",
        source_path=Path("nvim"),
        local_path=Path(".config/nvim"),
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
