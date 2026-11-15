import json
import os
from uuid import uuid4

import pika
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field
from redis import Redis, RedisError


router = APIRouter(
    prefix="/analytics/jobs",
    tags=["jobs"],
)

QUEUE_NAME = "analytics_jobs"
JOB_TTL = 86400


class JobRequest(BaseModel):
    team: str = Field(min_length=2, max_length=100)
    season: str = Field(pattern=r"^\d{4}/\d{2}$")


def get_redis() -> Redis:
    return Redis(
        host="redis",
        port=6379,
        decode_responses=True,
        socket_connect_timeout=1,
        socket_timeout=1,
    )


def save_job(job_id: str, data: dict) -> None:
    get_redis().setex(
        f"analytics:job:{job_id}",
        JOB_TTL,
        json.dumps(data),
    )


def publish_job(message: dict) -> None:
    credentials = pika.PlainCredentials(
        os.environ["RABBITMQ_USER"],
        os.environ["RABBITMQ_PASSWORD"],
    )

    parameters = pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
        port=5672,
        credentials=credentials,
        connection_attempts=2,
        retry_delay=1,
        socket_timeout=3,
        blocked_connection_timeout=5,
    )

    connection = pika.BlockingConnection(parameters)

    try:
        channel = connection.channel()

        channel.queue_declare(
            queue=QUEUE_NAME,
            durable=True,
        )

        channel.confirm_delivery()

        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=json.dumps(message).encode("utf-8"),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,
            ),
            mandatory=True,
        )

    finally:
        if connection.is_open:
            connection.close()


@router.post("", status_code=202)
def create_job(request: JobRequest):
    job_id = uuid4().hex

    message = {
        "job_id": job_id,
        "team": request.team,
        "season": request.season,
    }

    try:
        save_job(
            job_id,
            {**message, "status": "queued"},
        )
    except RedisError as exc:
        raise HTTPException(
            status_code=503,
            detail="Job storage unavailable",
        ) from exc

    try:
        publish_job(message)

    except (pika.exceptions.AMQPError, OSError) as exc:
        try:
            save_job(
                job_id,
                {**message, "status": "failed"},
            )
        except RedisError:
            pass

        raise HTTPException(
            status_code=503,
            detail="RabbitMQ unavailable",
        ) from exc

    return {
        "job_id": job_id,
        "status": "queued",
    }


@router.get("/{job_id}")
def get_job(
    job_id: str = Path(pattern=r"^[0-9a-f]{32}$"),
):
    try:
        value = get_redis().get(
            f"analytics:job:{job_id}"
        )
    except RedisError as exc:
        raise HTTPException(
            status_code=503,
            detail="Job storage unavailable",
        ) from exc

    if value is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return json.loads(value)