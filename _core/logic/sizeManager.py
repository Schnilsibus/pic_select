from screeninfo import get_monitors
from typing import Tuple


class SizeManager():
    
    def __init__(self):
        self._max_monitor_extension = self.get_max_monitor_extension()

    @property
    def max_monitor_extension(self) -> Tuple[int, int]:
        return self._max_monitor_extension

    @staticmethod
    def get_max_monitor_extension() -> Tuple[int, int]:
        widths, heights = zip(*[(m.width, m.height) for m in get_monitors()])
        return max(widths), max(heights)

    