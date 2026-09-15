from queue import Queue
from typing import Callable, Set
from pathlib import Path

from .loader import Loader



_FORWARD_REQUEST = "forward"
_BACKWARD_REQUEST = "backward"



def distance(indexA, indexB) -> int:
    return abs(indexA - indexB)



class LoaderController:
    def __init__(self, loader: Loader, preload_length: int = 6, batch_size: int = 3):
        self._preload_length = preload_length
        self._batch_size = batch_size

        self._loader = loader
        self._managed_files = self._loader.files

        self._current_index = -1
        self._centre_index = -1

        self._queue = Queue()

        self._idle_callbacks: Set[Callable[[], None]] = set()
        self._busy_callbacks: Set[Callable[[], None]] = set()

    def _run(self) -> None:
        while True:
            request = self._queue.get()
            self._trigger_busy()
            self._execute_requests(first_request=request)
            if self._queue.qsize() == 0:
                self._trigger_idle()

    def _execute_queue(self, first_request) -> None:
        requests = [first_request]

        while not self._queue.empty():
            requests.append(self._queue.get_nowait())

        for request in requests:
            if isinstance(request, Path):
                self._current_index = self._loader.getIndexOf(path=request)
            elif request == _FORWARD_REQUEST:
                self._current_index = self._current_index + 1
            elif request == _BACKWARD_REQUEST:
                self._current_index = self._current_index - 1
            self._queue.task_done()

        if self._current_index < 0:
            self._current_index = 0
        if self._current_index >= len(self._managed_files):
            self._current_index = len(self._managed_files) - 1

        self._updateLoader()

    def _updateLoader(self) -> None:

        if distance(self._current_index, self._centre_index) <= self._batch_size:
            return None

        self._unload_out_of_scope_images()
        self._load_in_scope_images()

    def _unload_out_of_scope_images(self) -> None:
        for path in self._loader.keys():
            index = self._loader.getIndexOf(path=path)
            if distance(self._current_index, index) > self._preload_length:
                self._loader.unload()

    def _load_in_scope_images(self) -> None:

        def load_index(index: int) -> None:
            if index < 0 or index >= len(self._managed_files):
                return None
            path = self._managed_files[index]
            if path in self._loader.keys():
                return None
            self._loader.load(path=path)

        load_index(self._current_index)
        for relative_position in range(1, self._preload_length):
            load_index(self._current_index + relative_position)
            load_index(self._current_index - relative_position)

    def _trigger_idle(self) -> None:
        for callback in self._idle_callbacks:
            callback()
    
    def _trigger_busy(self) -> None:
        for callback in self._busy_callbacks:
            callback()

    def mainloop(self) -> None:
            self._run()

    def current_file(self) -> Path:
        return self._managed_files[self._current_index]

    def append_reload(self, path: Path) -> None:
        self._queue.put(path)

    def append_forward(self) -> None:
        self._queue.put(_FORWARD_REQUEST)

    def append_backward(self) -> None:
        self._queue.put(_BACKWARD_REQUEST)

    def subscribe_on_idle(self, callback: Callable[[], None]):
        self._idle_callbacks.add(callback)

    def unsubscribe_on_idle(self, callback: Callable[[], None]):
        self._idle_callbacks.remove(callback)

    def subscribe_on_busy(self, callback: Callable[[], None]):
        self._busy_callbacks.add(callback)

    def unsubscribe_on_busy(self, callback: Callable[[], None]):
        self._busy_callbacks.remove(callback)