from pathlib import Path

from pydantic import BaseModel


class DotfileEntry(BaseModel):
    name: str
    path: Path
    is_dir: bool
