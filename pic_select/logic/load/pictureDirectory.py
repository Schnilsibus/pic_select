from pathlib import Path
from collections import UserList
from PIL import Image
from typing import Set, Callable, List



class PictureDirectory(UserList):
    
    def __init__(self, directory: Path = None):
        if directory is None:
            self._directory = directory
            self._files = list()
        else:
            self.directory = directory
        self.data = self._files

        self._file_removed_callbacks: Set[Callable[[Path], None]] = set()
    
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
            return None
        index = self.index(anchor) + distance
        if index < 0 or index >= len(self):
            return None
        file = self[index]
        if not PictureDirectory.is_valid_image(path=file):
            self.remove(file)
            self._trigger_file_removed(removed_file=file)
            return self.get_relative_file(anchor=file, distance=int(distance / abs(distance)))
        return file

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

    @staticmethod
    def is_valid_image(path: Path) -> bool:
        try:
            Image.open(path).verify()
        except Exception:
            return False
        return True

    def _trigger_file_removed(self, removed_file: List[Path]) -> None:
        for callback in self._file_removed_callbacks:
            callback(removed_file)

    def subscribe_to_file_removed(self, callback: Callable[[Path], None]) -> None:
        self._file_removed_callbacks.add(callback)

    def unsubscribe_to_file_removed(self, callback: Callable[[Path], None]) -> None:
        self._file_removed_callbacks.remove(callback)
