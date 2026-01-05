# Complete Setup Guide - Real-Time Data Pipeline Demo

This guide will walk you through setting up and running the complete system for a demo.

## 📋 Prerequisites

Before starting, ensure you have:

### Required Software

1. **Docker Desktop** (v20.10 or higher)
   - Download: https://www.docker.com/products/docker-desktop/
   - **Windows**: Docker Desktop for Windows
   - **Mac**: Docker Desktop for Mac (Intel or Apple Silicon)
   - **Linux**: Docker Engine + Docker Compose

2. **Git** (for cloning the repository)
   - Download: https://git-scm.com/downloads
   - Or use GitHub Desktop: https://desktop.github.com/

3. **Modern Web Browser**
   - Chrome, Firefox, Edge, or Safari (latest version)

### System Requirements

- **RAM**: 8GB minimum (16GB recommended)
- **CPU**: 4 cores minimum (8 cores recommended)
- **Disk Space**: 5GB free space
- **Network**: Internet connection (for fetching sports data)

---

## 🚀 Step-by-Step Setup

### Step 1: Install Docker Desktop

#### Windows:
1. Download Docker Desktop from https://www.docker.com/products/docker-desktop/
2. Run the installer (Docker Desktop Installer.exe)
3. Follow the installation wizard
4. Restart your computer when prompted
5. Launch Docker Desktop from Start Menu
6. Wait for Docker to start (whale icon in system tray should be steady)

**Verify Docker is Running:**
```powershell
# Open PowerShell or Command Prompt
docker --version
docker-compose --version
```

You should see version numbers like:
```
Docker version 24.0.x
Docker Compose version v2.x.x
```

#### Mac:
1. Download Docker Desktop from https://www.docker.com/products/docker-desktop/
2. Open the .dmg file and drag Docker to Applications
3. Launch Docker from Applications folder
4. Grant necessary permissions when prompted
5. Wait for Docker to start (whale icon in menu bar should be steady)

**Verify Docker is Running:**
```bash
# Open Terminal
docker --version
docker-compose --version
```

#### Linux:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect

# Verify
docker --version
docker-compose --version
```

---

### Step 2: Clone the Repository

#### Option A: Using Git Command Line

```bash
# Navigate to where you want the project
cd ~/Projects  # or C:\Projects on Windows

# Clone the repository
git clone https://github.com/Ethan-da-Tech-Wizard/CodexEterna.git

# Navigate into the project
cd CodexEterna

# Switch to the feature branch
git checkout claude/hybrid-data-pipeline-design-0Ekw7
```

#### Option B: Using GitHub Desktop

1. Open GitHub Desktop
2. Click "File" → "Clone Repository"
3. Enter: `Ethan-da-Tech-Wizard/CodexEterna`
4. Choose where to save it
5. Click "Clone"
6. Once cloned, click "Current Branch" dropdown
7. Select `claude/hybrid-data-pipeline-design-0Ekw7`

---

### Step 3: Navigate to Project Directory

Open a terminal/command prompt in the project folder:

**Windows:**
```powershell
cd C:\Users\YourName\Projects\CodexEterna
# Or wherever you cloned it
```

**Mac/Linux:**
```bash
cd ~/Projects/CodexEterna
# Or wherever you cloned it
```

**Verify you're in the right place:**
```bash
ls
# or on Windows:
dir
```

You should see:
```
PingService/
SportsService/
docs/
docker-compose.yml
README.md
...
```

---

### Step 4: Start the System

This is the magic command that starts everything!

```bash
docker-compose up --build
```

**What this does:**
- Builds Docker images for C# and Python services
- Starts PostgreSQL database
- Starts the Ping Service (C#)
- Starts the Sports Service (Python)
- Sets up networking between services

**What you'll see:**
```
[+] Building...
[+] Running...
pingservice     | info: Microsoft.Hosting.Lifetime[0]
pingservice     | Now listening on: http://[::]:5000
sportsservice   | INFO: Uvicorn running on http://0.0.0.0:5001
sportsdb        | database system is ready to accept connections
```

⏰ **First-time build takes 5-10 minutes** (downloads images and builds services)
⏰ **Subsequent starts take ~30 seconds**

**Keep this terminal window open!** This is where you'll see logs.

---

### Step 5: Wait for Services to Start

Watch the logs until you see:

```
pingservice     | Starting Coordinate Ping Service...
pingservice     | Dashboard: http://localhost:5000
sportsservice   | Database initialized successfully
sportsservice   | INFO: Application startup complete
```

✅ When you see these messages, the system is ready!

---

### Step 6: Open the Dashboard

Open your web browser and go to:

```
http://localhost:5000
```

🎉 **You should see the Real-Time Data Pipeline Dashboard!**

---

## 🎬 Demo Walkthrough

Now that everything is running, here's how to demonstrate the system:

### Part 1: Coordinate Ping Stream (Left Panel)

#### 1.1 Observe Live Data Generation

**What to show:**
- Point out the **"Total Pings"** counter rapidly increasing
- Show **"Pings/Second"** hovering around 20,000
- Watch the **"Unique Coordinates"** growing
- Note the **live-updating table** below

**Say to audience:**
> "This system is generating 20,000 random GPS coordinates per second—
> that's 1.2 million per minute—and tracking how many times each unique
> coordinate appears. Watch the counters updating in real-time."

#### 1.2 Demonstrate Pause/Resume

**Actions:**
1. Click the **"Pause"** button
2. Point out that all counters stop updating
3. Status changes to "Paused"
4. Click **"Resume"** button
5. Counters start updating again

**Say to audience:**
> "I can pause the data stream to examine the results, then resume
> instantly. This is useful for debugging or taking snapshots."

#### 1.3 Show Search/Filter

**Actions:**
1. In the search box, type: `33.4`
2. Click **"Search"**
3. Table filters to show only matching coordinates
4. Click **"Top 100"** to see most frequent coordinates

**Say to audience:**
> "We can search for specific coordinates or view the top 100 most
> frequently occurring coordinates to identify hotspots."

---

### Part 2: Sports Data (Right Panel)

#### 2.1 Fetch Live Sports Data

**Actions:**
1. Select **"NFL Football"** from the dropdown
2. Click **"Fetch Latest"**
3. Wait 2-3 seconds
4. Game cards appear with live scores

**Say to audience:**
> "This demonstrates integration with ESPN's API. We're fetching live
> NFL game data, parsing it, and storing it in PostgreSQL. The data
> persists even if we restart the system."

#### 2.2 Try Different Sports

**Actions:**
1. Select **"NBA Basketball"**
2. Click **"Fetch Latest"**
3. Show the NBA games appear
4. Try **"MLB Baseball"** or **"NHL Hockey"**

**Say to audience:**
> "The system supports multiple sports leagues: NFL, NBA, MLB, NHL,
> MLS, and WNBA. Each has its own data structure but we normalize
> it into our database schema."

#### 2.3 Demonstrate Persistence

**Actions:**
1. Click **"Load Stored"** without fetching first
2. Previously fetched games appear from database

**Say to audience:**
> "Notice I didn't fetch new data—this is coming from our PostgreSQL
> database. The data persists across sessions, demonstrating proper
> data storage and retrieval."

---

### Part 3: API Demonstration

Open a new terminal/PowerShell window (keep the first one running!):

#### 3.1 Test Ping Service API

```bash
# Get current statistics
curl http://localhost:5000/api/ping/stats

# Get top 10 coordinates
curl "http://localhost:5000/api/ping/top?count=10"

# Filter by hemisphere
curl "http://localhost:5000/api/ping/filter?hemisphere=north&limit=20"

# Get aggregate stats
curl http://localhost:5000/api/ping/aggregate?groupBy=hemisphere
```

**Say to audience:**
> "The system exposes RESTful APIs for programmatic access. Here I'm
> querying statistics, filtering by hemisphere, and getting aggregate
> data—all via simple HTTP requests."

#### 3.2 Test Sports Service API

```bash
# Get high-scoring NBA games
curl "http://localhost:5001/api/sports/high-scoring?threshold=150&league=basketball/nba"

# Get close NFL games
curl "http://localhost:5001/api/sports/close-games?max_diff=3&league=football/nfl"

# Get aggregate statistics
curl "http://localhost:5001/api/sports/aggregate?group_by=league"
```

**Say to audience:**
> "The sports service has comprehensive filtering: high-scoring games,
> close games, filtering by date, team, venue, and more. We can combine
> filters to find exactly what we're looking for."

---

### Part 4: Advanced Filtering Demo

#### 4.1 Coordinate Filtering

```bash
# Find all coordinates in North America
curl "http://localhost:5000/api/ping/region/north_america"

# Find high-frequency coordinates (seen 10+ times)
curl "http://localhost:5000/api/ping/filter?minCount=10&sortBy=count&limit=20"

# Find coordinates from last 5 minutes
curl "http://localhost:5000/api/ping/filter?lastSeenMinutes=5&limit=50"
```

**Say to audience:**
> "We have 11+ different filters for coordinate data: geographic regions,
> hemispheres, frequency ranges, time-based, and multiple sort options."

#### 4.2 Sports Data Filtering

```bash
# Find high-scoring games
curl "http://localhost:5001/api/sports/high-scoring?threshold=200"

# Find games by specific team
curl "http://localhost:5001/api/sports/filter?home_team=Lakers&sort_by=total_score"

# Get games by status
curl "http://localhost:5001/api/sports/by-status?status=Final&league=football/nfl"
```

**Say to audience:**
> "The sports service has 15+ filters: by league, team, status, score
> range, date range, venue, and more. All filters are composable."

---

### Part 5: Architecture Highlight

Open API documentation in browser:

```
http://localhost:5000/swagger    # C# Service API docs
http://localhost:5001/docs        # Python Service API docs
```

**Say to audience:**
> "The system uses Swagger/OpenAPI for auto-generated documentation.
> Developers can test all endpoints directly from this interface."

**Key Points to Mention:**
- **Microservices Architecture**: C# for high-performance, Python for flexibility
- **Real-Time Communication**: WebSocket (SignalR) for <100ms latency
- **Containerization**: Everything runs in Docker—identical in dev and prod
- **12-Factor App**: Cloud-native design, environment-based config
- **Scalability**: Stateless services, ready for horizontal scaling

---

## 🛠️ Troubleshooting

### Issue: Docker not starting

**Solution:**
```bash
# Check if Docker daemon is running
docker ps

# If error, restart Docker Desktop
# Windows: Restart Docker Desktop from system tray
# Mac: Restart Docker Desktop from menu bar
# Linux: sudo systemctl restart docker
```

---

### Issue: Port already in use

**Error:**
```
Error: bind: address already in use 0.0.0.0:5000
```

**Solution:**

**Windows:**
```powershell
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

**Mac/Linux:**
```bash
# Find what's using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>
```

**Or change the port in docker-compose.yml:**
```yaml
ports:
  - "5001:5000"  # Maps host 5001 to container 5000
```

---

### Issue: Services not connecting

**Symptoms:**
- Dashboard shows "Connection Failed"
- Sports data won't fetch

**Solution:**
```bash
# Check all containers are running
docker-compose ps

# Should show 3 containers: pingservice, sportsservice, sportsdb
# All should have status "Up"

# If any are not running, check logs
docker-compose logs pingservice
docker-compose logs sportsservice
docker-compose logs sportsdb

# Restart everything
docker-compose down
docker-compose up --build
```

---

### Issue: Database connection errors

**Error:**
```
Connection to database failed
```

**Solution:**
```bash
# Wait longer - database takes ~10 seconds to initialize
# Watch logs for:
sportsdb | database system is ready to accept connections

# If still failing, restart database
docker-compose restart sportsdb

# Or rebuild everything
docker-compose down -v  # -v removes volumes
docker-compose up --build
```

---

### Issue: ESPN API not returning data

**Symptoms:**
- "Failed to fetch sports data"
- No games appear

**Possible Causes:**
1. **No games scheduled**: Try a different sport/league
2. **API rate limiting**: Wait a few minutes and try again
3. **Network issues**: Check internet connection

**Solution:**
```bash
# Test ESPN API directly
curl "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"

# If that works but service doesn't, check logs
docker-compose logs sportsservice
```

---

### Issue: Out of memory

**Symptoms:**
- System slows down
- Containers crash
- "Cannot allocate memory" errors

**Solution:**

**In Docker Desktop:**
1. Open Docker Desktop Settings
2. Go to "Resources" → "Advanced"
3. Increase "Memory" to at least 4GB (8GB recommended)
4. Click "Apply & Restart"

**Or reduce ping generation rate:**
Edit `PingService/Services/PingGeneratorService.cs`:
```csharp
private const int TARGET_PINGS_PER_SECOND = 10000;  // Reduced from 20000
```
Then rebuild:
```bash
docker-compose down
docker-compose up --build
```

---

### Issue: Slow performance

**Solutions:**

1. **Reduce ping rate** (see above)

2. **Limit table size in dashboard:**
   Edit `PingService/wwwroot/js/dashboard.js`:
   ```javascript
   const MAX_TABLE_ROWS = 500;  // Reduced from 1000
   ```

3. **Close other applications** to free up resources

4. **Check Docker stats:**
   ```bash
   docker stats
   ```
   Look for containers using >80% CPU or memory

---

## 🔄 Restarting the System

### Graceful Restart

```bash
# Stop services (Ctrl+C in the terminal with logs)
# Then:
docker-compose down

# Start again
docker-compose up
```

### Full Rebuild

```bash
# Stop and remove everything (including database data)
docker-compose down -v

# Rebuild and start
docker-compose up --build
```

### Quick Restart (Just one service)

```bash
# In a new terminal:
docker-compose restart pingservice
# or
docker-compose restart sportsservice
```

---

## 📝 Quick Command Reference

```bash
# Start system (first time or after code changes)
docker-compose up --build

# Start system (normal)
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f pingservice

# Stop system (Ctrl+C if running in foreground, or:)
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Restart a specific service
docker-compose restart pingservice

# Check status
docker-compose ps

# Check resource usage
docker stats

# Access database
docker exec -it sportsdb psql -U postgres sportsdata
```

---

## 🎯 Demo Script Summary

**1. Show Dashboard** (2 min)
   - Open http://localhost:5000
   - Point out live updating statistics
   - Show pause/resume functionality

**2. Demonstrate Sports Data** (2 min)
   - Fetch NFL data
   - Show data persists via "Load Stored"
   - Try different sports

**3. Show API** (3 min)
   - Open Swagger docs
   - Test a few endpoints via curl
   - Show advanced filtering

**4. Explain Architecture** (3 min)
   - Microservices (C# + Python)
   - Real-time WebSocket
   - Docker containerization
   - 12-Factor App principles

**Total Demo Time: ~10 minutes**

---

## 🎓 What You've Built

After running this demo, you can highlight:

✅ **Microservices Architecture** - Language-agnostic design
✅ **Real-Time Data Processing** - 20,000 events/second
✅ **WebSocket Communication** - Live dashboard updates
✅ **RESTful APIs** - Comprehensive filtering & querying
✅ **Containerization** - Docker & Docker Compose
✅ **Database Integration** - PostgreSQL with ORM
✅ **12-Factor App** - Cloud-native design principles
✅ **Scalable Design** - Ready for horizontal scaling
✅ **Production-Ready** - Health checks, logging, monitoring

---

## 📞 Need Help?

If you run into issues:

1. Check the logs: `docker-compose logs -f`
2. Verify Docker is running: `docker ps`
3. Check README.md for additional documentation
4. Review docs/SYSTEM_DESIGN.md for architecture details

---

## 🎉 You're Ready!

Everything should now be running. Open your browser to:

```
http://localhost:5000
```

Enjoy your demo! 🚀
