from pathlib import Path

from .loaderThread import LoaderThread



class DisplayTracker:
    def __init__(self, loaderThread: LoaderThread, currentDisplayPath: Path = None):
        self._loaderThread = loaderThread

        self._currently_displayed_path = currentDisplayPath

    @property
    def currentDisplayPath(self) -> Path:
        return self._currently_displayed_path

    @property.setter
    def currentDisplayPath(self, path: Path) -> None:
        self._currently_displayed_path = path
        self._loaderThread.update_to(path=path)