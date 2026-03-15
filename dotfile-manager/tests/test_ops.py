from pathlib import Path

import pytest

from dotfile_manager.ops import sync_local, update_source
from dotfile_manager.registry.model import DotfileEntry


@pytest.fixture()
def patched_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from dotfile_manager import tool_config

    source_repo = tmp_path / "source_repo"
    source_repo.mkdir()
    local_root = tmp_path / "local"
    local_root.mkdir()

    monkeypatch.setattr(tool_config.TOOL_CONFIG, "source_root", source_repo)
    monkeypatch.setattr(tool_config.TOOL_CONFIG, "local_root", local_root)
    return tmp_path


def _accept_all(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch prompt_hunks to auto-accept every hunk (no stdin needed)."""
    from dotfile_manager.ops._partial import _split_into_hunks

    monkeypatch.setattr(
        "dotfile_manager.ops.prompt_hunks",
        lambda lines, console: [True] * len(_split_into_hunks(lines)),
    )


def test_sync_local_file(patched_config: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from dotfile_manager import tool_config

    _accept_all(monkeypatch)

    entry = DotfileEntry(
        name="zsh",
        source_path=Path("zsh/.zshrc"),
        local_path=Path(".zshrc"),
    )

    source_file = tool_config.TOOL_CONFIG.source_root / entry.source_path
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("source content\n")

    sync_local(entry)

    local_file = tool_config.TOOL_CONFIG.local_root / entry.local_path
    assert local_file.read_text() == "source content\n"


def test_update_source_file(patched_config: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from dotfile_manager import tool_config

    _accept_all(monkeypatch)

    entry = DotfileEntry(
        name="zsh",
        source_path=Path("zsh/.zshrc"),
        local_path=Path(".zshrc"),
    )

    source_file = tool_config.TOOL_CONFIG.source_root / entry.source_path
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("old source\n")

    local_file = tool_config.TOOL_CONFIG.local_root / entry.local_path
    local_file.write_text("local content\n")

    update_source(entry)

    assert source_file.read_text() == "local content\n"


def test_sync_local_dir(patched_config: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from dotfile_manager import tool_config

    _accept_all(monkeypatch)

    entry = DotfileEntry(
        name="nvim",
        source_path=Path("nvim"),
        local_path=Path(".config/nvim"),
    )

    source_dir = tool_config.TOOL_CONFIG.source_root / entry.source_path
    source_dir.mkdir(parents=True)
    (source_dir / "init.lua").write_text("-- config\n")

    sync_local(entry)

    local_dir = tool_config.TOOL_CONFIG.local_root / entry.local_path
    assert (local_dir / "init.lua").read_text() == "-- config\n"
