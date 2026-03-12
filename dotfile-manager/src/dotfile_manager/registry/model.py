from enum import StrEnum, auto
from pathlib import Path

from pydantic import BaseModel


class DotfileType(StrEnum):
    NVIM = auto()
    GHOSTTY = auto()
    ZSH = auto()


class DotfileEntry(BaseModel):
    name: str
    source_path: Path
    file_type: DotfileType
    is_dir: bool
