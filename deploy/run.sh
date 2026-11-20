#!/usr/bin/env bash
# Runtime wrapper for the Hyprland/Wayland port. Sets session-specific env that
# a static systemd unit cannot know, then launches the app.
set -euo pipefail

export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export DISPLAY="${DISPLAY:-:0}"
export YDOTOOL_SOCKET="${YDOTOOL_SOCKET:-$XDG_RUNTIME_DIR/.ydotool_socket}"

# hyprctl cursorpos/monitors need the instance signature. `hyprctl instances`
# works without it, so derive it when missing. (control/mouse.py also does this.)
if command -v hyprctl >/dev/null 2>&1 && [ -z "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]; then
  sig="$(hyprctl instances -j 2>/dev/null \
        | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d[0]["instance"] if d else "")' \
        2>/dev/null || true)"
  [ -n "$sig" ] && export HYPRLAND_INSTANCE_SIGNATURE="$sig"
fi

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$DIR/venv311/bin/python3"
[ -x "$PY" ] || PY="$DIR/venv/bin/python3"
exec "$PY" "$DIR/main.py"