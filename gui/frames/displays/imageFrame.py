import tkinter as tk
from PIL import Image, ImageTk
from typing import Tuple, Dict, Callable, Set
from pathlib import Path
import math

from .loader import Loader
from .selector import Selector



_GAP_SIZE = 3
_BORDER_SIZE = 3


# TODO: Image seems to be slightly cut of when selected by the border - redo!
class ImageFrame(tk.Frame):

    def __init__(self, master: tk.Widget, image: Image.Image, image_bounds: Tuple[int, int], selected: bool = False):
        super().__init__(master=master)
        
        self._image = image
        self._selected = selected

        self._create_gui_elements(image_bounds=image_bounds)
        
        if self._selected:
            self.select()
        else:
            self.unselect()

    @staticmethod
    def calculate_new_size_from_bounds(image_bounds: Tuple[int, int], current_size: Tuple[int, int]) -> Tuple[int, int]:
        width_factor = image_bounds[0] / current_size[0]
        height_factor = image_bounds[1] / current_size[1]
        factor = min(width_factor, height_factor)
        return (int(math.floor(current_size[0] * factor)), int(math.floor(current_size[1] * factor))) 

    def _create_gui_elements(self, image_bounds: Tuple[int, int], resample = Image.Resampling.LANCZOS):
        new_size = ImageFrame.calculate_new_size_from_bounds(image_bounds=image_bounds, current_size=self._image.size)

        self._display_image = ImageTk.PhotoImage(image = self._image.resize(size=new_size, resample=resample))

        image_width = self._display_image.width()
        image_height = self._display_image.height()

        self._border_frame = tk.Frame(self,
                        width=image_width + _GAP_SIZE + _BORDER_SIZE,
                        height=image_height + _GAP_SIZE + _BORDER_SIZE,
                        background="#074bb8")
        
        self._gap_frame = tk.Frame(self._border_frame,
                        width=image_width + _GAP_SIZE,
                        height=image_height + _GAP_SIZE,
                        background="white")

        self._selected_label = tk.Label(master=self._gap_frame, image=self._display_image)

        self._border_frame.pack_propagate(False)
        self._gap_frame.pack_propagate(False)
        self._selected_label.pack_propagate(False)

        self._selected_label.pack(padx=_GAP_SIZE, pady=_GAP_SIZE)
        self._gap_frame.pack(padx=_BORDER_SIZE, pady=_BORDER_SIZE)

        self._unselected_label = tk.Label(master=self, image=self._display_image)

        self._unselected_label.pack_propagate(False)
     
    def select(self) -> None:
        self._selected = True
        self._unselected_label.pack_forget()
        self._border_frame.pack()

    def unselect(self) -> None:
        self._selected = False
        self._unselected_label.pack()
        self._border_frame.pack_forget()

    def toggle_selected(self) -> None:
        if self._selected:
            self.unselect()
        else:
            self.select()



class ImageFrameFactory:

    def __init__(self, master: tk.Widget, loader: Loader, selector: Selector, image_bounds: Tuple[int, int]):
        self._frames: Dict[Path, ImageFrame] = {}
        self._master = master
        self._selector = selector
        self._current_image_bounds = image_bounds
        self._frame_creation_callbacks: Set[Callable[[Path], None]] = set()

        loader.subscribe_on_load(callback = self._on_load)
        loader.subscribe_on_unload(callback = self._on_unload)

    def _on_load(self, path: Path, image: Image.Image) -> None:
        self._create_image_frame(path=path, image=image)

    def _on_unload(self, unloaded: Path) -> None:
        if unloaded is not None:
            self._frames.pop(unloaded)

    def _trigger_frame_creation(self, path: Path):
        for callback in self._frame_creation_callbacks:
            callback(path)

    def _create_image_frame(self, path: Path, image: Image.Image) -> None:
        self._frames[path] = ImageFrame(master=self._master,
                                        image=image,
                                        image_bounds=self._current_image_bounds,
                                        selected=self._selector.is_selected(path))
        self._trigger_frame_creation(path=path)

    def get_frame(self, path: Path) -> ImageFrame:
        try:
            return self._frames[path]
        except KeyError as ex:
            raise KeyError(f"No frame for '{str(path)}'") from ex
        
    def select_all(self, unselect = False):
        for frame in self._frames.values():
            if unselect:
                frame.unselect()
            else:
                frame.select()

    def subscribe_on_frame_creation(self, callback: Callable[[Path], None]) -> None:
        self._frame_creation_callbacks.add(callback)
    
    def unsubscribe_on_frame_creation(self, callback: Callable[[Path], None]) -> None:
        self._frame_creation_callbacks.remove(callback)



