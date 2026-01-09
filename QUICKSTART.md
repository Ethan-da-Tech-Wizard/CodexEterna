# 🚀 CodexEterna - Complete VS Code Quickstart Guide

**Welcome to CodexEterna!** This is your ONE complete guide to get the hybrid C# + Python data pipeline running in VS Code on Windows.

> 📝 **What You'll Get:** A beautiful, customizable web dashboard showing real-time coordinate pings (20,000/second) and live sports data - all running from VS Code!

---

## ✨ What This App Does

**CodexEterna** is a real-time data pipeline that:
- 📍 Generates 20,000 GPS coordinate pings per second
- 🏆 Fetches live sports data from ESPN
- 💾 Stores everything in a PostgreSQL database
- 🎨 Displays it all in a gorgeous, customizable web UI
- 🛠 Built with C# (.NET 8) + Python (3.12) + Docker

**Perfect for learning:** Microservices, WebSockets, Real-time Data, Docker, VS Code workflows

---

## 📋 Prerequisites (One-Time Setup)

### 1. Install Docker Desktop
**Windows:**
1. Download from: https://www.docker.com/products/docker-desktop/
2. Run the installer
3. Restart your computer when prompted
4. Launch Docker Desktop and wait for it to start

**Verify it's working:**
```powershell
docker --version
```
You should see something like `Docker version 24.x.x`

### 2. Install VS Code
1. Download from: https://code.visualstudio.com/
2. Install it
3. Launch VS Code

### 3. Install Recommended Extensions
When you open the project, VS Code will suggest extensions. Click "Install All" or manually install:
- **Docker** - Docker integration
- **C#** - C# language support
- **Python** - Python language support

---

## 🎯 Running the App (The Easy Way)

### Step 1: Open Project in VS Code

1. Download this repository:
   - Click the green "Code" button on GitHub
   - Select "Download ZIP"
   - Extract to your Desktop or Documents folder

2. Open VS Code

3. Click **File → Open Folder**

4. Navigate to and select the **CodexEterna** folder
   - ⚠️ **CRITICAL:** Select the ROOT folder (where `docker-compose.yml` is)
   - NOT a subfolder like `PingService` or `SportsService`

### Step 2: Start Everything (One Click!)

Press **`Ctrl+Shift+B`** on your keyboard

**OR**

1. Press **`Ctrl+Shift+P`**
2. Type: `Tasks: Run Build Task`
3. Press Enter

**What happens:**
- Docker will build the C# service
- Docker will build the Python service
- Docker will start PostgreSQL database
- Everything launches automatically
- First time takes 3-5 minutes (downloads images)

### Step 3: Open the Dashboard

Once you see these messages in the terminal:
```
pingservice     | Now listening on: http://[::]:5000
sportsservice   | INFO: Application startup complete
```

**Open your browser to:**
```
http://localhost:5000
```

🎉 **You're done!** The app is running!

---

## 🎨 Using the Dashboard

### Overview

The dashboard shows two main panels:

**Left Panel - Coordinate Ping Stream**
- Watch 20,000 GPS coordinates being tracked per second
- See real-time statistics (Total Pings, Unique Coordinates, Pings/Second)
- Search and filter coordinates
- Pause/Resume the stream

**Right Panel - Sports Data Feed**
- Select a sport (NFL, NBA, MLB, NHL, MLS, WNBA)
- Click "Fetch Latest" to get live game data from ESPN
- View scores and game status

### Customize Your Vibe 🎨

Click the **⚙️ button** (top-right corner) to customize:

**Background Themes:**
- ☕ Cozy Café (warm brown tones)
- 🌙 Midnight Coder (dark blue)
- 🌲 Forest Retreat (green nature vibes)
- 🌅 Sunset Lounge (purple/pink)
- 🌊 Ocean Breeze (cool blues)
- 💜 Lavender Dreams (soft purple)
- 🌃 Retro Synthwave (neon 80s)
- 🧘 Minimal Zen (calm grays)

**Custom Gradient:**
- Pick your own colors
- Adjust gradient angle
- Real-time preview

**Effects:**
- 🌟 Floating Particles - animated background particles
- 🔲 Glass Blur Effect - frosted glass panels
- ✨ Smooth Animations - hover effects and transitions

**Panel Transparency:**
- Adjust from 70% to 100% opacity
- Make panels more or less see-through

**All settings auto-save!** Your theme persists across sessions.

---

## 🎮 VS Code Tasks & Commands

Access via `Ctrl+Shift+P` → Type "Tasks: Run Task":

| Task | What It Does |
|------|--------------|
| **Docker Compose: Build and Start** | Build and start all services (use this first time) |
| **Docker Compose: Start** | Start services without rebuilding (faster) |
| **Docker Compose: Stop** | Stop all services |
| **Docker Compose: Restart** | Restart all services |
| **Docker Compose: View Logs** | See live logs from all services |
| **Docker Compose: Clean Up** | Stop and remove volumes |

**Keyboard Shortcut:**
- `Ctrl+Shift+B` - Runs the default task (Build and Start)

---

## 🧪 Testing the App

### Test Coordinate Pings

In the dashboard:
1. Watch "Total Pings" counting up rapidly
2. Click **"Pause"** - numbers should stop
3. Click **"Resume"** - numbers start again
4. Click **"Top 100"** - see most frequent coordinates

### Test Sports Data

1. Click the sport dropdown
2. Select **"NFL Football"** (or any sport)
3. Click **"📡 Fetch Latest"**
4. Wait 2-3 seconds
5. Game cards appear with scores!

**No games showing?**
- Might be off-season or no games today
- Try different sports (NBA usually has more games)

---

## 🛑 Stopping the App

### Method 1: Via Terminal
In the VS Code terminal where it's running:
1. Press `Ctrl+C`
2. Wait for services to stop

### Method 2: Via Task
1. Press `Ctrl+Shift+P`
2. Type: `Tasks: Run Task`
3. Select: **Docker Compose: Stop**

---

## 🔧 Troubleshooting

### Problem: "no configuration file provided: not found"

**Cause:** You're in the wrong folder

**Solution:**
1. Close VS Code
2. Make sure you open the **CodexEterna** root folder
3. Check that you see `docker-compose.yml` in the file explorer
4. Run the task again

### Problem: "Docker daemon is not running"

**Solution:**
1. Open Docker Desktop
2. Wait for it to fully start (whale icon stops animating)
3. Try again

### Problem: "Port 5000 is already in use"

**Solution:**
1. Something else is using port 5000
2. Stop that service OR
3. Edit `docker-compose.yml`:
   - Find `"5000:5000"`
   - Change to `"5002:5000"`
   - Open browser to `http://localhost:5002` instead

### Problem: Dashboard shows "Connection Failed"

**Solutions:**
1. Wait 30 more seconds (services still starting)
2. Refresh browser (`F5`)
3. Check terminal for error messages
4. Restart everything:
   - Stop: `Ctrl+C` in terminal
   - Clean: Run "Docker Compose: Clean Up" task
   - Start: `Ctrl+Shift+B`

### Problem: "No games found" for all sports

**This is normal!**
- ESPN API might be down temporarily
- Try again in 10 minutes
- Or the sport is in off-season

---

## 📁 Project Structure

```
CodexEterna/
├── .vscode/                     # VS Code configuration
│   ├── tasks.json              # Docker tasks
│   ├── launch.json             # Debug configs
│   ├── settings.json           # Workspace settings
│   └── extensions.json         # Recommended extensions
├── PingService/                # C# Coordinate Service (.NET 8)
│   ├── wwwroot/
│   │   ├── index.html          # Dashboard UI
│   │   ├── css/dashboard.css   # Cozy hipster styles
│   │   └── js/dashboard.js     # Customization + real-time logic
│   ├── Dockerfile
│   └── PingService.csproj
├── SportsService/              # Python Sports Service (Python 3.12)
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml          # Orchestrates all services
├── QUICKSTART.md              # This guide!
└── README.md                   # Full technical documentation
```

---

## 🎓 What You're Learning

By running this project, you're learning:

**Technologies:**
- ✅ Docker & Docker Compose
- ✅ Microservices Architecture
- ✅ C# & .NET 8 (ASP.NET Core)
- ✅ Python 3.12 & FastAPI
- ✅ PostgreSQL Database
- ✅ WebSockets & SignalR
- ✅ REST APIs
- ✅ Real-time Data Processing
- ✅ Modern JavaScript (ES6+)
- ✅ CSS Variables & Theming
- ✅ VS Code Workflows

**Made with 💜 using C#, Python, and lots of coffee ☕**
