"""Central API foundation for OpenAutoCore.

The health endpoint is always available. Authentication routes are mounted only
when OAC_ENABLE_TENANT_AUTH is explicitly enabled after the tenant schema
migration is applied and validated. Business-data routes remain unavailable.
"""
from fastapi import FastAPI

app = FastAPI(
    title="OpenAutoCore API",
    version="0.2.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@app.get("/health", tags=["operations"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "openautocore-api", "stage": "foundation"}


# Keep default startup independent of database credentials and schema state.
from api.auth_routes import enabled_by_environment

if enabled_by_environment():
    from api.auth_routes import router as auth_router
    app.include_router(auth_router)
