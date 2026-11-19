#!/usr/bin/env bash
# Setup for the AR Hand Tracking Hyprland/Wayland port.
# Creates a Python 3.11 venv, installs the pinned deps, and installs the systemd
# user units. Review this script before running it.
set -euo pipefail
cd "$(dirname "$0")"
REPO="$(pwd)"

PY311="$(command -v python3.11 || true)"
if [ -z "$PY311" ]; then
  echo "ERROR: Python 3.11 is required but was not found on PATH." >&2
  echo "Install it first (see README 'Python Version Warning'), e.g. via your" >&2
  echo "distro package manager, mise, or uv." >&2
  exit 1
fi

echo "==> Creating venv311 with $PY311"
"$PY311" -m venv venv311
./venv311/bin/python -m pip install --upgrade pip
./venv311/bin/python -m pip install -r requirements.txt

echo "==> Installing systemd user units"
mkdir -p "$HOME/.config/systemd/user"
cp deploy/systemd/ydotoold.service "$HOME/.config/systemd/user/ydotoold.service"
# Point the app unit at this clone's actual location.
sed "s|%h/Projects/AR-Hand-Tracking|$REPO|g" \
  deploy/systemd/ar-hand-tracking.service \
  > "$HOME/.config/systemd/user/ar-hand-tracking.service"
chmod +x deploy/run.sh
systemctl --user daemon-reload
systemctl --user enable --now ydotoold.service

cat <<EOF

Done. Next steps:
  systemctl --user start ar-hand-tracking.service     # start the app
  systemctl --user stop  ar-hand-tracking.service     # stop it
  journalctl --user -u ar-hand-tracking.service -f    # logs

Notes:
  - Requires Hyprland (for hyprctl cursor read/move) and ydotool.
  - The app unit is installed but NOT auto-started; start it on demand.
  - Movement mode / gestures are tuned in config.json (see PORTING.md).
EOF