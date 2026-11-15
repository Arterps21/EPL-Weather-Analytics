from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_engine
from .models import MatchWeather


def get_weather_by_match(match_id: str) -> MatchWeather | None:
    with Session(get_engine()) as session:
        return session.get(MatchWeather, match_id)


def get_weather_batch(match_ids: list[str]) -> list[MatchWeather]:
    with Session(get_engine()) as session:
        statement = select(MatchWeather).where(
            MatchWeather.match_id.in_(match_ids)
        )

        records = session.scalars(statement).all()

        weather_by_id = {
            record.match_id: record
            for record in records
        }

        return [
            weather_by_id[match_id]
            for match_id in dict.fromkeys(match_ids)
            if match_id in weather_by_id
        ]