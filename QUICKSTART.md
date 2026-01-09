# 🚀 CodexEterna v2.0 - Complete VS Code Quickstart Guide

**Welcome to CodexEterna!** Your complete guide to running a professional, multi-source real-time data pipeline in VS Code.

> 📝 **What You'll Get:** A professional web dashboard with 3 real-time data sources: coordinate pings (20k/sec), live crypto prices (Binance), and sports data (ESPN) - all running from VS Code with Docker!

---

## ✨ What This App Does

**CodexEterna v2.0** is a professional-grade real-time data collection platform featuring:

### 📍 **Coordinate Ping Stream**
- Generates 20,000 GPS coordinate pings per second
- Tracks all unique coordinates with occurrence counting
- Real-time stats, sorting, and filtering
- **Manual start required** - prevents accidental memory overflow

### 💰 **Crypto Monitoring** *(NEW!)*
- Live connection to Binance WebSocket (BTC/USDT)
- Real-time price updates every 2 seconds
- Automatic 10-minute timestamped snapshots
- Historical data viewing by date
- **Manual start required** - connects to Binance only when you confirm

### 🏆 **Sports Data Feed**
- On-demand sports data from ESPN API
- Supports NFL, NBA, MLB, NHL, MLS, WNBA
- Automatic timestamping and historical storage
- Date-based filtering for past data

### 🛠 **Tech Stack**
- C# (.NET 8) + Python (3.12) + Docker
- Professional UI with 6 customizable themes
- PostgreSQL database
- SignalR WebSockets for real-time updates

**Perfect for learning:** Microservices, Real-time Data, WebSockets, Docker, Data Collection Safety

---

## 📋 Prerequisites (One-Time Setup)

### 1. Install Docker Desktop
**Windows:**
1. Download from: https://www.docker.com/products/docker-desktop/
2. Run the installer
3. Restart your computer when prompted
4. Launch Docker Desktop and **wait for it to fully start**

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

1. **Clone or Download** this repository:
   ```bash
   git clone https://github.com/YOUR-USERNAME/CodexEterna.git
   ```
   OR
   - Click the green "Code" button on GitHub
   - Select "Download ZIP"
   - Extract to your desired folder

2. **Open VS Code**

3. Click **File → Open Folder**

4. Navigate to and select the **CodexEterna** folder
   - ⚠️ **CRITICAL:** Select the ROOT folder (where `docker-compose.yml` is)
   - NOT a subfolder like `PingService` or `SportsService`

### Step 2: Start Docker Services

Press **`Ctrl+Shift+B`** on your keyboard

**OR**

1. Press **`Ctrl+Shift+P`**
2. Type: `Tasks: Run Build Task`
3. Press Enter

**What happens:**
- Docker builds C# service (PingService) with .NET 8
- Docker builds Python service (SportsService) with Python 3.12
- PostgreSQL database starts
- All services launch automatically
- **First time takes 3-5 minutes** (downloads Docker images)

### Step 3: Open the Dashboard

Once you see these messages in the terminal:
```
pingservice     | CodexEterna Data Pipeline v2.0
pingservice     | NOTE: All data collection requires MANUAL START
sportsservice   | INFO: Application startup complete
```

**Open your browser to:**
```
http://localhost:5000
```

🎉 **Services are ready!** Now you need to manually start data collection.

---

## 🚀 Starting Data Collection (IMPORTANT!)

### ⚠️ **All systems start in STOPPED state for safety**

Each data source requires manual confirmation before starting:

### 1️⃣ Start Coordinate Ping Stream

**Click the "Coordinate Ping Stream" tab**

1. Click **▶ START Collection** button
2. Confirm the warning dialog:
   ```
   ⚠️ START PING COLLECTION?
   This will generate 20,000 coordinates per second
   and consume significant memory.
   Click OK to confirm.
   ```
3. Click **OK**
4. Watch the stats update in real-time!

**Controls:**
- **⏹ STOP Collection** - Immediately ceases all ping generation
- **⏸ Pause** - Temporarily pauses (only when running)
- **🔄 Reset Data** - Clears all coordinate counts
- **🗑 Clear Saved** - Removes localStorage data

### 2️⃣ Start Crypto Monitoring

**Click the "Crypto Monitoring" tab**

1. Click **▶ START Monitoring** button
2. Confirm the warning dialog:
   ```
   🔗 START CRYPTO MONITORING?
   This will connect to Binance WebSocket for real-time
   BTC/USDT price monitoring.
   Snapshots will be taken every 10 minutes.
   Click OK to confirm.
   ```
3. Click **OK**
4. Watch real-time BTC price updates!

**What happens:**
- Connects to Binance WebSocket
- Updates price every 2 seconds
- Takes snapshot every 10 minutes with timestamp
- Tracks: Current Price, High, Low, Total Trades

**Controls:**
- **⏹ STOP Monitoring** - Immediately disconnects from Binance
- **📊 View Snapshots** - Display all historical snapshots
- **Filter by Date** - View snapshots from specific dates

### 3️⃣ Fetch Sports Data

**Click the "Sports Data Feed" tab**

1. Select a sport from dropdown (NFL, NBA, MLB, etc.)
2. Click **Fetch Latest Data**
3. View live game scores and status!

**Features:**
- Each fetch is automatically timestamped
- Stored in browser localStorage for history
- Filter by date to view past fetches
- No confirmation needed (on-demand fetching)

---

## 🎨 Using the Dashboard

### Professional Themes

Click the **⚙️ Settings** button (top-right) to customize:

**Professional Themes:**
- **Executive Dark** (default) - Professional blues and grays
- **Corporate Blue** - Business-grade blue tones
- **Clean Light** - Bright, minimal design
- **Minimalist Slate** - Muted gray aesthetic
- **Professional Navy** - Deep blue corporate style
- **Modern Charcoal** - Contemporary dark theme

**Custom Options:**
- Pick your own gradient colors
- Adjust gradient angle (0-360°)
- Panel opacity slider (70-100%)
- Toggle blur effects
- Toggle animations

**All settings auto-save!** Your theme persists across sessions.

### Data Visualization

**Coordinate Ping Stream Tab:**
- Real-time statistics (Total Pings, Unique Coords, Pings/Sec)
- Sortable table (Most/Least Frequent, Newest/Oldest)
- Search and filter coordinates
- All unique lat/long coordinates displayed

**Crypto Monitoring Tab:**
- Live price display ($XX,XXX.XX)
- High/Low price tracking per interval
- Snapshot counter
- Historical snapshots with timestamps
- Date-based filtering

**Sports Data Feed Tab:**
- Game cards with team names and scores
- Game status (Live, Final, Scheduled)
- Fetch timestamp for each data pull
- Historical data organized by date
- Clear history option

---

## 🎮 VS Code Tasks & Commands

Access via `Ctrl+Shift+P` → Type "Tasks: Run Task":

| Task | What It Does | When to Use |
|------|--------------|-------------|
| **Docker Compose: Build and Start** | Build and start all services | First time or after code changes |
| **Docker Compose: Start** | Start services without rebuilding | Daily use (faster) |
| **Docker Compose: Stop** | Stop all services | When done working |
| **Docker Compose: Restart** | Restart all services | After config changes |
| **Docker Compose: View Logs** | See live logs from all services | Debugging |
| **Docker Compose: Clean Up** | Stop and remove volumes | Fresh start needed |

**Keyboard Shortcuts:**
- `Ctrl+Shift+B` - Runs the default build task
- `Ctrl+C` - Stop services in terminal

---

## 🧪 Testing the System

### Test Ping Generation

1. Navigate to **Coordinate Ping Stream** tab
2. Click **▶ START Collection** and confirm
3. Watch "Total Pings" rapidly increment
4. Verify "Pings/Second" shows ~20,000
5. Click **⏸ Pause** - numbers should freeze
6. Click **▶ Resume** (button changes) - numbers continue
7. Click **⏹ STOP Collection** and confirm - all generation stops

### Test Crypto Monitoring

1. Navigate to **Crypto Monitoring** tab
2. Click **▶ START Monitoring** and confirm
3. Watch "Current Price" update every 2 seconds
4. Wait 10 minutes - snapshot counter increases
5. Click **📊 View Snapshots** - see historical data
6. Click **⏹ STOP Monitoring** - connection closes

### Test Sports Data

1. Navigate to **Sports Data Feed** tab
2. Select **"NBA Basketball"** (usually has games)
3. Click **Fetch Latest Data**
4. Game cards appear with scores
5. Use date filter to view past fetches
6. Try different sports

**No games showing?**
- Might be off-season or no games today
- Try different sports
- Check console (F12) for errors

---

## 🛑 Stopping the App

### Stop Data Collection First

**Before closing:**
1. Click **⏹ STOP Collection** on Ping tab (if running)
2. Click **⏹ STOP Monitoring** on Crypto tab (if running)
3. This ensures clean shutdown and data saving

### Stop Docker Services

**Method 1: Via Terminal**
1. Go to VS Code terminal where services are running
2. Press `Ctrl+C`
3. Wait for services to stop gracefully

**Method 2: Via Task**
1. Press `Ctrl+Shift+P`
2. Type: `Tasks: Run Task`
3. Select: **Docker Compose: Stop**

---

## 🔧 Troubleshooting

### "no configuration file provided: not found"

**Cause:** You're in the wrong folder

**Solution:**
1. Close VS Code
2. Make sure you open the **CodexEterna** root folder
3. Check that you see `docker-compose.yml` in the file explorer sidebar
4. NOT in `PingService/` or `SportsService/` subfolder
5. Run the build task again

### "Docker daemon is not running"

**Solution:**
1. Open Docker Desktop application
2. Wait for it to fully start (whale icon stops animating in system tray)
3. You should see "Docker Desktop is running" in Docker Desktop
4. Try the build task again

### "Port 5000 is already in use"

**Solution:**
1. Another application is using port 5000
2. **Option A:** Stop that application
3. **Option B:** Change port in `docker-compose.yml`:
   ```yaml
   ports:
     - "5002:5000"  # Change first number only
   ```
4. Open browser to `http://localhost:5002` instead

### Services start but dashboard won't load

**Solutions:**
1. **Wait longer** - services take 10-20 seconds to fully initialize
2. **Check logs** - look for errors in VS Code terminal
3. **Refresh browser** - Press `F5`
4. **Verify services** - You should see both these messages:
   ```
   pingservice     | Dashboard: http://localhost:5000
   sportsservice   | INFO: Application startup complete
   ```
5. **Clean restart:**
   - Stop: `Ctrl+C`
   - Clean: Run "Docker Compose: Clean Up" task
   - Start: `Ctrl+Shift+B`

### "Failed to start ping system" error

**Cause:** Backend service not ready or already running

**Solutions:**
1. Check if ping system is already running (look at status indicator)
2. Try stopping first, then starting again
3. Refresh the page (`F5`)
4. Check console (F12) for detailed error messages

### "Failed to start crypto monitoring"

**Possible causes:**
1. No internet connection (Binance requires internet)
2. Binance WebSocket temporarily down
3. Service still initializing

**Solutions:**
1. Check your internet connection
2. Wait 30 seconds and try again
3. Check browser console (F12) for specific errors
4. Restart the Docker services

### Crypto monitoring shows $0.00

**Cause:** WebSocket not yet connected or data not received

**Solutions:**
1. Wait 5-10 seconds after starting
2. Check that status shows "Connected" (green dot)
3. Refresh the page
4. Stop and start crypto monitoring again

### Sports data shows "No games found" for all leagues

**This is often normal!**
- ESPN API might be experiencing issues
- Sport might be in off-season
- No games scheduled for today

**Try:**
1. Different sport (NBA usually has more games)
2. Wait 10 minutes and try again
3. Check if ESPN.com itself is working
4. Check browser console for API errors

---

## 📊 Data Storage & Memory

### Where Data is Stored

**Ping Coordinates:**
- In-memory in C# service
- Auto-saved to browser localStorage every 10 seconds
- ⚠️ Can consume significant RAM at 20k/sec

**Crypto Snapshots:**
- In-memory in C# service
- Automatically saved every 10 minutes with timestamp
- Stored in memory until service restarts

**Sports Data:**
- Browser localStorage
- Each fetch timestamped by date
- Filterable by date range

### Memory Management

**Ping System:**
- **20,000 pings/second** = ~1.2 million pings/minute
- Can consume 500MB - 1GB RAM over time
- **Use STOP button** to prevent memory overflow
- Reset data periodically with "Reset Data" button

**Crypto System:**
- Minimal memory usage
- Only stores 10-minute snapshots
- Safe to run continuously

**Best Practices:**
1. Only start systems when actively monitoring
2. Use STOP buttons when done
3. Don't leave ping system running overnight
4. Monitor system memory usage

---

## 📁 Project Structure

```
CodexEterna/
├── .vscode/                     # VS Code configuration
│   ├── tasks.json              # Docker Compose tasks
│   ├── launch.json             # Debug configurations
│   ├── settings.json           # Workspace settings
│   └── extensions.json         # Recommended extensions
│
├── PingService/                # C# Data Pipeline Service (.NET 8)
│   ├── Controllers/
│   │   ├── PingController.cs   # Ping generation API
│   │   └── CryptoController.cs # Crypto monitoring API
│   ├── Services/
│   │   ├── PingGeneratorService.cs  # 20k/sec generator
│   │   └── CryptoService.cs         # Binance WebSocket
│   ├── Models/
│   │   ├── CoordinatePing.cs   # Ping data model
│   │   └── CryptoModels.cs     # Crypto snapshot models
│   ├── wwwroot/
│   │   ├── index.html          # Professional dashboard UI
│   │   ├── css/dashboard.css   # Professional themes
│   │   └── js/dashboard.js     # Client-side logic
│   ├── Dockerfile              # .NET 8 container
│   ├── Program.cs              # Service registration
│   └── PingService.csproj      # .NET 8 project
│
├── SportsService/              # Python Sports Service (Python 3.12)
│   ├── app/
│   │   ├── main.py             # FastAPI application
│   │   └── database.py         # PostgreSQL connection
│   ├── Dockerfile              # Python 3.12 container
│   ├── requirements.txt        # Python dependencies
│   └── init_db.py              # Database initialization
│
├── docker-compose.yml          # Orchestrates all 3 services
├── QUICKSTART.md              # This guide!
├── README.md                   # Technical documentation
└── VSCODE_GUIDE.md            # Advanced VS Code workflows
```

---

## 🎓 What You're Learning

By running this project, you're learning:

### Technologies
- ✅ Docker & Docker Compose orchestration
- ✅ Microservices Architecture (3 services)
- ✅ C# & .NET 8 (ASP.NET Core, SignalR)
- ✅ Python 3.12 & FastAPI
- ✅ PostgreSQL Database
- ✅ WebSocket connections (Binance, SignalR)
- ✅ REST API design
- ✅ Real-time Data Processing (20k/sec)
- ✅ Browser localStorage & data persistence
- ✅ Modern JavaScript (ES6+, async/await)
- ✅ CSS Variables & Professional Theming
- ✅ VS Code Task automation

### Concepts
- ✅ Data collection safety (manual confirmations)
- ✅ Memory management at scale
- ✅ Timestamped data storage
- ✅ Historical data filtering
- ✅ Multi-source data aggregation
- ✅ WebSocket vs HTTP trade-offs
- ✅ Client-server real-time communication

---

## 🔗 Additional Resources

**Documentation:**
- [VSCODE_GUIDE.md](./VSCODE_GUIDE.md) - Advanced VS Code workflows
- [DOCKER_SETUP.md](./DOCKER_SETUP.md) - Docker Desktop deep dive
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Comprehensive troubleshooting
- [README.md](./README.md) - Full technical documentation

**API Documentation:**
- Once running, visit: `http://localhost:5000/swagger`
- Interactive API testing and documentation

**Services:**
- Ping Service: `http://localhost:5000`
- Sports Service: `http://localhost:5001`
- PostgreSQL: `localhost:5432`

---

## 📝 Quick Reference

### Starting Everything
1. Open CodexEterna folder in VS Code
2. Press `Ctrl+Shift+B`
3. Wait for services to start
4. Open `http://localhost:5000`
5. Click START buttons with confirmation

### Stopping Everything
1. Click STOP on active tabs
2. Press `Ctrl+C` in terminal
3. Or run "Docker Compose: Stop" task

### Keyboard Shortcuts
- `Ctrl+Shift+B` - Build and start
- `Ctrl+Shift+P` - Command palette
- `Ctrl+C` - Stop services
- `F5` - Refresh browser
- `F12` - Open browser console

---

**Made with 💜 by the CodexEterna team**

**Stack:** C# (.NET 8) + Python (3.12) + Docker + PostgreSQL + SignalR + Binance API + ESPN API

**Version:** 2.0.0 - Professional Data Pipeline Edition
