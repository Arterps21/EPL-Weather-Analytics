import httpx


MATCH_URL = "http://match-service:8001"
WEATHER_URL = "http://weather-service:8002"


def summarize(group: dict[str, list[float]]) -> dict[str, int | float | None]:
    goals = group["goals"]
    xg = group["xg"]

    return {
        "matches": len(goals),
        "avg_goals": round(sum(goals) / len(goals), 2) if goals else None,
        "avg_xg": round(sum(xg) / len(xg), 2) if xg else None,
    }


def calculate_team_weather(team: str, season: str) -> dict:
    with httpx.Client(timeout=10.0) as client:
        matches_response = client.get(
            f"{MATCH_URL}/matches",
            params={"team": team, "season": season, "limit": 100},
        )
        matches_response.raise_for_status()
        matches = matches_response.json()

        if not matches:
            raise ValueError("No matches found")

        weather_response = client.get(
            f"{WEATHER_URL}/weather/matches",
            params=[("match_id", match["match_id"]) for match in matches],
        )
        weather_response.raise_for_status()
        weather_records = weather_response.json()

    weather_by_id = {
        record["match_id"]: record
        for record in weather_records
    }
    groups = {
        "rain": {"goals": [], "xg": []},
        "dry": {"goals": [], "xg": []},
    }
    missing_weather = 0

    for match in matches:
        weather = weather_by_id.get(match["match_id"])

        if weather is None:
            missing_weather += 1
            continue

        is_home = match["home_team"] == team
        goals = match["home_goals"] if is_home else match["away_goals"]
        xg = match["home_xg"] if is_home else match["away_xg"]
        category = "rain" if weather["is_rain"] else "dry"

        groups[category]["goals"].append(goals)
        if xg is not None:
            groups[category]["xg"].append(xg)

    return {
        "team": team,
        "season": season,
        "matches_total": len(matches),
        "missing_weather": missing_weather,
        "rain": summarize(groups["rain"]),
        "dry": summarize(groups["dry"]),
    }
