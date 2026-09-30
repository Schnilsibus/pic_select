import tkinter as tk
from tkinter import ttk
from typing import List, Tuple
from pathlib import Path

from ...logic.load.loaderController import LoaderController
from ...logic.selector import Selector

from .displays.selectImageFrame import SelectImageFrame
from .displays.imageViewFrame import ImageViewFrame

_PADDING_PIXELS = 70

class DisplayFrame(ttk.Frame):

    def __init__(self, master: tk.Widget, loaderController: LoaderController, selector: Selector):
        super().__init__(master=master)

        loaderController.subscribe_on_busy(callback=self._on_loader_busy)
        loaderController.subscribe_on_idle(callback=self._on_loader_idle)

        selector.subscribe_on_select(callback=self._on_select)

        self._selection_count: tk.StringVar = tk.StringVar(self, f"{0:04}")
        self._selection_count_label: tk.Label = tk.Label(master=self,
                                                        textvariable=self._selection_count,
                                                        font=("Arial", -20),
                                                        background="grey")
        self._selection_count_label.place(relx=0, rely=0, anchor="nw")

        self._loader_busy: tk.StringVar = tk.StringVar(self, "")
        self._busy_indicator_label: tk.Label = tk.Label(master=self,
                                                        textvariable=self._loader_busy,
                                                        font=("Arial", -20),
                                                        background="grey")
        self._busy_indicator_label.place(relx=0, rely=1, anchor="sw")

        self._select_image_frame: SelectImageFrame = None
        self._image_view_frame: ImageViewFrame = None
                
    def _on_loader_busy(self) -> None:
        self._loader_busy.set("Loading ...")

    def _on_loader_idle(self) -> None:
        self._loader_busy.set("")

    def _on_select(self, selection: List[Path]) -> None:
        self._selection_count.set(f"{len(selection):04}")

    def setup_displays(self, selector: Selector) -> None:
        self.master.update_idletasks()

        self._image_view_frame = ImageViewFrame(master=self, display_size=self.display_size, selector=selector)
        self._select_image_frame.place(relx=0.5, rely=0.5, anchor="center")

        self._select_image_frame = SelectImageFrame(master=self, display_size=self.display_size())
        self._select_image_frame.place(relx=0.5, rely=0.5, anchor="center")

    def display_size(self) -> Tuple[int, int]:
        width, height = self.winfo_width(), self.winfo_height()
        return width - _PADDING_PIXELS, height -_PADDING_PIXELS

    def show_image(self, path: Path) -> None:
        raise NotImplementedError()

    def show_loading(self, path: Path) -> None:
        self._load_frame.set_text(name=path.name)
        self._load_frame.tkraise()

    def show_select_image(self) -> None:
        self._select_image_frame.tkraise()



"""
class GuiControl(object):
    
    def __init__(self, master: tk.Tk, loader_worker: LoaderWorker, selector: Selector, fullscreen = True):


        self._WIDTH: int = self._ROOT.winfo_width()
        self._HEIGHT: int = self._ROOT.winfo_height()



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
        
    def _on_new_frame_created(self, path: Path) -> None:
        self._image_frame_factory.get_frame(path=path).place(relx=0.5, rely=0.5, anchor="center")
        
        if self.is_waiting_on_loader() and self._current_image_path == path:
            self.update_current_image(path=path)
        
        self.refresh_display()

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

"""