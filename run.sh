#!/bin/bash
# Quick start script for Linux/macOS

echo "=========================================="
echo "  Pokémon & Satellite Image AI Tool"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import gradio" 2>/dev/null; then
    echo "⚠️  Dependencies not installed!"
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
fi

# Run the application
echo ""
echo "🚀 Starting application..."
echo "📝 The UI will open at http://localhost:7860"
echo ""
python app.py "$@"
