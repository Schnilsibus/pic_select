import threading

from .logic.load.loader import Loader
from .logic.load.loaderThread import LoaderThread
from .logic.load.pictureDirectory import PictureDirectory
from .logic.selector import Selector
from .logic.input.userInputHandler import UserInputHandler
from .logic.sizeManager import SizeManager

from .gui.app import App
from .gui.selectFile import ask_file_name



def start():
    picture_directory = PictureDirectory()
    size_manager = SizeManager()
    loader = Loader(picture_directory=picture_directory, max_image_size=size_manager.max_monitor_extension)
    loader_thread = LoaderThread(loader=loader, picture_directory=picture_directory)
    selector = Selector()
    input_handler = UserInputHandler(selector=selector, loader_thread=loader_thread, picture_directory=picture_directory)

    worker_thread = threading.Thread(target=loader_thread.mainloop, daemon=True)

    app = App(title="",
              input_handler=input_handler,
              loader=loader,
              loader_thread=loader_thread,
              selector=selector)

    input_handler.set_display_frame(display_frame=app.display_frame)
    input_handler.set_image_view_frame(image_view_frame=app.image_view_frame)

    worker_thread.start()

    app.mainloop()