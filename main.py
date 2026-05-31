import cv2
import time
import math
from utils.config import CFG
from core.detector import Detector
from core.gesture import recognize
from control.actions import dispatch
from utils.screen import get_resolution

_HINTS = {
    "idle":        "Idle",
    "move":        "Moving  [index up]",
    "click":       "Click!  [pinch]",
    "right_click": "R-Click [thumb+pinky]",
    "scroll_up":   "Scroll Up   [2 fingers]",
    "scroll_down": "Scroll Down [2 fingers]",
}
_COLOR = {
    "idle":        (120, 120, 120),
    "move":        (0, 220, 0),
    "click":       (0, 180, 255),
    "right_click": (0, 100, 255),
    "scroll_up":   (255, 200, 0),
    "scroll_down": (255, 200, 0),
}


def draw_hud(frame, gesture, active_zone, fps, lm, hand_size):
    h, w = frame.shape[:2]
    az = active_zone
    x0 = int(az[0] * w); y0 = int(az[1] * h)
    x1 = int(az[2] * w); y1 = int(az[3] * h)

    cv2.rectangle(frame, (x0, y0), (x1, y1), (80, 80, 80), 1)

    label = _HINTS.get(gesture, gesture)
    color = _COLOR.get(gesture, (255, 255, 255))
    cv2.putText(frame, label, (12, 34),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2, cv2.LINE_AA)

    cv2.putText(frame, f"{fps:.0f} fps", (w - 80, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1, cv2.LINE_AA)

    cv2.putText(frame, "Q to quit", (12, h - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (80, 80, 80), 1, cv2.LINE_AA)

    # Pinch proximity ring: turns grey → green as fingers approach click threshold
    if lm:
        base   = CFG["pinch_threshold"]
        thresh = base * (hand_size / CFG.get("ref_hand_size", 100)) if hand_size else base
        dist   = math.hypot(lm[4][1] - lm[8][1], lm[4][2] - lm[8][2])
        ratio  = max(0.0, min(1.0, 1.0 - (dist / (thresh * 2))))
        ring_color = (int(120 * (1 - ratio)), int(220 * ratio), int(120 * (1 - ratio)))
        mx = (lm[4][1] + lm[8][1]) // 2
        my = (lm[4][2] + lm[8][2]) // 2
        cv2.circle(frame, (mx, my), max(4, int(dist / 2)), ring_color, 2, cv2.LINE_AA)


def main():
    sw, sh = get_resolution()
    cap = cv2.VideoCapture(CFG.get("cam_index", 0))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CFG["cam_w"])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CFG["cam_h"])

    if not cap.isOpened():
        print("ERROR: Could not open camera. Check 'cam_index' in config.json.")
        return

    det = Detector()
    print(f"AR Hand Tracking started  |  screen {sw}x{sh}  |  press Q to quit")

    prev_time = time.time()
    fps = 0.0

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Camera read failed — check your webcam.")
                break

            frame    = cv2.flip(frame, 1)
            lm, frame = det.process(frame)
            fingers  = det.fingers_up()
            hs       = det.hand_size()
            gesture  = recognize(fingers, lm, hand_size=hs)

            # hand_size passed so actions.py can scale pinch threshold correctly
            dispatch(gesture, lm, sw, sh, hand_size=hs)

            now      = time.time()
            fps      = 0.9 * fps + 0.1 * (1.0 / max(now - prev_time, 1e-6))
            prev_time = now

            draw_hud(frame, gesture, CFG["active_zone"], fps, lm, hs)
            cv2.imshow("AR Hand Tracking", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Camera released. Goodbye.")


if __name__ == "__main__":
    main()
