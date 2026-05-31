import math
from cvzone.HandTrackingModule import HandDetector
from utils.config import CFG


class Detector:
    def __init__(self):
        self.d = HandDetector(
            detectionCon=CFG["detection_con"],
            maxHands=1
        )
        self.lm = []
        self._hands = []

    def process(self, frame):
        """Detect hand, draw landmarks, return (lm, annotated_frame).
        lm[i] = [id, x, y] for landmark i (0-20).

        WHY flipType=False to avoid wrong hand labels due to double swapping
        """
        self._hands, frame = self.d.findHands(frame, draw=True, flipType=False)

        if self._hands:
            raw = self._hands[0]['lmList']
            self.lm = [[i, pt[0], pt[1]] for i, pt in enumerate(raw)]
        else:
            self.lm = []

        return self.lm, frame

    def fingers_up(self):
        """[thumb, index, middle, ring, pinky] — 1=up, 0=down.
        fingersUp() uses hand['type'] internally for thumb direction.
        Label must be correct (see above) for thumb to read correctly."""
        if not self._hands:
            return [0, 0, 0, 0, 0]
        return self.d.fingersUp(self._hands[0])

    def hand_size(self):
        """Pixel distance wrist(0) to middle MCP(9).
        Used to scale pinch threshold with hand distance from camera."""
        if not self.lm:
            return None
        return math.hypot(
            self.lm[0][1] - self.lm[9][1],
            self.lm[0][2] - self.lm[9][2]
        )
