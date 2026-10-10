from queue import Queue
from typing import Callable, Set
from pathlib import Path

from .loader import Loader
from .pictureDirectory import PictureDirectory

from ...log import logger


# TODO: check for new queue event every time I finished loading an image -> discard old one and work on newest one
class LoaderThread:
    def __init__(self, loader: Loader, picture_directory: PictureDirectory, centre_file: Path = None, preload_length: int = 6, batch_size: int = 3):
        self._preload_length = preload_length
        self._batch_size = batch_size

        self._loader = loader
        self._picture_directory = picture_directory

        self._centre_file = centre_file

        self._queue = Queue()

        self._idle_callbacks: Set[Callable[[], None]] = set()
        self._busy_callbacks: Set[Callable[[], None]] = set()

    def _run(self) -> None:
        while True:
            request = self._queue.get()
            self._trigger_busy()
            self._execute_queue(first_request=request)
            if self._queue.qsize() == 0:
                self._trigger_idle()

    def _execute_queue(self, first_request) -> None:
        requests = [first_request]

        while not self._queue.empty():
            requests.append(self._queue.get_nowait())

        request = requests[-1]

        for i in range(len(requests) - 1):
            self._queue.task_done()

        self._updateLoader(path = request)

    def _is_update_needed(self, path: Path) -> bool:
        if self._centre_file is None:
            return True
        else:
            return self._picture_directory.distance(self._centre_file, path) > self._batch_size

    def _updateLoader(self, path: Path) -> None:

        if not self._is_update_needed(path=path):
            return None

        self._unload_out_of_scope_images(path=path)
        self._load_in_scope_images(path=path)

        self._centre_file = path

    def _unload_out_of_scope_images(self, path: Path) -> None:
        out_of_scope_images = []
        for path in self._loader.keys():
            if self._picture_directory.distance(self._centre_file, path) > self._preload_length:
                out_of_scope_images.append(path)
        for path in out_of_scope_images:
            self._loader.unload(path=path)

    def _load_in_scope_images(self, path: Path) -> None:

        def load_file(file: Path) -> None:
            if file is None:
                return None
            if file in self._loader.keys():
                return None
            self._loader.load(path=file)

        index = self._picture_directory.index(path)
        load_file(path)
        for relative_position in range(1, self._preload_length + 1):
            load_file(self._picture_directory.get_relative_file(anchor=path, distance=relative_position))
            load_file(self._picture_directory.get_relative_file(anchor=path, distance=-relative_position))

    def _trigger_idle(self) -> None:
        for callback in self._idle_callbacks:
            callback()
    
    def _trigger_busy(self) -> None:
        for callback in self._busy_callbacks:
            callback()

    def _clear_queue(self) -> None:
        while not self._queue.empty():
            self._queue.get_nowait()
            self._queue.task_done()

    def mainloop(self) -> None:
            self._run()

    def _append_reload(self, path: Path) -> None:
        self._queue.put(path)

    def update_to(self, path: Path) -> None:
        if self._centre_file is None or self._picture_directory.distance(self._centre_file, path) > self._batch_size:
            self._append_reload(path=path)
        else:
            self._clear_queue()

    def subscribe_on_idle(self, callback: Callable[[], None]):
        self._idle_callbacks.add(callback)

    def unsubscribe_on_idle(self, callback: Callable[[], None]):
        self._idle_callbacks.remove(callback)

    def subscribe_on_busy(self, callback: Callable[[], None]):
        self._busy_callbacks.add(callback)

    def unsubscribe_on_busy(self, callback: Callable[[], None]):
        self._busy_callbacks.remove(callback)