from PIL import Image, ImageOps
from pathlib import Path
from typing import Dict, Callable, Set, List
from collections.abc import Mapping
import gc

from .pictureDirectory import PictureDirectory

from ...log import logger



_EXIF_FORMATS = ["JPEG", "TIFF"]



class Loader(Mapping):

    def __init__(self, picture_directory: PictureDirectory):
        if picture_directory is None:
            raise RuntimeError("picture_directory can not be None")
        self._picture_directory = picture_directory

        self._images: Dict[Path, Image.Image] = dict()

        self._load_callbacks: Set[Callable[[Path, Image.Image], None]] = set()
        self._unload_callbacks: Set[Callable[[Path], None]] = set()

    def __getitem__(self, path: Path):
        if path not in self._images:
            raise KeyError(f"{path} is not loaded")
        return self._images[path]

    def __setitem__(self, path: Path, image: Image.Image):
        raise RuntimeError("use Loader.load()")

    def __delitem__(self, path: Path):
        raise RuntimeError("use Loader.unload()")

    def __contains__(self, path: Path):
        return path in self._images

    def __iter__(self):
        return iter(self._images)

    def __len__(self):
        return len(self._images)
    
    def load(self, path: Path) -> Image.Image:
        if path not in self._picture_directory:
            raise KeyError(f"{path} not in {self._picture_directory.directory}")
                
        image = Image.open(path)

        if image.format in _EXIF_FORMATS or image.format not in _EXIF_FORMATS:
            exif = image.getexif()
            orientation = exif.get(0x0112)
            if orientation is not None and orientation > 1:
                image = ImageOps.exif_transpose(image=image)
        
        self._images[path] = image
        logger.log_file_action(thread="bac", file=path, action="loaded")
        self._trigger_load(image=image, path=path)
        return image

    def unload(self, path) -> None:
        if path not in self._images:
            return None

        self._images[path].close()
        self._images.pop(path)
        gc.collect()
        logger.log_file_action(thread="bac", file=path, action="unloaded")
        self._trigger_unload(unloaded_path=path)

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