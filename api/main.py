"""Minimal central API foundation for OpenAutoCore.

Only a health endpoint is exposed until authentication and workshop isolation are implemented.
"""
from fastapi import FastAPI

app = FastAPI(title="OpenAutoCore API", version="0.1.0", redoc_url=None)


@app.get("/health", tags=["operations"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "openautocore-api", "stage": "foundation"}
