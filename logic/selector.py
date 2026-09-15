from pathlib import Path
from typing import Dict, List, Set, Callable
from collections.abc import Mapping



class Selector(Mapping):

    def __init__(self):
        self._files: Dict[Path, bool] = {}

        self._callbacks: Set[Callable[[List[Path]], None]] = set()

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

    def _trigger_select(self) -> None:
        selection = self.get_selection()
        for callback in self._callbacks:
            callback(selection)

    def toggle(self, path: Path) -> bool:
        if path in self._files:
            self._files[path] = not self._files[path]
        else:
            self._files[path] = True
        self._trigger_select()
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
        self._trigger_select()

    def select_all(self) -> None:
        self.multi_select(paths=self._files)
        self._trigger_select()
    
    def unselect_all(self) -> None:
        for path in self._files.keys():
            self._files[path] = False
        self._trigger_select()

    def subscribe_on_select(self, callback: Callable[[List[Path]], None]):
        self._callbacks.add(callback)

    def unsubscribe_on_select(self, callback: Callable[[List[Path]], None]):
        self._callbacks.remove(callback)