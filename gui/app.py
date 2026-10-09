import tkinter as tk
from pathlib import Path

from ..logic.input.UserInput import UserInput
from ..logic.input.userInputHandler import UserInputHandler
from ..logic.load.loader import Loader
from ..logic.load.loaderThread import LoaderThread
from ..logic.selector import Selector

from .frames.displayFrame import DisplayFrame
from .frames.displays.imageViewFrame import ImageViewFrame



_PADDING_PERCENT = 0.15

_MIN_WINDOW_DIM =  int(25 / _PADDING_PERCENT) + 1


# TODO: Add back Image number display
class App(tk.Tk):

    def __init__(
            self,
            title: str,
            inputHandler: UserInputHandler,
            loader: Loader,
            loaderController: LoaderThread,
            selector: Selector,
            fullscreen = True):
        super().__init__()

        self.title(title)

        self.minsize(_MIN_WINDOW_DIM, _MIN_WINDOW_DIM)
        self.state("zoomed")
        self.focus_force()
        self.lift()

        self.bind("<Left>", self._on_left_arrow)
        self.bind("<Right>", self._on_right_arrow)
        self.bind("<space>", self._on_space)
        self.bind("<Control-c>", self._on_strg_c)
        self.bind("<Control-C>", self._on_strg_c)
        self.bind("<Control-a>", self._on_strg_a)
        self.bind("<Control-A>", self._on_strg_a)
        self.bind("<Control-t>", self._on_strg_t)
        self.bind("<Control-T>", self._on_strg_t)
        self.bind("<Escape>", self._on_escape)
        self.bind("<F11>", self._on_f_11)

        self._is_fullscreen = fullscreen
        if self._is_fullscreen:
            self.enter_fullscreen()

        self._inputHandler = inputHandler

        self._displayFrame = DisplayFrame(master=self, loaderController=loaderController, selector=selector)
        self._displayFrame.pack(fill="both", expand=True)
        self._displayFrame.setup_displays(selector=selector, loader=loader)
        self._displayFrame.show_select_image()

    @property
    def displayFrame(self) -> DisplayFrame:
        return self._displayFrame
    
    @property
    def imageViewFrame(self) -> ImageViewFrame:
        return self._displayFrame.image_view_frame

    def _on_right_arrow(self, event) -> None:
        self._inputHandler.handle_input(input=UserInput.FORWARD)

    def _on_left_arrow(self, event) -> None:
        self._inputHandler.handle_input(input=UserInput.BACKWARD)

    def _on_space(self, event) -> None:
        self._inputHandler.handle_input(input=UserInput.SELECT)

    def _on_strg_c(self, evetn) -> None:
        self._inputHandler.handle_input(input=UserInput.COPY)

    def _on_strg_a(self, event) -> None:
        self._inputHandler.handle_input(input=UserInput.SELECT_ALL)
    
    def _on_escape(self, event) -> None:
        self._inputHandler.handle_input(input=UserInput.UNSELECT_ALL)

    def _on_strg_t(self, event) -> None:
        self.quit()

    def _on_f_11(self, event) -> None:
        self.toggle_fullscreen()

    # TODO: do not think I need this the show_image! -> should happen with loader event anyways
    def mainloop(self, path: Path, n = 0):
        self._displayFrame.show_image(path=path)
        return super().mainloop(n)

    def toggle_fullscreen(self) -> None:
        self._is_fullscreen = not self._is_fullscreen
        self.attributes("-fullscreen", self._is_fullscreen)
    
    def enter_fullscreen(self) -> None:
        self.attributes("-fullscreen", True)
        self._is_fullscreen = True

    def exit_fullscreen(self) -> None:
        self.attributes("-fullscreen", False)
        self._is_fullscreen = False

    def quit(self) -> None:
        self.destroy()