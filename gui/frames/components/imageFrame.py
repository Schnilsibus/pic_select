import tkinter as tk
from PIL import Image, ImageTk
from typing import Tuple
import math
from time import perf_counter

from .borderedImageFrame import BorderedImageFrame
from .paddedImageFrame import PaddedImageFrame

from ....log import logger



_GAP_SIZE = 10
_BORDER_SIZE = 10



class ImageFrame(tk.Frame):

    def __init__(self, master: tk.Widget, display_size: Tuple[int, int], image: Image.Image, selected: bool = False):
        super().__init__(master=master, background="yellow", width=display_size[0], height=display_size[1])

        image_bounds = display_size[0] - _GAP_SIZE - _BORDER_SIZE, display_size[1] - _GAP_SIZE - _BORDER_SIZE
        image_size = ImageFrame.calculate_max_inbound_size(image_bounds=image_bounds, full_size=(image.width, image.height))

        t0 = perf_counter()*1000
        resized_image = image.resize(image_size, resample=Image.Resampling.LANCZOS)
        t1 = perf_counter()*1000
        self._image = ImageTk.PhotoImage(image=resized_image)
        t2 = perf_counter()*1000
        self._selected_image_frame = BorderedImageFrame(master=self, image=self._image, padding=_GAP_SIZE, borderwidth=_BORDER_SIZE)
        t3 = perf_counter()*1000
        self._unselected_image_frame = PaddedImageFrame(master=self, image=self._image, padding=_GAP_SIZE + _BORDER_SIZE)
        t4 = perf_counter()*1000

        logger.log_benchmark("resize", t1-t0)
        logger.log_benchmark("tk image", t2-t1)
        logger.log_benchmark("border frame", t3-t2)
        logger.log_benchmark("padded frame", t4-t3)

        self._selected_image_frame.place(relx=0.5, rely=0.5, anchor="center")
        t5 = perf_counter()*1000
        self._unselected_image_frame.place(relx=0.5, rely=0.5, anchor="center")
        t6 = perf_counter()*1000

        logger.log_benchmark("place border", t5-t4)
        logger.log_benchmark("place padded", t6-t5)

        self._selected = selected

        if self._selected:
            self.select()
        else:
            self.unselect()

    @staticmethod
    def calculate_max_inbound_size(image_bounds: Tuple[int, int], full_size: Tuple[int, int]) -> Tuple[int, int]:
        width_factor = image_bounds[0] / full_size[0]
        height_factor = image_bounds[1] / full_size[1]
        factor = min(width_factor, height_factor)
        return (int(math.floor(full_size[0] * factor)), int(math.floor(full_size[1] * factor)))

    @property
    def selected(self) -> bool:
        return self._selected

    def select(self) -> None:
        self._selected = True
        self._selected_image_frame.tkraise()

    def unselect(self) -> None:
        self._selected = False
        self._unselected_image_frame.tkraise()

    def toggle(self) -> None:
        if self.selected:
            self.unselect()
        else:
            self.select()