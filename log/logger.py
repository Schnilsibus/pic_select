from pathlib import Path
from time import time
from enum import Enum

class Logger():
    def __init__(self, log_file: Path = None):
        self._log_file = log_file

    def log_file_action(self, thread: str, file: Path, action: str) -> None:
        message = f"{thread} - {file.name} - {action}"
        self._log(message=message)

    def log_user_input(self, input: str) -> None:
        self._log(message=input, new_line=True)

    def _log(self, message: str, new_line: bool = False) -> None:
        current_time = time()
        good_message = f"{current_time:.1}: {message}"
        if self._log_file is None:
            if new_line:
                print()
            print(good_message)
        else:
            raise NotImplementedError()
