from pathlib import Path

from pydantic import BaseModel


class DotfileEntry(BaseModel):
    name: str
    source_path: Path
    local_path: Path
