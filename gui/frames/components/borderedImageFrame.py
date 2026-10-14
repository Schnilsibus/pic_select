import tkinter as tk
from PIL import ImageTk

from .paddedImageFrame import PaddedImageFrame

class BorderedImageFrame(tk.Frame):

    def __init__(self, master: tk.Widget, image: ImageTk.PhotoImage, padding: int, borderwidth: int):
        full_width, full_height = image.width() + padding + borderwidth, image.height() + padding + borderwidth

        super().__init__(master, width = full_width, height = full_height)

        self._border_frame = tk.Frame(master=self, background="blue", width=full_width, height=full_height)
        self._padded_frame = PaddedImageFrame(master=self._border_frame, image=image, padding=padding)

        self._padded_frame.place(relx=0.5, rely=0.5, anchor="center")
        self._border_frame.place(relx=0.5, rely=0.5, anchor="center")







