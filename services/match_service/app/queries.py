from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from .database import get_engine
from .models import Match, Team
from .schemas import MatchRead


def get_matches(
    *,
    season: str | None,
    team: str | None,
    limit: int,
    offset: int,
) -> list[MatchRead]:

    statement = select(Match).options(
        joinedload(Match.home_team),
        joinedload(Match.away_team),
    )

    if season is not None:
        statement = statement.where(Match.season == season)

    if team is not None:
        statement = statement.where(
            or_(
                Match.home_team.has(Team.name == team),
                Match.away_team.has(Team.name == team),
            )
        )

    statement = (
        statement
        .order_by(Match.match_date, Match.match_id)
        .offset(offset)
        .limit(limit)
    )

    with Session(get_engine()) as session:
        matches = session.scalars(statement).all()

        return [
            MatchRead(
                match_id=match.match_id,
                season=match.season,
                match_date=match.match_date,
                kickoff_utc=match.kickoff_utc,
                home_team=match.home_team.name,
                away_team=match.away_team.name,
                home_goals=match.home_goals,
                away_goals=match.away_goals,
                home_xg=match.home_xg,
                away_xg=match.away_xg,
                home_shots=match.home_shots,
                away_shots=match.away_shots,
                home_shots_on_target=match.home_shots_on_target,
                away_shots_on_target=match.away_shots_on_target,
            )
            for match in matches
        ]