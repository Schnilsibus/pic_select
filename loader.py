from PIL import Image
from pathlib import Path
from typing import Dict, Callable, Set, Literal, List

# TODO: handle case some pictures have been deleted (1,2,3,114) - NOT IMPORTANT
# TODO: handle case last of all images

# TODO: generalize for different image naming conventions

class Loader(object):

    def __init__(self, path: Path, preload_length: int = 4):
        if not path.is_file:
            raise ValueError(f"{path} is no file")

        self._preload_length = preload_length
        self._callbacks: Set[Callable[[Image.Image, Image.Image], None]] = set()
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
            raise ValueError("File does not exist")
        return self._files[index]
    
    def _load_image(self, relative: int = 0) -> Image.Image:
        try:
            path = self._get_path(relative=relative)
            image = Image.open(path)
            self._images[path] = image
            return image
        except ValueError:
            return None

    def get_current_image(self) -> Image.Image:
        return self._images[self._get_path()]
    
    def get_current_path(self) -> Path:
        return self._get_path()
    
    def get_neighbor_path(self, neighbor: Literal["Left", "Right"]) -> Path:
        if neighbor == "Left":
            return self._get_path(relative=-1)
        if neighbor == "Right":
            return self._get_path(relative=1)

    def forward(self) -> Path:
        self._current_index = self._current_index + 1
        if self._current_index not in range(0, len(self._files)):
            self._current_index = self._current_index - 1
            raise RuntimeError("Reached last image!")
        
        loaded = self._load_image(relative=self._preload_length)
        unloaded = self._images.pop(self._get_path(relative=-self._preload_length - 1))
        self._trigger_load(loaded=loaded, unloaded=unloaded)
        return self.get_current_path()

    def backward(self) -> Path:
        self._current_index = self._current_index - 1
        if self._current_index not in range(0, len(self._files)):
            self._current_index = self._current_index + 1
            raise RuntimeError("Reached first image!")
        
        loaded = self._load_image(relative=-self._preload_length)
        unloaded = self._images.pop(self._get_path(relative=self._preload_length + 1))
        self._trigger_load(loaded=loaded, unloaded=unloaded)
        return self.get_current_path()
    
    def get_preload_length(self) -> int:
        return self._preload_length
    
    def subscribe_on_load(self, callback: Callable[[Image.Image, Image.Image], None]):
        self._callbacks.add(callback)
    
    def unsubscribe_on_load(self, callback: Callable[[Image.Image, Image.Image], None]):
        self._callbacks.remove(callback)

    def _trigger_load(self, loaded: Image.Image, unloaded: Image.Image) -> None:
        for callback in self._callbacks:
            callback(loaded, unloaded)
    
    def get_images(self) -> Dict[Path, Image.Image]:
        return self._images