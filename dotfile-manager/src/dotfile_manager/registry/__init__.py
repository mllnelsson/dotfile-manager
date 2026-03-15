import tomllib

from dotfile_manager.errors import RegistryNotFoundError
from dotfile_manager.tool_config import TOOL_CONFIG

from .model import DotfileEntry


def load_entries_from_file() -> list[DotfileEntry]:
    registry_file = TOOL_CONFIG.registry_file
    if registry_file is None:
        raise RegistryNotFoundError("No Registry file set")
    if not registry_file.exists():
        raise RegistryNotFoundError(f"Registry file not found: {registry_file}")
    with open(registry_file, "rb") as f:
        data = tomllib.load(f)
    entries = data.get("entries", [])
    return [DotfileEntry.model_validate(entry) for entry in entries]


__all__ = [
    "DotfileEntry",
    "load_entries_from_file",
]
