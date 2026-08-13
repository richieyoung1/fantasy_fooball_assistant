"""Configurable fantasy scoring shared by prediction interfaces."""


DEFAULT_SCORING = {
    "Pass Yards": 0.04,
    "Pass TDs": 4.0,
    "Interceptions": -2.0,
    "Rush Yards": 0.1,
    "Rush TDs": 6.0,
    "Receptions": 0.0,
    "Rec Yards": 0.1,
    "Rec TDs": 6.0,
}

SLIDER_RANGES = {
    "Pass Yards": (0.0, 0.1, 0.01),
    "Pass TDs": (0.0, 8.0, 0.5),
    "Interceptions": (-6.0, 0.0, 0.5),
    "Rush Yards": (0.0, 0.2, 0.01),
    "Rush TDs": (0.0, 10.0, 0.5),
    "Receptions": (0.0, 2.0, 0.1),
    "Rec Yards": (0.0, 0.2, 0.01),
    "Rec TDs": (0.0, 10.0, 0.5),
}


def prediction_column(stat, year=2025):
    return f"Predicted_{stat.replace(' ', '')}_{year}"


def find_prediction_column(columns, stat, year=2025):
    """Match both legacy snake-case and current generated column names."""
    normalized = {"".join(character for character in column.lower() if character.isalnum()): column
                  for column in columns}
    names = [f"predicted{stat.replace(' ', '').lower()}{year}",
             f"predicted{stat.replace(' ', '').lower()}"]
    names.extend(name.replace("yards", "yds") for name in list(names))
    return next((normalized[name] for name in names if name in normalized), None)


def calculate_fantasy_points(frame, scoring, year=2025):
    """Return a Series calculated from every predicted stat present in frame."""
    points = 0.0
    for stat, value in scoring.items():
        column = find_prediction_column(frame.columns, stat, year)
        if column:
            points = points + frame[column].fillna(0) * value
    return points
