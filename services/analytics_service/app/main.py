from redis import Redis, RedisError
from fastapi import FastAPI, HTTPException
from .jobs import router as jobs_router

app = FastAPI(
    title="EPL Weather Analytics - Analytics Service",
    version="0.1.0",
)

app.include_router(jobs_router)

def get_redis() -> Redis:
    return Redis(
        host="redis",
        port=6379,
        decode_responses=True,
        socket_connect_timeout=1,
        socket_timeout=1,
    )


@app.get("/health")
def health():
    return {"status": "ok", "service": "analytics-service"}


@app.get("/health/redis")
def redis_health():
    try:
        get_redis().ping()
    except RedisError:
        raise HTTPException(
            status_code=503,
            detail="Redis unavailable",
        )

    return {"status": "ok", "cache": "redis"}
