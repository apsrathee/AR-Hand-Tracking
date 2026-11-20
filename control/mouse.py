"""Mouse control.

Primary backend: pynput (the original implementation) — works on X11 and Windows.

Wayland fallback: on a Wayland session pynput usually cannot acquire an X
connection ("failed to acquire X connection" / "too many values to unpack"),
so we fall back to ydotool (uinput) for clicks/scroll and Hyprland IPC
(`hyprctl`) for reading/warping the cursor. Requires `ydotoold` running and,
for cursor read/move, Hyprland.

Coordinate note (ydotool backend): ydotool's ABSOLUTE axis space matches the
monitor's NATIVE mode, while Hyprland / screeninfo report the current logical
mode. On a 4K-native panel running at 1080p that is a 2x factor, so absolute
moves are divided by _ABS_SCALE (computed from `hyprctl monitors`).
"""
import json
import os
import re
import subprocess

# ---------------------------------------------------------------------------
# Backend selection: prefer pynput; fall back to ydotool on Wayland.
# ---------------------------------------------------------------------------
try:
    from pynput.mouse import Button, Controller as _MouseController
    _m = _MouseController()
    BACKEND = "pynput"
except Exception:
    BACKEND = "ydotool"


def _compute_abs_scale():
    try:
        out = subprocess.run(["hyprctl", "monitors"],
                             capture_output=True, text=True, timeout=3).stdout
        cur = re.search(r"(\d+)x(\d+)@[\d.]+ at ", out)
        modes = re.findall(r"(\d+)x(\d+)@", out)
        if cur and modes:
            cur_w = int(cur.group(1))
            max_w = max(int(w) for w, _ in modes)
            if cur_w > 0:
                return max_w / cur_w
    except Exception:
        pass
    return 1.0


def _ensure_hypr_signature():
    # hyprctl cursorpos/monitors need HYPRLAND_INSTANCE_SIGNATURE, but
    # `hyprctl instances` works without it — derive it when missing so the
    # ydotool backend also works when launched manually (not via the service).
    if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        return
    try:
        out = subprocess.run(["hyprctl", "instances", "-j"],
                             capture_output=True, text=True, timeout=3).stdout
        inst = json.loads(out)
        if inst:
            os.environ["HYPRLAND_INSTANCE_SIGNATURE"] = inst[0]["instance"]
    except Exception:
        pass


if BACKEND == "ydotool":
    _ensure_hypr_signature()
_ABS_SCALE = _compute_abs_scale() if BACKEND == "ydotool" else 1.0


def _run(*args):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=3)
        if r.returncode != 0:
            print(f"[mouse] FAIL {' '.join(args)} rc={r.returncode} err={r.stderr.strip()}", flush=True)
        return r
    except Exception as e:
        print(f"[mouse] EXC {' '.join(args)}: {e}", flush=True)


def position():
    """Current OS cursor (x, y) in logical screen coords."""
    if BACKEND == "pynput":
        return _m.position
    try:
        out = subprocess.run(["hyprctl", "cursorpos"],
                             capture_output=True, text=True, timeout=3).stdout.strip()
        x, y = out.split(",")
        return int(x.strip()), int(y.strip())
    except Exception:
        return 0, 0


def move(x, y):
    if BACKEND == "pynput":
        _m.position = (int(x), int(y))
        return
    _run("ydotool", "mousemove", "-a",
         "-x", str(int(x / _ABS_SCALE)), "-y", str(int(y / _ABS_SCALE)))


def click():
    if BACKEND == "pynput":
        _m.click(Button.left, 1)
        return
    _run("ydotool", "click", "0xC0")


def right_click():
    if BACKEND == "pynput":
        _m.click(Button.right, 1)
        return
    _run("ydotool", "click", "0xC1")


def double_click():
    if BACKEND == "pynput":
        _m.click(Button.left, 2)
        return
    _run("ydotool", "click", "0xC0", "0xC0")


def scroll(dy):
    # positive dy = scroll up
    if BACKEND == "pynput":
        _m.scroll(0, int(dy))
        return
    _run("ydotool", "mousemove", "-w", "-x", "0", "-y", str(int(dy)))