# CodexEterna

A multi-source data-pipeline prototype combining generated coordinates, crypto market streams, and sports-data collection.

**Status:** Data-pipeline prototype  
**Built with:** .NET 8, Python, Docker, PostgreSQL

## Reading order

1. Read the root README for project purpose and setup navigation.
2. Follow the entry points below to find the implementation.
3. Use the file guide to locate individual modules, tests, assets, and configuration.
4. Check component licenses before redistributing dependencies or assets.

## Important paths

- [QUICKSTART.md](../QUICKSTART.md) — Documentation: 🚀 CodexEterna v2.0 - Complete VS Code Quickstart Guide. Covers ✨ What This App Does; 📍 **Coordinate Ping Stream**; 💰 **Crypto Monitoring** *(NEW!)*.
- [docker-compose.yml](../docker-compose.yml) — Configuration or build metadata for docker compose; read alongside the application or tool that loads it.
- [PROJECT_NOTES.md](../PROJECT_NOTES.md) — Preserved detailed setup, usage, architecture, and development notes from the earlier README.

## Structure

| Path | Role |
| --- | --- |
| [.vscode/](../.vscode/) | Project-specific .vscode components (4 tracked entries). |
| [PingService/](../PingService/) | Project-specific PingService components (13 tracked entries). |
| [SportsService/](../SportsService/) | Project-specific SportsService components (11 tracked entries). |
| [docs/](../docs/) | Project documentation, decisions, and reference material (6 tracked entries). |

## Scope

Throughput and production-readiness claims in older notes are historical claims, not newly verified performance guarantees. Data-provider terms remain separate from the source license.

## Maintaining the guide

The file catalog is a source-inspection snapshot, not proof that every runtime path works. Update it when moving files or changing module responsibilities. The 2026-10-12 documentation review did not run every application, deploy services, or validate all historical performance claims.
