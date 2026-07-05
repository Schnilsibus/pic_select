from loader import Loader
from selector import Selector
from gui import GuiControl, ask_file_name
from pathlib import Path

def start():
    selector = Selector()
    loader = Loader(path=Path(ask_file_name()))
    display = GuiControl(loader=loader, selector=selector)
    display.start_display()