
from pathlib import Path

from modules.tags import Tag

class Picture:
    def __init__(self, path: Path):
        self.path = path
        self.name = self.path.name

        self.tags = [ Tag("тэг") ]

    def get(self):
        with open(self.path) as file:
            return file
