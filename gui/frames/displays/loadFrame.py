import tkinter as tk
from typing import Tuple




class LoadFrame(tk.Frame):

    def __init__(self, master: tk.Widget, display_size: Tuple[int, int]):
        super().__init__(master=master, width=display_size[0], height=display_size[1])

        self.pack_propagate(False)

        self._text: tk.StringVar = tk.StringVar(self)
        self._label: tk.Label = tk.Label(master=self,
                                         textvariable=self._text,
                                         font=("Arial, 18"))
        self._label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def set_text(self, name: str) -> None:
        self._text.set(f"loading image '{name}'")