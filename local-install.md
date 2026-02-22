# Local Install

## Requirements
- Windows 10/11
- Python 3.13+
- Node.js 20+

## Backend
1. `cd services/backend`
2. `py -m pip install --user fastapi uvicorn pytest httpx sqlalchemy`
3. `py -m uvicorn app.main:app --reload`

## Desktop
1. `cd apps/desktop`
2. `npm install`
3. `npm run dev`

## Validation
- Run `pwsh ./scripts/check.ps1`
- Run backend tests: `cd services/backend && py -m pytest tests -v -p no:cacheprovider`
