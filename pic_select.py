import threading

from .logic.load.loader import Loader
from .logic.load.loaderThread import LoaderThread
from .logic.load.pictureDirectory import PictureDirectory
from .logic.selector import Selector
from .logic.input.userInputHandler import UserInputHandler

from .gui.app import App
from .gui.selectFile import ask_file_name



def start():
    pictureDirectory = PictureDirectory()
    loader = Loader(picture_directory=pictureDirectory)
    loaderThread = LoaderThread(loader=loader, picture_directory=pictureDirectory)
    selector = Selector()
    inputHandler = UserInputHandler(selector=selector, loaderThread=loaderThread, pictureDirectory=pictureDirectory)

    worker_thread = threading.Thread(target=loaderThread.mainloop, daemon=True)

    app = App(title="",
              inputHandler=inputHandler,
              loader=loader,
              loaderThread=loaderThread,
              selector=selector,
              fullscreen=False)

    inputHandler.set_display_frame(displayFrame=app.displayFrame)
    inputHandler.set_image_view_frame(imageViewFrame=app.imageViewFrame)

    worker_thread.start()

    selected_file = ask_file_name(parent=app)

    pictureDirectory.directory = selected_file.parent

    app.after(0, loaderThread.update_to(path=selected_file))

    app.mainloop(path=selected_file)