import csv
import sys

from datetime import date, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_engine
from .models import Team, Match


def required(row: dict, field: str) -> str:
    value = (row.get(field) or "").strip()

    if not value:
        raise ValueError(f"Missing required field: {field}")

    return value


def optional_int(value: str | None) -> int | None:
    return int(value) if value and value.strip() else None


def optional_float(value: str | None) -> float | None:
    return float(value) if value and value.strip() else None


def import_matches(csv_path: Path) -> None:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise ValueError("CSV is empty")

    team_names = {
        required(row, field)
        for row in rows
        for field in ("home_team", "away_team")
    }

    inserted = 0
    skipped = 0
    created_teams = 0

    with Session(get_engine()) as session:
        with session.begin():

            # Загружаем уже существующие команды.
            teams = {
                team.name: team
                for team in session.scalars(select(Team)).all()
            }

            # Создаём только отсутствующие команды.
            for name in sorted(team_names):
                if name not in teams:
                    team = Team(name=name)
                    session.add(team)
                    teams[name] = team
                    created_teams += 1

            # Получаем ID созданных команд.
            session.flush()

            # Запоминаем уже импортированные матчи.
            existing_ids = set(
                session.scalars(select(Match.match_id)).all()
            )

            for line_number, row in enumerate(rows, start=2):
                try:
                    match_id = required(row, "match_id")

                    if match_id in existing_ids:
                        skipped += 1
                        continue

                    kickoff_value = (
                        row.get("kickoff_utc") or ""
                    ).strip()

                    kickoff = (
                        datetime.fromisoformat(kickoff_value)
                        if kickoff_value
                        else None
                    )

                    if kickoff is not None and kickoff.utcoffset() is None:
                        raise ValueError("kickoff_utc must have a timezone")

                    match = Match(
                        match_id=match_id,
                        season=required(row, "season"),
                        match_date=date.fromisoformat(
                            required(row, "date")
                        ),
                        kickoff_utc=kickoff,

                        home_team_id=teams[
                            required(row, "home_team")
                        ].id,

                        away_team_id=teams[
                            required(row, "away_team")
                        ].id,

                        stadium_name=row.get("stadium_name") or None,

                        home_goals=int(required(row, "home_goals")),
                        away_goals=int(required(row, "away_goals")),

                        home_xg=optional_float(row.get("home_xg")),
                        away_xg=optional_float(row.get("away_xg")),

                        home_shots=optional_int(row.get("home_shots")),
                        away_shots=optional_int(row.get("away_shots")),

                        home_shots_on_target=optional_int(
                            row.get("home_shots_on_target")
                        ),
                        away_shots_on_target=optional_int(
                            row.get("away_shots_on_target")
                        ),
                    )

                    session.add(match)
                    existing_ids.add(match_id)
                    inserted += 1

                except (ValueError, KeyError) as exc:
                    raise ValueError(
                        f"CSV line {line_number}: {exc}"
                    ) from exc

    print(f"Teams created: {created_teams}")
    print(f"Matches inserted: {inserted}")
    print(f"Matches skipped: {skipped}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python -m app.import_matches <csv_path>"
        )

    import_matches(Path(sys.argv[1]))