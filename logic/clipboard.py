import os
from typing import List
from pathlib import Path

def copy_files_to_clipboard(files: List[Path]) -> None:
    if files is None or len(files) == 0:
        return None
    seperator = "', '"
    cmd = f"powershell Set-Clipboard -Path '{seperator.join([str(p) for p in files])}'"
    os.system(command=cmd)
    