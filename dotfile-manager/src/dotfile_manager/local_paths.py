from pathlib import Path

from dotfile_manager.errors import LocalPathNotFoundError
from dotfile_manager.registry.model import DotfileEntry, DotfileType

LOCAL_PATH_MAP: dict[DotfileType, Path] = {
    DotfileType.NVIM: Path.home() / ".config" / "nvim",
    DotfileType.GHOSTTY: Path.home() / ".config" / "ghostty",
    DotfileType.ZSH: Path.home() / ".config" / "zsh",
}


def resolve_local_path(entry: DotfileEntry) -> Path:
    path = LOCAL_PATH_MAP.get(entry.file_type)
    if path is None:
        raise LocalPathNotFoundError(
            f"No local path mapping for type '{entry.file_type}'"
        )
    return path
