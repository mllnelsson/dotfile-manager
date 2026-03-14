from pathlib import Path

import pytest

from dotfile_manager.errors import RegistryNotFoundError
from dotfile_manager.registry import load_entries_from_file


def test_load_entries_from_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    registry = tmp_path / "registry.toml"
    registry.write_text(
        '[[entries]]\nname = "nvim"\nsource_path = "nvim"\nlocal_path = ".config/nvim"\n'
    )
    from dotfile_manager import tool_config

    monkeypatch.setattr(tool_config.TOOL_CONFIG, "registry_file", registry)

    entries = load_entries_from_file()
    assert len(entries) == 1
    assert entries[0].name == "nvim"
    assert entries[0].source_path == Path("nvim")
    assert entries[0].local_path == Path(".config/nvim")


def test_load_entries_missing_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from dotfile_manager import tool_config

    monkeypatch.setattr(
        tool_config.TOOL_CONFIG, "registry_file", tmp_path / "missing.toml"
    )

    with pytest.raises(RegistryNotFoundError):
        load_entries_from_file()
