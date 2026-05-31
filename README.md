# AR Hand Tracking — Gesture Mouse Controller

Control your PC's mouse cursor entirely with hand gestures via your webcam. No extra hardware needed. Built with Python, OpenCV, cvzone, and MediaPipe's 21-point hand skeleton model.

---

## Table of Contents

1. [How It Works](#how-it-works)
2. [Python Version Warning](#python-version-warning)
3. [Requirements](#requirements)
4. [Installation — Linux](#installation--linux)
5. [Installation — Windows](#installation--windows)
6. [Running the App](#running-the-app)
7. [Gesture Reference](#gesture-reference)
8. [Understanding the Camera Window](#understanding-the-camera-window)
9. [Configuration (config.json)](#configuration-configjson)
10. [Project Structure](#project-structure)
11. [How the Code Works](#how-the-code-works)
12. [Troubleshooting](#troubleshooting)
13. [Adding New Gestures](#adding-new-gestures)
14. [Dependencies](#dependencies)

---

## How It Works

Each webcam frame is passed through MediaPipe's hand landmark model, which detects 21 key points on your hand (fingertips, knuckles, wrist) and returns their X/Y pixel coordinates in real time.

Cursor movement uses **relative positioning** (like a trackpad). When you raise your index finger, the cursor continues from wherever it already was and moves based on how much your hand moves — not based on the absolute position of your hand in the camera frame. This means no sudden jumps when you start moving.

Clicks fire at the exact position the cursor was at before you pinched — a freeze window stops all cursor movement the moment a pinch gesture is detected, so the cursor stays put while the click fires.

---

## ⚠️ Python Version Warning

**Python 3.11 is required. Python 3.12 and 3.13 will NOT work.**

MediaPipe dropped support for the `mp.solutions` API in Python 3.12+. Running on the wrong version gives this immediately on launch:

```
AttributeError: module 'mediapipe' has no attribute 'solutions'
```

The only fix is Python 3.11. Always use a virtual environment (venv) so your system Python doesn't matter.

---

## Requirements

- Python 3.11 (not 3.12, not 3.13)
- A working webcam (built-in or USB)
- Decent lighting — MediaPipe struggles in dim or backlit conditions
- A plain background helps detection accuracy
- Linux or Windows

---

## Installation — Linux

Works on Fedora, Nobara, Ubuntu, Debian, and most other distros.

### Step 1 — Install Python 3.11

```bash
python3.11 --version
```

If not installed:

**Fedora / Nobara:**
```bash
sudo dnf install python3.11 python3.11-devel
```

**Ubuntu / Debian:**
```bash
sudo apt update && sudo apt install python3.11 python3.11-venv python3.11-dev
```

> `python3.11-devel` / `python3.11-dev` is required for building the `evdev` C extension that `pynput` depends on.

### Step 2 — Navigate to project folder

```bash
cd "AR Hand Tracking"
```

### Step 3 — Create and activate virtual environment

```bash
python3.11 -m venv venv
source venv/bin/activate
```

Your prompt will show `(venv)` when active.

### Step 4 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 5 — Verify

```bash
python -c "import mediapipe; import cvzone; import pynput; print('All good')"
```

---

## Installation — Windows

### Step 1 — Install Python 3.11

Download from: https://www.python.org/downloads/release/python-3119/

Scroll to **Files** → download **Windows installer (64-bit)**.

During install, check ✅ **Add Python to PATH**.

Verify:
```cmd
py -3.11 --version
```

### Step 2 — Navigate to project folder

```cmd
cd "C:\Users\YourName\Documents\AR Hand Tracking"
```

### Step 3 — Create and activate virtual environment

```cmd
py -3.11 -m venv venv
venv\Scripts\activate
```

> PowerShell: if activation is blocked, run once:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Step 4 — Install dependencies

```cmd
pip install -r requirements.txt
```

### Step 5 — Verify

```cmd
python -c "import mediapipe; import cvzone; import pynput; print('All good')"
```

---

## Running the App

**Always activate the venv first.**

### Linux

```bash
source venv/bin/activate
python main.py
```

### Windows (CMD)

```cmd
venv\Scripts\activate
python main.py
```

### Windows (PowerShell)

```powershell
.\venv\Scripts\Activate.ps1
python main.py
```

A window opens showing your webcam feed with hand landmarks. Raise your index finger to start moving the cursor — it continues from wherever your cursor already was.

### Quitting

- Press **Q** while the camera window is focused
- Or close the terminal running the script

---

## Gesture Reference

| Gesture | Hand pose | Action |
|---|---|---|
| **Move cursor** | Index finger up. Thumb state doesn't matter. Middle/ring/pinky folded. | Cursor moves relative to hand movement |
| **Left click** | Pinch — bring thumb tip close to index tip | Single left click |
| **Scroll up** | Index + middle fingers up, index higher than middle | Scrolls up |
| **Scroll down** | Index + middle fingers up, middle higher than index | Scrolls down |
| **Right click** | Thumb + pinky up, index/middle/ring folded | Single right click |
| **Idle** | Any other pose, or no hand detected | Nothing — cursor stays put |

### Tips for reliable gestures

- Good lighting from the front is the single biggest factor in detection quality
- Face your palm toward the camera — don't angle it too far sideways
- Use **Idle** deliberately to reposition your hand without moving the cursor — just fold all fingers or show a flat palm, reposition, then raise your index again
- The pinch proximity ring (circle between thumb and index in the camera window) turns green as you approach the click threshold — use it to calibrate your pinch distance
- Clicks have a cooldown (default 400ms) to prevent double-firing

---

## Understanding the Camera Window

| Element | What it is |
|---|---|
| Coloured dots + lines | 21 MediaPipe landmarks — the hand skeleton |
| Grey rectangle | Active zone reference (informational only in relative mode) |
| Top-left label | Currently detected gesture, colour-coded |
| Top-right number | Live FPS counter |
| Circle between thumb and index | Pinch proximity ring — grey → green as you approach click |
| Bottom-left | Q to quit reminder |

---

## Configuration (config.json)

```json
{
  "cam_index": 0,
  "cam_w": 640,
  "cam_h": 480,
  "detection_con": 0.8,
  "active_zone": [0.2, 0.2, 0.8, 0.8],
  "smooth_frames": 8,
  "click_cooldown_ms": 400,
  "scroll_speed": 3,
  "scroll_min_diff": 15,
  "pinch_threshold": 40,
  "pinch_scale_to_hand": false,
  "ref_hand_size": 100,
  "gesture_debounce_frames": 2,
  "move_sensitivity": 3.5
}
```

| Key | Default | What it does | Tuning advice |
|---|---|---|---|
| `cam_index` | 0 | Which camera to open | Change to 1 or 2 if you have multiple cameras |
| `cam_w` / `cam_h` | 640 / 480 | Capture resolution | 640×480 is the sweet spot. Higher = heavier CPU |
| `detection_con` | 0.8 | MediaPipe detection confidence (0.0–1.0) | Lower to 0.6 if hand isn't detected. Raise to 0.9 to reduce false positives |
| `active_zone` | [0.2,0.2,0.8,0.8] | Reference rectangle drawn on screen. Informational in relative mode. | Leave as-is |
| `smooth_frames` | 8 | Frames to average cursor position over | Raise to 10–12 for smoother but slightly laggy cursor. Lower to 4–5 for snappier |
| `click_cooldown_ms` | 400 | Minimum ms between clicks | Raise if double-clicking accidentally |
| `scroll_speed` | 3 | Scroll lines per gesture frame | Raise for faster scroll |
| `scroll_min_diff` | 15 | Min pixel gap between index/middle tips to confirm scroll direction | Raise if scroll flickers |
| `pinch_threshold` | 40 | Pixel distance for pinch detection | Raise (50–60) if clicking accidentally. Lower (25–30) if pinch doesn't register |
| `gesture_debounce_frames` | 2 | Gesture must hold N frames before firing | Raise to 3–4 if random false clicks occur |
| `move_sensitivity` | 3.5 | How many screen pixels to move per camera pixel of hand movement | Raise for faster cursor. Lower for more precision |

---

## Project Structure

```
AR Hand Tracking/
│
├── main.py                   Entry point. Webcam loop, HUD drawing, graceful shutdown.
├── config.json               All runtime settings — the only file to edit for tuning.
├── requirements.txt          pip dependencies.
├── README.md                 This file.
│
├── core/
│   ├── detector.py           Wraps cvzone HandDetector. flipType=False (mirror handled
│   │                         in main.py). Exposes process(), fingers_up(), hand_size().
│   ├── gesture.py            fingers[] + lm[] → gesture string. MOVE ignores thumb
│   │                         state for robustness against label inconsistencies.
│   └── smoother.py           Rolling average deque. flush() clears buffer after clicks.
│
├── control/
│   ├── actions.py            Gesture → action. Relative cursor movement (trackpad style).
│   │                         Click freeze window prevents cursor drift during pinch.
│   └── mouse.py              pynput wrapper. Uses XTest — reliable under Wayland/XWayland.
│
└── utils/
    ├── config.py             Loads config.json once, exposes CFG dict to all modules.
    ├── mapping.py            Camera→screen coordinate mapping (kept for reference).
    └── screen.py             Gets monitor resolution at startup.
```

---

## How the Code Works

```
Webcam frame
    ↓
cv2.flip(frame, 1)                      mirror — natural left/right feel
    ↓
Detector.process(frame)
    ├── findHands(flipType=False)        cvzone + MediaPipe, draws skeleton
    └── lmList → [[id,x,y], ...]        21 landmarks
    ↓
Detector.fingers_up()                   [thumb, index, middle, ring, pinky]
Detector.hand_size()                    wrist-to-MCP9 distance
    ↓
gesture.recognize(fingers, lm)
    ├── pinch dist < threshold          → CLICK
    ├── index up, mid/ring/pinky down   → MOVE  (thumb ignored)
    ├── index+middle up, deadzone check → SCROLL UP/DOWN
    └── thumb+pinky up                  → RIGHT_CLICK
    ↓
actions.dispatch(gesture, lm, sw, sh)
    ├── MOVE
    │   ├── if freeze window active → skip (cursor stays frozen)
    │   ├── if _prev_hand is None → read OS cursor via pynput.position()
    │   │   set anchor, return (no movement this frame)
    │   └── else: dx/dy delta from prev_hand → scale by sensitivity
    │         → smoother.smooth() → pynput.move()
    ├── CLICK/RIGHT_CLICK
    │   ├── extend freeze window (cursor not touched during pinch)
    │   ├── reset _prev_hand (next MOVE re-anchors to OS cursor)
    │   └── if confirmed + cooldown: pynput.click() at current cursor pos
    └── SCROLL → pynput.scroll()
    ↓
draw_hud() → cv2.imshow()
```

---

## Troubleshooting

### `mediapipe has no attribute 'solutions'`
Wrong Python version. Recreate venv with 3.11:
```bash
rm -rf venv && python3.11 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

### `evdev` build fails during `pip install pynput`
Missing Python dev headers:
```bash
# Fedora/Nobara:
sudo dnf install python3.11-devel
# Ubuntu/Debian:
sudo apt install python3.11-dev
```
Then retry `pip install -r requirements.txt`.

### Cursor jumps to a random position when raising index finger
Make sure you have the latest `actions.py` which uses relative (delta) movement. Old versions used absolute coordinate mapping.

### Cursor only moves when thumb is also raised (V shape)
Make sure you have the latest `gesture.py`. The MOVE check now ignores thumb state — only index up + middle/ring/pinky down is required.

### Cursor is too slow
Increase `move_sensitivity` in `config.json` (try 4.0 or 5.0).

### Cursor is too fast / hard to control precisely
Lower `move_sensitivity` (try 2.5). Also increase `smooth_frames` to 10–12.

### Left and right hands swapped
In `core/detector.py`, confirm `findHands` is called with `flipType=False`. Do NOT add any manual label swap.

### Clicks not registering on Linux (Wayland)
Make sure `pynput` is installed: `pip install pynput`. The `mouse.py` must use pynput, not pyautogui.

### Cursor is jittery
Increase `smooth_frames` to 10–12 in `config.json`.

### Scroll flickers between up and down
Raise `scroll_min_diff` to 25–30.

### Hand not detected
- Improve front lighting
- Lower `detection_con` to 0.6
- Hold hand 30–60cm from camera
- Use a plain background

### Camera not found
Change `cam_index` in `config.json` from 0 to 1 or 2.

### QFont warnings flooding terminal (Linux KDE)
Harmless Qt scaling warning. Suppress with:
```bash
QT_FONT_DPI=96 QT_AUTO_SCREEN_SCALE_FACTOR=0 python main.py
```
Or add to top of `main.py` before imports:
```python
import os
os.environ.setdefault('QT_FONT_DPI', '96')
os.environ.setdefault('QT_AUTO_SCREEN_SCALE_FACTOR', '0')
```

---

## Adding New Gestures

### Step 1 — Add constant + condition in `core/gesture.py`

```python
DOUBLE_CLICK = "double_click"

# Inside recognize(), before the final return IDLE:
if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
    return DOUBLE_CLICK
```

### Step 2 — Handle in `control/actions.py`

```python
from core.gesture import MOVE, CLICK, RIGHT_CLICK, SCROLL_UP, SCROLL_DOWN, DOUBLE_CLICK

elif gesture == DOUBLE_CLICK and confirmed:
    _freeze_until = now + _FREEZE_S
    _prev_hand = None
    if now - _last_click > _COOLDOWN:
        from control.mouse import double_click
        double_click()
        _last_click = now
        _smoother.flush()
```

### Step 3 — Add HUD label in `main.py`

```python
_HINTS["double_click"] = "Double Click!"
_COLOR["double_click"]  = (0, 255, 180)
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `opencv-python` | Webcam capture, frame display, drawing |
| `cvzone` | HandDetector wrapper around MediaPipe |
| `mediapipe` | 21-point hand landmark model — **Python 3.11 only** |
| `pynput` | Mouse control via XTest — reliable under Wayland/XWayland |
| `pyautogui` | Screen size fallback only |
| `numpy` | Coordinate math |
| `screeninfo` | Primary monitor resolution detection |
