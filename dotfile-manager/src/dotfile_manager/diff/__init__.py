from pathlib import Path

from dotfile_manager.registry.model import DotfileEntry
from dotfile_manager.tool_config import TOOL_CONFIG

from ._engine import _diff_dirs, _diff_files


def compute_diff(
    entry: DotfileEntry, local_path: Path
) -> list[str] | dict[str, list[str]]:
    source_path = TOOL_CONFIG.source_root / entry.source_path
    if source_path.is_dir():
        return _diff_dirs(source_path, local_path)
    return _diff_files(source_path, local_path)


def has_diff(entry: DotfileEntry, local_path: Path) -> bool:
    result = compute_diff(entry, local_path)
    if isinstance(result, dict):
        return any(lines for lines in result.values())
    return bool(result)


__all__ = ["compute_diff", "has_diff"]
