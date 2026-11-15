from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Identity,
    Integer,
    SmallInteger,
    String,
    Text,
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )


class Match(Base):
    __tablename__ = "matches"

    match_id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
    )

    season: Mapped[str] = mapped_column(String(20))
    match_date: Mapped[date] = mapped_column(Date)

    kickoff_utc: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    home_team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id")
    )

    away_team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id")
    )

    stadium_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    home_goals: Mapped[int] = mapped_column(SmallInteger)
    away_goals: Mapped[int] = mapped_column(SmallInteger)

    home_xg: Mapped[float | None] = mapped_column(
        Float(53),
        nullable=True,
    )

    away_xg: Mapped[float | None] = mapped_column(
        Float(53),
        nullable=True,
    )

    home_shots: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
    )

    away_shots: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
    )

    home_shots_on_target: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
    )

    away_shots_on_target: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
    )

    home_team: Mapped[Team] = relationship(
        foreign_keys=[home_team_id]
    )

    away_team: Mapped[Team] = relationship(
        foreign_keys=[away_team_id]
    )