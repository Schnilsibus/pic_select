from pathlib import Path
import tkinter as tk
from tkinter import filedialog



def ask_file_name(parent: tk.Tk) -> Path:
    path = filedialog.askopenfilename(parent=parent)
    return Path(path)