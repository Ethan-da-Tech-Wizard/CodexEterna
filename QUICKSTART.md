# 🚀 Quick Start Guide

Get up and running with the LLM-Powered Pokémon Data & Satellite Image Tool in 5 minutes!

## Prerequisites
- Python 3.10+
- 8-16GB RAM
- ~10GB free disk space

## Installation (3 steps)

### 1. Clone and Navigate
```bash
git clone https://github.com/Ethan-da-Tech-Wizard/CodexEterna.git
cd CodexEterna
```

### 2. Set Up Environment
**Linux/macOS:**
```bash
./run.sh
```

**Windows:**
```cmd
run.bat
```

These scripts will automatically:
- Create a virtual environment
- Install all dependencies
- Start the application

### 3. Open Browser
Navigate to: **http://localhost:7860**

## First Time Usage

### Try Pokémon Q&A
1. Upload `data/pokemon/sample_pokemon.csv` (included)
2. Click "Load Pokémon Data"
3. Ask: *"Which Pokémon has the highest Attack stat?"*

### Try Image Analysis
1. Upload two images (before/after)
2. Ask: *"What are the main differences between these images?"*

## Manual Installation

If you prefer manual setup:

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

## Command Line Options

```bash
# Simple mode (default, less RAM)
python app.py

# Full LLM mode (better quality, more RAM)
python app.py --full-llm

# Custom port
python app.py --port 8080

# Public sharing
python app.py --share
```

## Common Issues

### Out of Memory
- Use simple mode (default)
- Close other applications

### Slow Performance
- First run downloads models (~5GB)
- Subsequent runs are faster
- Consider using GPU if available

### Import Errors
```bash
pip install --upgrade -r requirements.txt
```

## What Can I Do?

### Pokémon Queries
- "What are Fire-type Pokémon?"
- "Which Pokémon has HP over 100?"
- "Compare Pikachu and Raichu"

### Image Analysis
- "Describe the first image"
- "What changed between the images?"
- "Are these the same location?"
- "What objects do you see?"

## Next Steps

📖 Read the full [README.md](README.md) for:
- Detailed architecture
- Advanced configuration
- Troubleshooting tips
- Contributing guidelines

## Need Help?

- 📝 [GitHub Issues](https://github.com/Ethan-da-Tech-Wizard/CodexEterna/issues)
- 💬 [Discussions](https://github.com/Ethan-da-Tech-Wizard/CodexEterna/discussions)

---

**Happy exploring! 🎮🛰️**
