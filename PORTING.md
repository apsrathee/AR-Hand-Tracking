# Hyprland / Wayland port — notes & credits

## Credit & license

This is a **modified version** of **AR-Hand-Tracking** by **apsrathee (_cloud-)**:
<https://github.com/apsrathee/AR-Hand-Tracking>

The original is **MIT licensed**. The `LICENSE` file and the original copyright
notice are retained unchanged. All credit for the original application, its
design, and its code belongs to the upstream author. The modifications below are
local changes made to run it on a specific Linux setup, shared in the same MIT
spirit — not a claim of original authorship.

## What this fork changes, and why

Target environment: Arch-based **Omarchy**, **Hyprland (Wayland)**, AMD Radeon GPU,
Python 3.14 host. Each change is labelled as a *workaround*, a *platform port*, a
*feature*, or a *fix* so it's clear what is what.

### 1. MediaPipe pinned to `0.10.35` — *workaround for an upstream bug*
- MediaPipe **1.x self-SIGKILLs** during CPU/XNNPACK init on Arch Linux. The kill
  comes from MediaPipe's own internal `drishti` profiler thread, **not** the OOM
  killer. Tracked upstream as
  [google-ai-edge/mediapipe#6375](https://github.com/google-ai-edge/mediapipe/issues/6375).
- The upstream README **already requires Python 3.11**; the loose `mediapipe>=0.10.9`
  pin simply let pip install the buggy 1.x. Pinning `0.10.35` honours the author's
  stated requirement and avoids the crash. This is not a change to the app's logic.
- The GPU delegate is **not** a workaround here: it initialises but fails at
  inference on this AMD/WebGPU stack ("Failed to create custom tensor buffer").

### 2. Mouse input: pynput kept, ydotool added — *platform port*
- `pynput` cannot acquire an X connection on this Wayland session.
- `control/mouse.py` now **tries pynput first** (X11/Windows — original behaviour
  unchanged) and **falls back to ydotool + Hyprland IPC** on Wayland. Cross-platform
  support is preserved, not replaced.
- ydotool's absolute coordinates are in the monitor's **native** mode space, so they
  are scaled to the current logical mode (e.g. 2x on a 4K-native panel at 1080p).
- `hyprctl cursorpos/monitors` need `HYPRLAND_INSTANCE_SIGNATURE`; it is derived
  automatically from `hyprctl instances` when missing.

### 3. `movement_mode` option — *feature, respects the original design*
- The original deliberately uses **relative / trackpad** movement ("no sudden
  jumps"). That remains the **default**.
- Added `config.json` key `"movement_mode": "relative" | "positional"`.
  `positional` maps the hand's spot inside the `active_zone` (the inner square on
  the feed) 1:1 to the full screen.
- This fork's `config.json` ships `"positional"` as a user preference; upstream
  behaviour is untouched when the key is absent or `"relative"`.

### 4. Gesture reliability — *fixes*
- **Pinch gated on the index being curled** (`fingers[1]==0`). Previously a pointing
  hand (thumb naturally near the index) was misread as a pinch, so the cursor never
  received a MOVE.
- **MOVE made lenient** (index extended; an open hand also works). The strict
  index-only pose was too finicky to hold reliably.
- `detection_con` lowered `0.8 -> 0.6` to keep the hand locked in dim lighting;
  `smooth_frames` `8 -> 3` for a crisper positional feel.

## Setup gotchas (handled by `deploy/` + `setup.sh`)
- `DISPLAY=:0` — **not** `unix:0` (which fails to connect and breaks pynput and Qt).
- `QT_QPA_PLATFORM=xcb` — OpenCV's bundled Qt only ships the xcb platform plugin.
- `OPENBLAS_NUM_THREADS=1` — avoids an OpenBLAS thread-pool SIGABRT under systemd.
- ydotoold socket pinned to `$XDG_RUNTIME_DIR/.ydotool_socket` — **not** `/tmp`,
  which gets cleaned and silently breaks injection.
- Runs as a **systemd user service** (`deploy/systemd/`), not a shell background job.

## Install / run
Requires Python 3.11, Hyprland, and ydotool. See `setup.sh` and `deploy/`.
```bash
./setup.sh
systemctl --user start ar-hand-tracking.service
```

## Giving back
- The broadly-useful changes (gesture fixes, `movement_mode` option) can be offered
  back to `apsrathee/AR-Hand-Tracking` as a pull request.
- The MediaPipe crash workaround belongs on
  [google-ai-edge/mediapipe#6375](https://github.com/google-ai-edge/mediapipe/issues/6375),
  where others hitting the same SIGKILL will find it.