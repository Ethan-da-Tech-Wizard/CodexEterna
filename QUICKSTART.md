# ⚡ Quick Start Guide (5 Minutes)

Get the Real-Time Data Pipeline running in **5 minutes or less**.

## Prerequisites

- ✅ Docker Desktop installed and running
- ✅ Git installed
- ✅ 8GB+ RAM available

---

## 3 Commands to Run

```bash
# 1. Clone and enter directory
git clone https://github.com/Ethan-da-Tech-Wizard/CodexEterna.git
cd CodexEterna

# 2. Switch to feature branch
git checkout claude/hybrid-data-pipeline-design-0Ekw7

# 3. Start everything
docker-compose up --build
```

⏰ **First run**: 5-10 minutes (builds images)
⏰ **Subsequent runs**: ~30 seconds

---

## Access the Dashboard

When you see logs like this:
```
pingservice     | Now listening on: http://[::]:5000
sportsservice   | INFO: Application startup complete
```

**Open your browser:**
```
http://localhost:5000
```

---

## Quick Demo

### Test Coordinate Pings

1. **Watch live updates** - Counters increase rapidly
2. **Click "Pause"** - Data stream stops
3. **Click "Resume"** - Data stream continues
4. **Click "Top 100"** - See most frequent coordinates

### Test Sports Data

1. **Select "NFL Football"** from dropdown
2. **Click "Fetch Latest"**
3. **See live game scores** appear
4. **Click "Load Stored"** - Data persists!

### Test APIs

Open new terminal:
```bash
# Get ping statistics
curl http://localhost:5000/api/ping/stats

# Get high-scoring games
curl "http://localhost:5001/api/sports/high-scoring?threshold=150"

# API Documentation
open http://localhost:5000/swagger  # Mac
start http://localhost:5000/swagger  # Windows
```

---

## Stop the System

Press `Ctrl+C` in the terminal, then:
```bash
docker-compose down
```

---

## Troubleshooting

### Port Already in Use
```bash
# Change port 5000 to 5001 in docker-compose.yml
ports:
  - "5001:5000"
```

### Services Not Starting
```bash
# Check Docker is running
docker ps

# View logs
docker-compose logs -f

# Full rebuild
docker-compose down -v
docker-compose up --build
```

### Database Issues
```bash
# Wait 30 seconds for DB to initialize
# Or restart database
docker-compose restart sportsdb
```

---

## What You're Running

✅ **C# Ping Service** - Generates 20,000 coordinates/second
✅ **Python Sports Service** - ESPN API integration
✅ **PostgreSQL Database** - Persistent storage
✅ **Real-Time Dashboard** - WebSocket updates
✅ **REST APIs** - Comprehensive filtering

---

## Next Steps

📖 **Full Guide**: See `DEMO_GUIDE.md` for detailed walkthrough
📚 **System Design**: See `docs/SYSTEM_DESIGN.md` for architecture
🔧 **README**: See `README.md` for complete documentation

---

## 🎉 That's It!

You're now running a production-ready microservices system with:
- 20,000 events/second real-time processing
- Multi-language architecture (C# + Python)
- WebSocket communication
- RESTful APIs with 26+ filters
- Docker containerization

**Enjoy! 🚀**
