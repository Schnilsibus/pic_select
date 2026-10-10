import tkinter as tk
from typing import Tuple, Dict, Self
from pathlib import Path
from collections.abc import Mapping
from PIL import Image

from ....logic.selector import Selector
from ....logic.load.loader import Loader
from ....logic.load.loaderThread import LoaderThread

from ..components.imageFrame import ImageFrame
from ..displays.loadFrame import LoadFrame

from ....log import logger


# TODO: Problem: selecting moves the image slightly -> Only in full size app not in isolated test!
# TODO: Problem: fame is slightly cut of at bottom! -> Only in full size app not in isolated test!
class ImageViewFrame(tk.Frame, Mapping):

    def __init__(self, master: tk.Widget, display_size: Tuple[int, int], selector: Selector, loader: Loader):
        super().__init__(master=master, width=display_size[0], height=display_size[1], background="black")

        self.pack_propagate(False)

        loader.subscribe_on_load(callback=self._on_load)
        loader.subscribe_on_unload(callback=self._on_unload)

        selector.subscribe_on_select(callback=self._on_select)
        
        self._selector = selector

        self._image_frames: Dict[Path, ImageFrame] = {}

        self._current_image_path: Path = None

        self._load_frame: LoadFrame = LoadFrame(master=self, display_size=display_size)
        self._load_frame.place(relx=0.5, rely=0.5, anchor="center", )

    def __getitem__(self, path: Path):
        if path not in self._images:
            raise KeyError(f"{path} is not framed")
        return self._image_frames[path]

    def __setitem__(self, path: Path, image: Image.Image):
        raise RuntimeError("use ImageViewFrame.create_image_frame()")

    def __delitem__(self, path: Path):
        raise RuntimeError("use ImageViewFrame.remove_image_frame()")

    def __contains__(self, path: Path):
        return path in self._image_frames

    def __iter__(self):
        return iter(self._image_frames)

    def __len__(self):
        return len(self._image_frames)

    def _on_load(self, path: Path, image: Image.Image) -> None:
        self._create_image_frame(path=path, image=image)
        logger.log_file_action(thread="gui", file=path, action="created")
        if self._current_image_path == path:
            self.display_image_frame(path=path)
    
    def _on_unload(self, unloaded: Path) -> None:
        if unloaded is not None:
            self.remove_image_frame(path=unloaded)
        logger.log_file_action(thread="gui", file=unloaded, action="destroyed")

    def _on_select(self, path: Path, selected: bool) -> None:
        if path not in self._image_frames:
            return None
        if selected:
            self._image_frames[path].select()
        else:
            self._image_frames[path].unselect()

    def _create_image_frame(self, path: Path, image: Image.Image) -> Self:
        self._image_frames[path] = ImageFrame(master=self,
                                              display_size=(self.winfo_width(), self.winfo_height()),
                                              image=image,
                                              selected=self._selector.is_selected(path=path))
        self._image_frames[path].place(relx=0.5, rely=0.5, anchor="center")
        if self._current_image_path in self:
            self._image_frames[self._current_image_path].tkraise()
        else:
            self._load_frame.tkraise()

    @property
    def current_image_path(self) -> Path:
        return self._current_image_path

    def remove_image_frame(self, path: Path) -> None:
        self._image_frames.pop(path)

    def display_image_frame(self, path: Path) -> None:
        if path not in self:
            self._load_frame.set_text(name=path.name)
            self._load_frame.tkraise()
            logger.log_file_action(thread="gui", file=path, action="waiting")
        else:
            self._image_frames[path].tkraise()
            logger.log_file_action(thread="gui", file=path, action="displaying")
        self._current_image_path = path

    def select_all(self, unselect = False):
        for frame in self._image_frames.values():
            if unselect:
                frame.unselect()
            else:
                frame.select()

    def is_waiting_on_loader(self) -> bool:
        return self._current_image_path not in self