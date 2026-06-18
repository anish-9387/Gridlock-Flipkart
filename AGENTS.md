# CascadeIQ — AGENTS.md

## Project structure

```
app.py          Streamlit dashboard (14 pages); loads saved artifacts, never refits for serving
train.py        Training pipeline: split → fit-on-train (honest eval) → refit-all → save
src/            ML + intelligence modules (see README "Project structure")
data/           dataset.csv (8173 events), junction_vulnerability.csv, junction_centrality.csv
models/         impact/cascade/prolonged classifiers, resolution_regressor (AFT .ubj),
                cascade_calibrator, encoders.pkl, network.pkl, metrics.json
```

No tests beyond the Streamlit AppTest smoke-check (below). No CI/lint tooling.

## Commands

```bash
pip install -r requirements.txt
python train.py                     # retrain all models + write metrics.json
streamlit run app.py                # launch dashboard
# headless validation of all 14 pages:
python -c "from streamlit.testing.v1 import AppTest; \
  a=AppTest.from_file('app.py',default_timeout=180).run(); print('ok' if not a.exception else a.exception)"
```

## Architecture notes (post-v2 rewrite)

- **Leakage-safe by construction.** `train.py` does a chronological split BEFORE fitting.
  `engineer_features(df, is_train=True)` fits encoders/scaler; `is_train=False` transforms
  with passed-in `encoders`. App loads `models/encoders.pkl` (fit on full data) for serving —
  it does NOT refit. `status` is intentionally excluded from features (outcome leak).
- **Unified feature API:** `engineer_features(...) -> (X, targets_dict, encoders, feature_cols)`
  for BOTH train and inference (consistent arity). `targets_dict` keys: resolution_minutes,
  reliable, y_lower, y_upper, impact_level, duration_band, prolonged, cascade, sample_weight.
- **Targets:** impact = composite severity index (cause prior + priority + closure + peak +
  corridor, nudged by duration where reliable). resolution = AFT survival with interval-
  censored admin-closes (`y_lower`/`y_upper`). cascade = high-impact AND long-run.
- **Models:** AFT resolution is an `xgboost.Booster` (saved as `.ubj` + a `.pkl` pointer);
  classifiers are `XGBClassifier`. `models.load_model` handles both. Cascade probabilities go
  through `predict_cascade_proba(model, calibrator, X)` (isotonic).
- **Resolution display:** raw AFT is noisy for rare causes → `display_resolution()` shrinks
  toward the cause's historical prior (used everywhere user-facing, NOT in metrics).
- **Network:** `network.py` builds a NetworkX junction graph (kNN + shared-corridor edges);
  `centrality_feature_map` feeds 3 features into the models; also powers propagation,
  percolation early-warning, and diversion. `cmap` is stored inside `encoders.pkl`.
- **SHAP:** `models.explain_prediction` uses XGBoost native `pred_contribs` (no `shap` import
  needed at inference); `shap` lib is only an optional extra.

## Conventions

- String cats normalised in `feature_engineering._normalize_cats` (lower/strip/fillna 'unknown';
  junctions also strip spaces). Unseen categories → encoded as -1, target-enc → global mean.
- Metrics in `models/metrics.json` are the chronological held-out numbers (honest). The Model
  Card page renders them. Don't replace them with in-sample numbers.
- `data/predictions_log.csv` is a runtime store (gitignored); the Post-Event page seeds it
  from history on demand.
