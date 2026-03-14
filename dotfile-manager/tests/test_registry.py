from pathlib import Path

import pytest

from dotfile_manager.errors import RegistryNotFoundError
from dotfile_manager.registry import load_entries_from_file
from dotfile_manager.registry.model import DotfileType


def test_load_entries_from_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry = tmp_path / "registry.toml"
    registry.write_text(
        '[[ entries ]]\nname = "nvim"\nsource_path = "nvim"\nfile_type = "nvim"\nis_dir = true\n'
    )
    from dotfile_manager import tool_config

    monkeypatch.setattr(tool_config.TOOL_CONFIG, "registry_file", registry)

    entries = load_entries_from_file()
    assert len(entries) == 1
    assert entries[0].name == "nvim"
    assert entries[0].file_type == DotfileType.NVIM
    assert entries[0].is_dir is True


def test_load_entries_missing_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from dotfile_manager import tool_config

    monkeypatch.setattr(
        tool_config.TOOL_CONFIG, "registry_file", tmp_path / "missing.toml"
    )

    with pytest.raises(RegistryNotFoundError):
        load_entries_from_file()
