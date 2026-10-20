import tkinter as tk
from tkinter import ttk
from typing import Tuple
from pathlib import Path

from ...logic.load.loaderThread import LoaderThread
from ...logic.load.loader import Loader
from ...logic.selector import Selector

from .displays.selectImageFrame import SelectImageFrame
from .displays.imageViewFrame import ImageViewFrame



_PADDING_PIXELS = 70



class DisplayFrame(ttk.Frame):

    def __init__(self, master: tk.Widget, loader_controller: LoaderThread, selector: Selector):
        super().__init__(master=master)

        loader_controller.subscribe_on_busy(callback=self._on_loader_busy)
        loader_controller.subscribe_on_idle(callback=self._on_loader_idle)

        selector.subscribe_on_select(callback=self._on_select)

        self._selection_count: tk.StringVar = tk.StringVar(self, f"{0:05}")
        self._selection_count_label: tk.Label = tk.Label(master=self,
                                                        textvariable=self._selection_count,
                                                        font=("Arial", -20))
        self._selection_count_label.place(relx=0, rely=0, anchor="nw")

        self._loader_busy: tk.StringVar = tk.StringVar(self, "")
        self._busy_indicator_label: tk.Label = tk.Label(master=self,
                                                        textvariable=self._loader_busy,
                                                        font=("Arial", -20))
        self._busy_indicator_label.place(relx=0, rely=1, anchor="sw")

        self._image_name: tk.StringVar = tk.StringVar(self, "")
        self._image_name_label: tk.Label = tk.Label(master=self,
                                                    textvariable=self._image_name,
                                                    font=("Arial", -20))
        self._image_name_label.place(relx=0.5, rely=1, anchor="s")

        self._select_image_frame: SelectImageFrame = None
        self._image_view_frame: ImageViewFrame = None

    @property
    def image_view_frame(self) -> ImageViewFrame:
        return self._image_view_frame
                
    def _on_loader_busy(self) -> None:
        self._loader_busy.set("Loading ...")

    def _on_loader_idle(self) -> None:
        self._loader_busy.set("")

    def _on_new_image(self, path: Path) -> None:
        self.show_image(path=path)

    def _on_select(self, path: Path, selected: bool, count: int) -> None:
        self._selection_count.set(f"{count:05}")

    def setup_displays(self, selector: Selector, loader: Loader) -> None:
        self.master.update_idletasks()

        self._image_view_frame = ImageViewFrame(master=self, display_size=self.display_size(), selector=selector, loader=loader)
        self._image_view_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self._select_image_frame = SelectImageFrame(master=self, display_size=self.display_size())
        self._select_image_frame.place(relx=0.5, rely=0.5, anchor="center")

    def display_size(self) -> Tuple[int, int]:
        width, height = self.winfo_width(), self.winfo_height()
        return width - _PADDING_PIXELS, height -_PADDING_PIXELS

    def show_image(self, path: Path) -> None:
        self._image_name.set(path.name)
        self._image_view_frame.display_image_frame(path=path)
        self._image_view_frame.tkraise()
        self._image_view_frame.focus()

    def show_select_image(self) -> None:
        self._select_image_frame.tkraise()
        self._select_image_frame.focus()

    def set_image_name(self, path: Path) -> None:
        self._image_name.set(path.name)