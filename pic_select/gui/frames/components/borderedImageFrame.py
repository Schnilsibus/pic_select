import tkinter as tk
from PIL import ImageTk

from .paddedImageFrame import PaddedImageFrame



class BorderedImageFrame(tk.Frame):

    def __init__(self, master: tk.Widget, image: ImageTk.PhotoImage, padding: int, borderwidth: int):
        full_width = image.width() + (padding * 2) + (borderwidth * 2)
        full_height = image.height() + (padding * 2) + (borderwidth * 2)

        super().__init__(master, width = full_width, height = full_height, borderwidth=0, highlightthickness=0)

        self._border_frame = tk.Frame(master=self,
                                      background="blue",
                                      width=full_width,
                                      height=full_height,
                                      borderwidth=0,
                                      highlightthickness=0)

        self._padded_frame = PaddedImageFrame(master=self._border_frame, image=image, padding=padding)

        self._padded_frame.place(x=borderwidth, y=borderwidth)
        self._border_frame.place(x=0, y=0)

        self.pack_propagate(False)







