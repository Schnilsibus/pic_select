from typing import Literal

from ..clipboard import copy_files_to_clipboard
from ..load.loaderThread import LoaderThread
from ..selector import Selector
from .UserInput import UserInput

from ...gui.frames.displays.imageViewFrame import ImageViewFrame
from ...gui.frames.displayFrame import DisplayFrame

from ...log import logger


# TODO: change too many clicks protection!! -> only ignore input when at the edge of the loaded images
class UserInputHandler:

    def __init__(self, selector: Selector, loaderController: LoaderThread):

        self._selector = selector
        self._loaderController = loaderController
        
        self._imageViewFrame = None
        self._displayFrame = None

        self._last_arrow_input: Literal[UserInput.FORWARD, UserInput.BACKWARD] = None
        self._loader_busy: bool = False

    def set_image_view_frame(self, imageViewFrame: ImageViewFrame) -> None:
        self._imageViewFrame = imageViewFrame

    def set_display_frame(self, displayFrame: DisplayFrame) -> None:
            self._displayFrame = displayFrame

    def handle_input(self, input: UserInput):
        if input not in UserInput:
            raise RuntimeError("Invalid input")

        match input:
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

    def _forward(self) -> None:
        if self._loader_busy and self._last_arrow_input == UserInput.FORWARD:
            return None

        logger.log_user_input(input=str(UserInput.FORWARD))

        next_file = self._loaderController.next_file()
        self._imageViewFrame.display_image_frame(path=next_file)
        self._displayFrame.set_image_name(path=next_file)

        self._last_arrow_input = UserInput.FORWARD
        self._loaderController.append_forward()

    def _backward(self) -> None:
        if self._loader_busy and self._last_arrow_input == UserInput.BACKWARD:
            return None

        logger.log_user_input(input=str(UserInput.BACKWARD))
        
        previous_file = self._loaderController.previous_file()
        print(previous_file)
        self._imageViewFrame.display_image_frame(path=previous_file)
        self._displayFrame.set_image_name(path=previous_file)
        
        self._last_arrow_input = UserInput.BACKWARD
        self._loaderController.append_backward()

    def _select(self) -> None:
        path = self._loaderController.current_file()
        self._selector.toggle(path)

    def _copy(self) -> None:
        selection = self._selector.get_selection()
        copy_files_to_clipboard(files=selection)

    def _select_all(self) -> None:
        self._selector.select_all()

    def _unselect_all(self) -> None:
        self._selector.unselect_all()