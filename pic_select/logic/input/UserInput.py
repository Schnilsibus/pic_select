from enum import Enum



class UserInput(Enum):
    OPEN = "open"
    FORWARD = "forward"
    BACKWARD = "backward"
    SELECT = "select"
    COPY = "copy"
    SELECT_ALL = "selectAll"
    UNSELECT_ALL = "unselectAll"