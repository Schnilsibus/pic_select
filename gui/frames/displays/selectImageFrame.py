import tkinter as tk


class SelectImageFrame(tk.Frame):

    def __init__(self, master: tk.Widget, width: int, height: int):
        super().__init__(master=master, background="yellow", width=width, height=height)

        self.pack_propagate(False)
        
        self._label: tk.Label = tk.Label(master=self,
                                         text="Select a file",
                                         font=("Arial, 18"),
                                         bg="white")
        self._label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)