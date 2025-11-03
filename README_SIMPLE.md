# 🎮🛰️ Pokemon & Satellite Image Comparison Tool

**A simple, working web app for Pokemon data management and satellite image change detection**

![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## ✨ Features

1. **📊 Pokemon Data Manager**
   - Upload CSV/Excel files with Pokemon data
   - Search Pokemon by name, type, stats
   - View and analyze Pokemon information

2. **🛰️ Satellite Image Fetcher**
   - Fetch FREE satellite images from NASA (NO API key needed!)
   - Select from example locations or enter custom coordinates
   - Choose before/after dates for comparison

3. **🔍 Image Change Detection**
   - Upload or fetch satellite images
   - Automated change detection analysis
   - Visual difference maps with detailed statistics
   - Similarity scoring and change assessment

---

## 🚀 Quick Start (5 Minutes!)

### Step 1: Check Python Version

You need **Python 3.10 or higher**.

```bash
python --version
```

If you see `Python 3.10.x` or higher, you're good! If not, download from [python.org](https://python.org)

---

### Step 2: Install

```bash
# Clone or download this repository
cd CodexEterna

# Create virtual environment
python -m venv venv

# Activate virtual environment

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Note:** If you get errors installing dependencies, try:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 3: Run the App

```bash
# Make sure you're in the CodexEterna folder
cd backend

# Run the server
python app.py
```

You should see:
```
✅ Starting server...
📍 Open your browser to: http://localhost:5000
```

---

### Step 4: Open in Browser

Open your web browser and go to:

```
http://localhost:5000
```

You should see the app with 3 tabs:
- 🎮 Pokemon Data
- 🛰️ Satellite Images
- 🔍 Image Comparison

---

## 📖 How to Use

### 🎮 Tab 1: Pokemon Data

**Upload Your Data:**

1. Click the "Pokemon Data" tab
2. Click "Choose File" and select your Pokemon CSV or Excel file
   - Sample file: `data/pokemon/sample_pokemon.csv`
3. Click "Upload Pokemon Data"
4. You'll see: "✅ Loaded XX Pokemon!"

**Search Pokemon:**

1. Type in the search box (e.g., "Pikachu", "Fire", "Attack")
2. Click "Search"
3. Results appear below with all Pokemon details

**Example Searches:**
- `Pikachu` - Find Pikachu
- `Fire` - Find all Fire-type Pokemon
- `Electric` - Find Electric-type Pokemon
- `100` - Find Pokemon with stats containing 100

---

### 🛰️ Tab 2: Satellite Images

**Quick Start with Examples:**

1. Click the "Satellite Images" tab
2. Select "Dubai (Urban Development)" from dropdown
3. Keep the default dates (or change them)
4. Click "📥 Fetch Before Image"
5. Click "📥 Fetch After Image"
6. Images appear below!

**Custom Location:**

1. Enter your own coordinates:
   - Latitude: e.g., `25.2048` (Dubai)
   - Longitude: e.g., `55.2708`
2. Set dates (YYYY-MM-DD format)
3. Click fetch buttons

**Example Locations:**
- **Dubai**: 25.2048, 55.2708 (urban growth)
- **Amazon**: -3.4653, -62.2159 (deforestation)
- **Las Vegas**: 36.1699, -115.1398 (desert expansion)
- **Aral Sea**: 45.0, 60.0 (water loss)

**Notes:**
- Uses NASA GIBS (completely FREE, no API key!)
- Historical data from 2000-present
- May take 5-10 seconds to fetch

---

### 🔍 Tab 3: Image Comparison

**Option A: Use Fetched Images (Recommended)**

1. Go to "Satellite Images" tab first
2. Fetch before and after images
3. Switch to "Image Comparison" tab
4. Click "🔍 Compare Images & Detect Changes"
5. See detailed analysis!

**Option B: Upload Your Own Images**

1. Click "Image Comparison" tab
2. Upload "Before Image" (any image file)
3. Upload "After Image" (any image file)
4. Click "🔍 Compare Images & Detect Changes"

**What You'll See:**

- **Similarity Score**: How similar the images are (0-100%)
  - < 30%: MAJOR changes
  - 30-60%: SIGNIFICANT changes
  - 60-85%: MODERATE changes
  - > 85%: MINOR changes

- **Change Assessment**: Text description of changes

- **Difference Map**: Visual heatmap showing where changes occurred (red = most change)

- **Changed Regions**: List of areas that changed with coordinates and sizes

- **Interpretation**: What the changes likely mean

---

## 📁 Project Structure

```
CodexEterna/
├── README_SIMPLE.md          ← You are here!
├── requirements.txt          ← Python dependencies
│
├── backend/
│   └── app.py               ← Flask server (run this!)
│
├── frontend/
│   ├── index.html           ← Main web page
│   ├── style.css            ← Styling (gold/purple/pink theme)
│   └── script.js            ← JavaScript logic
│
├── data/
│   └── pokemon/
│       └── sample_pokemon.csv  ← Sample data
│
└── uploads/                 ← Images stored here
```

---

## 🔧 Troubleshooting

### "Module not found" error

```bash
# Make sure virtual environment is activated
# You should see (venv) in your terminal

# Reinstall dependencies
pip install -r requirements.txt
```

### "Address already in use" error

Another program is using port 5000. Change the port:

```python
# In backend/app.py, change the last line to:
app.run(debug=True, host='0.0.0.0', port=5001)

# Then access at: http://localhost:5001
```

### Images won't load

- Check your internet connection (NASA images are fetched online)
- Try different dates (some dates may not have imagery)
- Try different coordinates

### "Failed to fetch images"

- NASA servers may be slow - try again
- Check coordinates are valid:
  - Latitude: -90 to 90
  - Longitude: -180 to 180
- Check date format: YYYY-MM-DD

### Pokemon upload fails

- Make sure file is CSV or Excel (.xlsx, .xls)
- Check file has data (not empty)
- File should have column headers

---

## 💡 Tips & Tricks

### Best Practices for Change Detection

1. **Choose locations with known changes:**
   - Cities (urban development)
   - Forests (deforestation)
   - Coasts (land reclamation)
   - Deserts (agriculture expansion)

2. **Pick appropriate time ranges:**
   - Urban development: 5-10 years apart
   - Deforestation: 1-3 years apart
   - Seasonal changes: Same month, different years

3. **Use consistent zoom/area:**
   - Keep same coordinates for before/after
   - Don't change coordinates between fetches

### Pokemon Data Tips

1. **File format:**
   - CSV works best
   - Excel also supported
   - Include column headers

2. **Search tips:**
   - Search by name: "Pikachu"
   - Search by type: "Fire", "Water"
   - Search by stats: "100" finds Pokemon with stats containing 100
   - Partial matches work: "Char" finds Charmander, Charmeleon, Charizard

---

## 📊 System Requirements

**Minimum:**
- Python 3.10+
- 2GB RAM
- Internet connection (for NASA images)

**Recommended:**
- Python 3.11+
- 4GB RAM
- Modern web browser (Chrome, Firefox, Edge)

---

## 🆓 What's Free?

✅ **Everything!**

- NASA GIBS satellite images: **Completely FREE, unlimited, no API key**
- All Python libraries: **Open source, free**
- No subscriptions, no limits, no hidden costs

---

## 🐛 Known Issues

1. **First image fetch may be slow** (5-10 seconds)
   - NASA servers can be slow
   - Be patient!

2. **Some dates have no imagery**
   - Try different dates if you get errors
   - Most dates from 2015+ work well

3. **Large Pokemon files may take time**
   - Files with 1000+ rows work fine
   - Just be patient during upload

---

## 🎨 Customization

### Change Colors

Edit `frontend/style.css`:

```css
:root {
    --primary-purple: #9370DB;  /* Change this */
    --gold: #DAA520;            /* And this */
    --light-pink: #FFB6C1;      /* And this */
}
```

### Change Port

Edit `backend/app.py`, last line:

```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change port number
```

---

## 📚 Example Workflow

**Complete Tutorial - Finding Changes in Dubai:**

1. **Start the app:**
   ```bash
   cd backend
   python app.py
   ```

2. **Open browser:** http://localhost:5000

3. **Go to Satellite Images tab**

4. **Select "Dubai" from dropdown**

5. **Set dates:**
   - Before: 2015-01-01
   - After: 2023-01-01

6. **Fetch images:**
   - Click "Fetch Before Image" (wait 5-10 sec)
   - Click "Fetch After Image" (wait 5-10 sec)

7. **Go to Image Comparison tab**

8. **Click "Compare Images & Detect Changes"**

9. **See the results:**
   - Similarity score (probably ~40-60% for Dubai)
   - Change assessment
   - Difference map
   - Changed regions

10. **Interpret:**
    - Red areas = significant changes
    - Dubai shows lots of urban development
    - New buildings, roads visible

---

## ❓ FAQ

**Q: Do I need an API key?**
A: No! NASA GIBS is completely free, no registration needed.

**Q: Can I use my own images?**
A: Yes! Upload any images in the Comparison tab.

**Q: What image formats work?**
A: JPG, PNG, and most common formats.

**Q: How accurate is change detection?**
A: Very accurate for clear changes (buildings, deforestation). Less accurate for subtle changes.

**Q: Can I save results?**
A: Take screenshots for now. We may add export in future.

**Q: Where do uploaded files go?**
A: `uploads/` folder. You can delete them anytime.

---

## 🤝 Contributing

Found a bug? Have a suggestion?

1. Create an issue on GitHub
2. Or submit a pull request

---

## 📝 License

MIT License - Use freely!

---

## 🙏 Credits

- **NASA GIBS** for free satellite imagery
- **Flask** for backend framework
- **OpenCV** for image processing

---

## 🆘 Still Having Issues?

1. Make sure Python 3.10+ is installed
2. Make sure virtual environment is activated (you see `(venv)` in terminal)
3. Make sure you're in the `backend` folder when running `python app.py`
4. Check http://localhost:5000 in your browser
5. Try the sample Pokemon data first to test

**If nothing works:**
1. Delete `venv` folder
2. Start fresh from Step 2 of Quick Start
3. Copy/paste any error messages if asking for help

---

**Made with ❤️ for easy satellite image analysis and Pokemon data fun!**

**No API keys • No subscriptions • No complexity • Just works!** ✨
