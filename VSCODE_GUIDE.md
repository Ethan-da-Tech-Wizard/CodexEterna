# VS Code Guide - Hybrid C# & Python Data Pipeline

## 🚀 Quick Start in VS Code

### Prerequisites
- Docker Desktop installed and running
- VS Code with recommended extensions (see below)

### Opening the Project
1. Open VS Code
2. File → Open Folder
3. Navigate to the **root folder** of this project (where `docker-compose.yml` is located)
   - ⚠️ **Important**: Make sure you open the root folder, not a subfolder

### Running the Pipeline

#### Method 1: Using VS Code Tasks (Recommended)
1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "Tasks: Run Task"
3. Select **"Docker Compose: Build and Start"**

Or use the keyboard shortcut:
- Press `Ctrl+Shift+B` (Windows/Linux) or `Cmd+Shift+B` (Mac) to run the default build task

#### Method 2: Using Integrated Terminal
1. Open Terminal in VS Code: `Ctrl+`` (backtick) or View → Terminal
2. Make sure you're in the root folder (you should see `docker-compose.yml` when you run `dir` or `ls`)
3. Run:
   ```bash
   docker-compose up --build
   ```

### Available VS Code Tasks

Access these via `Ctrl+Shift+P` → "Tasks: Run Task":

- **Docker Compose: Build and Start** - Build and start all services (default task)
- **Docker Compose: Start** - Start services without rebuilding
- **Docker Compose: Stop** - Stop all services
- **Docker Compose: Restart** - Restart all services
- **Docker Compose: View Logs** - View live logs from all services
- **Docker Compose: Clean Up** - Stop services and remove volumes

### Testing the Pipeline

Once running, test the services:

#### PowerShell (VS Code Terminal):
```powershell
# Test C# Ping Service
Invoke-WebRequest -Uri http://localhost:5000/coordinates -Method GET

# Test Python Sports Service
Invoke-WebRequest -Uri http://localhost:5001/games -Method GET
```

#### Command Prompt:
```cmd
curl http://localhost:5000/coordinates
curl http://localhost:5001/games
```

### Recommended VS Code Extensions

The project includes extension recommendations. Install them by:
1. Press `Ctrl+Shift+P`
2. Type "Extensions: Show Recommended Extensions"
3. Click "Install" on each recommended extension

**Required Extensions:**
- **Python** - Python language support
- **C#** - C# language support
- **Docker** - Docker integration
- **Remote - Containers** - Work inside Docker containers

### Debugging in VS Code

#### Debugging Python Service (SportsService):
1. Modify `SportsService/Dockerfile` to enable debugging (add debugpy)
2. Use the launch configuration: **"Docker: Attach to Python (SportsService)"**

#### Debugging C# Service (PingService):
1. Use the launch configuration: **".NET: Attach to Container (PingService)"**

### Common Issues & Solutions

#### ❌ Error: "no configuration file provided: not found"
**Problem**: You're not in the root folder

**Solution**:
1. In VS Code, check the terminal path
2. Make sure you opened the folder containing `docker-compose.yml`
3. Use `cd` to navigate to the root if needed:
   ```bash
   cd C:\Users\eman7\OneDrive\Desktop\Dev_Bois\Project_1
   ```

#### ❌ Error: "Docker daemon is not running"
**Solution**: Start Docker Desktop

#### ❌ Error: "Port already in use"
**Solution**: Stop conflicting services or change ports in `docker-compose.yml`

### File Structure
```
CodexEterna/
├── .vscode/                    # VS Code configuration
│   ├── tasks.json             # Docker Compose tasks
│   ├── launch.json            # Debug configurations
│   ├── settings.json          # Workspace settings
│   └── extensions.json        # Recommended extensions
├── PingService/               # C# Coordinate Service
├── SportsService/             # Python Sports Service
├── docker-compose.yml         # Docker configuration (MUST be in root!)
├── VSCODE_GUIDE.md           # This file
├── START_HERE.md             # Quick start guide
└── README.md                 # Full documentation
```

### VS Code Settings

The workspace includes settings for:
- Python formatting with Black
- C# auto-formatting
- Docker integration
- Terminal defaults for Windows

### Keyboard Shortcuts

- `Ctrl+Shift+B` - Build and start Docker containers
- `Ctrl+Shift+P` - Command palette
- `Ctrl+`` - Toggle terminal
- `F5` - Start debugging
- `Ctrl+C` (in terminal) - Stop Docker containers

### Next Steps

1. ✅ Install recommended extensions
2. ✅ Open the project folder in VS Code
3. ✅ Run the default build task (`Ctrl+Shift+B`)
4. ✅ Test the endpoints using PowerShell/curl
5. 📖 Read [START_HERE.md](START_HERE.md) for more details

### Additional Resources

- [Full Documentation](README.md)
- [Quick Start Guide](QUICKSTART.md)
- [Demo Guide](DEMO_GUIDE.md)

---

**Pro Tip**: Keep Docker Desktop running in the background while working in VS Code!
