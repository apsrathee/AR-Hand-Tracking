import numpy as np
from utils.config import CFG

_CW = CFG["cam_w"]
_CH = CFG["cam_h"]
_AZ = CFG["active_zone"]   # [x0, y0, x1, y1] as 0.0–1.0 fractions of frame

_X0, _Y0 = _AZ[0] * _CW, _AZ[1] * _CH
_X1, _Y1 = _AZ[2] * _CW, _AZ[3] * _CH


def to_screen(cx, cy, sw, sh):
    """Map camera pixel coords (inside active zone) → screen pixel coords.
    Points outside the active zone are clamped to screen edges."""
    x = int(np.interp(cx, [_X0, _X1], [0, sw]))
    y = int(np.interp(cy, [_Y0, _Y1], [0, sh]))
    return max(0, min(x, sw)), max(0, min(y, sh))
