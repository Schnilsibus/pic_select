import tkinter as tk
from tkinter import filedialog
from pathlib import Path

from .loader import Loader
from .selector import Selector
from .image_frame import ImageFrame, ImageFrameFactory
from .clipboard import copy_files_to_clipboard

# TODO: remember user input (right now klicks are ignored if loader is busy) OR figure out how to not wait for loader (defeats the point)
"""
THE PROBLEM:
What happens: multiple klicks overwhelm the system:
- on_left/ right is triggerd
    - this will show the next frame
    - call the loader to update
        - this will call on_load which creates new frames (VERY SLOW!!)
If a new keyboard event is triggered before the GUI has created frames:
    - this will show the next frame
    - call the loader to update
        - call on_load BUT this on_load has priority!! (idk why - it is beeing processed first!)
        - SOOO the frames that are needed more in the future are created first - which is bad!

The Thing that takes forever is exif_transpose

SOLUTION:
    - when calling show - check if the frame exists yet

    - solve the order in which the frames are created - maybe py FiFo queeu implementation -> try remove root.update() calls

    - maybe restrict user input to smth reasonable research online
        or logical whould be to only allow _preload_length quick clicks then wait 
        or query how many frames created and ignore a click if it is requesting a not loaded frame - give visual feedback
        
    - analize times for frame creation and try to create ImageFrames quicker 
        -> exif transpose takes forever -> actually it is getting the exif data
        give the loader its own thread
"""
_PADDING = 100

def ask_file_name() -> str:
    _root = tk.Tk()
    _root.withdraw()
    path = filedialog.askopenfilename()
    _root.destroy()
    return path

class GuiControl(object):
    
    def __init__(self, master: tk.Tk, loader: Loader, selector: Selector):
        self._ROOT: tk.Tk = master
        self._loader = loader
        self._selector = selector
        
        self._ROOT.title(str(self._loader.get_directory()))
        self._ROOT.bind("<Left>", self._on_left_arrow_key)
        self._ROOT.bind("<Right>", self._on_right_arrow_key)
        self._ROOT.bind("<space>", self._on_space)
        self._ROOT.bind("<Control-c>", self._on_copy)
        self._ROOT.bind("<Control-C>", self._on_copy)
        self._ROOT.bind("<Control-a>", self._on_strg_a)
        self._ROOT.bind("<Control-A>", self._on_strg_a)
        self._ROOT.bind("<Escape>", self._on_escape)

        self._ROOT.state("zoomed")
        self._ROOT.focus_force()
        self._ROOT.lift()

        self._WIDTH: int = self._ROOT.winfo_width()
        self._HEIGHT: int = self._ROOT.winfo_height()

        self._current_image_name: tk.StringVar = tk.StringVar()
        self._current_image_label: tk.Label = tk.Label(master=self._ROOT,
                                                       textvariable=self._current_image_name,
                                                       font=("Arial, 18"))

        self._image_frame_factory = ImageFrameFactory(master=self._ROOT,
                                                      loader=self._loader,
                                                      selector=self._selector,
                                                      max_image_size=(self._WIDTH - _PADDING, self._HEIGHT - _PADDING))
        self._current_image_frame: ImageFrame = None

        self._current_image_label.place(relx=0.5, rely=1.0, anchor=tk.S)

    def _on_left_arrow_key(self, event) -> None:
        path = self._loader.get_neighbor_path("Left")
        if path is not None:
            self.update_image_frame(path=path)
            self._loader.backward()

    def _on_right_arrow_key(self, event) -> None:
        path = self._loader.get_neighbor_path("Right")
        if path is not None:
            self.update_image_frame(path=path)
            self._loader.forward()

    def _on_space(self, event) -> None:
        path = self._loader.get_current_path()
        self._selector.toggle(key=path)
        self._current_image_frame.toggle_selected()

    def _on_copy(self, evetn) -> None:
        copy_files_to_clipboard(self._selector.get_selection())

    def _on_strg_a(self, event) -> None:
        paths = self._loader.get_all_paths()
        self._selector.multi_select(keys=paths)
        self._image_frame_factory.select_all()
    
    def _on_escape(self, event) -> None:
        self._selector.unselect_all()
        self._image_frame_factory.select_all(unselect=True)
        
    def update_image_frame(self, path: Path) -> None:
        if self._current_image_frame is not None:
            self._current_image_frame.place_forget()

        self._current_image_name.set(value=path.name)

        # TODO: Implement wait for frame_factory functionality:
        #    add callback to frame_factory that gets called if specific image is loaded
        #    display dummy frame - loading image "..." in the mean time
        #    could add: if this case happens -> everything is kinda reset -> load to display more or less re initialize loader -> give Prio to the image that should be displayed at the moment; reuse already loaded images of course 

        try:
            self._current_image_frame = self._image_frame_factory.get_frame(path=path)
        except KeyError as ex:
            raise ex

        self._current_image_frame.place(relx=0.5, rely=0.5, anchor="center")