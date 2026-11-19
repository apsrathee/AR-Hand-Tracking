import time
from control.mouse import move, click, right_click, scroll, position
from core.smoother import Smoother
from core.gesture import MOVE, CLICK, RIGHT_CLICK, SCROLL_UP, SCROLL_DOWN
from utils.config import CFG

_COOLDOWN     = CFG["click_cooldown_ms"] / 1000
_SCROLL_SPD   = CFG["scroll_speed"]
_DEBOUNCE     = CFG.get("gesture_debounce_frames", 2)
_SENSITIVITY  = CFG.get("move_sensitivity", 2.5)
_FREEZE_S     = 0.25   # seconds to freeze cursor on click gesture

_smoother     = Smoother()
_last_click   = 0.0
_pending      = None

# Relative movement state
_prev_hand    = None   # (x, y) hand position on previous frame
_cur_x        = 0.0   # tracked cursor x — float for sub-pixel precision
_cur_y        = 0.0   # tracked cursor y


# Click freeze state
_freeze_until = 0.0


def dispatch(gesture, lm, screen_w, screen_h, hand_size=None):
    global _last_click, _pending, _freeze_until
    global _prev_hand, _cur_x, _cur_y

    now = time.time()

    # Debounce: gesture must hold N consecutive frames before action fires
    if _pending and _pending[0] == gesture:
        _pending = (gesture, _pending[1] + 1)
    else:
        _pending = (gesture, 1)
    confirmed = _pending[1] >= _DEBOUNCE

    # ------------------------------------------------------------------ MOVE
    if gesture == MOVE and lm:
        if now < _freeze_until:
            # Inside click freeze window: hold the cursor still so a pinch
            # doesn't drag it.
            return

        raw_x, raw_y = float(lm[8][1]), float(lm[8][2])

        if CFG.get("movement_mode", "relative") == "positional":
            # ABSOLUTE / positional (opt-in): map the index tip's location inside
            # the active_zone (inner square on the feed) to the full screen.
            # Zone centre -> screen centre; zone edge -> that screen edge.
            az = CFG["active_zone"]
            cam_w, cam_h = CFG["cam_w"], CFG["cam_h"]
            x0, y0 = az[0] * cam_w, az[1] * cam_h
            x1, y1 = az[2] * cam_w, az[3] * cam_h
            nx = max(0.0, min(1.0, (raw_x - x0) / max(1e-6, x1 - x0)))
            ny = max(0.0, min(1.0, (raw_y - y0) / max(1e-6, y1 - y0)))
            _cur_x = nx * (screen_w - 1)
            _cur_y = ny * (screen_h - 1)
        else:
            # RELATIVE / trackpad (default, original behaviour): continue from the
            # current cursor position and move by the hand's frame-to-frame delta.
            if _prev_hand is None:
                cx, cy = position()
                _cur_x, _cur_y = float(cx), float(cy)
                _prev_hand = (raw_x, raw_y)
                _smoother.flush()
                return  # anchor frame — don't move yet
            dx = raw_x - _prev_hand[0]
            dy = raw_y - _prev_hand[1]
            _prev_hand = (raw_x, raw_y)
            _cur_x = max(0.0, min(_cur_x + dx * _SENSITIVITY, float(screen_w - 1)))
            _cur_y = max(0.0, min(_cur_y + dy * _SENSITIVITY, float(screen_h - 1)))

        sx, sy = _smoother.smooth(int(_cur_x), int(_cur_y))
        move(sx, sy)

    # --------------------------------------------------------------- CLICK / RIGHT CLICK
    elif gesture in (CLICK, RIGHT_CLICK):
        # Extend freeze window every CLICK frame so cursor stays frozen for as long as the pinch is held.
        _freeze_until = now + _FREEZE_S
        _prev_hand = None  # reset relative tracking — next MOVE starts fresh

        if confirmed and now - _last_click > _COOLDOWN:
            # Cursor sits exactly at the last MOVE position.
            (click if gesture == CLICK else right_click)()
            _last_click = now
            _smoother.flush()

    # ----------------------------------------------------------------- SCROLL
    elif gesture == SCROLL_UP and confirmed:
        _prev_hand = None
        scroll(_SCROLL_SPD)

    elif gesture == SCROLL_DOWN and confirmed:
        _prev_hand = None
        scroll(-_SCROLL_SPD)

    # ------------------------------------------------------------------ IDLE
    else:
        # Any non-MOVE gesture resets relative tracking.
        # Next MOVE will re-anchor to actual cursor position.
        _prev_hand = None
