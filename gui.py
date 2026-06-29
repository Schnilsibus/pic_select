import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
from loader import Loader
from typing import Dict
from pathlib import Path

_PADDING = 100
_MIN_SIZE = "600x600"

# TODO: solve order: at the moment: first load then change display but the whole point is to change display first then load

def ask_file_name() -> str:
    _root = tk.Tk()
    _root.withdraw()
    path = filedialog.askopenfilename()
    _root.destroy()
    return path

class Display(object):
    
    def __init__(self, loader: Loader, fullscreen = True):
        self._loader = loader
        self._loader.subscribe_on_load(callback=self._on_load)
        
        self._fullscreen = fullscreen
        
        self._ROOT: tk.Tk = tk.Tk()
        self._ROOT.withdraw()
        self._ROOT.bind("<Left>", self._on_left_arrow_key)
        self._ROOT.bind("<Right>", self._on_right_arrow_key)
        self._ROOT.bind("<Escape>", self._stop_loop)

        self._current_label: tk.Label = None

        self._WIDTH: int = None
        self._HEIGHT: int = None

        self._labels: Dict[Path, (tk.tkLabel, Image.Image)] = {}
        
        if self._fullscreen:
            self._ROOT.attributes('-fullscreen', True)
            self._ROOT.attributes("-topmost", True)
        else:
            self._ROOT.geometry(_MIN_SIZE)

    def _on_load(self, loaded: Image.Image, unloaded: Image.Image) -> None:
        self._create_label(path=Path(loaded.filename), image=loaded)
        self._labels.pop(Path(unloaded.filename))

    def _on_left_arrow_key(self, event) -> None:
        self.show(self._loader.get_neighbor_path("Left"))
        self._loader.backward()

    def _on_right_arrow_key(self, event) -> None:
        self.show(self._loader.get_neighbor_path("Right"))
        self._loader.forward()

    def _stop_loop(self, event) -> None:
        self.destroy_display()

    def _create_labels(self) -> None:
        for path, image in self._loader.get_images().items():
            self._create_label(path=path, image=image)

    def _create_label(self, path: Path, image: Image.Image) -> None:
        display_image = ImageOps.exif_transpose(image=image)
        display_image.thumbnail(size = (self._WIDTH - _PADDING, self._HEIGHT - _PADDING), resample = Image.Resampling.LANCZOS)
        
        tk_image = ImageTk.PhotoImage(display_image)
        self._labels[path] = (tk.Label(self._ROOT, image=tk_image), tk_image)

    def start_display(self) -> None:
        self._ROOT.deiconify()
        self._ROOT.focus_force()
        self._ROOT.lift()

        self._WIDTH: int = self._ROOT.winfo_width()
        self._HEIGHT: int = self._ROOT.winfo_height()

        self._create_labels()
        self.show(path=self._loader.get_current_path())
        self._ROOT.mainloop()
        
    def show(self, path: Path) -> None:
        if self._current_label is not None:
            self._current_label.pack_forget()

        label, image = self._labels[path]
        self._current_label = label

        self._current_label.pack(side = "bottom", fill = "both", expand = "yes")
        self._ROOT.update()

    def destroy_display(self) -> None:
        self._ROOT.destroy()