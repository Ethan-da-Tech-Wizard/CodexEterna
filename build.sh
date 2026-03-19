#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# build.sh  —  Builds the CodexEterna desktop app for macOS / Linux
#
# Requirements (install once):
#   • Node.js 18+      https://nodejs.org
#   • .NET 7 SDK       https://dotnet.microsoft.com/download
#   • Python 3.11+     https://python.org
#   • pip install pyinstaller
#
# Run:
#   chmod +x build.sh
#   ./build.sh
#
# Output:
#   dist/CodexEterna-1.0.0.dmg       (macOS)
#   dist/CodexEterna-1.0.0.AppImage  (Linux)
# ─────────────────────────────────────────────────────────────────────────────
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   CodexEterna — Desktop App Builder      ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Step 1: Build the C# PingService ─────────────────────────────────────────
echo "▶ Step 1/4  Building C# PingService (self-contained)…"
cd "$ROOT/PingService"

if [[ "$OSTYPE" == "darwin"* ]]; then
  RID="osx-x64"
else
  RID="linux-x64"
fi

dotnet publish -c Release -r "$RID" --self-contained true \
  -p:PublishSingleFile=true \
  -p:PublishTrimmed=false \
  -o "$ROOT/PingService/bin/Release/net7.0/publish"

echo "   ✅ PingService built"

# ── Step 2: Build the Python SportsService ───────────────────────────────────
echo ""
echo "▶ Step 2/4  Building Python SportsService (PyInstaller)…"
cd "$ROOT/SportsService"

# Install deps into a local venv for a clean build
python3 -m venv .build-venv
source .build-venv/bin/activate
pip install --quiet -r requirements.txt pyinstaller

pyinstaller --onefile \
  --name SportsService \
  --distpath dist \
  --hidden-import uvicorn.logging \
  --hidden-import uvicorn.loops \
  --hidden-import uvicorn.loops.auto \
  --hidden-import uvicorn.protocols \
  --hidden-import uvicorn.protocols.http \
  --hidden-import uvicorn.protocols.http.auto \
  --hidden-import uvicorn.protocols.websockets \
  --hidden-import uvicorn.protocols.websockets.auto \
  --hidden-import uvicorn.lifespan \
  --hidden-import uvicorn.lifespan.on \
  --hidden-import sqlalchemy.dialects.sqlite \
  run.py

deactivate
echo "   ✅ SportsService built → dist/SportsService"

# ── Step 3: Install Electron dependencies ────────────────────────────────────
echo ""
echo "▶ Step 3/4  Installing Electron dependencies…"
cd "$ROOT/electron"
npm install --silent
echo "   ✅ Node modules ready"

# ── Step 4: Package into installer ───────────────────────────────────────────
echo ""
echo "▶ Step 4/4  Packaging Electron app…"
npm run "build:$([ "$OSTYPE" == "darwin"* ] && echo mac || echo linux)"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   ✅  Build complete!                    ║"
echo "║   Output: dist/                          ║"
echo "╚══════════════════════════════════════════╝"
echo ""
ls -lh "$ROOT/dist/"
