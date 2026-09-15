import tkinter as tk
import threading

def start():
    path = ask_file_name()
    selector = Selector()
    loader = Loader(path=path)
    worker = LoaderWorker(loader=loader)
    worker_thread = threading.Thread(target=worker.mainloop, daemon=True)
    root = tk.Tk()
    gui = GuiControl(master=root, loader_worker=worker, selector=selector)
    gui.update_current_image(path=path)
    gui.refresh_display()
    worker_thread.start()
    root.after(ms=5, func=worker.queue_load_path(path=path))
    root.mainloop()