# 🛰️ Satellite Image API Setup Guide

Complete guide to setting up free satellite imagery APIs for the enhanced change detection feature.

---

## Overview

The enhanced version of the tool allows you to fetch satellite images directly from free APIs for change detection analysis. This guide covers setting up three free satellite image providers.

## 🌍 Quick Comparison

| Provider | Free Tier | API Key Required | Historical Data | Resolution | Best For |
|----------|-----------|------------------|-----------------|------------|----------|
| **NASA GIBS** | ✅ Unlimited | ❌ No | ✅ 2000-present | Medium (250m-1km) | **Testing & Education** |
| **Sentinel Hub** | 5,000 requests/month | ✅ Yes (free) | ✅ 2015-present | High (10-60m) | **Professional Use** |
| **Mapbox** | 50,000 requests/month | ✅ Yes (free) | ❌ Current only | Very High | **High-res Current** |

---

## 1️⃣ NASA GIBS (Recommended for Getting Started)

### ✅ Advantages
- **Completely FREE** - No limits, no API key
- **No registration required**
- **Global coverage** with daily updates
- **Historical data** back to 2000
- **Perfect for testing** and education

### 📋 Setup Steps

**NO SETUP NEEDED!** Just run the app and select "NASA" as your image source.

### 📚 Data Available
- MODIS Terra/Aqua True Color
- VIIRS True Color
- Landsat imagery
- Sentinel-2 (via NASA's mirror)

### 🔗 More Info
- Website: https://worldview.earthdata.nasa.gov/
- Docs: https://wiki.earthdata.nasa.gov/display/GIBS

---

## 2️⃣ Sentinel Hub

### ✅ Advantages
- **High resolution** (10-60m)
- **5,000 free requests/month**
- **Sentinel-2** L1C and L2A data
- **Custom scripts** for specialized analysis
- **Historical data** from 2015

### 📋 Setup Steps

#### Step 1: Create Account
1. Go to https://www.sentinel-hub.com/
2. Click "Sign Up" (top right)
3. Choose "Free Trial" plan
4. Complete registration

#### Step 2: Create Configuration
1. Log in to your dashboard
2. Go to "Configuration Utility"
3. Click "Add New Configuration"
4. Fill in:
   - **Name**: "CodexEterna" (or any name)
   - **Description**: "Change detection tool"
5. Click "Create"

#### Step 3: Get Instance ID
1. In your configuration list, click on your new configuration
2. Copy the **Instance ID** (looks like: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

#### Step 4: Set Environment Variable

**Linux/macOS:**
```bash
export SENTINEL_HUB_INSTANCE_ID="your-instance-id-here"
```

**Windows PowerShell:**
```powershell
$env:SENTINEL_HUB_INSTANCE_ID="your-instance-id-here"
```

**Or create `.env` file** in project root:
```
SENTINEL_HUB_INSTANCE_ID=your-instance-id-here
```

### 💡 Usage Tips
- Free tier resets monthly
- 5,000 requests = ~166 requests per day
- Each image fetch = 1 request
- Image pairs = 2 requests

### 🔗 More Info
- Dashboard: https://apps.sentinel-hub.com/dashboard/
- Docs: https://docs.sentinel-hub.com/

---

## 3️⃣ Mapbox Satellite

### ✅ Advantages
- **Very high resolution**
- **50,000 free requests/month**
- **Easy to use API**
- **Beautiful imagery**

### ⚠️ Limitations
- **No historical data** (current imagery only)
- Less useful for temporal change detection
- Better for location context

### 📋 Setup Steps

#### Step 1: Create Account
1. Go to https://account.mapbox.com/auth/signup/
2. Sign up for free account
3. Confirm your email

#### Step 2: Get Access Token
1. Log in to https://account.mapbox.com/
2. Go to "Access Tokens" section
3. Copy your **Default Public Token**
   - Or click "Create a token" for a new one

#### Step 3: Set Environment Variable

**Linux/macOS:**
```bash
export MAPBOX_ACCESS_TOKEN="pk.eyJ1IjoibXl1c2VybmFtZSIsImEiOiJjbGo..."
```

**Windows PowerShell:**
```powershell
$env:MAPBOX_ACCESS_TOKEN="pk.eyJ1IjoibXl1c2VybmFtZSIsImEiOiJjbGo..."
```

**Or add to `.env` file:**
```
MAPBOX_ACCESS_TOKEN=pk.eyJ1IjoibXl1c2VybmFtZSIsImEiOiJjbGo...
```

### 💡 Usage Tips
- Free tier = 50,000 tile requests/month
- Monitor usage at https://account.mapbox.com/
- Best for high-res static imagery

### 🔗 More Info
- Docs: https://docs.mapbox.com/api/maps/static-images/
- Account: https://account.mapbox.com/

---

## 🚀 Using the APIs in the Tool

### Method 1: Using the Enhanced UI

1. **Launch with enhanced mode:**
   ```bash
   python app.py --enhanced
   ```

2. **Navigate to "🛰️ Satellite Image Analysis" tab**

3. **Choose your workflow:**

   **Option A: Use Example Locations**
   - Select from dropdown (e.g., "Dubai (Urban Development)")
   - Adjust dates if needed
   - Select API source
   - Click "Fetch Satellite Images"

   **Option B: Custom Location**
   - Enter location name
   - Input latitude and longitude
   - Enter before/after dates (YYYY-MM-DD format)
   - Select API source
   - Click "Fetch Satellite Images"

4. **Run Change Detection:**
   - Once images are fetched
   - Click "Run Change Detection Analysis"
   - View comprehensive report

### Method 2: Using API Directly in Code

```python
from src.modules.satellite_fetcher import SatelliteImageFetcher

# Initialize fetcher
fetcher = SatelliteImageFetcher()

# Fetch image pair (NASA GIBS - no key needed)
img_before, img_after = fetcher.fetch_image_pair(
    latitude=25.2048,    # Dubai
    longitude=55.2708,
    date1="2015-01-01",
    date2="2023-01-01",
    source="nasa"
)

# Save images
fetcher.save_image(img_before, "before.jpg")
fetcher.save_image(img_after, "after.jpg")
```

---

## 📝 Example Locations

The tool includes pre-configured example locations:

1. **Amazon Rainforest** (Deforestation)
   - Lat: -3.4653, Lon: -62.2159
   - Shows forest loss over time

2. **Dubai** (Urban Development)
   - Lat: 25.2048, Lon: 55.2708
   - Rapid city growth

3. **Aral Sea** (Water Loss)
   - Lat: 45.0, Lon: 60.0
   - Dramatic lake shrinkage

4. **Las Vegas** (Urban Expansion)
   - Lat: 36.1699, Lon: -115.1398
   - Desert city expansion

5. **Jakarta Bay** (Land Reclamation)
   - Lat: -6.1751, Lon: 106.8650
   - Coastal development

---

## 🔧 Environment Variables Setup

### Using .env File (Recommended)

Create a `.env` file in the project root:

```bash
# Satellite Image API Keys
SENTINEL_HUB_INSTANCE_ID=your-sentinel-instance-id
MAPBOX_ACCESS_TOKEN=your-mapbox-token

# Optional: Other settings
LOG_LEVEL=INFO
```

The app automatically loads this file on startup.

### Using Shell Profile (Persistent)

**Linux/macOS** - Add to `~/.bashrc` or `~/.zshrc`:
```bash
export SENTINEL_HUB_INSTANCE_ID="your-instance-id"
export MAPBOX_ACCESS_TOKEN="your-token"
```

**Windows** - Add to System Environment Variables:
1. Search "Environment Variables"
2. Click "New" under User Variables
3. Add each variable

---

## ❓ Troubleshooting

### "Failed to fetch images"

**Check:**
1. ✅ API key is set correctly
2. ✅ Date format is YYYY-MM-DD
3. ✅ Coordinates are valid (-90 to 90 lat, -180 to 180 lon)
4. ✅ Internet connection is active

**For Sentinel Hub:**
- Verify Instance ID is correct
- Check your free tier quota
- Try using NASA instead (no key required)

**For NASA GIBS:**
- Check date is between 2000 and present
- Try different zoom level (8-12 works best)

### "API key not configured"

- Make sure `.env` file exists
- Restart the application after setting variables
- Check environment variable spelling

### "Rate limit exceeded"

- **Sentinel Hub**: Wait for monthly reset or use NASA
- **Mapbox**: Monitor usage at account dashboard
- **NASA**: No limits!

---

## 💰 Cost Tracking

### Sentinel Hub
- Dashboard: https://apps.sentinel-hub.com/dashboard/
- View usage under "Statistics"
- Free tier: 5,000 requests/month

### Mapbox
- Dashboard: https://account.mapbox.com/
- View usage under "Statistics"
- Free tier: 50,000 requests/month

### NASA GIBS
- ✅ **Completely free, unlimited!**

---

## 🎯 Best Practices

1. **Start with NASA GIBS** for testing
2. **Use Sentinel Hub** for production/research
3. **Save fetched images** to avoid re-downloading
4. **Monitor API usage** if using paid tiers
5. **Choose appropriate date ranges**:
   - Urban development: 1-5 years
   - Deforestation: 6 months - 2 years
   - Natural disasters: Days to weeks

---

## 📚 Additional Resources

### Satellite Imagery Basics
- [NASA Earthdata](https://earthdata.nasa.gov/)
- [Copernicus Open Access Hub](https://scihub.copernicus.eu/)
- [Remote Sensing Tutorial](https://www.nrcan.gc.ca/maps-tools-and-publications/satellite-imagery-and-air-photos/tutorial-fundamentals-remote-sensing/9309)

### Change Detection Techniques
- [Earth Engine Change Detection](https://developers.google.com/earth-engine/tutorials/community/detecting-changes-in-sentinel-1-imagery)
- [Temporal Analysis Methods](https://www.un-spider.org/advisory-support/recommended-practices/recommended-practice-flood-mapping/step-by-step/time-series-analysis)

---

## 🆘 Support

Need help?
- 📖 [Main README](README.md)
- 🐛 [GitHub Issues](https://github.com/Ethan-da-Tech-Wizard/CodexEterna/issues)
- 💬 [Discussions](https://github.com/Ethan-da-Tech-Wizard/CodexEterna/discussions)

---

**Happy satellite imaging! 🛰️🌍**
