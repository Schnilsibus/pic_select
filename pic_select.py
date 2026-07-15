import tkinter as tk
import threading

from .loader import Loader, LoaderWorker
from .selector import Selector
from .gui import GuiControl, ask_file_name

def start():
    selector = Selector()
    loader = Loader(path=ask_file_name())
    worker = LoaderWorker(loader=loader)
    worker_thread = threading.Thread(target=worker.mainloop, daemon=True)
    root = tk.Tk()
    gui = GuiControl(master=root, loader_worker=worker, selector=selector)
    gui.update_current_image(path=loader.get_current_path())
    gui.refresh_display()
    worker_thread.start()
    root.after(ms=5, func=loader.preload_images) # TODO: the initial load should be done by the worker thread as well -> idea: puting a Path object in the queue will (re-) initialize the loader
    root.mainloop()