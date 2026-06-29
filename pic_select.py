from loader import Loader
from gui import Display, ask_file_name
from pathlib import Path

def start():
    loader = Loader(path=Path(ask_file_name()))
    display = Display(loader=loader, fullscreen=False)
    display.start_display()