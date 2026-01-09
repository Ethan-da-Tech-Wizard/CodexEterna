# 🔧 Troubleshooting Guide - "I Pressed Ctrl+Shift+B But No UI"

## Step-by-Step Diagnosis

### Step 1: Is Docker Desktop Running?

**Check the system tray (bottom-right of Windows):**
- Look for the Docker whale icon 🐳
- If it's there and NOT animated = Docker is running ✅
- If it's animated/spinning = Docker is starting (wait 1-2 minutes)
- If it's NOT there = Docker Desktop isn't open

**Fix:** Open Docker Desktop from Start Menu and wait for it to fully start

### Step 2: Check What VS Code Actually Did

**Look at the VS Code terminal output:**

1. In VS Code, look at the bottom panel (Terminal)
2. You should see something like this:

**✅ GOOD (Working):**
```
[+] Building 45.2s (12/12) FINISHED
[+] Running 3/3
 ✔ Container sportsdb         Started
 ✔ Container sportsservice    Started  
 ✔ Container pingservice      Started
Attaching to pingservice, sportsdb, sportsservice
pingservice     | info: Microsoft.Hosting.Lifetime[14]
pingservice     |       Now listening on: http://[::]:5000
sportsservice   | INFO: Application startup complete.
```

**❌ BAD (Not Working):**
```
Cannot connect to the Docker daemon
ERROR: error during connect
```

OR

```
no configuration file provided: not found
```

### Step 3: What Does Each Error Mean?

#### Error: "Cannot connect to the Docker daemon"

**Cause:** Docker Desktop isn't running

**Fix:**
1. Open Docker Desktop from Start Menu
2. Wait for the whale icon to stop animating (30-60 seconds)
3. In VS Code terminal, press `Ctrl+C` to stop
4. Press `Ctrl+Shift+B` again

#### Error: "no configuration file provided: not found"

**Cause:** VS Code is in the wrong folder

**Fix:**
1. Close VS Code
2. In File Explorer, navigate to the CodexEterna folder
3. You should see these files:
   - docker-compose.yml ← MUST be visible
   - PingService (folder)
   - SportsService (folder)
4. Right-click in empty space → "Open with Code"
5. Press `Ctrl+Shift+B` again

#### Error: "Port 5000 is already in use"

**Cause:** Something else is using port 5000

**Check what's using it:**
Open PowerShell and run:
```powershell
netstat -ano | findstr :5000
```

**Fix Option 1 - Kill the process:**
```powershell
# If you see a PID (last number), like 12345:
taskkill /PID 12345 /F
```

**Fix Option 2 - Change the port:**
1. Edit `docker-compose.yml`
2. Find this line under `pingservice`:
   ```yaml
   ports:
     - "5000:5000"
   ```
3. Change to:
   ```yaml
   ports:
     - "5002:5000"
   ```
4. Save and run `Ctrl+Shift+B` again
5. Open browser to `http://localhost:5002` (not 5000!)

### Step 4: How Long Should I Wait?

**First time running:**
- Build time: 3-5 minutes (downloads images)
- You'll see lots of text scrolling
- Wait for "Now listening on:" messages

**Subsequent runs:**
- Build time: 10-30 seconds
- Much faster!

### Step 5: Check if Containers Actually Started

**In VS Code terminal, run this:**
```powershell
docker ps
```

**✅ You should see 3 containers:**
```
CONTAINER ID   IMAGE                          STATUS         PORTS
abc123...      codexeterna-pingservice        Up 1 minute    0.0.0.0:5000->5000/tcp
def456...      codexeterna-sportsservice      Up 1 minute    0.0.0.0:5001->5001/tcp
ghi789...      postgres:15-alpine             Up 1 minute    0.0.0.0:5432->5432/tcp
```

**❌ If you see nothing:** Containers didn't start. Check errors above.

### Step 6: Try Opening the UI

**Once you see "Now listening on: http://[::]:5000"**

1. Open your browser (Chrome, Edge, Firefox)
2. Go to: `http://localhost:5000`
3. You should see the CodexEterna dashboard!

**If browser shows "Can't connect":**
- Wait 30 more seconds (services still starting)
- Refresh the page (`F5`)
- Check Step 5 to confirm containers are running

---

## 🐛 About That MSSQL Popup

The MSSQL extension message you saw is **unrelated to CodexEterna**.

**What happened:**
- VS Code detected you installed the MSSQL extension
- It's just telling you it's available
- You can safely ignore/close it

**To disable MSSQL notifications:**
1. Click the gear icon ⚙️ in bottom-left of VS Code
2. Extensions
3. Find "SQL Server (mssql)"
4. Click "Disable" or "Uninstall"

---

## 📋 Complete Checklist

Run through this in order:

- [ ] Docker Desktop is installed
- [ ] Docker Desktop is RUNNING (whale icon in system tray, not animated)
- [ ] VS Code is open in the CodexEterna ROOT folder
- [ ] Can see `docker-compose.yml` in VS Code file explorer
- [ ] Pressed `Ctrl+Shift+B`
- [ ] Wait 3-5 minutes on first run
- [ ] See "Now listening on:" in terminal
- [ ] Run `docker ps` and see 3 containers
- [ ] Open `http://localhost:5000` in browser
- [ ] Dashboard loads!

---

## 🚨 Still Not Working?

### Run This Diagnostic

**Copy and paste these commands in VS Code terminal:**

```powershell
# Check Docker
docker --version
docker info

# Check if in right folder
dir docker-compose.yml

# Try starting manually
docker-compose up --build
```

**Share the output with me!**

### Common Issues Summary

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Cannot connect to Docker daemon" | Docker Desktop not running | Start Docker Desktop, wait, retry |
| "no configuration file provided" | Wrong folder in VS Code | Open root folder with docker-compose.yml |
| "Port already in use" | Port 5000 taken | Change to 5002 in docker-compose.yml |
| Build runs but no UI | Services still starting | Wait for "Now listening", then open localhost:5000 |
| Browser shows "Can't connect" | Containers not running | Run `docker ps` to check status |
| MSSQL popup | VS Code extension | Ignore it - unrelated to this project |

---

## 🎯 The Correct Flow

Here's what SHOULD happen:

1. ✅ Press `Ctrl+Shift+B`
2. ✅ Terminal shows: "Docker Compose: Build and Start"
3. ✅ See lots of "Downloading..." and "Building..." messages
4. ✅ Wait 3-5 minutes (first time)
5. ✅ See "Now listening on: http://[::]:5000"
6. ✅ See "Application startup complete"
7. ✅ Open browser to `http://localhost:5000`
8. ✅ CodexEterna dashboard appears!
9. ✅ See coordinate pings counting up
10. ✅ Click ⚙️ to customize theme

**If ANY step fails, check this guide!**

---

## 💡 Pro Tips

**Speed up subsequent runs:**
```powershell
# After first successful build, use this for faster starts:
docker-compose up
# (No --build flag = uses cached images)
```

**View logs if something's wrong:**
```powershell
docker-compose logs
```

**Completely reset if things are broken:**
```powershell
docker-compose down -v    # Stop and remove everything
docker-compose up --build # Fresh start
```

---

**Need more help?** Check [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed Docker integration info!
