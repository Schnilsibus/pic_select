from PIL import Image, ImageOps
from pathlib import Path
from typing import Dict, Callable, Set, Literal, List
from queue import Queue
import gc

_EXIF_FORMATS = ["JPEG", "TIFF"]
_FORWARD_REQUEST = "forward"
_BACKWARD_REQUEST = "backward"

# TODO: remove logic from loader - should only have load and unload requests no remembering current image etc.
class Loader(object):

    def __init__(self, path: Path, preload_length: int = 6, batch_size: int = 3):
        if not path.is_file:
            raise ValueError(f"{path} is no file")

        self._preload_length = preload_length
        self._batch_size = batch_size
        self._load_callbacks: Set[Callable[[Path, Image.Image], None]] = set()
        self._unload_callbacks: Set[Callable[[Path], None]] = set()
        self._images: Dict[Path, Image.Image] = dict()
        self._directory: Path = path.parent
        self._files: List[Path] = [f for f in self._directory.iterdir() if f.is_file()]
        self._files.sort()
        self._current_index: int = self._files.index(path)

    def _get_path(self, relative: int = 0, anchor = None) -> Path:
        anchor_index = self._current_index if anchor is None else self.get_all_paths().index(anchor)

        index = self._current_index + (anchor_index - self._current_index) + relative

        if index not in range(len(self._files)):
            return None
        return self._files[index]
    
    def _load_image(self, relative: int = 0) -> Image.Image:
        path = self._get_path(relative=relative)
        if path is None:
            return None
        
        image = Image.open(path)

        if image.format in _EXIF_FORMATS or image.format not in _EXIF_FORMATS:
            exif = image.getexif()
            orientation = exif.get(0x0112)
            if orientation is not None and orientation > 1:
                image = ImageOps.exif_transpose(image=image)
        
        self._images[path] = image
        self._trigger_load(image=image, path=path)
        return image

    def _unload_image(self, relative: int = 0) -> Path:
        path = self._get_path(relative=relative)
        
        if path not in self._images:
            return None

        self._images[path].close()
        self._images.pop(path)
        gc.collect()
        self._trigger_unload(unloaded_path=path)
        return path

    def load_path(self, path: Path) -> None:
        self._current_index = self._files.index(path)
        for path in self._images.keys():
            self._images.pop(path)
        self._preload_images()

    def _preload_images(self) -> None:
        self._load_image()
        for i in range(1, self._preload_length + 1, 1):
            self._load_image(relative=i)
            self._load_image(relative=-i)

    def get_current_image(self) -> Image.Image:
        return self._images[self.get_current_path()]
    
    def get_image(self, path: Path) -> Image.Image:
        if path in self._images:
            return self._images[path]
        else:
            raise KeyError(f"'{str(path)}' has not yet been loaded!")
    
    def get_current_path(self) -> Path:
        return self._get_path()
    
    def get_neighbor_path(self, neighbor: Literal["Left", "Right"], anchor: Path = None) -> Path:
        if neighbor == "Left":
            return self._get_path(relative=-1, anchor=anchor)
        if neighbor == "Right":
            return self._get_path(relative=1, anchor=anchor)
    
    def get_all_paths(self) -> List[Path]:
        return self._files
    
    def get_loaded_paths(self) -> List[Path]:
        return list(self._images.keys())

    def forward(self) -> None:
        self._current_index = self._current_index + 1
        if self._current_index not in range(0, len(self._files)):
            self._current_index = self._current_index - 1
            return None
        
        self._load_image(relative=self._preload_length)
        self._unload_image(relative=-self._preload_length - 1)

    def backward(self) -> None:
        self._current_index = self._current_index - 1
        if self._current_index not in range(0, len(self._files)):
            self._current_index = self._current_index + 1
            return None
        
        self._load_image(relative=-self._preload_length)
        self._unload_image(relative=self._preload_length + 1)
    
    def get_preload_length(self) -> int:
        return self._preload_length
    
    def get_directory(self) -> Path:
        return self._directory

    def _trigger_load(self, image: Image.Image, path: Path) -> None:
        for callback in self._load_callbacks:
            callback(path, image)
    
    def _trigger_unload(self, unloaded_path: Path) -> None:
        for callback in self._unload_callbacks:
            callback(unloaded_path)
    
    def subscribe_on_load(self, callback: Callable[[Path, Image.Image], None]):
        self._load_callbacks.add(callback)
    
    def unsubscribe_on_load(self, callback: Callable[[Path, Image.Image], None]):
        self._load_callbacks.remove(callback)
    
    def subscribe_on_unload(self, callback: Callable[[Path], None]):
        self._unload_callbacks.add(callback)
    
    def unsubscribe_on_unload(self, callback: Callable[[Path], None]):
        self._unload_callbacks.remove(callback)

    def get_images(self) -> Dict[Path, Image.Image]:
        return self._images