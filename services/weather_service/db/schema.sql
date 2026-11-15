CREATE TABLE IF NOT EXISTS match_weather (
    match_id TEXT PRIMARY KEY,

    temperature_c DOUBLE PRECISION NOT NULL,
    relative_humidity DOUBLE PRECISION NOT NULL,

    precipitation_mm DOUBLE PRECISION,
    rain_mm DOUBLE PRECISION NOT NULL,

    wind_speed DOUBLE PRECISION NOT NULL,
    wind_gust DOUBLE PRECISION NOT NULL,

    weather_code SMALLINT NOT NULL,
    is_rain BOOLEAN NOT NULL,

    weather_status VARCHAR(30),

    CONSTRAINT valid_humidity
        CHECK (relative_humidity BETWEEN 0 AND 100),

    CONSTRAINT non_negative_weather
        CHECK (
            (precipitation_mm IS NULL OR precipitation_mm >= 0)
            AND rain_mm >= 0
            AND wind_speed >= 0
            AND wind_gust >= 0
        )
);