# TorquePilotOS web foundation

This branch adds a small FastAPI web foundation alongside the existing OpenAutoCore desktop application. It does not replace or modify the desktop entry point.

## Render settings
- Runtime: Python 3
- Build command: `pip install -r requirements-render.txt`
- Start command: `uvicorn torquepilotos_web:app --host 0.0.0.0 --port $PORT`
- Health check path (if available): `/health`
- Plan: Free

## Endpoints
- `/`: TorquePilotOS preview page
- `/health`: lightweight health check
- `/api/status`: foundation status and whether all four legacy MySQL variables are present

## Important
This is a UI/API foundation only. It is not yet connected to the workshop database and has no login/authentication. Do not enter real customer or workshop data until authentication, authorisation, database operations, migrations and tests are implemented. The original project is GPL-3.0; review licence obligations before commercial distribution.
