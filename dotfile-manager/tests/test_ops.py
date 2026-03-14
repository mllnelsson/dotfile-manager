from pathlib import Path

import pytest

from dotfile_manager.ops import update_source, sync_local
from dotfile_manager.registry.model import DotfileEntry, DotfileType


@pytest.fixture()
def patched_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from dotfile_manager import tool_config

    monkeypatch.setattr(
        tool_config.TOOL_CONFIG, "root_source", tmp_path / "source_repo"
    )
    (tmp_path / "source_repo").mkdir()
    return tmp_path


@pytest.fixture()
def file_entry() -> DotfileEntry:
    return DotfileEntry(
        name="zsh",
        source_path=Path("zsh/.zshrc"),
        file_type=DotfileType.ZSH,
        is_dir=False,
    )


def test_sync_local_file(
    patched_config: Path, file_entry: DotfileEntry, monkeypatch: pytest.MonkeyPatch
) -> None:
    from dotfile_manager import local_paths

    local_dir = patched_config / "local"
    local_dir.mkdir()
    local_path = local_dir / ".zshrc"
    monkeypatch.setitem(local_paths.LOCAL_PATH_MAP, file_entry.file_type, local_path)

    # Create source file
    from dotfile_manager import tool_config

    source_file = tool_config.TOOL_CONFIG.root_source / file_entry.source_path
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("source content\n")

    sync_local(file_entry)

    assert local_path.read_text() == "source content\n"


def test_update_source_file(
    patched_config: Path, file_entry: DotfileEntry, monkeypatch: pytest.MonkeyPatch
) -> None:
    from dotfile_manager import local_paths, tool_config

    local_dir = patched_config / "local"
    local_dir.mkdir()
    local_path = local_dir / ".zshrc"
    local_path.write_text("local content\n")
    monkeypatch.setitem(local_paths.LOCAL_PATH_MAP, file_entry.file_type, local_path)

    # Create source dir
    source_file = tool_config.TOOL_CONFIG.root_source / file_entry.source_path
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("old source\n")

    update_source(file_entry)

    assert source_file.read_text() == "local content\n"


def test_sync_local_dir(patched_config: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from dotfile_manager import local_paths, tool_config

    entry = DotfileEntry(
        name="nvim",
        source_path=Path("nvim"),
        file_type=DotfileType.NVIM,
        is_dir=True,
    )

    local_path = patched_config / "nvim_local"
    monkeypatch.setitem(local_paths.LOCAL_PATH_MAP, entry.file_type, local_path)

    source_dir = tool_config.TOOL_CONFIG.root_source / entry.source_path
    source_dir.mkdir(parents=True)
    (source_dir / "init.lua").write_text("-- config\n")

    sync_local(entry)

    assert (local_path / "init.lua").read_text() == "-- config\n"
