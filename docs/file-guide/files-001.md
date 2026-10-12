# Files 1 of 1 — CodexEterna

[All pages](../FILE_GUIDE.md) · [Project guide](../PROJECT_GUIDE.md)

| File | Role and useful details |
| --- | --- |
| [.env.example](../../.env.example) | Tracked .env resource in .; 442 bytes. |
| [.gitignore](../../.gitignore) | Defines local data, credentials, dependencies, and generated outputs that Git should leave untracked. |
| [.vscode/extensions.json](../../.vscode/extensions.json) | Structured extensions data; top-level fields: `recommendations`. |
| [.vscode/launch.json](../../.vscode/launch.json) | Structured launch data; top-level fields: `version`, `configurations`, `compounds`. |
| [.vscode/settings.json](../../.vscode/settings.json) | Structured settings data; top-level fields: `files.exclude`, `python.defaultInterpreterPath`, `python.linting.enabled`, `python.linting.pylintEnabled`, `python.formatting.provider`, `[python]`, `[csharp]`, `docker.commands.build`, `docker.commands.run`. |
| [.vscode/tasks.json](../../.vscode/tasks.json) | Structured tasks data; top-level fields: `version`, `tasks`. |
| [DOCKER_SETUP.md](../../DOCKER_SETUP.md) | Documentation: 🐳 Docker Desktop Integration Guide. Covers How CodexEterna Links to Docker; Architecture Overview; ✅ Step-by-Step: Linking to Docker. |
| [LICENSE](../../LICENSE) | Preserved license, copyright, or attribution terms; read the full text before reusing the covered component. |
| [PROJECT_NOTES.md](../../PROJECT_NOTES.md) | Preserved detailed setup, usage, architecture, and development notes from the earlier README. |
| [PingService/Controllers/CryptoController.cs](../../PingService/Controllers/CryptoController.cs) | Source module for CryptoController; defines `CryptoController`. |
| [PingService/Controllers/PingController.cs](../../PingService/Controllers/PingController.cs) | Source module for PingController; defines `PingController`. |
| [PingService/Dockerfile](../../PingService/Dockerfile) | Tracked Dockerfile resource in PingService; 860 bytes. |
| [PingService/Hubs/PingHub.cs](../../PingService/Hubs/PingHub.cs) | Source module for PingHub; defines `PingHub`. |
| [PingService/Models/CoordinatePing.cs](../../PingService/Models/CoordinatePing.cs) | Source module for CoordinatePing; defines `CoordinatePing`, `PingUpdate`, `PingStats`. |
| [PingService/Models/CryptoModels.cs](../../PingService/Models/CryptoModels.cs) | Source module for CryptoModels; defines `CryptoSnapshot`, `CryptoTrade`, `CryptoStats`. |
| [PingService/PingService.csproj](../../PingService/PingService.csproj) | Configuration or build metadata for PingService; read alongside the application or tool that loads it. |
| [PingService/Program.cs](../../PingService/Program.cs) | Source module for Program. |
| [PingService/Services/CryptoService.cs](../../PingService/Services/CryptoService.cs) | Source module for CryptoService; defines `CryptoService`, `BinanceTradeMessage`. |
| [PingService/Services/PingGeneratorService.cs](../../PingService/Services/PingGeneratorService.cs) | Source module for PingGeneratorService; defines `PingGeneratorService`. |
| [PingService/wwwroot/css/dashboard.css](../../PingService/wwwroot/css/dashboard.css) | Presentation rules for dashboard; controls layout, typography, color, states, and responsive behavior. |
| [PingService/wwwroot/index.html](../../PingService/wwwroot/index.html) | Browser document: CodexEterna - Real-Time Data Pipeline; provides page structure and may include inline styles or application logic. |
| [PingService/wwwroot/js/dashboard.js](../../PingService/wwwroot/js/dashboard.js) | Source module for dashboard; defines `initializeSignalR`, `reconnect`, `handlePingBatch`, `processUpdateQueue`, `handleStats`, `updateStatValue`, `updateConnectionStatus` and 52 more symbols. |
| [QUICKSTART.md](../../QUICKSTART.md) | Documentation: 🚀 CodexEterna v2.0 - Complete VS Code Quickstart Guide. Covers ✨ What This App Does; 📍 **Coordinate Ping Stream**; 💰 **Crypto Monitoring** *(NEW!)*. |
| [README.md](../../README.md) | Project overview, current status, entry points, setup navigation, and documentation links. |
| [START_HERE.md](../../START_HERE.md) | Documentation: HOW TO RUN THIS - SUPER SIMPLE VERSION. Covers 🎯 USING VS CODE? START HERE!; PART 1: Install Docker (ONE TIME ONLY); If you're on Windows:. |
| [SportsService/Dockerfile](../../SportsService/Dockerfile) | Tracked Dockerfile resource in SportsService; 933 bytes. |
| [SportsService/app/__init__.py](../../SportsService/app/__init__.py) | Empty marker or reserved file; contains no executable behavior or data. |
| [SportsService/app/main.py](../../SportsService/app/main.py) | Sports Data Service - FastAPI Application Fetches and stores sports data from ESPN API Defines `startup_event`, `root`, `health_check`, `fetch_sports_data`, `get_games`, `get_game` and 8 more top-level symbols. |
| [SportsService/init_db.py](../../SportsService/init_db.py) | Database initialization script Run this to create database tables Defines `main`. |
| [SportsService/models/__init__.py](../../SportsService/models/__init__.py) | Empty marker or reserved file; contains no executable behavior or data. |
| [SportsService/models/database.py](../../SportsService/models/database.py) | Database models and configuration for Sports Data Service Defines `Game`, `Team`, `init_db`, `get_db`. |
| [SportsService/models/schemas.py](../../SportsService/models/schemas.py) | Pydantic schemas for API request/response validation Defines `GameBase`, `GameCreate`, `GameUpdate`, `GameResponse`, `TeamBase`, `TeamCreate` and 3 more top-level symbols. |
| [SportsService/requirements.txt](../../SportsService/requirements.txt) | Python dependency requirements and optional dependency groups; install with the project’s documented interpreter and environment. |
| [SportsService/services/__init__.py](../../SportsService/services/__init__.py) | Empty marker or reserved file; contains no executable behavior or data. |
| [SportsService/services/espn_api.py](../../SportsService/services/espn_api.py) | ESPN API Service - Fetches sports data from ESPN's unofficial API Defines `ESPNAPIService`. |
| [SportsService/services/game_service.py](../../SportsService/services/game_service.py) | Game Service - Database operations for games Defines `GameService`. |
| [TROUBLESHOOTING.md](../../TROUBLESHOOTING.md) | Documentation: 🔧 Troubleshooting Guide - "I Pressed Ctrl+Shift+B But No UI". Covers Step-by-Step Diagnosis; Step 1: Is Docker Desktop Running?; Step 2: Check What VS Code Actually Did. |
| [VSCODE_GUIDE.md](../../VSCODE_GUIDE.md) | Documentation: VS Code Guide - Hybrid C# & Python Data Pipeline. Covers 🚀 Quick Start in VS Code; Prerequisites; Opening the Project. |
| [docker-compose.yml](../../docker-compose.yml) | Configuration or build metadata for docker compose; read alongside the application or tool that loads it. |
| [docs/DEPENDENCIES.csv](../../docs/DEPENDENCIES.csv) | Machine-readable inventory of declared and locked dependencies, versions, reported licenses, and evidence URLs. |
| [docs/FILE_GUIDE.md](../../docs/FILE_GUIDE.md) | Index of the complete tracked-file guide, with one entry for every file and links to the paginated descriptions. |
| [docs/LICENSE_REVIEW.md](../../docs/LICENSE_REVIEW.md) | Original-code license, preserved component notices, dependency-license evidence, and unresolved distribution questions. |
| [docs/PROJECT_GUIDE.md](../../docs/PROJECT_GUIDE.md) | Maintainer orientation: purpose, important entry points, source layout, commands, and project-specific boundaries. |
| [docs/SYSTEM_DESIGN.md](../../docs/SYSTEM_DESIGN.md) | Documentation: Real-Time Data Pipeline - System Design Document. Covers Executive Summary; System Overview; Purpose. |
| [docs/file-guide/files-001.md](../../docs/file-guide/files-001.md) | One page of the tracked-file catalog; links each listed path to its role and source-derived details. |
