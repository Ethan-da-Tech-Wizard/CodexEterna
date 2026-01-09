# 🐳 Docker Desktop Integration Guide

## How CodexEterna Links to Docker

### Architecture Overview

```
Your Machine
│
├── VS Code
│   └── Tasks (Ctrl+Shift+B)
│       └── Runs: docker-compose up --build
│
├── Docker Desktop
│   ├── Docker Engine (runs containers)
│   ├── Docker Compose (orchestrates services)
│   └── Docker Networks (connects services)
│
└── CodexEterna Containers
    ├── sportsdb (PostgreSQL on port 5432)
    ├── sportsservice (Python on port 5001)
    └── pingservice (C# on port 5000)
```

---

## ✅ Step-by-Step: Linking to Docker

### 1. Verify Docker Desktop is Installed

**Windows:**
```powershell
docker --version
docker-compose --version
```

**Expected Output:**
```
Docker version 24.0.7, build afdd53b
Docker Compose version v2.23.0
```

If you get errors, install Docker Desktop from https://www.docker.com/products/docker-desktop/

### 2. Check Docker Desktop is Running

**Windows - Check System Tray:**
- Look for the Docker whale icon 🐳 in the system tray (bottom-right)
- Click it - should say "Docker Desktop is running"
- Icon should NOT be animated

**Verify via Command:**
```powershell
docker info
```

If you see "Cannot connect to Docker daemon", Docker Desktop isn't running.

### 3. Configure Docker Desktop Settings

**Open Docker Desktop → Settings:**

**Resources (Recommended Settings):**
- **CPUs:** 4 (minimum 2)
- **Memory:** 4 GB (minimum 2 GB)
- **Swap:** 1 GB
- **Disk:** 60 GB available

**Docker Engine (Advanced):**
```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false
}
```

**WSL Integration (Windows Only):**
- If using WSL2, enable "WSL 2 based engine"
- Check "Enable integration with my default WSL distro"

---

## 🔗 How docker-compose.yml Links to Docker

Your `docker-compose.yml` file tells Docker Desktop what to do:

```yaml
version: '3.8'

services:
  # Service 1: PostgreSQL Database
  sportsdb:
    image: postgres:15-alpine          # ← Docker pulls this from Docker Hub
    container_name: sportsdb           # ← Name Docker Desktop shows
    environment:                       # ← Environment variables
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: sportsdata
    volumes:
      - sportsdb_data:/var/lib/postgresql/data  # ← Persistent storage
    ports:
      - "5432:5432"                    # ← Port mapping (host:container)
    networks:
      - data-pipeline-network          # ← Custom Docker network

  # Service 2: Python Sports Service
  sportsservice:
    build:
      context: ./SportsService          # ← Docker builds from this folder
      dockerfile: Dockerfile
    container_name: sportsservice
    environment:
      DATABASE_URL: postgresql://postgres:secret@sportsdb:5432/sportsdata
    ports:
      - "5001:5001"
    depends_on:                         # ← Wait for database to be healthy
      sportsdb:
        condition: service_healthy
    networks:
      - data-pipeline-network

  # Service 3: C# Ping Service
  pingservice:
    build:
      context: ./PingService
      dockerfile: Dockerfile
    container_name: pingservice
    ports:
      - "5000:5000"                     # ← Main UI accessible here
    networks:
      - data-pipeline-network
    depends_on:
      - sportsservice

networks:
  data-pipeline-network:                # ← Docker creates this network
    driver: bridge
    name: data-pipeline-network

volumes:
  sportsdb_data:                        # ← Docker manages this volume
    name: sportsdb_data
```

---

## 🖥️ View in Docker Desktop

### Dashboard View

After running `Ctrl+Shift+B`, open Docker Desktop:

**Containers Tab:**
```
codexeterna (3 containers)
├── pingservice     [Running] Port 5000:5000
├── sportsservice   [Running] Port 5001:5001
└── sportsdb        [Running] Port 5432:5432
```

**Click on each container to:**
- View logs in real-time
- Inspect environment variables
- See network connections
- Monitor CPU/Memory usage
- Open terminal inside container

**Images Tab:**
```
codexeterna-pingservice     latest    567 MB
codexeterna-sportsservice   latest    234 MB
postgres                    15-alpine  123 MB
```

**Volumes Tab:**
```
sportsdb_data               Local     45.2 MB
```

**Networks Tab:**
```
data-pipeline-network       bridge    3 containers
```

---

## 🔍 Verify Docker Connection

### From VS Code Terminal:

```powershell
# Check if Docker daemon is accessible
docker ps

# Should show 3 running containers:
# CONTAINER ID   IMAGE                          STATUS         PORTS
# abc123def456   codexeterna-pingservice        Up 2 minutes   0.0.0.0:5000->5000/tcp
# def456ghi789   codexeterna-sportsservice      Up 2 minutes   0.0.0.0:5001->5001/tcp
# ghi789jkl012   postgres:15-alpine             Up 2 minutes   0.0.0.0:5432->5432/tcp
```

### Test Docker Network:

```powershell
# Check network exists
docker network ls | findstr data-pipeline

# Inspect network (see all connected containers)
docker network inspect data-pipeline-network
```

### Test Volume:

```powershell
# Check volume exists
docker volume ls | findstr sportsdb

# Inspect volume
docker volume inspect sportsdb_data
```

---

## 🚀 How VS Code Talks to Docker

### The Command Chain:

1. **You press** `Ctrl+Shift+B` in VS Code

2. **VS Code reads** `.vscode/tasks.json`:
   ```json
   {
     "label": "Docker Compose: Build and Start",
     "command": "docker-compose up --build",
     "options": {
       "cwd": "${workspaceFolder}"
     }
   }
   ```

3. **VS Code runs** the command in integrated terminal:
   ```
   docker-compose up --build
   ```

4. **Docker Compose** reads `docker-compose.yml`

5. **Docker Engine** (via Docker Desktop):
   - Pulls/builds images
   - Creates network
   - Creates volume
   - Starts containers in order
   - Maps ports to host machine

6. **You access** the app at `http://localhost:5000`

---

## 🌐 Port Mapping Explained

```
Your Browser (localhost:5000)
        ↓
Windows Port 5000
        ↓
Docker Desktop (Port Forwarding)
        ↓
Container 'pingservice' Port 5000
        ↓
C# Application listening on :5000
```

**How it works:**
- `"5000:5000"` in docker-compose.yml means:
  - `5000` (left) = Your computer's port
  - `5000` (right) = Container's port
- Docker Desktop forwards traffic between them

**Change ports if needed:**
```yaml
ports:
  - "8080:5000"  # Access at localhost:8080 instead
```

---

## 📦 Docker Images & Building

### First Time (Slow):

```
docker-compose up --build
```

**What happens:**
1. ✅ Downloads base images:
   - `mcr.microsoft.com/dotnet/sdk:8.0` (~500 MB)
   - `mcr.microsoft.com/dotnet/aspnet:8.0` (~200 MB)
   - `python:3.12-slim` (~150 MB)
   - `postgres:15-alpine` (~100 MB)

2. ✅ Builds your images:
   - Compiles C# code
   - Installs Python packages
   - Creates optimized containers

3. ✅ Total download: ~1-2 GB (first time only!)

### Subsequent Runs (Fast):

```
docker-compose up
```

**What happens:**
1. ✅ Uses cached images (no download)
2. ✅ Starts containers in seconds
3. ✅ Much faster!

---

## 🔧 Troubleshooting Docker Connection

### Problem: "Cannot connect to Docker daemon"

**Check:**
```powershell
# Is Docker Desktop running?
docker version

# Expected output should show:
# Client: Docker Engine...
# Server: Docker Engine...
```

**Fix:**
1. Open Docker Desktop
2. Wait for it to fully start (30-60 seconds)
3. Try again

### Problem: "Port 5000 is already in use"

**Check what's using it:**
```powershell
netstat -ano | findstr :5000
```

**Fix:**
1. Kill the process using that port OR
2. Change port in `docker-compose.yml`:
   ```yaml
   ports:
     - "5002:5000"  # Use 5002 on your machine
   ```
3. Access at `http://localhost:5002`

### Problem: "No space left on device"

**Clean up Docker:**
```powershell
# Remove unused containers, networks, images
docker system prune -a

# Remove unused volumes (BE CAREFUL!)
docker volume prune
```

### Problem: Containers won't start

**Check logs in Docker Desktop:**
1. Open Docker Desktop
2. Click Containers tab
3. Click on failing container
4. View Logs tab
5. Look for errors in red

**Or via command:**
```powershell
docker-compose logs
```

---

## 🎯 Quick Docker Desktop Workflow

### Start the App:
1. Open Docker Desktop (ensure it's running)
2. Open VS Code
3. Press `Ctrl+Shift+B`
4. Wait for "Now listening" messages
5. Open `http://localhost:5000`

### Stop the App:
**Method 1 - VS Code:**
- Press `Ctrl+C` in terminal

**Method 2 - Docker Desktop:**
- Open Docker Desktop
- Click on `codexeterna` container group
- Click "Stop" button

**Method 3 - Command:**
```powershell
docker-compose down
```

### Restart the App:
```powershell
docker-compose restart
```

### View Logs:
**In Docker Desktop:**
- Containers → Click container → Logs tab

**Via Command:**
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f pingservice
```

---

## 📊 Monitor Resources in Docker Desktop

### Dashboard:
- Click on running container
- See real-time:
  - CPU usage %
  - Memory usage MB
  - Network I/O
  - Disk I/O

### Via Command:
```powershell
# Live stats
docker stats

# Shows:
# CONTAINER ID   NAME              CPU %   MEM USAGE / LIMIT   MEM %   NET I/O
# abc123...      pingservice       2.5%    124 MB / 4 GB       3.1%    1.2 MB / 800 KB
```

---

## 🔐 Docker Networks Explained

### Why We Use a Custom Network:

```yaml
networks:
  data-pipeline-network:
    driver: bridge
```

**Benefits:**
1. ✅ Containers can talk to each other by name:
   ```
   postgresql://postgres:secret@sportsdb:5432/sportsdata
                               ↑
                          Container name (not IP!)
   ```

2. ✅ Isolated from other Docker containers

3. ✅ Automatic DNS resolution

**View network:**
```powershell
docker network inspect data-pipeline-network
```

---

## 💾 Docker Volumes Explained

### Why We Use a Volume:

```yaml
volumes:
  sportsdb_data:
    name: sportsdb_data
```

**Benefits:**
1. ✅ Database persists when container stops
2. ✅ Data survives container deletion
3. ✅ Can backup/restore easily

**Backup volume:**
```powershell
docker run --rm -v sportsdb_data:/data -v ${PWD}:/backup ubuntu tar czf /backup/sportsdb-backup.tar.gz /data
```

**Where is it stored?**
- Windows: `\\wsl$\docker-desktop-data\data\docker\volumes\`
- Docker Desktop manages it automatically

---

## 🎓 Docker Commands Cheat Sheet

```powershell
# Start everything
docker-compose up -d              # Detached mode (background)

# Stop everything
docker-compose down               # Stop and remove containers
docker-compose down -v            # Also remove volumes (deletes data!)

# View status
docker-compose ps                 # List containers
docker ps                         # List all running containers

# Logs
docker-compose logs               # All logs
docker-compose logs -f            # Follow logs (live)
docker-compose logs pingservice   # Specific service

# Rebuild
docker-compose build              # Rebuild images
docker-compose up --build         # Rebuild and start

# Execute commands in container
docker exec -it pingservice sh    # Open shell in C# container
docker exec -it sportsservice bash  # Open bash in Python container
docker exec -it sportsdb psql -U postgres  # PostgreSQL CLI

# Clean up
docker system prune -a            # Remove all unused data
docker volume ls                  # List volumes
docker network ls                 # List networks
```

---

## ✅ Final Checklist

- [ ] Docker Desktop installed
- [ ] Docker Desktop running (whale icon in system tray)
- [ ] Can run `docker --version` successfully
- [ ] Can run `docker ps` without errors
- [ ] Enough disk space (10+ GB free)
- [ ] Enough RAM allocated (4+ GB recommended)
- [ ] Ports 5000, 5001, 5432 not in use
- [ ] VS Code tasks configured (`.vscode/tasks.json`)
- [ ] `docker-compose.yml` in project root

**All checked?** You're ready to run! Press `Ctrl+Shift+B` in VS Code!

---

**Made with 💜 for CodexEterna**
