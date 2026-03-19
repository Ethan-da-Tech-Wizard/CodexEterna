# Real-Time Data Pipeline - CodexEterna

A production-ready hybrid C# and Python microservices system demonstrating high-throughput real-time data processing, WebSocket communication, and modern cloud-native architecture.

---

## 👉 [HOW_TO_RUN.md](HOW_TO_RUN.md) — Start here

Builds a real desktop installer (`.exe` / `.dmg`) **or** runs via Docker.

---

## 🚀 Features

- **High-Throughput Coordinate Tracking**: Generates and processes 20,000 GPS coordinate pings per second
- **Real-Time Dashboard**: Live-updating web interface with WebSocket communication
- **Sports Data Integration**: Fetches and stores live sports data from ESPN API
- **Microservices Architecture**: Clean separation of concerns with containerized services
- **Pause/Resume Controls**: Interactive controls for data stream management
- **Persistent Storage**: PostgreSQL database for sports data with full CRUD operations
- **12-Factor App Compliant**: Follows cloud-native best practices
- **Docker Containerized**: Easy deployment with Docker Compose
- **Scalable Design**: Ready for horizontal scaling and production deployment

## 📋 Quick Start

### Prerequisites

- Docker Desktop (v20.10+)
- Docker Compose (v2.0+)
- 8GB+ RAM recommended
- Modern web browser

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/CodexEterna.git
cd CodexEterna

# 2. Start all services with Docker Compose
docker-compose up --build

# 3. Access the dashboard
# Open http://localhost:5000 in your browser
```

That's it! The system is now running with:
- ✅ C# Ping Service on port 5000 (with dashboard)
- ✅ Python Sports Service on port 5001
- ✅ PostgreSQL database on port 5432

### First Steps

1. **Watch Live Pings**: The dashboard shows 20,000 pings/second being generated
2. **Test Controls**: Click "Pause" to stop, "Resume" to continue
3. **Fetch Sports Data**: Select "NFL Football" → Click "Fetch Latest"
4. **Explore API**: Visit http://localhost:5000/swagger for API docs

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User's Browser                            │
│                   Real-Time Dashboard (HTML/JS)                  │
└──────────────┬─────────────────────────────┬────────────────────┘
               │                             │
        WebSocket (SignalR)            HTTP REST API
               │                             │
               ▼                             ▼
┌──────────────────────────┐    ┌───────────────────────────┐
│  C# Ping Service         │    │  Python Sports Service     │
│  Port: 5000              │    │  Port: 5001               │
└──────────────────────────┘    └───────────┬───────────────┘
                                            │
                                            ▼
                                ┌───────────────────────────┐
                                │  PostgreSQL Database      │
                                │  Port: 5432               │
                                └───────────────────────────┘
```

### Technology Stack

**C# Ping Service:**
- .NET 7.0 / ASP.NET Core
- SignalR for real-time WebSocket communication
- Multi-threaded background service for 20K pings/sec
- ConcurrentDictionary for thread-safe operations

**Python Sports Service:**
- Python 3.11 / FastAPI
- SQLAlchemy ORM
- PostgreSQL for persistent storage
- ESPN API integration

**Frontend:**
- Vanilla JavaScript (ES6+)
- SignalR JavaScript Client
- Modern CSS3 (Grid/Flexbox)

## 📁 Project Structure

```
CodexEterna/
├── PingService/              # C# Coordinate Ping Service
│   ├── Controllers/          # REST API endpoints
│   ├── Services/             # Background ping generation
│   ├── Hubs/                 # SignalR WebSocket hub
│   ├── Models/               # Data models
│   ├── wwwroot/              # Dashboard UI (HTML/CSS/JS)
│   └── Dockerfile
│
├── SportsService/            # Python Sports Data Service
│   ├── app/                  # FastAPI application
│   ├── models/               # Database models & schemas
│   ├── services/             # ESPN API & database operations
│   ├── requirements.txt
│   └── Dockerfile
│
├── docs/                     # Documentation
│   └── SYSTEM_DESIGN.md      # Comprehensive architecture guide
│
├── docker-compose.yml        # Orchestrates all services
└── README.md                 # This file
```

## 📖 Usage Guide

### Dashboard Interface

The web dashboard (http://localhost:5000) has two main panels:

**Left Panel - Coordinate Ping Stream:**
- Real-time statistics (total pings, unique coordinates, pings/sec)
- Pause/Resume/Reset controls
- Search coordinates by pattern
- Live-updating table of coordinate counts

**Right Panel - Sports Data:**
- Select sport (NFL, NBA, MLB, NHL, MLS, WNBA)
- Fetch latest data from ESPN API
- View stored games with scores and status

### API Endpoints

**Ping Service (http://localhost:5000):**

```bash
# Get current statistics
curl http://localhost:5000/api/ping/stats

# Pause ping generation
curl -X POST http://localhost:5000/api/ping/pause

# Resume ping generation
curl -X POST http://localhost:5000/api/ping/resume

# Get top 100 coordinates
curl http://localhost:5000/api/ping/top?count=100

# Search coordinates
curl "http://localhost:5000/api/ping/search?pattern=33.42"

# API Documentation
http://localhost:5000/swagger
```

**Sports Service (http://localhost:5001):**

```bash
# Fetch NFL data from ESPN
curl "http://localhost:5001/api/sports/fetch?league=football/nfl"

# Get stored NFL games
curl "http://localhost:5001/api/sports/games?league=football/nfl"

# Get games from last 3 days
curl "http://localhost:5001/api/sports/games?days=3"

# Search by team
curl "http://localhost:5001/api/sports/games?team=Lakers"

# List supported leagues
curl http://localhost:5001/api/sports/leagues

# API Documentation
http://localhost:5001/docs
```

### WebSocket (SignalR)

Connect to real-time ping updates:

```javascript
const connection = new signalR.HubConnectionBuilder()
    .withUrl("http://localhost:5000/hubs/ping")
    .build();

// Receive batched ping updates
connection.on("ReceivePingBatch", (updates) => {
    console.log("Received", updates.length, "updates");
});

// Receive statistics every second
connection.on("ReceiveStats", (stats) => {
    console.log("Pings/sec:", stats.pingsPerSecond);
});

await connection.start();
```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` to customize:

```bash
# Database
DATABASE_URL=postgresql://postgres:secret@sportsdb:5432/sportsdata

# Service Ports
PING_SERVICE_PORT=5000
SPORTS_SERVICE_PORT=5001

# Application Settings
ASPNETCORE_ENVIRONMENT=Production
PYTHONUNBUFFERED=1
```

### Adjusting Ping Rate

Edit `PingService/Services/PingGeneratorService.cs`:

```csharp
private const int TARGET_PINGS_PER_SECOND = 20000;  // Change this
```

## 🛠️ Development

### Local Development (Without Docker)

**C# Service:**
```bash
cd PingService
dotnet restore
dotnet run
# Runs on http://localhost:5000
```

**Python Service:**
```bash
cd SportsService
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --port 5001 --reload
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f pingservice
docker-compose logs -f sportsservice
```

### Database Access

```bash
# Connect to PostgreSQL
docker exec -it sportsdb psql -U postgres sportsdata

# Or use connection string
psql postgresql://postgres:secret@localhost:5432/sportsdata
```

## 🧪 Testing

### Health Checks

```bash
curl http://localhost:5000/api/ping/health
curl http://localhost:5001/health
```

### Load Testing

```bash
# Using Apache Bench
ab -n 10000 -c 100 http://localhost:5000/api/ping/stats

# Monitor performance
docker stats
```

### Manual Testing

1. Start the system: `docker-compose up`
2. Open browser to http://localhost:5000
3. Verify:
   - ✅ Ping counter is increasing (~20K/sec)
   - ✅ Unique coordinates are being tracked
   - ✅ Pause/Resume works
   - ✅ Sports data can be fetched and displayed

## 🚢 Deployment

### Docker Compose (Production)

```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose up --scale pingservice=3 --scale sportsservice=2
```

### Kubernetes

```bash
# Deploy to Kubernetes cluster
kubectl apply -f k8s/

# Check status
kubectl get pods
kubectl get services
```

### Cloud Deployment

See [docs/SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md) for detailed scaling strategies including:
- AWS ECS Fargate deployment
- Horizontal scaling with load balancers
- Database replication and caching
- Estimated costs (~$180/month for production)

## 🐛 Troubleshooting

### Ports Already in Use

```bash
# Check what's using port 5000
lsof -i :5000

# Change ports in docker-compose.yml if needed
```

### Database Connection Issues

```bash
# Restart database
docker-compose restart sportsdb

# Check database logs
docker-compose logs sportsdb

# Verify connection
docker exec sportsdb pg_isready -U postgres
```

### SignalR Not Connecting

- Clear browser cache
- Check browser console for errors
- Verify firewall settings
- Try different browser

### High Memory Usage

```bash
# Monitor container resources
docker stats

# Reduce ping generation rate if needed
# or restart services
docker-compose restart
```

## 📚 Documentation

- **[System Design](docs/SYSTEM_DESIGN.md)** - Comprehensive architecture guide
  - High-level architecture
  - Data flow diagrams
  - Performance characteristics
  - Scaling strategies
  - 12-Factor App compliance
  - Security considerations
  - Monitoring and observability

## 🎯 Key Features Demonstrated

This project showcases:

✅ **Microservices Architecture** - Clean separation of concerns
✅ **Real-Time Communication** - WebSocket/SignalR implementation
✅ **High-Throughput Processing** - 20,000 events/second
✅ **Polyglot Programming** - C# + Python integration
✅ **Containerization** - Docker multi-stage builds
✅ **Database Design** - PostgreSQL with ORM
✅ **REST API Design** - FastAPI and ASP.NET Core
✅ **12-Factor App** - Cloud-native best practices
✅ **Observability** - Health checks and logging
✅ **Scalable Design** - Ready for production deployment

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- ESPN for sports data API
- Microsoft for SignalR and .NET
- FastAPI team for excellent Python framework
- PostgreSQL community
- Docker ecosystem

---

**Built with ❤️ using C#, Python, and modern cloud-native technologies**

⭐ **If you find this project useful, please star it on GitHub!**

## 📧 Support

For questions or issues:
- Open an issue on GitHub
- Check the [System Design Documentation](docs/SYSTEM_DESIGN.md)
- Review API documentation at http://localhost:5000/swagger

---

**Project Status**: ✅ Production Ready | **Last Updated**: January 2024
