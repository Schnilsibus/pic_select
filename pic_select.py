from loader import Loader
from selector import Selector
from gui import Display, ask_file_name
from pathlib import Path

def start():
    selector = Selector()
    loader = Loader(path=Path(ask_file_name()))
    display = Display(loader=loader, selector=selector, fullscreen=False)
    display.start_display()