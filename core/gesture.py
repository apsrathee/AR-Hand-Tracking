import math
from utils.config import CFG

IDLE        = "idle"
MOVE        = "move"
CLICK       = "click"
RIGHT_CLICK = "right_click"
SCROLL_UP   = "scroll_up"
SCROLL_DOWN = "scroll_down"

_BASE_PINCH      = CFG["pinch_threshold"]
_SCALE_PINCH     = CFG.get("pinch_scale_to_hand", True)
_REF_HAND_SIZE   = CFG.get("ref_hand_size", 100)
# Min y-pixel gap between index and middle tips to confirm scroll direction.
# Without this, a nearly-flat hand flickers between scroll_up and scroll_down.
_SCROLL_DEADZONE = CFG.get("scroll_min_diff", 15)


def _dist(lm, a, b):
    return math.hypot(lm[a][1] - lm[b][1], lm[a][2] - lm[b][2])


def recognize(fingers, lm, hand_size=None) -> str:
    """
    fingers    : [thumb, index, middle, ring, pinky] — 1=up, 0=down
    lm         : landmark list [[id,x,y], ...] from Detector.process()
    hand_size  : wrist-to-MCP9 px distance from Detector.hand_size() — optional

    Gesture map:
      pinch (thumb tip near index tip)  → left click   (threshold scales with hand distance)
      index only up                     → move cursor
      index + middle up                 → scroll up/down (deadzone prevents flat-hand flicker)
      thumb + pinky up                  → right click
      anything else                     → idle
    """
    if not lm:
        return IDLE

    # Adaptive pinch: scale threshold proportionally to hand size in frame.
    if _SCALE_PINCH and hand_size and hand_size > 0:
        pinch_thresh = _BASE_PINCH * (hand_size / _REF_HAND_SIZE)
    else:
        pinch_thresh = _BASE_PINCH

    # Pinch checked before finger combos — pinch overrides everything
    if _dist(lm, 4, 8) < pinch_thresh:
        return CLICK

    # MOVE: index up, middle/ring/pinky down. Thumb state intentionally ignored.
    # fingersUp() reads thumb direction based on hand['type'] label to avoid confusions diue to mirror flip.
    if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
        return MOVE

    if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
        # positive diff = middle tip is lower on screen = index is higher = scroll up
        diff = lm[12][2] - lm[8][2]
        if abs(diff) < _SCROLL_DEADZONE:
            return IDLE   # ambiguous flat pose, do nothing
        return SCROLL_UP if diff > 0 else SCROLL_DOWN

    if fingers == [1, 0, 0, 0, 1]:
        return RIGHT_CLICK

    return IDLE
