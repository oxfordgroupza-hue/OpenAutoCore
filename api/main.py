"""Minimal central API foundation for OpenAutoCore.

Only a health endpoint is exposed until authentication and workshop isolation are implemented.
"""
from fastapi import FastAPI

# Keep interactive API documentation and the OpenAPI schema disabled by default.
# Enable them deliberately in a local development-only configuration if needed.
app = FastAPI(
    title="OpenAutoCore API",
    version="0.1.1",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@app.get("/health", tags=["operations"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "openautocore-api", "stage": "foundation"}
