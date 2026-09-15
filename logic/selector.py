from pathlib import Path
from typing import Dict, List
from collections.abc import Mapping



class Selector(Mapping):

    def __init__(self):
        self._files: Dict[Path, bool] = {}

    def __getitem__(self, path: Path):
        if path not in self._files:
            return False
        return self._files[path]
    
    def __setitem__(self, path: Path, selected: bool):
        self._files[path] = selected

    def __delitem__(self, path: Path):
        del self._files[path]

    def __contains__(self, path: Path):
        return path in self._files

    def __iter__(self):
        return iter(self._files)

    def __len__(self):
        return len(self._files)

    def toggle(self, path: Path) -> bool:
        if path in self._files:
            self._files[path] = not self._files[path]
        else:
            self._files[path] = True
        return self._files[path]

    def get_selection(self) -> List[Path]:
        return list({k: v for k, v in self._files.items() if v is True}.keys())

    def is_selected(self, path: Path) -> bool:
        if path in self._files:
            return self._files[path]
        else:
            return False
        
    def multi_select(self, paths: List[Path]) -> None:
        for paths in paths:
            self._files[paths] = True

    def select_all(self) -> None:
        self.multi_select(paths=self._files)
    
    def unselect_all(self) -> None:
        for path in self._files.keys():
            self._files[path] = False