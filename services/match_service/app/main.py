from fastapi import FastAPI, HTTPException

from .database import database_is_available
from .matches import router as matches_router


app = FastAPI(
    title="EPL Weather Analytics - Match Service",
    version="0.1.0",
)

app.include_router(matches_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "match-service",
    }


@app.get("/health/db")
def database_health() -> dict[str, str]:
    if not database_is_available():
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable",
        )

    return {
        "status": "ok",
        "database": "postgresql",
    }