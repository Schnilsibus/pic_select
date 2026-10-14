from typing import Literal
from pathlib import Path

from ..clipboard import copy_files_to_clipboard
from ..load.loaderThread import LoaderThread
from ..load.pictureDirectory import PictureDirectory
from ..selector import Selector
from .UserInput import UserInput

from ...gui.frames.displays.imageViewFrame import ImageViewFrame
from ...gui.frames.displayFrame import DisplayFrame



class UserInputHandler:

    def __init__(self, selector: Selector, loaderThread: LoaderThread, pictureDirectory: PictureDirectory):

        self._selector = selector
        self._loaderThread = loaderThread
        self._pictureDirectory = pictureDirectory
        
        self._imageViewFrame = None
        self._displayFrame = None

        self._last_arrow_input: Literal[UserInput.FORWARD, UserInput.BACKWARD] = None

    def set_image_view_frame(self, imageViewFrame: ImageViewFrame) -> None:
        self._imageViewFrame = imageViewFrame

    def set_display_frame(self, displayFrame: DisplayFrame) -> None:
            self._displayFrame = displayFrame

    def handle_input(self, input: UserInput, **kwargs):
        if input not in UserInput:
            raise RuntimeError("Invalid input")

        match input:
            case UserInput.OPEN:
                self._open(file = kwargs["file"])
            case UserInput.FORWARD:
                self._forward()
            case UserInput.BACKWARD:
                self._backward()
            case UserInput.SELECT:
                self._select()
            case UserInput.COPY:
                self._copy()
            case UserInput.SELECT_ALL:
                self._select_all()
            case UserInput.UNSELECT_ALL:
                self._unselect_all()

    def _open(self, file: Path) -> None:
        print(f"Shoud open {file}")
        self._pictureDirectory.directory = file.parent
        self._loaderThread.update_to(path=file)
        self._displayFrame.show_image(path=file)

    def _forward(self) -> None:
        if self._imageViewFrame.is_waiting_on_loader() and self._last_arrow_input == UserInput.FORWARD:
            return None

        self._last_arrow_input = UserInput.FORWARD

        next_file = self._pictureDirectory.next_file(anchor=self._imageViewFrame.current_image_path)
        if next_file is not None:
            self._displayFrame.show_image(path=next_file)
            self._loaderThread.update_to(path=next_file)

    def _backward(self) -> None:
        if self._imageViewFrame.is_waiting_on_loader() and self._last_arrow_input == UserInput.BACKWARD:
            return None

        self._last_arrow_input = UserInput.BACKWARD
        
        previous_file = self._pictureDirectory.previous_file(anchor=self._imageViewFrame.current_image_path)
        if previous_file is not None:
            self._displayFrame.show_image(path=previous_file)
            self._loaderThread.update_to(path=previous_file)

    def _select(self) -> None:
        path = self._imageViewFrame.current_image_path
        self._selector.toggle(path)

    def _copy(self) -> None:
        selection = self._selector.get_selection()
        copy_files_to_clipboard(files=selection)

    def _select_all(self) -> None:
        self._selector.select_all()

    def _unselect_all(self) -> None:
        self._selector.unselect_all()