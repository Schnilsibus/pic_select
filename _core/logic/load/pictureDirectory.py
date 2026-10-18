from pathlib import Path
from typing import List
from collections import UserList



class PictureDirectory(UserList):
    
    def __init__(self, directory: Path = None):
        if directory is None:
            self._directory = directory
            self._files = list()
        else:
            self.directory = directory
        self.data = self._files
    
    def _lookup_files(self) -> None:
        self._files = [f for f in self._directory.iterdir() if f.is_file()]
        self._files.sort()

    @property
    def directory(self) -> Path:
        return self._directory

    @directory.setter
    def directory(self, directory: Path):
        if not directory.is_dir():
            raise ValueError(f"{directory} is no directory")
        else:
            self._directory = directory
        self._lookup_files()
        self.data = self._files

    def get_relative_file(self, anchor: Path, distance: int) -> Path:
        if anchor not in self:
            raise RuntimeError(f"{anchor} not in {self._directory}")
        index = self.index(anchor) + distance
        if index < 0 or index >= len(self):
            return None
        return self[index]

    def previous_file(self, anchor: Path) -> Path:
        return self.get_relative_file(anchor=anchor, distance=-1)

    def next_file(self, anchor: Path) -> Path:
        return self.get_relative_file(anchor=anchor, distance=1)

    def distance(self, pathA: Path, pathB: Path) -> int:
        if pathA not in self:
            raise RuntimeError(f"{pathA} not in {self._directory}")
        if pathB not in self:
            raise RuntimeError(f"{pathB} not in {self._directory}")
        return abs(self.index(pathA) - self.index(pathB))