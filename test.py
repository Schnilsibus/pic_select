import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

def _on_left_arrow_key(event) -> None:
        print(f"{event.keysym} LEFT")

def _on_esc(event) -> None:
        root.destroy()

root = tk.Tk()
root.bind("<Left>", _on_left_arrow_key)
root.bind("<Escape>", _on_left_arrow_key)

root.mainloop()