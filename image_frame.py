import tkinter as tk
from PIL import Image, ImageOps, ImageTk
from typing import Tuple

_GAP_SIZE = 3
_BORDER_SIZE = 3

class ImageFrame(tk.Frame):

    def __init__(self, master, image: Image.Image, max_image_size: Tuple[int, int], selected: bool = False):
        super().__init__(master=master)
        
        self._image = image
        self._selected = selected

        self._display_image = ImageTk.PhotoImage(image = ImageOps.contain(image = image, size = (max_image_size)))

        self._max_width = self._display_image.width()
        self._max_height = self._display_image.height()

        self._border_frame = tk.Frame(self,
                        width=self._max_width + _GAP_SIZE + _BORDER_SIZE,
                        height=self._max_height + _GAP_SIZE + _BORDER_SIZE,
                        background="#074bb8")
        self._gap_frame = tk.Frame(self._border_frame,
                        width=self._max_width + _GAP_SIZE,
                        height=self._max_height + _GAP_SIZE,
                        background="white")
        self._selected_label = tk.Label(master=self._gap_frame, image=self._display_image)

        self._border_frame.pack_propagate(False)
        self._gap_frame.pack_propagate(False)
        self._selected_label.pack_propagate(False)

        self._selected_label.pack(padx=_GAP_SIZE, pady=_GAP_SIZE)
        self._gap_frame.pack(padx=_BORDER_SIZE, pady=_BORDER_SIZE)

        self._unselected_Label = tk.Label(master=self, image=self._display_image)

        self._unselected_Label.pack_propagate(False)
        
        if self._selected:
            self.select()
        else:
            self.unselect() 
        
     
    def select(self):
        self._selected = True
        self._unselected_Label.pack_forget()
        self._border_frame.pack()
        self.winfo_toplevel().update()

    def unselect(self):
        self._selected = False
        self._unselected_Label.pack()
        self._border_frame.pack_forget()
        self.winfo_toplevel().update()

    def toggle_selected(self):
        if self._selected:
            self.unselect()
        else:
            self.select()