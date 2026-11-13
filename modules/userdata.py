
from pathlib import Path

class Userdata:
    def __init__(self, path: Path):
        self.path = path

    def join(self, path: str | Path) -> Path:
        return Path(self.path, path)

    def __str__(self):
        return str(self.path)
