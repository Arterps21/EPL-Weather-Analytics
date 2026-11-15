from datetime import date, datetime

from pydantic import BaseModel


class MatchRead(BaseModel):
    match_id: str
    season: str
    match_date: date
    kickoff_utc: datetime | None

    home_team: str
    away_team: str

    home_goals: int
    away_goals: int

    home_xg: float | None
    away_xg: float | None

    home_shots: int | None
    away_shots: int | None

    home_shots_on_target: int | None
    away_shots_on_target: int | None