from pydantic import BaseModel, ConfigDict


class WeatherRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    match_id: str

    temperature_c: float
    relative_humidity: float

    precipitation_mm: float | None
    rain_mm: float

    wind_speed: float
    wind_gust: float

    weather_code: int
    is_rain: bool
    weather_status: str | None