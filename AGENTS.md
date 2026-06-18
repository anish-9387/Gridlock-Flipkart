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

## Domino Labs UI Rules

### 1. Streamlit First
This is a Streamlit application. Do NOT treat it like Next.js, React, Tailwind, Framer, or a custom frontend. Work WITH Streamlit. Do NOT fight Streamlit.

### 2. One CSS Injection Method Only
Use exactly ONE method across the entire project: `st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)`. Do NOT use: SVG style injection, Base64 stylesheet injection, iframe tricks, HTML wrappers, embedded CSS in images, or alternate CSS delivery systems. If CSS injection breaks: STOP. Fix injection first. Do not continue styling.

### 3. Never Print CSS
Before every commit verify: CSS is not visible on screen, CSS is not rendered as text, no style content appears in page body. If CSS text is visible: STOP. Fix that issue before making any design changes.

### 4. No Emotion Cache Classes
Never target `.st-emotion-cache-*` or `.css-*`. Only use: data-testid selectors, Streamlit component selectors, or custom classes we create ourselves.

### 5. No nth-child Hacks
Never use `:nth-child(...)` or `:nth-of-type(...)` for navigation structure. Never create sidebar sections through CSS. Create section headers in Python, then style them with CSS.

### 6. No Fake UI Through CSS
Do not create application structure via `content: "..."`. All structure must exist in Python. CSS should only style, never create application structure.

### 7. No Layout Hacks
Avoid `position: absolute`, `position: fixed`, `transform`, and negative margins unless absolutely necessary. Use Streamlit layouts (columns, containers).

### 8. No Aggressive Plotly Styling
Never style Plotly containers with `overflow: hidden`, fixed heights, or absolute positioning. Do not force chart dimensions. Let Plotly remain responsive. Cards wrap charts. Charts do not wrap cards.

### 9. No Column Selectors
Avoid `div[data-testid="column"]:has(...)` — this is fragile. Instead, create explicit wrapper classes like `chart-card`, `metric-card`, `table-card` and style those.

### 10. Use Reusable Components
Create reusable classes: `.metric-card`, `.chart-card`, `.table-card`, `.page-header`, `.sidebar-section`. Avoid huge one-off selectors.

### 11. CSS File Structure
Keep exactly: ui/assets/logo.svg, ui/styles/base.py, ui/styles/sidebar.py, ui/styles/cards.py. Do not create more style files unless necessary. Typography belongs in base.py.

### 12. Keep CSS Small
Target: base.py <= 150 lines, sidebar.py <= 150 lines, cards.py <= 200 lines. Avoid CSS bloat. Prefer clarity.

### 13. Build UI In Passes
Never redesign everything simultaneously. Work in this order: Pass 1 Typography, Pass 2 Sidebar, Pass 3 Metric cards, Pass 4 Chart cards, Pass 5 Tables, Pass 6 Spacing & polish. Finish one layer before moving to the next.

### 14. Verify Before Every UI Change
Before declaring a UI task complete, verify: CSS is loading correctly, no CSS text visible, no graph clipping, no overflow issues, no broken sidebar, no duplicated headings, no broken logo sizing, no functionality changed.

### 15. Never Touch Business Logic
UI work must never modify: data loading, ML code, models, predictions, routing, calculations, page logic. Only presentation.

### 16. If Something Breaks
Do not redesign further. First identify: what broke, which file caused it, why it broke. Then fix the root cause. Only continue styling after the foundation works again.
