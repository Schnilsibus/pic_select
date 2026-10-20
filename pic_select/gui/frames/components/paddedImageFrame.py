import tkinter as tk
from PIL import ImageTk



class PaddedImageFrame(tk.Frame):

    def __init__(self, master: tk.Widget, image: ImageTk.PhotoImage, padding: int):
        full_width = image.width() + (padding * 2)
        full_height =image.height() + (padding * 2)

        super().__init__(master, width = full_width, height = full_height, borderwidth=0, highlightthickness=0)

        self._pad_Frame = tk.Frame(master=self, width = full_width, height=full_height, borderwidth=0, highlightthickness=0)
        self._image_label = tk.Label(master=self._pad_Frame, image=image, borderwidth=0, highlightthickness=0, padx=0, pady=0)

        self._image_label.place(x=padding, y=padding)
        self._pad_Frame.place(x=0, y=0)

        self.pack_propagate(False)




