import threading

from .logic.load.loader import Loader
from .logic.load.loaderController import LoaderController
from .logic.selector import Selector
from .logic.input.userInputHandler import UserInputHandler

from .gui.app import App
from .gui.selectFile import ask_file_name



def start():
    loader = Loader()
    loaderController = LoaderController(loader=loader)
    selector = Selector()
    inputHandler = UserInputHandler(selector=selector, loaderController=loaderController)

    worker_thread = threading.Thread(target=loaderController.mainloop, daemon=True)

    app = App(title="",
              inputHandler=inputHandler,
              loader=loader,
              loaderController=loaderController,
              selector=selector,
              fullscreen=True)

    worker_thread.start()

    selected_file = ask_file_name(parent=app)

    loader.directory = selected_file.parent

    loaderController.append_reload(path=selected_file)

    app.mainloop(path=selected_file)