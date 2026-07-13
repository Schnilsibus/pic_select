import tkinter as tk
from tkinter import filedialog
from pathlib import Path

from .loader import Loader
from .selector import Selector
from .image_frame import ImageFrame, ImageFrameFactory, LoadFrame
from .clipboard import copy_files_to_clipboard

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

    - maybe restrict user input to smth reasonable research online
        or logical whould be to only allow _preload_length quick clicks then wait 
        or query how many frames created and ignore a click if it is requesting a not loaded frame - give visual feedback
        
    - give the loader its own thread
"""
_PADDING = 100

def ask_file_name() -> Path:
    _root = tk.Tk()
    _root.withdraw()
    path = filedialog.askopenfilename()
    _root.destroy()
    return Path(path)

class GuiControl(object):
    
    def __init__(self, master: tk.Tk, loader: Loader, selector: Selector):
        self._ROOT: tk.Tk = master
        self._loader = loader
        self._selector = selector
        
        self._ROOT.title(str(self._loader.get_directory()))
        self._ROOT.bind("<Left>", self._on_left_arrow_key)
        self._ROOT.bind("<Right>", self._on_right_arrow_key)
        self._ROOT.bind("<space>", self._on_space)
        self._ROOT.bind("<Control-c>", self._on_copy)
        self._ROOT.bind("<Control-C>", self._on_copy)
        self._ROOT.bind("<Control-a>", self._on_strg_a)
        self._ROOT.bind("<Control-A>", self._on_strg_a)
        self._ROOT.bind("<Escape>", self._on_escape)

        self._ROOT.state("zoomed")
        self._ROOT.focus_force()
        self._ROOT.lift()

        self._WIDTH: int = self._ROOT.winfo_width()
        self._HEIGHT: int = self._ROOT.winfo_height()

        self._image_frame_factory = ImageFrameFactory(master=self._ROOT,
                                                      loader=self._loader,
                                                      selector=self._selector,
                                                      max_image_size=(self._WIDTH - _PADDING, self._HEIGHT - _PADDING))
        self._image_frame_factory.subscribe_on_frame_creation(callback=self._on_new_frame_created)

        self._current_image_frame: ImageFrame = None
        self._current_image_name: tk.StringVar = tk.StringVar()
        self._current_image_label: tk.Label = tk.Label(master=self._ROOT,
                                                       textvariable=self._current_image_name,
                                                       font=("Arial, 18"),
                                                       background="white")

        self._load_frame: LoadFrame = LoadFrame(master=self._ROOT)
        self._load_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relheight=1.0, relwidth=1.0)
        self._separator_frame = tk.Frame(master=self._ROOT, background="white")
        self._separator_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relheight=1.0, relwidth=1.0)

        self._current_image_label.place(relx=0.5, rely=1.0, anchor=tk.S)

    def _on_left_arrow_key(self, event) -> None:
        print("LEFT")
        if self.is_waiting_on_loader():
            return None

        path = self._loader.get_neighbor_path("Left")

        if path is None:
            return None
        
        self.update_current_image(path=path)
        self.refresh_display()
        
        self._loader.backward()

    def _on_right_arrow_key(self, event) -> None:
        print("RIGHT")
        if self.is_waiting_on_loader():
            return None
        
        path = self._loader.get_neighbor_path("Right")
        
        if path is None:
            return None
        
        self.update_current_image(path=path)
        self.refresh_display()
        
        self._loader.forward()

    def _on_space(self, event) -> None:
        path = self._loader.get_current_path()
        self._selector.toggle(key=path)
        self._current_image_frame.toggle_selected()

    def _on_copy(self, evetn) -> None:
        copy_files_to_clipboard(self._selector.get_selection())

    def _on_strg_a(self, event) -> None:
        paths = self._loader.get_all_paths()
        self._selector.multi_select(keys=paths)
        self._image_frame_factory.select_all()
    
    def _on_escape(self, event) -> None:
        self._selector.unselect_all()
        self._image_frame_factory.select_all(unselect=True)
    
    def _on_new_frame_created(self, path: Path) -> None:
        self._image_frame_factory.get_frame(path=path).place(relx=0.5, rely=0.5, anchor="center")
        
        if self.is_waiting_on_loader() and self._current_image_name.get() == path.name:
            self.update_current_image(path=path)
        
        self.refresh_display()

    # TODO: figure out proper first loading logic 
    def refresh_display(self) -> None:
        self._separator_frame.tkraise()
        
        if self.is_waiting_on_loader():
            self._load_frame.tkraise()
        else:
            self._current_image_frame.tkraise()
            self._current_image_label.tkraise()
        
    def update_current_image(self, path: Path) -> None:
        self._current_image_name.set(value=path.name)
        
        try:
            self._current_image_frame = self._image_frame_factory.get_frame(path=path)
        except KeyError as ex:
            self._current_image_frame = None
            self._load_frame.set_text(name=path.name)
            print(f"displaying load {path.name}")
            return None
        
        print(f"displaying image {path.name}")

    def is_waiting_on_loader(self) -> bool:
        return self._current_image_frame is None