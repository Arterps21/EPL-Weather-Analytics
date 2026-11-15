import csv
import math
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_engine
from .models import MatchWeather


def parse_float(row: dict, field: str) -> float:
    value = float(row[field])

    if not math.isfinite(value):
        raise ValueError(f"Invalid value in {field}")

    return value


def import_weather(csv_path: Path) -> None:
    inserted = 0
    skipped = 0

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        with Session(get_engine()) as session:
            with session.begin():

                existing_ids = set(
                    session.scalars(
                        select(MatchWeather.match_id)
                    ).all()
                )

                for row in csv.DictReader(file):
                    match_id = row["match_id"].strip()

                    if match_id in existing_ids:
                        skipped += 1
                        continue

                    weather_code = parse_float(row, "weather_code")

                    if not weather_code.is_integer():
                        raise ValueError("Invalid weather_code")

                    rain_value = row["is_rain"].strip().lower()

                    if rain_value not in ("true", "false"):
                        raise ValueError("Invalid is_rain")

                    precipitation = row["precipitation_mm"].strip()

                    weather = MatchWeather(
                        match_id=match_id,
                        temperature_c=parse_float(row, "temperature_c"),
                        relative_humidity=parse_float(row, "relative_humidity"),
                        precipitation_mm=(
                            float(precipitation) if precipitation else None
                        ),
                        rain_mm=parse_float(row, "rain_mm"),
                        wind_speed=parse_float(row, "wind_speed"),
                        wind_gust=parse_float(row, "wind_gust"),
                        weather_code=int(weather_code),
                        is_rain=(rain_value == "true"),
                        weather_status=row["weather_status"].strip() or None,
                    )

                    session.add(weather)
                    existing_ids.add(match_id)
                    inserted += 1

    print(f"Weather records inserted: {inserted}")
    print(f"Weather records skipped: {skipped}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python -m app.import_weather <csv_path>"
        )

    import_weather(Path(sys.argv[1]))