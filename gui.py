import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
from loader import Loader
from selector import Selector
from image_frame import ImageFrame
from clipboard import copy_files_to_clipboard
from typing import Dict, List
from pathlib import Path

# TODO: make a reset functionality (unselect all)
# TODO: display img name

_PADDING = 100

def ask_file_name() -> str:
    _root = tk.Tk()
    _root.withdraw()
    path = filedialog.askopenfilename()
    _root.destroy()
    return path

class Display(object):
    
    def __init__(self, loader: Loader, selector: Selector):
        self._loader = loader
        self._loader.subscribe_on_load(callback=self._on_load)

        self._selector = selector
        
        self._ROOT: tk.Tk = tk.Tk()
        self._ROOT.withdraw()
        self._ROOT.bind("<Left>", self._on_left_arrow_key)
        self._ROOT.bind("<Right>", self._on_right_arrow_key)
        self._ROOT.bind("<Escape>", self._stop_loop)
        self._ROOT.bind("<space>", self._on_space)
        self._ROOT.bind("<Control-c>", self._on_copy)
        self._ROOT.bind("<Control-C>", self._on_copy)

        self._current_image_frame: ImageFrame = None

        self._WIDTH: int = None
        self._HEIGHT: int = None

        self._image_frames: Dict[Path, ImageFrame] = {}
        
        self._ROOT.state("zoomed")

    def _on_load(self, loaded: Image.Image, unloaded: Image.Image) -> None:
        self._image_frames.pop(Path(unloaded.filename))
        if loaded is not None:
            self._create_image_frame(path=Path(loaded.filename), image=loaded)

    def _on_left_arrow_key(self, event) -> None:
        if self.show(self._loader.get_neighbor_path("Left")):
            self._loader.backward()

    def _on_right_arrow_key(self, event) -> None:
        if self.show(self._loader.get_neighbor_path("Right")):
            self._loader.forward()

    def _on_space(self, event) -> None:
        path = self._loader.get_current_path()
        self._selector.toggle(key=path)
        self._current_image_frame.toggle_selected()

    def _on_copy(self, evetn) -> None:
        copy_files_to_clipboard(self._selector.get_selection())

    def _stop_loop(self, event) -> None:
        self.destroy_display()

    def _create_image_frames(self) -> None:
        for path, image in self._loader.get_images().items():
            self._create_image_frame(path=path, image=image)

    def _create_image_frame(self, path: Path, image: Image.Image) -> None:
        self._image_frames[path] = ImageFrame(master=self._ROOT,
                                              image=image,
                                              max_image_size=(self._WIDTH - _PADDING, self._HEIGHT - _PADDING),
                                              selected=self._selector.is_selected(path))

    def create_display_image(self, image: Image.Image) -> ImageTk.PhotoImage:
        path = self._loader.get_current_path()
        display_image = ImageOps.exif_transpose(image=image)
        display_image.thumbnail(size = (self._WIDTH - _PADDING, self._HEIGHT - _PADDING), resample = Image.Resampling.LANCZOS)

    def start_display(self) -> None:
        self._ROOT.deiconify()
        self._ROOT.focus_force()
        self._ROOT.lift()

        self._WIDTH: int = self._ROOT.winfo_width()
        self._HEIGHT: int = self._ROOT.winfo_height()

        self._create_image_frames()
        self.show(path=self._loader.get_current_path())
        
        self._ROOT.mainloop()
        
    def show(self, path: Path) -> bool:
        if path not in self._image_frames:
            return False

        if self._current_image_frame is not None:
            self._current_image_frame.place_forget()

        self._current_image_frame = self._image_frames[path]

        self._current_image_frame.place(relx=0.5, rely=0.5, anchor="center")
        self._ROOT.update()

    def destroy_display(self) -> None:
        self._ROOT.destroy()