from pathlib import Path
from typing import Dict, List

class Selector(object):

    def __init__(self):
        self._files: Dict[Path, bool] = {}

    def toggle(self, key: Path) -> bool:
        if key in self._files:
            self._files[key] = not self._files[key]
        else:
            self._files[key] = True
        return self._files[key]

    def get_selection(self) -> List[Path]:
        return list({k: v for k, v in self._files.items() if v is True}.values())

    def is_selected(self, key: Path) -> bool:
        if key in self._files:
            return self._files[key]
        else:
            return False