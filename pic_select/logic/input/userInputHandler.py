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

    def __init__(self, selector: Selector, loader_thread: LoaderThread, picture_directory: PictureDirectory):

        self._selector = selector
        self._loader_thread = loader_thread
        self._picture_directory = picture_directory
        
        self._image_view_frame = None
        self._display_frame = None

        self._last_arrow_input: Literal[UserInput.FORWARD, UserInput.BACKWARD] = None

    def set_image_view_frame(self, image_view_frame: ImageViewFrame) -> None:
        self._image_view_frame = image_view_frame

    def set_display_frame(self, display_frame: DisplayFrame) -> None:
            self._display_frame = display_frame

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
        self._picture_directory.directory = file.parent
        self._loader_thread.update_to(path=file)
        self._display_frame.show_image(path=file)

    def _forward(self) -> None:
        if self._image_view_frame.is_waiting_on_loader() and self._last_arrow_input == UserInput.FORWARD:
            return None

        self._last_arrow_input = UserInput.FORWARD

        next_file = self._picture_directory.next_file(anchor=self._image_view_frame.current_image_path)
        if next_file is not None:
            self._display_frame.show_image(path=next_file)
            self._loader_thread.update_to(path=next_file)

    def _backward(self) -> None:
        if self._image_view_frame.is_waiting_on_loader() and self._last_arrow_input == UserInput.BACKWARD:
            return None

        self._last_arrow_input = UserInput.BACKWARD
        
        previous_file = self._picture_directory.previous_file(anchor=self._image_view_frame.current_image_path)
        if previous_file is not None:
            self._display_frame.show_image(path=previous_file)
            self._loader_thread.update_to(path=previous_file)

    def _select(self) -> None:
        path = self._image_view_frame.current_image_path
        if path in self._image_view_frame:
            self._selector.toggle(path)

    def _copy(self) -> None:
        selection = self._selector.get_selection()
        copy_files_to_clipboard(files=selection)

    def _select_all(self) -> None:
        self._selector.select_all()

    def _unselect_all(self) -> None:
        self._selector.unselect_all()