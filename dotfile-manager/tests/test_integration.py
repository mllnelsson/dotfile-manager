"""Integration tests using fixture dotfiles in tests/fixtures/.

Each test works against tmp_path copies of the fixtures so the repo files
are never mutated.  ROOT_SOURCE is patched to the copied source tree and
LOCAL_PATH_MAP is redirected to the copied local tree.
"""

import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from dotfile_manager.cli import app

FIXTURES = Path(__file__).parent / "fixtures"
runner = CliRunner()


@pytest.fixture()
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Copy fixtures to tmp_path, patch ROOT_SOURCE and LOCAL_PATH_MAP."""
    source = tmp_path / "source"
    local = tmp_path / "local"
    shutil.copytree(FIXTURES / "source", source)
    shutil.copytree(FIXTURES / "local", local)

    # Patch the singleton config object so all modules see the new root
    from dotfile_manager import tool_config

    monkeypatch.setattr(tool_config.TOOL_CONFIG, "root_source", source)
    monkeypatch.setattr(
        tool_config.TOOL_CONFIG, "registry_file", source / "registry.toml"
    )

    # Redirect LOCAL_PATH_MAP entries to the tmp local tree
    from dotfile_manager import local_paths
    from dotfile_manager.registry.model import DotfileType

    monkeypatch.setitem(
        local_paths.LOCAL_PATH_MAP, DotfileType.NVIM, local / "nvim"
    )
    monkeypatch.setitem(
        local_paths.LOCAL_PATH_MAP, DotfileType.GHOSTTY, local / "ghostty"
    )
    monkeypatch.setitem(
        local_paths.LOCAL_PATH_MAP, DotfileType.ZSH, local / "zsh" / ".zshrc"
    )

    return {"source": source, "local": local}


# ---------------------------------------------------------------------------
# dfm list
# ---------------------------------------------------------------------------


def test_list_shows_all_entries(env: dict) -> None:
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "nvim" in result.output
    assert "ghostty" in result.output
    assert "zsh" in result.output


# ---------------------------------------------------------------------------
# dfm compare
# ---------------------------------------------------------------------------


def test_compare_detects_diff_in_file(env: dict) -> None:
    result = runner.invoke(app, ["compare", "zsh"])
    assert result.exit_code == 0
    # local .zshrc has extra aliases — we expect additions in the diff
    assert "gc" in result.output or "+" in result.output


def test_compare_detects_diff_in_dir(env: dict) -> None:
    result = runner.invoke(app, ["compare", "nvim"])
    assert result.exit_code == 0
    # local init.lua has relativenumber + tabstop=2; plugins.lua adds which-key
    assert "relativenumber" in result.output or "+" in result.output


def test_compare_no_diff_when_identical(env: dict, tmp_path: Path) -> None:
    """Sync first to make source == local, then compare should show nothing."""
    from dotfile_manager.ops import sync_local
    from dotfile_manager.registry import load_entries_from_file

    entries = {e.name: e for e in load_entries_from_file()}
    sync_local(entries["zsh"])

    result = runner.invoke(app, ["compare", "zsh"])
    assert result.exit_code == 0
    assert "No differences" in result.output


# ---------------------------------------------------------------------------
# dfm sync  (source → local)
# ---------------------------------------------------------------------------


def test_sync_file_overwrites_local(env: dict) -> None:
    source_content = (env["source"] / "zsh" / ".zshrc").read_text()
    local_file = env["local"] / "zsh" / ".zshrc"

    result = runner.invoke(app, ["sync", "zsh"])
    assert result.exit_code == 0
    assert local_file.read_text() == source_content


def test_sync_dir_overwrites_local(env: dict) -> None:
    source_init = (env["source"] / "nvim" / "init.lua").read_text()
    local_init = env["local"] / "nvim" / "init.lua"

    result = runner.invoke(app, ["sync", "nvim"])
    assert result.exit_code == 0
    assert local_init.read_text() == source_init


def test_sync_all_entries(env: dict) -> None:
    result = runner.invoke(app, ["sync"])
    assert result.exit_code == 0
    # All three entries synced without error
    for name in ("nvim", "ghostty", "zsh"):
        assert name in result.output


# ---------------------------------------------------------------------------
# dfm update  (local → source)
# ---------------------------------------------------------------------------


def test_update_file_overwrites_source(env: dict) -> None:
    local_content = (env["local"] / "zsh" / ".zshrc").read_text()
    source_file = env["source"] / "zsh" / ".zshrc"

    result = runner.invoke(app, ["update", "zsh"])
    assert result.exit_code == 0
    assert source_file.read_text() == local_content


def test_update_dir_overwrites_source(env: dict) -> None:
    local_plugins = (env["local"] / "nvim" / "lua" / "plugins.lua").read_text()
    source_plugins = env["source"] / "nvim" / "lua" / "plugins.lua"

    result = runner.invoke(app, ["update", "nvim"])
    assert result.exit_code == 0
    assert source_plugins.read_text() == local_plugins


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_unknown_entry_exits_nonzero(env: dict) -> None:
    result = runner.invoke(app, ["compare", "does-not-exist"])
    assert result.exit_code != 0


def test_missing_registry_exits_nonzero(
    env: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    from dotfile_manager import tool_config

    monkeypatch.setattr(
        tool_config.TOOL_CONFIG,
        "registry_file",
        Path("/nonexistent/registry.toml"),
    )
    result = runner.invoke(app, ["list"])
    assert result.exit_code != 0
