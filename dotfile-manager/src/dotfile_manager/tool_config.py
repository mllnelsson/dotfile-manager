from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_ROOT = Path(__file__).parent.parent.parent.parent


class ToolConfig(BaseSettings):
    root_source: Path = Field(_DEFAULT_ROOT, alias="ROOT_SOURCE")
    model_config = SettingsConfigDict(env_file=".env")


TOOL_CONFIG = ToolConfig()
