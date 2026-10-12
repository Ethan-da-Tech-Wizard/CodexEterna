# CodexEterna

A multi-source data-pipeline prototype combining generated coordinates, crypto market streams, and sports-data collection.

**Status:** Data-pipeline prototype  
**Built with:** .NET 8, Python, Docker, PostgreSQL

[Project guide](docs/PROJECT_GUIDE.md) · [Every file explained](docs/FILE_GUIDE.md) · [Licenses and dependencies](docs/LICENSE_REVIEW.md)

## Start here

- [QUICKSTART.md](QUICKSTART.md) — Documentation: 🚀 CodexEterna v2.0 - Complete VS Code Quickstart Guide. Covers ✨ What This App Does; 📍 **Coordinate Ping Stream**; 💰 **Crypto Monitoring** *(NEW!)*.
- [docker-compose.yml](docker-compose.yml) — Configuration or build metadata for docker compose; read alongside the application or tool that loads it.
- [PROJECT_NOTES.md](PROJECT_NOTES.md) — Preserved detailed setup, usage, architecture, and development notes from the earlier README.

[Detailed setup, usage, and development notes](PROJECT_NOTES.md) preserve the previous project documentation.

## Repository layout

| Path | Role |
| --- | --- |
| [.vscode/](.vscode/) | Project-specific .vscode components (4 tracked entries). |
| [PingService/](PingService/) | Project-specific PingService components (13 tracked entries). |
| [SportsService/](SportsService/) | Project-specific SportsService components (11 tracked entries). |
| [docs/](docs/) | Project documentation, decisions, and reference material (6 tracked entries). |

## Scope and current limits

Throughput and production-readiness claims in older notes are historical claims, not newly verified performance guarantees. Data-provider terms remain separate from the source license.

## License

Original project code retains **MIT** terms in [LICENSE](LICENSE). Third-party libraries, media, data, models, and tools retain their own terms. See the [license review](docs/LICENSE_REVIEW.md) and [dependency inventory](docs/DEPENDENCIES.csv).
