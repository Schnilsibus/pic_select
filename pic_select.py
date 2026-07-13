import tkinter as tk
from pathlib import Path

from .loader import Loader
from .selector import Selector
from .gui import GuiControl, ask_file_name

# TODO: Add functionality: first image is displayed as soon as it is loaded -> shoudl be easy once loader has own thread and ImageFactory has callbacks
def start():
    selector = Selector()
    loader = Loader(path=ask_file_name())
    root = tk.Tk()
    gui = GuiControl(master=root, loader=loader, selector=selector)
    gui.update_current_image(path=loader.get_current_path())
    gui.refresh_display()
    root.after(ms=5, func=loader.preload_images)
    root.mainloop()


"""
ORDER!! - visible:
- window opens - displays loading image ...
- changes to the image that should be displayed first as soon as loaded
- in the background other images are loaded

Sooo:
first inital gui without any loading
then call loader preload from start -> gui will automatically react

"""