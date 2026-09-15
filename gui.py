import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import Literal, Tuple
import math
from time import time_ns

from .loader import LoaderWorker
from .selector import Selector
from .image_frame import ImageFrame, ImageFrameFactory, LoadFrame
from .clipboard import copy_files_to_clipboard


_PADDING_PERCENT = 0.15

_MIN_WINDOW_DIM =  int(25 / _PADDING_PERCENT) + 1

def ask_file_name() -> Path:
    _root = tk.Tk()
    _root.withdraw()
    path = filedialog.askopenfilename()
    _root.destroy()
    return Path(path)   

class GuiControl(object):
    
    def __init__(self, master: tk.Tk, loader_worker: LoaderWorker, selector: Selector, fullscreen = True):
        self._ROOT: tk.Tk = master
        self._loader_worker = loader_worker
        self._selector = selector

        self._loader = self._loader_worker.get_loader()
        
        self._ROOT.title(str(self._loader.get_directory()))
        self._ROOT.bind("<Left>", self._on_left_arrow_key)
        self._ROOT.bind("<Right>", self._on_right_arrow_key)
        self._ROOT.bind("<space>", self._on_space)
        self._ROOT.bind("<Control-c>", self._on_copy)
        self._ROOT.bind("<Control-C>", self._on_copy)
        self._ROOT.bind("<Control-a>", self._on_strg_a)
        self._ROOT.bind("<Control-A>", self._on_strg_a)
        self._ROOT.bind("<Control-t>", self._on_exit)
        self._ROOT.bind("<Control-T>", self._on_exit)
        self._ROOT.bind("<Escape>", self._on_escape)
        self._ROOT.bind("<F11>", self._on_f_11)
        
        self._ROOT.minsize(_MIN_WINDOW_DIM, _MIN_WINDOW_DIM)
        self._ROOT.state("zoomed")
        self._ROOT.focus_force()
        self._ROOT.lift()

        self._is_fullscreen = fullscreen
        if self._is_fullscreen:
            self.enter_fullscreen()

        self._WIDTH: int = self._ROOT.winfo_width()
        self._HEIGHT: int = self._ROOT.winfo_height()

        self._last_arrow: Literal["Left", "Right"] = None

        self._loader_busy: bool = False

        self._loader_worker.subscribe_on_idle(callback=self._on_loader_idle)
        self._loader_worker.subscribe_on_busy(callback=self._on_loader_busy)

        self._image_frame_factory = ImageFrameFactory(master=self._ROOT,
                                                      loader=self._loader,
                                                      selector=self._selector,
                                                      image_bounds=self._calculate_image_bounds())
        self._image_frame_factory.subscribe_on_frame_creation(callback=self._on_new_frame_created)

        self._current_image_path: Path = None
        self._current_image_frame: ImageFrame = None
        self._current_image_name: tk.StringVar = tk.StringVar()
        self._current_image_label: tk.Label = tk.Label(master=self._ROOT,
                                                       textvariable=self._current_image_name,
                                                       font=("Arial, -20"),
                                                       background="white")
        self._current_image_label.place(relx=0.5, rely=1.0, y=-5, anchor=tk.S)

        self._load_frame: LoadFrame = LoadFrame(master=self._ROOT)
        self._load_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relheight=1.0, relwidth=1.0)
        self._separator_frame = tk.Frame(master=self._ROOT, background="white")
        self._separator_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relheight=1.0, relwidth=1.0)

        self._busy_indicator: tk.Label = tk.Label(master=self._ROOT,
                                                  text="Loading ...",
                                                  font=("Arial", -20),
                                                  background="white")
        self._busy_indicator.place(relx=0, rely=1, anchor="sw")
    
    def _calculate_image_bounds(self) -> Tuple[int, int]:
        padding = min(self._WIDTH, self._HEIGHT) * _PADDING_PERCENT
        padding = int(math.ceil(padding))
        return (self._WIDTH - padding, self._HEIGHT - padding)
    
    def _on_left_arrow_key(self, event) -> None:
        if self.is_waiting_on_loader() and self._last_arrow == "Left":
            return None

        self._last_arrow = "Left"
        path = self._loader.get_neighbor_path("Left", anchor=self._current_image_path)

        if path is None:
            return None
        
        self.update_current_image(path=path)
        self.refresh_display()
        
        self._loader_worker.queue_backward()


    def _on_right_arrow_key(self, event) -> None:
        if self.is_waiting_on_loader() and self._last_arrow == "Right":
            return None
        
        self._last_arrow = "Right"
        path = self._loader.get_neighbor_path("Right", anchor=self._current_image_path)

        if path is None:
            return None
        
        self.update_current_image(path=path)
        self.refresh_display()
        
        self._loader_worker.queue_forward()

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
        
        if self.is_waiting_on_loader() and self._current_image_path == path:
            self.update_current_image(path=path)
        
        self.refresh_display()

    def _on_f_11(self, event) -> None:
        self.toggle_fullscreen()

    def _on_loader_busy(self) -> None:
        self._loader_busy = True
        self.refresh_display()

    def _on_loader_idle(self) -> None:
        self._loader_busy = False
        self.refresh_display()

    def _on_exit(self, event) -> None:
        self._ROOT.destroy()

    def toggle_fullscreen(self) -> None:
        self._is_fullscreen = not self._is_fullscreen
        self._ROOT.attributes("-fullscreen", self._is_fullscreen)
    
    def enter_fullscreen(self) -> None:
        self._ROOT.attributes("-fullscreen", True)
        self._is_fullscreen = True

    def exit_fullscreen(self) -> None:
        self._ROOT.attributes("-fullscreen", False)
        self._is_fullscreen = False

    def refresh_display(self) -> None:
        self._separator_frame.tkraise()
        
        if self.is_waiting_on_loader():
            self._load_frame.tkraise()
        else:
            self._current_image_frame.tkraise()
            self._current_image_label.tkraise()

        if self._loader_busy:
            self._busy_indicator.tkraise()
        
    def update_current_image(self, path: Path) -> None:
        self._current_image_path = path
        self._current_image_name.set(value=path.name)
        
        try:
            self._current_image_frame = self._image_frame_factory.get_frame(path=path)
        except KeyError as ex:
            self._current_image_frame = None
            self._load_frame.set_text(name=path.name)
            return None

    def is_waiting_on_loader(self) -> bool:
        return self._current_image_frame is None