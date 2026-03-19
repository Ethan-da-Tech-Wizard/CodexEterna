@echo off
REM ─────────────────────────────────────────────────────────────────────────────
REM build.bat  —  Builds the CodexEterna desktop app for Windows
REM
REM Requirements (install once, then restart your PC):
REM   • Node.js 18+   https://nodejs.org        (check "Add to PATH" during install)
REM   • .NET 7 SDK    https://dotnet.microsoft.com/download
REM   • Python 3.11+  https://python.org        (check "Add to PATH" during install)
REM
REM Run:
REM   Double-click build.bat   OR   open Command Prompt here and type: build.bat
REM
REM Output:
REM   dist\CodexEterna Setup 1.0.0.exe
REM ─────────────────────────────────────────────────────────────────────────────

setlocal enabledelayedexpansion
set ROOT=%~dp0
cd /d "%ROOT%"

echo.
echo ╔══════════════════════════════════════════╗
echo ║   CodexEterna — Desktop App Builder      ║
echo ╚══════════════════════════════════════════╝
echo.

REM ── Step 1: Build C# PingService ─────────────────────────────────────────
echo [1/4] Building C# PingService...
cd /d "%ROOT%PingService"

dotnet publish -c Release -r win-x64 --self-contained true ^
  -p:PublishSingleFile=true ^
  -p:PublishTrimmed=false ^
  -o "%ROOT%PingService\bin\Release\net7.0\publish"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: PingService build failed.
    echo Make sure .NET 7 SDK is installed: https://dotnet.microsoft.com/download
    pause
    exit /b 1
)
echo    OK  PingService built

REM ── Step 2: Build Python SportsService ───────────────────────────────────
echo.
echo [2/4] Building Python SportsService...
cd /d "%ROOT%SportsService"

python -m venv .build-venv
call .build-venv\Scripts\activate.bat
pip install --quiet -r requirements.txt pyinstaller

pyinstaller --onefile ^
  --name SportsService ^
  --distpath dist ^
  --hidden-import uvicorn.logging ^
  --hidden-import uvicorn.loops ^
  --hidden-import uvicorn.loops.auto ^
  --hidden-import uvicorn.protocols ^
  --hidden-import uvicorn.protocols.http ^
  --hidden-import uvicorn.protocols.http.auto ^
  --hidden-import uvicorn.protocols.websockets ^
  --hidden-import uvicorn.protocols.websockets.auto ^
  --hidden-import uvicorn.lifespan ^
  --hidden-import uvicorn.lifespan.on ^
  --hidden-import sqlalchemy.dialects.sqlite ^
  run.py

call .build-venv\Scripts\deactivate.bat

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: SportsService build failed.
    echo Make sure Python 3.11+ is installed: https://python.org
    pause
    exit /b 1
)
echo    OK  SportsService built

REM ── Step 3: Install Electron deps ────────────────────────────────────────
echo.
echo [3/4] Installing Electron dependencies...
cd /d "%ROOT%electron"
npm install

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: npm install failed.
    echo Make sure Node.js 18+ is installed: https://nodejs.org
    pause
    exit /b 1
)
echo    OK  Node modules ready

REM ── Step 4: Package ──────────────────────────────────────────────────────
echo.
echo [4/4] Packaging Electron app...
npm run build:win

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Electron packaging failed.
    pause
    exit /b 1
)

echo.
echo ╔══════════════════════════════════════════╗
echo ║   Build complete!                        ║
echo ║   Open the  dist\  folder to find        ║
echo ║   your installer .exe                    ║
echo ╚══════════════════════════════════════════╝
echo.
explorer "%ROOT%dist"
pause
