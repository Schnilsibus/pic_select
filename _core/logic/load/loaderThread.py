from queue import Queue
from typing import Callable, Set
from pathlib import Path

from .loader import Loader
from .pictureDirectory import PictureDirectory



class LoaderThread:
    def __init__(self, loader: Loader, picture_directory: PictureDirectory, centre_file: Path = None, preload_length: int = 6, batch_size: int = 3):
        self._preload_length = preload_length
        self._batch_size = batch_size

        self._loader = loader
        self._picture_directory = picture_directory

        self._centre_file = centre_file

        self._queue = Queue()
        self._queue_size = 0

        self._idle_callbacks: Set[Callable[[], None]] = set()
        self._busy_callbacks: Set[Callable[[], None]] = set()

    def _run(self) -> None:
        while True:
            request = self._queue.get()
            self._execute_queue(first_request=request)
            if self._queue.qsize() == 0:
                self._trigger_idle()

    def _execute_queue(self, first_request) -> None:
        requests = [first_request]

        while not self._queue.qsize() == 0:
            requests.append(self._queue.get_nowait())

        request = requests[-1]

        for i in range(len(requests) - 1):
            self._queue.task_done()
        self._queue_size = self._queue.qsize()

        self._trigger_busy()
        self._updateLoader(path = request)
        self._queue.task_done()

    def _updateLoader(self, path: Path) -> None:
        if self._centre_file is None:
            self._centre_file = path

        if self._unload_out_of_scope_images(path=path):
            self._centre_file = path
            return None
        if self._load_in_scope_images(path=path):
            self._centre_file = path
            return None

        self._centre_file = path

    def _unload_out_of_scope_images(self, path: Path) -> bool:
        out_of_scope_images = []
        for path in self._loader.keys():
            if self._picture_directory.distance(self._centre_file, path) > self._preload_length:
                out_of_scope_images.append(path)
        for path in out_of_scope_images:
            self._loader.unload(path=path)
            if self._queue_size < self._queue.qsize():
                return True

    def _load_in_scope_images(self, path: Path) -> bool:

        def load_file(file: Path) -> None:
            if file is None:
                return None
            if file in self._loader.keys():
                return None
            self._loader.load(path=file)

        load_file(path)
        for relative_position in range(1, self._preload_length + 1):
            load_file(self._picture_directory.get_relative_file(anchor=path, distance=relative_position))
            if self._queue_size < self._queue.qsize():
                return True
            load_file(self._picture_directory.get_relative_file(anchor=path, distance=-relative_position))
            if self._queue_size < self._queue.qsize():
                return True

    def _trigger_idle(self) -> None:
        for callback in self._idle_callbacks:
            callback()
    
    def _trigger_busy(self) -> None:
        for callback in self._busy_callbacks:
            callback()

    def _clear_queue(self) -> None:
        while not self._queue.qsize() == 0:
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
            self._append_reload(path=self._centre_file)

    def subscribe_on_idle(self, callback: Callable[[], None]):
        self._idle_callbacks.add(callback)

    def unsubscribe_on_idle(self, callback: Callable[[], None]):
        self._idle_callbacks.remove(callback)

    def subscribe_on_busy(self, callback: Callable[[], None]):
        self._busy_callbacks.add(callback)

    def unsubscribe_on_busy(self, callback: Callable[[], None]):
        self._busy_callbacks.remove(callback)