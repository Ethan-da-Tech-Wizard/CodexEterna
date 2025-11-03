@echo off
REM Quick start script for Windows

echo ==========================================
echo   Pokemon and Satellite Image AI Tool
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo WARNING: Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import gradio" 2>nul
if errorlevel 1 (
    echo WARNING: Dependencies not installed!
    echo Installing dependencies...
    pip install --upgrade pip
    pip install -r requirements.txt
    echo Dependencies installed
)

REM Run the application
echo.
echo Starting application...
echo The UI will open at http://localhost:7860
echo.
python app.py %*
