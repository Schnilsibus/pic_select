from PIL import Image
from pathlib import Path
from typing import Dict, Callable, Set, Literal

# TODO: handle case some pictures have been deleted (1,2,3,114) - NOT IMPORTANT

class Loader(object):

    def __init__(self, path: Path, preload_length: int = 2):
        self._preload_length = preload_length
        self._callbacks: Set[Callable[[Image.Image, Image.Image], None]] = set()
        self._images: Dict[Path, Image.Image] = dict()
        self._directory: Path = path.parent
        self._current_image: int = int(path.name[4:8])

        if not path.is_file:
            raise ValueError(f"{path} is no file")

        for i in range(-self._preload_length, self._preload_length + 1, 1):
            self._load_image(relative=i)

    def _get_path(self, relative: int = 0) -> Path:
        return Path(f"{self._directory}\IMG_{self._current_image + relative:04d}.png")
    
    def _load_image(self, relative: int = 0) -> Image.Image:
        path = self._get_path(relative=relative)
        if not path.exists():
            return None
        else:
            self._images[path] = Image.open(path)
            return self._images[path]

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
        self._current_image = self._current_image + 1
        loaded = self._load_image(relative=self._preload_length)
        unloaded = self._images.pop(self._get_path(relative=-self._preload_length - 1))
        self._trigger_load(loaded=loaded, unloaded=unloaded)
        return self.get_current_path()

    def backward(self) -> Path:
        self._current_image = self._current_image - 1
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