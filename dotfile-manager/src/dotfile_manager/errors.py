class DfmError(Exception):
    """Base error for all dotfile-manager failures."""


class RegistryNotFoundError(DfmError):
    """registry.toml is missing or unreadable."""


class EntryNotFoundError(DfmError):
    """Named entry not found in registry."""


class LocalPathNotFoundError(DfmError):
    """Local config path does not exist or has no mapping."""


class DiffError(DfmError):
    """Diff or patch operation failed."""
