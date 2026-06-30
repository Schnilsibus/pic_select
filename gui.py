import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
from loader import Loader
from selector import Selector
from image_frame import ImageFrame
from typing import Dict
from pathlib import Path

# TODO: copy to clipboard on enter
# TODO: react to strg+c
# TODO: make Gui more snappy - see what can be done

_PADDING = 100
_BORDER_SIZE = 3
_GAP_SIZE = 3
_MIN_SIZE = "600x600"

def ask_file_name() -> str:
    _root = tk.Tk()
    _root.withdraw()
    path = filedialog.askopenfilename()
    _root.destroy()
    return path

class Display(object):
    
    def __init__(self, loader: Loader, selector: Selector, fullscreen = True):
        self._loader = loader
        self._loader.subscribe_on_load(callback=self._on_load)

        self._selector = selector
        
        self._fullscreen = fullscreen
        
        self._ROOT: tk.Tk = tk.Tk()
        self._ROOT.withdraw()
        self._ROOT.bind("<Left>", self._on_left_arrow_key)
        self._ROOT.bind("<Right>", self._on_right_arrow_key)
        self._ROOT.bind("<Escape>", self._stop_loop)
        self._ROOT.bind("<Return>", self._on_enter)
        self._ROOT.bind("<space>", self._on_space)

        self._current_image_frame: ImageFrame = None

        self._WIDTH: int = None
        self._HEIGHT: int = None

        self._image_frames: Dict[Path, ImageFrame] = {}
        
        if self._fullscreen:
            self._ROOT.attributes('-fullscreen', True)
            self._ROOT.attributes("-topmost", True)
        else:
            self._ROOT.geometry(_MIN_SIZE)

    def _on_load(self, loaded: Image.Image, unloaded: Image.Image) -> None:
        self._image_frames.pop(Path(unloaded.filename))
        if loaded is None:
            raise RuntimeError("No More Images!")
        self._create_image_frame(path=Path(loaded.filename), image=loaded)

    def _on_left_arrow_key(self, event) -> None:
        self.show(self._loader.get_neighbor_path("Left"))
        self._loader.backward()

    def _on_right_arrow_key(self, event) -> None:
        self.show(self._loader.get_neighbor_path("Right"))
        self._loader.forward()

    def _on_space(self, event) -> None:
        path = self._loader.get_current_path()
        self._selector.toggle(key=path)
        self._current_image_frame.toggle_selected()

    def _on_enter(self, event) -> None:
        for path in self._selector.get_selection():
            print(path)

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
        
    def show(self, path: Path) -> None:
        if self._current_image_frame is not None:
            self._current_image_frame.place_forget()

        self._current_image_frame = self._image_frames[path]

        self._current_image_frame.place(relx=0.5, rely=0.5, anchor="center")
        self._ROOT.update()

    def destroy_display(self) -> None:
        self._ROOT.destroy()