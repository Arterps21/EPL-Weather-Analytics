from typing import Annotated

from fastapi import APIRouter, Query

from .queries import get_matches
from .schemas import MatchRead


router = APIRouter(
    prefix="/matches",
    tags=["matches"],
)


@router.get("", response_model=list[MatchRead])
def list_matches(
    season: Annotated[
        str | None,
        Query(pattern=r"^\d{4}/\d{2}$"),
    ] = None,

    team: Annotated[
        str | None,
        Query(min_length=2, max_length=100),
    ] = None,

    limit: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,

    offset: Annotated[
        int,
        Query(ge=0, le=100000),
    ] = 0,
) -> list[MatchRead]:

    return get_matches(
        season=season,
        team=team,
        limit=limit,
        offset=offset,
    )