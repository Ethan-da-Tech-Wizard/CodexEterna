# CodexEterna v2.0 - Professional Real-Time Data Pipeline

A production-ready multi-source data collection platform featuring high-throughput coordinate generation (20,000/sec), live cryptocurrency monitoring (Binance), and sports data aggregation (ESPN). Built with C# (.NET 8), Python (3.12), and Docker.

[![.NET 8](https://img.shields.io/badge/.NET-8.0-512BD4)](https://dotnet.microsoft.com/)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)](https://www.docker.com/)
[![PostgreSQL 15](https://img.shields.io/badge/PostgreSQL-15-316192)](https://www.postgresql.org/)

---

## 🚨 NEW USER? START HERE! 🚨

**👉 [QUICKSTART.md](QUICKSTART.md) - Complete setup guide for VS Code (10 minutes)**

**Just want to run it?**
1. Install Docker Desktop
2. Open CodexEterna folder in VS Code
3. Press `Ctrl+Shift+B`
4. Open `http://localhost:5000`
5. Click START buttons to begin data collection

**Important:** All data collection systems require **manual confirmation** before starting. This prevents accidental memory overflow from 20k/sec ping generation.

---

## ✨ What's New in v2.0

### 🔐 **Safety-First Design**
- All systems start in **stopped state**
- Manual confirmation required before data collection
- Immediate STOP buttons to prevent memory overflow
- Clear warning dialogs explain implications

### 💰 **Binance Crypto Monitoring** *(NEW!)*
- Real-time WebSocket connection to Binance
- Live BTC/USDT price tracking (updates every 2 seconds)
- Automatic 10-minute timestamped snapshots
- Historical data viewing with date filtering
- Minimal memory footprint

### 📍 **Enhanced Coordinate Ping System**
- Still generates 20,000 pings/second
- Now with **manual start/stop controls**
- Comprehensive coordinate tracking (all unique lat/long)
- Advanced sorting and filtering
- localStorage persistence with auto-save

### 🏆 **Improved Sports Data Feed**
- On-demand ESPN API integration
- Automatic timestamping for all fetches
- Historical data organized by date
- Better error handling and UX

### 🎨 **Professional UI Redesign**
- Tabbed interface (Ping | Crypto | Sports)
- 6 professional color themes
- Cleaner, less chaotic layout
- Real-time status indicators
- Responsive design

---

## 🏗 Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser (localhost:5000)                  │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Ping Tab   │  │  Crypto Tab  │  │   Sports Tab     │   │
│  │ (20k/sec)  │  │  (Binance)   │  │   (ESPN API)     │   │
│  └────────────┘  └──────────────┘  └──────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                        │
      ┌─────────▼──────────┐  ┌─────────▼──────────┐
      │   PingService      │  │  SportsService     │
      │   (C# / .NET 8)    │  │  (Python 3.12)     │
      │   Port 5000        │  │  Port 5001         │
      │                    │  │                    │
      │  • Ping Generator  │  │  • ESPN API        │
      │  • Crypto Monitor  │  │  • PostgreSQL      │
      │  • SignalR Hub     │  │  • FastAPI         │
      │  • Binance WS      │  │                    │
      └────────────────────┘  └──────────┬─────────┘
                                         │
                              ┌──────────▼──────────┐
                              │   PostgreSQL 15     │
                              │   Port 5432         │
                              │  (Sports Data DB)   │
                              └─────────────────────┘
```

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Ping Service** | C# / .NET | 8.0 | High-throughput coordinate generation + crypto monitoring |
| **Sports Service** | Python / FastAPI | 3.12 | Sports data aggregation from ESPN API |
| **Database** | PostgreSQL | 15 | Persistent storage for sports data |
| **Frontend** | Vanilla JS + CSS | ES6+ | Professional responsive dashboard |
| **Containerization** | Docker Compose | 3.8 | Multi-service orchestration |
| **Real-time Comm** | SignalR + WebSocket | 7.0 | Live data streaming to browser |
| **External APIs** | Binance + ESPN | - | Crypto prices + sports scores |

---

## 🚀 Features

### 📍 Coordinate Ping Stream

**Capabilities:**
- Generates **20,000 GPS coordinates per second**
- Tracks all unique coordinate occurrences
- Real-time statistics (total pings, unique coords, pings/sec)
- Advanced sorting (by frequency, timestamp, lat/long)
- Search and filter functionality
- Browser localStorage persistence

**Safety Features:**
- Manual START with confirmation dialog
- Immediate STOP button to prevent memory overflow
- Warning indicators when actively collecting
- Pause/Resume controls
- Data reset capability

**Technical Details:**
- Concurrent dictionary for thread-safe coordinate tracking
- Batched updates to reduce UI lag
- Auto-save every 10 seconds
- Comprehensive coordinate metadata (count, last seen, timestamp)

### 💰 Crypto Monitoring (Binance)

**Capabilities:**
- Real-time BTC/USDT price via WebSocket
- Price updates every 2 seconds
- 10-minute automatic snapshots with timestamps
- Historical data storage and viewing
- Date-based filtering
- High/Low price tracking per interval
- Trade count aggregation

**Safety Features:**
- Manual START with confirmation dialog
- Immediate STOP to disconnect WebSocket
- Clear connection status indicators
- Automatic reconnection on disconnect

**Technical Details:**
- Binance WebSocket Stream: `wss://stream.binance.com:9443/ws/btcusdt@trade`
- Snapshot model: Timestamp, Price, High, Low, TotalTrades
- Minimal memory footprint (only snapshots stored)
- Background service with cancellation token support

### 🏆 Sports Data Feed (ESPN)

**Capabilities:**
- On-demand data fetching from ESPN API
- Supports: NFL, NBA, MLB, NHL, MLS, WNBA
- Live game scores and status
- Team names and detailed match information
- Historical data with timestamps
- Date-based filtering
- Clear history option

**Data Storage:**
- Browser localStorage for client-side persistence
- PostgreSQL for server-side persistence (optional)
- Organized by sport and date
- Filterable by date range

**Technical Details:**
- ESPN API: `https://site.api.espn.com/apis/site/v2/sports/{sport}/scoreboard`
- Python FastAPI backend
- Automatic timestamp generation
- JSON data parsing and normalization

---

## 📊 Data Flow

### Ping System Data Flow

```
PingGeneratorService (C#)
    ↓ (20,000/sec)
ConcurrentDictionary<CoordinatePing>
    ↓ (batched every 100ms)
SignalR Hub → WebSocket
    ↓
Browser JavaScript
    ↓ (every 10s)
localStorage ('codexeterna_ping_data')
    ↓
Data Table Rendering
```

### Crypto System Data Flow

```
Binance WebSocket
    ↓ (real-time trades)
CryptoService (C#)
    ↓ (process + aggregate)
Price Tracking (current, high, low)
    ↓ (every 10 minutes)
CryptoSnapshot (timestamped)
    ↓ (polling every 2s)
Browser JavaScript → UI Update
```

### Sports System Data Flow

```
User Click "Fetch Latest"
    ↓
Browser → ESPN API (CORS-enabled)
    ↓
JSON Game Data
    ↓
Store in localStorage (timestamped)
    ↓
Render Game Cards
    ↓ (optional)
Python Service → PostgreSQL (server-side storage)
```

---

## 🎯 Quick Start

### Prerequisites

- **Docker Desktop** (v20.10+)
- **VS Code** (recommended)
- **8GB+ RAM** (for 20k/sec ping generation)
- **Internet connection** (for Binance WebSocket + ESPN API)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/CodexEterna.git
   cd CodexEterna
   ```

2. **Open in VS Code:**
   ```bash
   code .
   ```

3. **Start everything:**
   - Press `Ctrl+Shift+B`
   - OR run: `docker-compose up --build`

4. **Open dashboard:**
   - Navigate to: `http://localhost:5000`

5. **Start data collection:**
   - Click "Coordinate Ping Stream" tab
   - Click **▶ START Collection** and confirm
   - Click "Crypto Monitoring" tab
   - Click **▶ START Monitoring** and confirm

### First-Time Setup (3-5 minutes)

Docker will:
1. Pull base images (.NET 8, Python 3.12, PostgreSQL 15)
2. Build PingService container
3. Build SportsService container
4. Initialize PostgreSQL database
5. Start all services

**Subsequent starts:** 10-20 seconds (images cached)

---

## 🎮 Usage

### Starting Data Collection

**Ping System:**
```
1. Navigate to "Coordinate Ping Stream" tab
2. Click "▶ START Collection"
3. Confirm warning dialog
4. Watch real-time statistics update
```

**Crypto Monitoring:**
```
1. Navigate to "Crypto Monitoring" tab
2. Click "▶ START Monitoring"
3. Confirm connection dialog
4. Watch BTC/USDT price update every 2 seconds
```

**Sports Data:**
```
1. Navigate to "Sports Data Feed" tab
2. Select a sport from dropdown
3. Click "Fetch Latest Data"
4. View live game scores
```

### Stopping Data Collection

**Always stop before closing:**
1. Click **⏹ STOP Collection** (Ping tab)
2. Click **⏹ STOP Monitoring** (Crypto tab)
3. Press `Ctrl+C` in terminal to stop Docker

**Why this matters:**
- Ping system at 20k/sec can consume 500MB-1GB RAM
- Proper shutdown ensures data is saved
- Clean disconnect from Binance WebSocket

---

## 📡 API Documentation

### Ping Service API (Port 5000)

#### Ping Generation Endpoints

```http
POST /api/ping/start
Start ping generation (requires manual confirmation)

POST /api/ping/stop
Stop ping generation immediately

POST /api/ping/pause
Pause ping generation (temporary)

POST /api/ping/resume
Resume ping generation

POST /api/ping/reset
Reset all coordinate data

GET /api/ping/stats
Get current system statistics

GET /api/ping/all?limit=100000
Get all unique coordinates

GET /api/ping/top?count=100
Get top N coordinates by frequency

GET /api/ping/filter?minLat=0&maxLat=90
Advanced coordinate filtering

GET /api/ping/health
Health check endpoint
```

#### Crypto Monitoring Endpoints

```http
POST /api/crypto/start
Start Binance WebSocket monitoring

POST /api/crypto/stop
Stop crypto monitoring immediately

GET /api/crypto/stats
Get current crypto statistics

GET /api/crypto/snapshots
Get all timestamped snapshots

GET /api/crypto/snapshots/range?startDate=2026-01-01&endDate=2026-01-09
Filter snapshots by date range

GET /api/crypto/health
Health check endpoint
```

### Sports Service API (Port 5001)

```http
GET /games?sport=basketball/nba
Fetch games for a specific sport

GET /health
Health check endpoint
```

### Swagger Documentation

Once running, visit:
- **Ping Service:** `http://localhost:5000/swagger`
- **Sports Service:** `http://localhost:5001/docs`

Interactive API testing and full documentation available.

---

## 🏅 Project Structure

```
CodexEterna/
├── .vscode/                           # VS Code configuration
│   ├── tasks.json                    # Docker Compose tasks (Ctrl+Shift+B)
│   ├── launch.json                   # Debugging configurations
│   ├── settings.json                 # Workspace settings
│   └── extensions.json               # Recommended extensions
│
├── PingService/                      # C# Data Pipeline Service
│   ├── Controllers/
│   │   ├── PingController.cs         # Ping generation API
│   │   └── CryptoController.cs       # Crypto monitoring API
│   ├── Services/
│   │   ├── PingGeneratorService.cs   # 20k/sec background service
│   │   └── CryptoService.cs          # Binance WebSocket service
│   ├── Models/
│   │   ├── CoordinatePing.cs         # Ping data model
│   │   └── CryptoModels.cs           # Crypto snapshot models
│   ├── Hubs/
│   │   └── PingHub.cs                # SignalR real-time hub
│   ├── wwwroot/
│   │   ├── index.html                # Professional dashboard UI
│   │   ├── css/dashboard.css         # Professional themes
│   │   └── js/dashboard.js           # Client-side logic (1500+ lines)
│   ├── Dockerfile                    # .NET 8 container
│   ├── Program.cs                    # Service registration & startup
│   └── PingService.csproj            # .NET 8 project file
│
├── SportsService/                    # Python Sports Service
│   ├── app/
│   │   ├── main.py                   # FastAPI application
│   │   ├── database.py               # PostgreSQL ORM
│   │   └── models.py                 # Data models
│   ├── Dockerfile                    # Python 3.12 container
│   ├── requirements.txt              # Python dependencies
│   └── init_db.py                    # Database initialization script
│
├── docker-compose.yml                # Service orchestration
├── QUICKSTART.md                     # Complete setup guide
├── README.md                         # This file
├── VSCODE_GUIDE.md                   # Advanced VS Code workflows
├── DOCKER_SETUP.md                   # Docker Desktop guide
└── TROUBLESHOOTING.md                # Common issues & solutions
```

---

## 🧪 Development

### Running Locally (Without Docker)

**Ping Service (C#):**
```bash
cd PingService
dotnet restore
dotnet run
```

**Sports Service (Python):**
```bash
cd SportsService
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --host 0.0.0.0 --port 5001
```

### Building Docker Images

**Build all services:**
```bash
docker-compose build
```

**Build specific service:**
```bash
docker-compose build pingservice
docker-compose build sportsservice
```

### Viewing Logs

**All services:**
```bash
docker-compose logs -f
```

**Specific service:**
```bash
docker-compose logs -f pingservice
docker-compose logs -f sportsservice
```

### Database Access

**Connect to PostgreSQL:**
```bash
docker exec -it sportsdb psql -U postgres -d sportsdata
```

**Common queries:**
```sql
-- View all games
SELECT * FROM games;

-- Count games by sport
SELECT sport, COUNT(*) FROM games GROUP BY sport;

-- Recent games
SELECT * FROM games ORDER BY game_date DESC LIMIT 10;
```

---

## 📊 Performance

### Benchmarks

**Ping Generation:**
- Target: 20,000 pings/second
- Actual: 18,000-22,000 pings/second (±10%)
- Memory: ~500MB-1GB over 10 minutes at full speed
- CPU: ~15-25% (single-core)

**Crypto Monitoring:**
- WebSocket latency: <100ms
- Update frequency: Every 2 seconds (client-side polling)
- Memory: <50MB (minimal footprint)
- CPU: <5%

**Sports Data:**
- API response time: 200-800ms (ESPN servers)
- Data size: ~10-50KB per fetch
- localStorage: ~1MB per 100 fetches

### Scaling Considerations

**Horizontal Scaling:**
- Multiple PingService instances (load balanced)
- Shared PostgreSQL database
- Redis for distributed caching (not implemented)

**Vertical Scaling:**
- Increase Docker memory limits
- Tune batch sizes in PingGeneratorService
- Optimize table rendering with virtualization

---

## 🔧 Configuration

### Environment Variables

**PingService:**
```env
ASPNETCORE_ENVIRONMENT=Production
ASPNETCORE_URLS=http://+:5000
```

**SportsService:**
```env
DATABASE_URL=postgresql://postgres:secret@sportsdb:5432/sportsdata
PYTHONUNBUFFERED=1
```

### Docker Compose Ports

| Service | Internal Port | External Port | Protocol |
|---------|--------------|---------------|----------|
| PingService | 5000 | 5000 | HTTP |
| SportsService | 5001 | 5001 | HTTP |
| PostgreSQL | 5432 | 5432 | TCP |

**Change ports in `docker-compose.yml`:**
```yaml
ports:
  - "YOUR_PORT:5000"  # Change first number only
```

---

## 🛡 Security

### Current Implementation

- ✅ CORS enabled for local development
- ✅ No authentication (local dev only)
- ✅ Manual confirmation for data collection
- ✅ Input validation on API endpoints
- ✅ PostgreSQL credentials in environment variables

### Production Recommendations

- 🔒 Add authentication (JWT, OAuth)
- 🔒 HTTPS/TLS encryption
- 🔒 Rate limiting on APIs
- 🔒 Move secrets to Docker secrets or vault
- 🔒 Network segmentation
- 🔒 Input sanitization for user-provided filters

---

## 🐛 Troubleshooting

### Common Issues

**See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for comprehensive guide.**

**Quick fixes:**
- **Port conflicts:** Change ports in `docker-compose.yml`
- **Docker not running:** Start Docker Desktop
- **Services won't start:** Run `docker-compose down -v` then rebuild
- **Crypto won't connect:** Check internet connection
- **No sports data:** Sport might be off-season

---

## 📚 Learning Resources

### Technologies Used

- [.NET 8 Documentation](https://learn.microsoft.com/en-us/dotnet/)
- [Python 3.12 Documentation](https://docs.python.org/3.12/)
- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SignalR Documentation](https://learn.microsoft.com/en-us/aspnet/core/signalr/)
- [Binance WebSocket API](https://binance-docs.github.io/apidocs/)
- [ESPN API (Unofficial)](https://gist.github.com/akeaswaran/b48b02f1c94f873c6655e7129910fc3b)

---

## 🤝 Contributing

This is a learning/demonstration project. Feel free to:
- Fork and experiment
- Report issues
- Suggest improvements
- Create pull requests

---

## 📝 License

MIT License - Feel free to use for learning and projects.

---

## 🙏 Acknowledgments

- **Binance** - Free WebSocket API for crypto prices
- **ESPN** - Sports data API
- **Microsoft** - .NET 8 and SignalR
- **Python** - FastAPI framework
- **Docker** - Containerization platform

---

## 📧 Contact & Support

- **Issues:** [GitHub Issues](https://github.com/YOUR-USERNAME/CodexEterna/issues)
- **Documentation:** See `/docs` folder for detailed guides

---

**Built with 💜 for learning microservices, real-time data, and modern architecture**

**CodexEterna v2.0** - Professional Data Pipeline Edition

---

## 🎯 Roadmap

### Completed ✅
- [x] 20,000 pings/second generation
- [x] Real-time WebSocket communication
- [x] Professional UI with themes
- [x] Binance crypto monitoring
- [x] Manual start/stop controls
- [x] Historical data storage
- [x] Sports data integration
- [x] Docker containerization
- [x] VS Code integration

### Future Enhancements 🚀
- [ ] Redis caching layer
- [ ] Authentication system
- [ ] Data export (CSV, JSON)
- [ ] More crypto pairs (ETH, BNB, etc.)
- [ ] Real-time charts/graphs
- [ ] Mobile-responsive improvements
- [ ] Kubernetes deployment config
- [ ] Prometheus monitoring
- [ ] Unit and integration tests
- [ ] CI/CD pipeline

---

**Version:** 2.0.0
**Last Updated:** January 2026
**Status:** Production-Ready (Learning/Demo)
