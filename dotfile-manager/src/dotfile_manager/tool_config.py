from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_ROOT = Path(__file__).parent.parent.parent.parent


class ToolConfig(BaseSettings):
    root_source: Path = Field(_DEFAULT_ROOT, alias="ROOT_SOURCE")
    registry_file: Path | None = Field(default=None)
    model_config = SettingsConfigDict(env_file=".env")

    @model_validator(mode="after")
    def _set_registry_file(self) -> "ToolConfig":
        if self.registry_file is None:
            self.registry_file = self.root_source / "registry.toml"
        return self


TOOL_CONFIG = ToolConfig()
