from PIL import Image
from pathlib import Path
from typing import Dict, Callable, Set, Literal, List

class Loader(object):

    def __init__(self, path: Path, preload_length: int = 4):
        if not path.is_file:
            raise ValueError(f"{path} is no file")
        
        self._count = 0

        self._preload_length = preload_length
        self._callbacks: Set[Callable[[Image.Image, Image.Image, int], None]] = set()
        self._images: Dict[Path, Image.Image] = dict()
        self._directory: Path = path.parent
        self._files: List[Path] = [f for f in self._directory.iterdir() if f.is_file()]
        self._files.sort()
        self._current_index: int = self._files.index(path)

        for i in range(-self._preload_length, self._preload_length + 1, 1):
            self._load_image(relative=i)

    def _get_path(self, relative: int = 0) -> Path:
        index = self._current_index + relative
        if index not in range(len(self._files)):
            return None
        return self._files[index]
    
    def _load_image(self, relative: int = 0) -> Image.Image:
        path = self._get_path(relative=relative)
        if path is None:
            return None
        
        image = Image.open(path)
        self._images[path] = image
        return image

    def get_current_image(self) -> Image.Image:
        return self._images[self.get_current_path()]
    
    def get_current_path(self) -> Path:
        return self._get_path()
    
    def get_neighbor_path(self, neighbor: Literal["Left", "Right"]) -> Path:
        if neighbor == "Left":
            return self._get_path(relative=-1)
        if neighbor == "Right":
            return self._get_path(relative=1)
    
    def get_all_paths(self) -> List[Path]:
        return self._files

    def forward(self) -> None:
        self._count = self._count + 1
        self._current_index = self._current_index + 1
        if self._current_index not in range(0, len(self._files)):
            self._current_index = self._current_index - 1
            return None
        
        loaded = self._load_image(relative=self._preload_length)
        unload_path = self._get_path(relative=-self._preload_length - 1)
        if unload_path in self._images:
            unloaded = self._images.pop(self._get_path(relative=-self._preload_length - 1))
        else:
            unloaded = None
        print(f"LOADER-UPDATE {self._count:04d}: {len(self._images)} - {self.get_images_debug()}")
        self._trigger_load(loaded=loaded, unloaded=unloaded, count=self._count)

    def backward(self) -> None:
        self._count = self._count + 1
        self._current_index = self._current_index - 1
        if self._current_index not in range(0, len(self._files)):
            self._current_index = self._current_index + 1
            return None
        
        loaded = self._load_image(relative=-self._preload_length)
        unload_path = self._get_path(relative=self._preload_length + 1)
        if unload_path in self._images:
            unloaded = self._images.pop(unload_path)
        else:
            unloaded = None
        print(f"LOADER-UPDATE {self._count:4d}: {len(self._images)} - {self.get_images_debug()}")
        self._trigger_load(loaded=loaded, unloaded=unloaded, count=self._count)
    
    def get_preload_length(self) -> int:
        return self._preload_length
    
    def get_directory(self) -> Path:
        return self._directory
    
    def subscribe_on_load(self, callback: Callable[[Image.Image, Image.Image, int], None]):
        self._callbacks.add(callback)
    
    def unsubscribe_on_load(self, callback: Callable[[Image.Image, Image.Image, int], None]):
        self._callbacks.remove(callback)

    def _trigger_load(self, loaded: Image.Image, unloaded: Image.Image, count: int) -> None:
        for callback in self._callbacks:
            callback(loaded, unloaded, count)
    
    def get_images(self) -> Dict[Path, Image.Image]:
        return self._images
    
    def get_images_debug(self) -> str:
        return ", ".join(sorted([str(int(k.name[4:8])) for k in self.get_images().keys()]))