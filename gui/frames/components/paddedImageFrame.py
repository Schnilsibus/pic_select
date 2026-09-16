import tkinter as tk
from PIL import ImageTk



class PaddedImageFrame(tk.Frame):

    def __init__(self, master: tk.Widget, image: ImageTk.PhotoImage, padding: int):
        full_width, full_height = image.width() + padding, image.height() + padding

        super().__init__(master, width = full_width, height = full_height)

        self._pad_Frame = tk.Frame(master=self, background="green", width = full_width, height=full_height)
        self._image_label = tk.Label(master=self._pad_Frame, image=image, borderwidth=0)

        self._image_label.place(relx=0.5, rely=0.5, anchor="center")
        self._pad_Frame.place(relx=0.5, rely=0.5, anchor="center")




