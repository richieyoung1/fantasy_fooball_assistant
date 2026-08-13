import pandas as pd
import joblib
import os
import numpy as np
import json

from feature_engineering import add_derived_features

POSITIONS = ['QB', 'RB', 'WR', 'TE']
DATA_YEAR_FOR_PREDICTION = 2024
PREDICT_YEAR = DATA_YEAR_FOR_PREDICTION + 1
MODEL_OUTPUT_DIR = "models"

FANTASY_RULES = {
    "QB": dict(pass_yd=0.04, pass_td=4, int_pts=-2, rush_yd=0.1, rush_td=6),
    "RB": dict(rush_yd=0.1, rush_td=6, rec_yd=0.1, rec_td=6, rec=0),  # update if using PPR
    "WR": dict(rec_yd=0.1, rec_td=6, rec=0),
    "TE": dict(rec_yd=0.1, rec_td=6, rec=0)
}

POSITION_CONFIGS = {
    "QB": {
        "raw_features": ['Age', 'Games', 'Completions', 'Pass Atts', 'Pass Yards', 'Pass TDs', 'Interceptions',
                         'Passer Rating', 'Rush Atts', 'Rush Yards', 'Rush TDs'],
        "stats_to_predict": ['Pass Yards', 'Pass TDs', 'Interceptions', 'Rush Yards', 'Rush TDs', 'Games'],
    },
    "RB": {
        "raw_features": ['Age', 'Games', 'GS', 'Rush Atts', 'Rush Yards', 'Rush TDs', 'Targets',
                         'Receptions', 'Rec Yards', 'Rec TDs'],
        "stats_to_predict": ['Rush Yards', 'Rush TDs', 'Rec Yards', 'Rec TDs', 'Receptions', 'Games']
    },
    "WR": {
        "raw_features": ['Age', 'Games', 'GS', 'Targets', 'Receptions', 'Rec Yards', 'Rec TDs'],
        "stats_to_predict": ['Rec Yards', 'Rec TDs', 'Receptions', 'Games']
    },
    "TE": {
        "raw_features": ['Age', 'Games', 'GS', 'Targets', 'Receptions', 'Rec Yards', 'Rec TDs'],
        "stats_to_predict": ['Rec Yards', 'Rec TDs', 'Receptions', 'Games']
    }
}

for pos in POSITIONS:
    print(f"\n===== Predicting {PREDICT_YEAR} Stats for {pos} =====")

    config = POSITION_CONFIGS[pos]
    raw_features = config["raw_features"]
    stats_to_predict = config["stats_to_predict"]
    model_features = [f"{f}_N" for f in raw_features]
    fantasy_rules = FANTASY_RULES[pos]

    data_file = f"{pos.lower()}_{DATA_YEAR_FOR_PREDICTION}_stats.csv"
    output_file = f"{pos.lower()}_{PREDICT_YEAR}_predictions.csv"

    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        continue

    df = pd.read_csv(data_file)

    # Attempt to handle Games column
    if 'Games' not in df.columns and 'G' in df.columns:
        df.rename(columns={'G': 'Games'}, inplace=True)

    # Clean and numeric conversion
    for col in raw_features:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            df[col] = 0

    df = df.dropna(subset=['Age'])

    # Rename features
    rename_map = {col: f"{col}_N" for col in raw_features}
    df_model = df.rename(columns=rename_map)
    X = df_model[model_features]

    if X.empty:
        print("❌ No valid data for prediction.")
        continue

    # Load models
    predictions_df = pd.DataFrame(index=df.index)
    for stat in stats_to_predict:
        model_path = os.path.join(MODEL_OUTPUT_DIR, f"{pos.lower()}_predictive_{stat.lower().replace(' ', '_')}_model.pkl")
        if not os.path.exists(model_path):
            print(f"❌ Missing model: {model_path}")
            predictions_df[f'Predicted_{stat.replace(" ", "")}_{PREDICT_YEAR}'] = 0
            continue

        model = joblib.load(model_path)
        metadata_path = model_path.replace("_model.pkl", "_metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, encoding="utf-8") as metadata_file:
                feature_names = json.load(metadata_file)["features"]
            enriched = add_derived_features(df, pos)
            X_for_model = enriched[feature_names]
        else:
            X_for_model = X
        y_pred = model.predict(X_for_model)
        if stat == 'Games':
            y_pred = np.clip(np.round(y_pred), 0, 17).astype(int)
        elif 'TD' in stat or stat == 'Interceptions':
            y_pred = np.round(y_pred).astype(int)
        y_pred = np.where(y_pred < 0, 0, y_pred)
        predictions_df[f'Predicted_{stat.replace(" ", "")}_{PREDICT_YEAR}'] = y_pred

    # Fantasy calculation
    print("Calculating fantasy points...")
    fpts = 0
    if pos == "QB":
        fpts += predictions_df.get(f'Predicted_PassYards_{PREDICT_YEAR}', 0) * fantasy_rules['pass_yd']
        fpts += predictions_df.get(f'Predicted_PassTDs_{PREDICT_YEAR}', 0) * fantasy_rules['pass_td']
        fpts += predictions_df.get(f'Predicted_Interceptions_{PREDICT_YEAR}', 0) * fantasy_rules['int_pts']
        fpts += predictions_df.get(f'Predicted_RushYards_{PREDICT_YEAR}', 0) * fantasy_rules['rush_yd']
        fpts += predictions_df.get(f'Predicted_RushTDs_{PREDICT_YEAR}', 0) * fantasy_rules['rush_td']
    else:
        fpts += predictions_df.get(f'Predicted_RecYards_{PREDICT_YEAR}', 0) * fantasy_rules.get('rec_yd', 0)
        fpts += predictions_df.get(f'Predicted_RecTDs_{PREDICT_YEAR}', 0) * fantasy_rules.get('rec_td', 0)
        fpts += predictions_df.get(f'Predicted_Receptions_{PREDICT_YEAR}', 0) * fantasy_rules.get('rec', 0)
        fpts += predictions_df.get(f'Predicted_RushYards_{PREDICT_YEAR}', 0) * fantasy_rules.get('rush_yd', 0)
        fpts += predictions_df.get(f'Predicted_RushTDs_{PREDICT_YEAR}', 0) * fantasy_rules.get('rush_td', 0)
    predictions_df[f'PredictedFantasyPts_{PREDICT_YEAR}'] = fpts

    # Merge and output
    df_output = pd.concat([df, predictions_df], axis=1)
    df_output.rename(columns={'Age': f'Age_{DATA_YEAR_FOR_PREDICTION}'}, inplace=True)
    df_output.sort_values(by=f'PredictedFantasyPts_{PREDICT_YEAR}', ascending=False, inplace=True)

    df_output.to_csv(output_file, index=False)
    print(f"✅ Saved predictions to {output_file}")
