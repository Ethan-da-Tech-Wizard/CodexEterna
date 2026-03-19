# How to Run CodexEterna

Two ways to run the app. Pick one.

---

## Option A — Build a Real Desktop App (Recommended)

This creates a proper `.exe` (Windows) or `.dmg` (Mac) installer.
Install it once, then launch it like any other app — no terminal ever again.

### What you need to install first (one time)

| Tool | Download | Notes |
|------|----------|-------|
| Node.js 18+ | https://nodejs.org | Click the "LTS" button |
| .NET 7 SDK | https://dotnet.microsoft.com/download | Pick ".NET 7.0" |
| Python 3.11+ | https://python.org/downloads | Tick **"Add to PATH"** during install |

Restart your computer after installing all three.

### Build on Windows

1. Open the `CodexEterna` folder
2. Double-click **`build.bat`**
3. A Command Prompt window opens — watch it build (takes ~5 minutes)
4. When it finishes, a `dist\` folder opens automatically
5. Double-click **`CodexEterna Setup 1.0.0.exe`**
6. Install it like any normal program
7. Launch **CodexEterna** from your Start Menu or Desktop

### Build on Mac

1. Open Terminal
2. Drag the `CodexEterna` folder into Terminal and press Enter
3. Run:
   ```
   chmod +x build.sh && ./build.sh
   ```
4. When done, open the `dist/` folder
5. Double-click **`CodexEterna-1.0.0.dmg`**
6. Drag the app to Applications
7. Launch **CodexEterna** from Launchpad

---

## Option B — Run with Docker (Developer Mode)

No installer. Uses Docker to run the app in your browser.

### What you need

- Docker Desktop → https://www.docker.com/products/docker-desktop/

### Steps

1. Install Docker Desktop and make sure it is running (whale icon = running)
2. Open a terminal **inside the CodexEterna folder**
   - **Windows:** Hold Shift + Right-click inside the folder → "Open PowerShell here"
   - **Mac:** Open Terminal, type `cd `, drag the folder in, press Enter
3. Run this one command:
   ```
   docker-compose up --build
   ```
4. Wait until you see: `Now listening on: http://[::]:5000`
5. Open your browser to: **http://localhost:5000**

To stop: press `Ctrl+C`, then type `docker-compose down`

---

## What you'll see when it's running

- **Left side:** Coordinate pings counting up at 20,000/second
- **Right side:** Sports data from ESPN
- Click **Pause** to freeze the stream, **Resume** to continue
- Select a sport, click **Fetch Latest** to load live scores

---

That's it.
