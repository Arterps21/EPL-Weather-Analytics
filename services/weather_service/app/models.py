from sqlalchemy import (
    Boolean,
    Float,
    SmallInteger,
    String,
    Text,
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


class Base(DeclarativeBase):
    pass


class MatchWeather(Base):
    __tablename__ = "match_weather"

    match_id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
    )

    temperature_c: Mapped[float] = mapped_column(Float(53))
    relative_humidity: Mapped[float] = mapped_column(Float(53))

    precipitation_mm: Mapped[float | None] = mapped_column(
        Float(53),
        nullable=True,
    )

    rain_mm: Mapped[float] = mapped_column(Float(53))
    wind_speed: Mapped[float] = mapped_column(Float(53))
    wind_gust: Mapped[float] = mapped_column(Float(53))

    weather_code: Mapped[int] = mapped_column(SmallInteger)
    is_rain: Mapped[bool] = mapped_column(Boolean)

    weather_status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )