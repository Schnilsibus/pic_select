import tkinter as tk
from tkinter import ttk


class LoadFrame(ttk.Frame):

    def __init__(self, master: tk.Widget, width: int, height: int):
        super().__init__(master=master, bg="yellow", width=width, height=height)

        self.pack_propagate(False)

        self._text: tk.StringVar = tk.StringVar(self)
        self._label: tk.Label = tk.Label(master=self,
                                         textvariable=self._text,
                                         font=("Arial, 18"),
                                         bg="white")
        self._label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def set_text(self, name: str) -> None:
        self._text.set(f"loading image '{name}'")