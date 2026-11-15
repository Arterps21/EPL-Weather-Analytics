from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from .models import MatchWeather
from .queries import get_weather_batch, get_weather_by_match
from .schemas import WeatherRead


router = APIRouter(
    prefix="/weather/matches",
    tags=["weather"],
)


@router.get("", response_model=list[WeatherRead])
def list_weather(
    match_ids: Annotated[
        list[str],
        Query(
            alias="match_id",
            min_length=1,
            max_length=100,
        ),
    ],
) -> list[MatchWeather]:
    return get_weather_batch(match_ids)


@router.get("/{match_id}", response_model=WeatherRead)
def get_weather(match_id: str) -> MatchWeather:
    weather = get_weather_by_match(match_id)

    if weather is None:
        raise HTTPException(
            status_code=404,
            detail="Weather not found",
        )

    return weather