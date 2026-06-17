# CascadeIQ — AGENTS.md

## Project structure

```
app.py          Streamlit dashboard entrypoint (7 modules)
train.py        End-to-end training pipeline (8 steps)
src/            ML modules: feature_engineering, models, hotspot_detection,
                vulnerability, similarity, resources, cascade_autopsy
data/           dataset.csv (8173 events), junction_vulnerability.csv
models/         6 .pkl artifacts + metrics.json (loaded at app startup)
```

No tests, no CI, no lint/format/typecheck tooling.

## Commands

```bash
poetry install                              # install deps (Python >=3.10,<3.12)
poetry run python train.py                  # train all models
poetry run streamlit run app.py             # launch dashboard
pip install -r requirements.txt             # pip alternative (venv recommended)
```

## Architecture notes

- **Time-aware split**: train.py uses chronological 80/20 split (not random).
- **Resolution regressor** predicts in log space (`np.log1p` / `np.expm1`).
- **Impact target** is rule-based (computed in `feature_engineering.py:create_impact_target`, not in data).
- **Cascade target**: resolution > 75th percentile AND impact >= 2.
- **29 engineered features**: cyclical time encoding, label encoding, target encoding (groupby means/counts).
- **Feature engineering must be trained first**: `engineer_features(df, is_train=True)` returns encoders used for inference.
- **scikit-learn pinned `<1.5`** in pyproject.toml (label encoder compatibility).
- **Joblib for models**, pickle for similarity/hotspots.
- `shap` and `matplotlib` in deps but not used in code.
- Resources module has in-memory `RESOURCE_HISTORY` (session-only, does not persist).

## Data conventions

- String columns normalized in `feature_engineering.py`: lowercased, stripped, fillna('unknown').
- Junctions additionally have spaces removed (`str.replace(' ', '')`).
- `engineer_features(inference)` maps unseen categories to -1 via LabelEncoder.
