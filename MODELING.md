# Prediction model workflow

## Refreshing the data

The season-stat scrapers calculate the latest completed NFL season from the current date. Running both scripts now creates `qb_2025_stats.csv`, `rb_2025_stats.csv`, `wr_2025_stats.csv`, and `te_2025_stats.csv` while retaining the prior seasons:

```bash
python scraping/scrape_qb_multi_year_stats.py
python scraping/scrape_skill_position_stats.py
```

The source site rate-limits automated requests, so keep the configured delay and do not repeatedly run the scrapers. Stat CSVs contain observed results; files named `*_predictions.csv` are projections and must never be used as observed 2025 labels.

## Training and tuning

Install `pandas`, `numpy`, `scikit-learn`, and `joblib`, then run:

```bash
python models/train_next_season_models.py
```

The trainer automatically discovers every `POSITION_YEAR_stats.csv`, including 2025 when present. It:

1. Adds per-game, workload, efficiency, rate, and touch-distribution features.
2. Only pairs genuinely consecutive seasons; a 2023 row is not paired directly with 2025 when 2024 is absent.
3. Holds out the latest target season as a chronological backtest.
4. Tunes gradient boosting tree count, learning rate, depth, leaf size, and subsampling with season-grouped cross-validation.
5. Prints MSE and R² for every position/stat model and writes MSE, MAE, R², row counts, and chosen parameters to `models/model_metrics.csv`.
6. Refits the selected configuration on all available consecutive-season pairs and saves both the model and its feature/metric metadata.

Use `--positions QB WR`, for example, to train only selected positions.

## Custom fantasy scoring

Run `python app/view_2025_predictions.py`. The scoring panel has sliders for passing yards, passing touchdowns, interceptions, rushing yards, rushing touchdowns, receptions, receiving yards, and receiving touchdowns. Changing any slider immediately recalculates the custom fantasy-points column without rerunning the statistical models.

## Remaining limitations

- A season-level dataset is small; tuning results can be unstable, especially for touchdowns.
- Players must have a row in consecutive seasons. Players who retire or miss a full year do not become explicit zero-stat examples, creating survivor bias.
- The models do not know depth-chart changes, injuries, contracts, rookies, coaching changes, offensive line quality, betting totals, or team play volume.
- Each output is modeled independently, so the collection of predicted stats is not guaranteed to describe an internally consistent stat line.
- Point estimates do not communicate floor, ceiling, or uncertainty.
- Player names are used as the join key; stable player IDs would handle duplicates and name changes more safely.
- The newest-season holdout is more realistic than a random split, but rolling-origin backtests across several seasons would provide a more reliable assessment.
- Missing inputs are still handled simply. A fitted preprocessing pipeline with explicit imputation would be safer for production use.
- Hyperparameter search improves the comparison among the tested Gradient Boosting configurations; it does not establish that Gradient Boosting is better than random forests, XGBoost/LightGBM, regularized linear baselines, or multi-output models.
