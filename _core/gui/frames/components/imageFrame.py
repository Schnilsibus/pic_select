import tkinter as tk
from PIL import Image, ImageTk
from typing import Tuple
import math
from time import perf_counter

from .borderedImageFrame import BorderedImageFrame
from .paddedImageFrame import PaddedImageFrame



_GAP_SIZE = 10
_BORDER_SIZE = 10



class ImageFrame(tk.Frame):

    def __init__(self, master: tk.Widget, display_size: Tuple[int, int], image: Image.Image, selected: bool = False):
        super().__init__(master=master, width=display_size[0], height=display_size[1])

        image_bounds = display_size[0] - (_GAP_SIZE * 2) - (_BORDER_SIZE * 2), display_size[1] - (_GAP_SIZE * 2) - (_BORDER_SIZE * 2)
        image_size = ImageFrame.calculate_max_inbound_size(image_bounds=image_bounds, full_size=(image.width, image.height))
        resized_image = image.resize(image_size, resample=Image.Resampling.LANCZOS)
        self._image = ImageTk.PhotoImage(image=resized_image)
        resized_image.close()
        
        self._borderedFrame = BorderedImageFrame(master=self, image=self._image, padding=_GAP_SIZE, borderwidth=_BORDER_SIZE)
        self._borderedFrame.place(relx=0.5, rely=0.5, anchor="center")

        self._selected = selected

        if self._selected:
            self.select()
        else:
            self.unselect()

        self.pack_propagate(False)

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
        self._borderedFrame._border_frame.configure(background="blue")

    def unselect(self) -> None:
        self._selected = False
        self._borderedFrame._border_frame.configure(background="SystemButtonFace")

    def toggle(self) -> None:
        if self.selected:
            self.unselect()
        else:
            self.select()