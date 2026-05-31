from pynput.mouse import Button, Controller as MouseController

_m = MouseController()

FAILSAFE_CORNER = (0, 0)  # move mouse here to kill app (checked in main.py)


def position():
    """Returns current OS cursor (x, y)."""
    return _m.position


def move(x, y):
    _m.position = (int(x), int(y))


def click():
    _m.click(Button.left, 1)


def right_click():
    _m.click(Button.right, 1)


def double_click():
    _m.click(Button.left, 2)


def scroll(dy):
    _m.scroll(0, int(dy))
