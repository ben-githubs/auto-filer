from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import os

@dataclass
class File:
    name: str
    ftype: str
    size: int
    date_created: datetime
    date_modified: datetime
    path: Path

    def from_pathlib(path):
        assert path.exists()
        assert path.is_file()
        
        stats = os.stat(path)
        return File(
            name = path.stem,
            ftype = path.suffix[1:].lower(),
            size = stats.st_size, # Size of file in bytes
            date_created = datetime.fromtimestamp(stats.st_ctime),
            date_modified = datetime.fromtimestamp(stats.st_mtime),
            path = path
        )
