import os
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ToolConfig(BaseSettings):
    source_root: Path = Field(alias="DFM_SOURCE_ROOT")
    registry_file: Path | None = Field(default=None, alias="DFM_REGISTRY_FILE")
    model_config = SettingsConfigDict(env_file=".env")
    local_root: Path | None = Field(default=None, alias="DFM_LOCAL_ROOT")

    @model_validator(mode="after")
    def _set_registry_file(self) -> "ToolConfig":
        if self.registry_file is None:
            self.registry_file = self.source_root / "registry.toml"
        return self

    @model_validator(mode="after")
    def _set_local_root(self) -> "ToolConfig":
        if self.local_root is not None:
            return self
        home = os.getenv("HOME")
        if home is None:
            raise ValueError("No local root set. Either set $DFM_LOCALROOT or $HOME")
        self.local_root = Path(home)
        return self


TOOL_CONFIG = ToolConfig()
