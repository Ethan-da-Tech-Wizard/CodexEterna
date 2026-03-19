#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# build.sh  —  Builds CodexEterna into a single portable binary
#
# Requirements (install once on THIS build machine, not on the target):
#   • Python 3.11+   https://python.org
#
# Run:
#   chmod +x build.sh && ./build.sh
#
# Output:
#   dist/CodexEterna          (macOS / Linux — share this file with anyone)
# ─────────────────────────────────────────────────────────────────────────────
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   CodexEterna — Portable App Builder     ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Check Python ──────────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo "ERROR: Python 3 not found."
  echo "Install Python 3.11+ from https://python.org"
  exit 1
fi

# ── Step 1: Create venv ───────────────────────────────────────────────────────
echo "▶ Step 1/3  Setting up Python environment…"
python3 -m venv .build-venv
source .build-venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt pyinstaller
echo "   ✅ Environment ready"

# ── Step 2: Build ─────────────────────────────────────────────────────────────
echo ""
echo "▶ Step 2/3  Building portable binary…"

pyinstaller --onefile \
  --name CodexEterna \
  --distpath dist \
  --add-data "templates:templates" \
  --add-data "static:static" \
  --hidden-import flask_socketio \
  --hidden-import engineio \
  --hidden-import engineio.async_drivers.threading \
  --hidden-import socketio \
  app.py

deactivate
echo "   ✅ Build complete → dist/CodexEterna"

# ── Step 3: Done ──────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   Done!                                  ║"
echo "║                                          ║"
echo "║   Your file:  dist/CodexEterna           ║"
echo "║                                          ║"
echo "║   Send that file to anyone.              ║"
echo "║   They just double-click it — done.      ║"
echo "╚══════════════════════════════════════════╝"
echo ""
ls -lh "$ROOT/dist/"
