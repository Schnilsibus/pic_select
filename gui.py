import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
from loader import Loader
from selector import Selector
from image_frame import ImageFrame
from clipboard import copy_files_to_clipboard
from typing import Dict
from pathlib import Path

# TODO: remember user input (right now klicks are ignored if loader is busy) OR figure out how to not wait for loader (defeats the point)
"""
THE PROBLEM:
What happens: multiple klicks overwhelm the system:
- on_left/ right is triggerd
    - this will show the next frame
    - call the loader to update
        - this will call on_load which creates new frames (VERY SLOW!!)
If a new keyboard event is triggered before the GUI has created frames:
    - this will show the next frame
    - call the loader to update
        - call on_load BUT this on_load has priority!! (idk why - it is beeing processed first!)
        - SOOO the frames that are needed more in the future are created first - which is bad!

The Thing that takes forever is exif_transpose

SOLUTION:
    - when calling show - check if the frame exists yet
    - solve the order in which the frames are created - maybe py FiFo queeu implementation -> try remove root.update() calls
    - maybe restrict user input to smth reasonable research online
        or logical whould be to only allow _preload_length quick clicks then wait 
        or query how many frames created and ignore a click if it is requesting a not loaded frame - give visual feedback
    - analize times for frame creation and try to create ImageFrames quicker -> exif transpose takes forever
        so move transpose logic to loader -> give the loader its own thread
"""
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
        self._ROOT.title(str(self._loader.get_directory()))
        self._ROOT.withdraw()
        self._ROOT.bind("<Left>", self._on_left_arrow_key)
        self._ROOT.bind("<Right>", self._on_right_arrow_key)
        self._ROOT.bind("<space>", self._on_space)
        self._ROOT.bind("<Control-c>", self._on_copy)
        self._ROOT.bind("<Control-C>", self._on_copy)
        self._ROOT.bind("<Control-a>", self._on_strg_a)
        self._ROOT.bind("<Control-A>", self._on_strg_a)
        self._ROOT.bind("<Escape>", self._on_escape)

        self._current_image_name: tk.StringVar = tk.StringVar()
        self._current_image_label: tk.Label = tk.Label(master=self._ROOT, textvariable=self._current_image_name, font=("Arial, 18"))

        self._current_image_frame: ImageFrame = None

        self._WIDTH: int = None
        self._HEIGHT: int = None

        self._image_frames: Dict[Path, ImageFrame] = {}
        
        self._ROOT.state("zoomed")

    def _on_left_arrow_key(self, event) -> None:
        path = self._loader.get_neighbor_path("Left")
        if path is not None:
            self.show(path=path)
            self._loader.backward()

    def _on_right_arrow_key(self, event) -> None:
        path = self._loader.get_neighbor_path("Right")
        if path is not None:
            self.show(path=path)
            self._loader.forward()

    def _on_load(self, loaded: Image.Image, unloaded: Image.Image, count: int) -> None:
        if unloaded is not None:
            self._image_frames.pop(Path(unloaded.filename))
        if loaded is not None:
            self._create_image_frame(path=Path(loaded.filename), image=loaded)
        frames = ", ".join(sorted([str(int(k.name[4:8])) for k in self._image_frames.keys()]))
        print(f"GUI   -UPDATE {count:04d}: {len(self._image_frames)} - {frames}\n")

    def _on_space(self, event) -> None:
        path = self._loader.get_current_path()
        self._selector.toggle(key=path)
        self._current_image_frame.toggle_selected()

    def _on_copy(self, evetn) -> None:
        copy_files_to_clipboard(self._selector.get_selection())

    def _on_strg_a(self, event) -> None:
        paths = self._loader.get_all_paths()
        self._selector.multi_select(keys=paths)
        for frame in self._image_frames.values():
            frame.select()
    
    def _on_escape(self, event) -> None:
        self._selector.unselect_all()
        for frame in self._image_frames.values():
            frame.unselect()

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

        self._current_image_label.place(relx=0.5, rely=1.0, anchor=tk.S)

        self._create_image_frames()
        self.show(path=self._loader.get_current_path())
        
        self._ROOT.mainloop()
        
    def show(self, path: Path) -> None:
        if self._current_image_frame is not None:
            self._current_image_frame.place_forget()

        self._current_image_name.set(value=path.name)

        self._current_image_frame = self._image_frames[path]

        self._current_image_frame.place(relx=0.5, rely=0.5, anchor="center")
        self._ROOT.update()