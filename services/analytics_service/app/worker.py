import json
import os
import time

import pika
from redis import Redis

from .analytics import calculate_team_weather


QUEUE_NAME = "analytics_jobs"
JOB_TTL = 86400

redis_client = Redis(
    host="redis",
    port=6379,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1,
)


def save_status(job_id: str, status: str, **extra):
    redis_client.setex(
        f"analytics:job:{job_id}",
        JOB_TTL,
        json.dumps({
            "job_id": job_id,
            "status": status,
            **extra,
        }),
    )


def process_job(channel, method, properties, body):
    job_id = None

    try:
        job = json.loads(body)

        job_id = job["job_id"]
        team = job["team"]
        season = job["season"]

        current = redis_client.get(
            f"analytics:job:{job_id}"
        )

        # Повторно доставленное выполненное задание
        # не рассчитываем заново.
        if current and json.loads(current).get("status") == "done":
            channel.basic_ack(method.delivery_tag)
            return

        save_status(
            job_id,
            "running",
            team=team,
            season=season,
        )

        result = calculate_team_weather(team, season)

        save_status(
            job_id,
            "done",
            team=team,
            season=season,
            result=result,
        )

        channel.basic_ack(method.delivery_tag)

        print(
            f"Job {job_id} completed: {team}, {season}",
            flush=True,
        )

    except Exception as exc:
        print(
            f"Job {job_id} failed: {exc}",
            flush=True,
        )

        if job_id is None:
            # Некорректное сообщение отклоняем.
            channel.basic_reject(
                method.delivery_tag,
                requeue=False,
            )
            return

        try:
            save_status(
                job_id,
                "failed",
                error="Job processing failed",
            )
        except Exception:
            # Если статус сохранить невозможно,
            # возвращаем сообщение в очередь.
            time.sleep(3)
            channel.basic_nack(
                method.delivery_tag,
                requeue=True,
            )
            return

        # Ошибка сохранена в Redis.
        # Автоматических повторов для неё пока нет.
        channel.basic_ack(method.delivery_tag)


def main():
    credentials = pika.PlainCredentials(
        os.environ["RABBITMQ_USER"],
        os.environ["RABBITMQ_PASSWORD"],
    )

    parameters = pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
        credentials=credentials,
        heartbeat=60,
        blocked_connection_timeout=30,
    )

    while True:
        connection = None

        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            channel.queue_declare(
                queue=QUEUE_NAME,
                durable=True,
            )

            channel.basic_qos(prefetch_count=1)

            channel.basic_consume(
                queue=QUEUE_NAME,
                on_message_callback=process_job,
                auto_ack=False,
            )

            print("Analytics worker started", flush=True)

            channel.start_consuming()

        except (pika.exceptions.AMQPError, OSError) as exc:
            print(
                f"RabbitMQ connection error: {exc}",
                flush=True,
            )
            time.sleep(3)

        finally:
            if connection and connection.is_open:
                connection.close()


if __name__ == "__main__":
    main()
