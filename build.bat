@echo off
REM ─────────────────────────────────────────────────────────────────────────────
REM build.bat  —  Builds CodexEterna into a single portable .exe
REM
REM Requirements (install once on THIS build machine, not on the target):
REM   • Python 3.11+  https://python.org  — tick "Add to PATH" during install
REM
REM Run:
REM   Double-click build.bat   OR   open Command Prompt here and type: build.bat
REM
REM Output:
REM   dist\CodexEterna.exe   (share this file with anyone — no installs needed)
REM ─────────────────────────────────────────────────────────────────────────────

setlocal enabledelayedexpansion
set ROOT=%~dp0
cd /d "%ROOT%"

echo.
echo ╔══════════════════════════════════════════╗
echo ║   CodexEterna — Portable App Builder     ║
echo ╚══════════════════════════════════════════╝
echo.

REM ── Check Python ─────────────────────────────────────────────────────────
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found.
    echo Install Python 3.11+ from https://python.org
    echo Make sure to tick "Add to PATH" during install, then restart this window.
    pause
    exit /b 1
)

REM ── Step 1: Create venv ───────────────────────────────────────────────────
echo [1/3] Setting up Python environment...
python -m venv .build-venv
call .build-venv\Scripts\activate.bat
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt pyinstaller
echo    OK  Environment ready

REM ── Step 2: Build ─────────────────────────────────────────────────────────
echo.
echo [2/3] Building portable executable...
pyinstaller --onefile ^
  --name CodexEterna ^
  --distpath dist ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --hidden-import flask_socketio ^
  --hidden-import engineio ^
  --hidden-import engineio.async_drivers.threading ^
  --hidden-import socketio ^
  app.py

call .build-venv\Scripts\deactivate.bat

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo    OK  Build complete

REM ── Step 3: Done ─────────────────────────────────────────────────────────
echo.
echo ╔══════════════════════════════════════════╗
echo ║   Done!                                  ║
echo ║                                          ║
echo ║   Your file:  dist\CodexEterna.exe       ║
echo ║                                          ║
echo ║   Send that file to anyone.              ║
echo ║   They just double-click it — done.      ║
echo ╚══════════════════════════════════════════╝
echo.
explorer "%ROOT%dist"
pause
