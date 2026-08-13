"""Shared feature definitions for next-season model training and inference."""

import numpy as np


BASE_FEATURES = {
    "QB": ["Age", "Games", "Completions", "Pass Atts", "Pass Yards", "Pass TDs",
           "Interceptions", "Passer Rating", "Rush Atts", "Rush Yards", "Rush TDs"],
    "RB": ["Age", "Games", "GS", "Rush Atts", "Rush Yards", "Rush TDs", "Targets",
           "Receptions", "Rec Yards", "Rec TDs"],
    "WR": ["Age", "Games", "GS", "Targets", "Receptions", "Rec Yards", "Rec TDs"],
    "TE": ["Age", "Games", "GS", "Targets", "Receptions", "Rec Yards", "Rec TDs"],
}

TARGETS = {
    "QB": ["Pass Yards", "Pass TDs", "Interceptions", "Rush Yards", "Rush TDs", "Games"],
    "RB": ["Rush Yards", "Rush TDs", "Rec Yards", "Rec TDs", "Receptions", "Games"],
    "WR": ["Rec Yards", "Rec TDs", "Receptions", "Games"],
    "TE": ["Rec Yards", "Rec TDs", "Receptions", "Games"],
}


def add_derived_features(df, position):
    """Add workload and efficiency features that are available at prediction time."""
    df = df.copy()
    original_columns = set(df.columns)
    games = df["Games"].replace(0, np.nan)
    starts = df.get("GS", df.get("Games Started", 0))
    df["Start Rate"] = starts / games

    if position == "QB":
        attempts = df["Pass Atts"].replace(0, np.nan)
        completions = df["Completions"].replace(0, np.nan)
        df["Pass Atts Per Game"] = df["Pass Atts"] / games
        df["Pass Yards Per Game"] = df["Pass Yards"] / games
        df["Pass Yards Per Attempt"] = df["Pass Yards"] / attempts
        df["Completion Rate"] = df["Completions"] / attempts
        df["Pass TD Rate"] = df["Pass TDs"] / attempts
        df["Interception Rate"] = df["Interceptions"] / attempts
        df["Rush Atts Per Game"] = df["Rush Atts"] / games
        df["Rush Yards Per Attempt"] = df["Rush Yards"] / df["Rush Atts"].replace(0, np.nan)
        df["Rush Share Of Touches"] = df["Rush Atts"] / (df["Rush Atts"] + attempts)
        df["Completions Per Game"] = completions / games
    else:
        touches = df.get("Rush Atts", 0) + df["Targets"]
        df["Targets Per Game"] = df["Targets"] / games
        df["Receptions Per Game"] = df["Receptions"] / games
        df["Catch Rate"] = df["Receptions"] / df["Targets"].replace(0, np.nan)
        df["Rec Yards Per Target"] = df["Rec Yards"] / df["Targets"].replace(0, np.nan)
        df["Rec Yards Per Reception"] = df["Rec Yards"] / df["Receptions"].replace(0, np.nan)
        df["Rec TD Rate"] = df["Rec TDs"] / df["Targets"].replace(0, np.nan)
        df["Touches Per Game"] = touches / games
        if position == "RB":
            df["Rush Atts Per Game"] = df["Rush Atts"] / games
            df["Rush Yards Per Attempt"] = df["Rush Yards"] / df["Rush Atts"].replace(0, np.nan)
            df["Rush TD Rate"] = df["Rush TDs"] / df["Rush Atts"].replace(0, np.nan)
            df["Target Share Of Touches"] = df["Targets"] / touches.replace(0, np.nan)

    df = df.replace([np.inf, -np.inf], np.nan)
    derived = [column for column in df.columns if column not in original_columns]
    df[derived] = df[derived].fillna(0)
    return df


def model_features(position, sample_df):
    """Return the stable ordered feature list after derived features are added."""
    return [column for column in sample_df.columns if column in BASE_FEATURES[position] or column in {
        "Start Rate", "Pass Atts Per Game", "Pass Yards Per Game", "Pass Yards Per Attempt",
        "Completion Rate", "Pass TD Rate", "Interception Rate", "Rush Atts Per Game",
        "Rush Yards Per Attempt", "Rush Share Of Touches", "Completions Per Game",
        "Targets Per Game", "Receptions Per Game", "Catch Rate", "Rec Yards Per Target",
        "Rec Yards Per Reception", "Rec TD Rate", "Touches Per Game", "Rush TD Rate",
        "Target Share Of Touches",
    }]
