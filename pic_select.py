import tkinter as tk
from pathlib import Path

from .loader import Loader
from .selector import Selector
from .gui import GuiControl, ask_file_name


def start():
    selector = Selector()
    loader = Loader(path=Path(ask_file_name()))
    root = tk.Tk()
    gui = GuiControl(master=root, loader=loader, selector=selector)
    # TODO: Add functionality: first image is displayed as soon as it is loaded -> shoudl be easy once loader has own thread and ImageFactory has callbacks
    loader.preload_images()
    gui.update_image_frame(path=loader.get_current_path())
    root.mainloop()