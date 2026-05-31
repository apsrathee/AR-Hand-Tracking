from collections import deque
from utils.config import CFG


class Smoother:
    def __init__(self):
        n = CFG["smooth_frames"]
        self.bx = deque(maxlen=n)
        self.by = deque(maxlen=n)

    def smooth(self, x, y):
        self.bx.append(x)
        self.by.append(y)
        return int(sum(self.bx) / len(self.bx)), int(sum(self.by) / len(self.by))

    def flush(self):
        self.bx.clear()
        self.by.clear()
