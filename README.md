# Wetpancake

Local B2B cold-calling training assistant scaffold.

## What is implemented
- Backend APIs for health, session creation, session retrieval, dialogue turn generation, and session scoring.
- SQLite persistence for sessions.
- Persona generation with anti-repeat objection guard.
- STT/TTS adapter contracts for local model integration.
- Desktop UI scaffold with start-call, in-call, and post-call scorecard states.

## Quick Start
1. Follow `docs/setup/local-install.md`.
2. Start backend with Uvicorn.
3. Start desktop app.
4. Run `pwsh ./scripts/check.ps1`.
