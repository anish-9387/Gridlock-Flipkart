<p align="center">
  <img src="assets/wordmark.png" width="280" alt="Rippl logo"/>
</p>

<p align="center">
  <strong>Predicting the impact of what happens next.</strong><br/>
  Gridlock × Flipkart 2.0 Hackathon &nbsp;·&nbsp; Theme 2: Event-Driven Congestion
</p>

---

> **Cities don't fail because of events. They fail because of cascades.**
>
> Rippl predicts how disruptions spread, how much time authorities have before escalation,
> and the exact decision window where intervention could have prevented city-wide failure —
> learned from **8,173 historical Bengaluru traffic events**.

---

## What this looks like in practice

A water logging event is reported in Bengaluru. Rippl flags it as Critical impact with a 76% cascade probability and a 07:18 Point of No Return — meaning authorities have a 10-minute window to act. The Cascade Autopsy module then shows that lifting the road closure would have cut cascade risk from 76% to 4% and extended Time-To-Failure from 24 minutes to 62 minutes. That's the difference between a managed disruption and a gridlock.

**→ [Screenshot: Cascade Autopsy — water logging event, Critical → Medium, 76% → 4% cascade risk]**

---

## Why this project is different

Most teams build an "event → congestion" classifier. Rippl models the real chain —
**event → local disruption → network stress → junction overload → spillback → escalation → gridlock** —
and is engineered for honesty and correctness, not just a headline accuracy number.

- A **survival model** that handles censored resolution times instead of trusting corrupt administrative timestamps.
- A **calibrated** cascade-risk model whose probabilities are trustworthy (Brier 0.24 → 0.038).
- A **road-network graph** with betweenness-centrality fragility and a percolation cascade tracker.
- A **leakage-free** evaluation with a Model Card that states the limits up front.

---

## Quickstart

```bash
pip install -r requirements.txt        # Python >= 3.10
python train.py                        # build network, train models, write metrics
cd frontend && pnpm install && pnpm dev # launch the dashboard
```

Poetry also works:

```bash
poetry install && poetry run python train.py
cd frontend && pnpm install && pnpm dev
```

> **Reproducibility note:** all encoders and scalers are fit on the training slice only. Running `train.py` on a fresh clone produces the same `models/metrics.json` within floating-point tolerance.

---

## Model performance

All metrics use a time-aware split (train Nov 2023 → Mar 2024, test Mar → Apr 2024).
Encoders are fit on training data only. The `status` column is excluded — it leaks the outcome.

| Model | Task | Technique | Result |
|---|---|---|---|
| Cascade Classifier | Will it escalate? | XGBoost + isotonic calibration | ROC-AUC 0.91, PR-AUC 0.64 (vs 0.08 base rate), Brier 0.038 |
| Impact Classifier | Severity (Low → Critical) | XGBoost, composite-severity label | 71.3% acc (vs 55.8% baseline), macro-F1 0.62 |
| AFT Resolution | How long? | XGBoost `survival:aft` (censoring-aware) | MedAE 60 min on reliable events |
| Prolonged (>60 min) | Quick vs long | XGBoost binary | in-dist AUC ~0.61 *(intrinsically weak — see limitations)* |

### Why the numbers are trustworthy (and what we fixed)

The raw dataset has two traps that inflate naive scores:

**1. Censored resolution times.** Only ~74 events have a real `resolved_datetime`. The rest fall back to `closed_datetime`, an administrative close (90th percentile ≈ 11.6 days). Rather than trust or discard these, the AFT model treats admin-closes as interval-censored and still-active events as right-censored — the principled survival-analysis approach.

**2. Leakage.** The split happens before any fitting. Label encoders, smoothed target encodings, and the scaler see training data only.

The dashboard's Model Card page renders all of this live, including the cascade confusion matrix and the calibration curve.

---

## Signature features

**Cascade Autopsy** — the standout module. Feed it any historical event and it quantifies how much escalation was preventable — by lifting a road closure, shifting the event off-peak, or both. It marks the Point of No Return: the exact timestep after which no intervention could have stopped gridlock. No other team in this space is doing counterfactual analysis at this level.

**Time-To-Failure (TTF)** — minutes until escalation, derived from cascade probability, severity, and junction fragility. Gives operators a concrete number to act on rather than an abstract risk score.

**Network Propagation Engine** — a data-derived road graph (NetworkX, 294 junctions), betweenness-centrality fragility scoring, a threshold/SIR cascade spread simulation, and a percolation connected-components tracker. The peak-cluster timestep from the percolation tracker is the published precursor to network collapse.

**Post-Event Learning loop** — predictions are stored, matched to outcomes, and scored over time. Closes the gap the brief identified: no existing post-event learning system.

**Explainability** — exact tree-SHAP per prediction via XGBoost's native `pred_contribs`. No extra dependency. Surfaced as a driver waterfall so operators can see exactly why a risk score is high.

---

## Dashboard modules

| # | Page | What it does |
|---|------|--------------|
| 1 | Dashboard Overview | KPIs, distributions, time series, fragility leaderboard |
| 2 | Event Impact Prediction | Impact + calibrated cascade % + TTF + tree-SHAP waterfall |
| 3 | Early Warning System | Pre-event 0–100 risk index, deployment lead time, city-wide percolation risk |
| 4 | Network Propagation | Cascade spread animation, betweenness fragility, collapse curve, diversion routing |
| 5 | Cascade Autopsy | Counterfactual levers → preventable share + Point of No Return |
| 6 | Traffic Black Box | Event reconstruction, root-cause analysis, avoidable-delay accounting |
| 7 | Junction Vulnerability | Fragility index (centrality-based) |
| 8 | Hotspot Analysis | DBSCAN spatial clusters by cause |
| 9 | Event Similarity Search | TF-IDF top-5 historical matches |
| 10 | Resource Recommendation | Officers / barricades / monitoring / diversion |
| 11 | Digital Twin Simulator | Side-by-side what-if scenario comparison |
| 12 | Knowledge Graph | Multi-dimensional event relationship graph |
| 13 | Post-Event Learning | Prediction-vs-actual log, calibration curve, accuracy drift |
| 14 | Model Card | Held-out metrics, methodology, and stated limitations |

---

## Architecture

```
8,173 historical events
        │
        ├─► Road Network Graph ── NetworkX · 294 junctions · betweenness fragility · percolation
        │
        ├─► Feature Pipeline ──── 28 leak-safe features (cyclical time, smoothed target encoding, centrality)
        │
        ├─► Impact Classifier ────────── XGBoost (composite severity)
        ├─► AFT Resolution Model ──────── XGBoost survival:aft
        ├─► Cascade Classifier ────────── XGBoost + isotonic calibration
        ├─► Time-To-Failure Estimator ─── escalation pressure → decision window
        │
        └─► Streamlit Decision-Support Dashboard (14 modules)
```

---

## Project structure

```
app.py                     dashboard (14 pages)
train.py                   leakage-safe training pipeline
src/
  feature_engineering.py   leak-safe features, composite impact, survival bounds
  models.py                XGBoost classifiers, AFT survival, isotonic calibration, SHAP
  network.py               road graph, betweenness fragility, cascade spread, percolation
  ttf.py                   Time-To-Failure estimator
  cascade_autopsy.py       counterfactual analysis + Point of No Return
  black_box.py             reconstruction, root cause, avoidable delay
  early_warning.py         pre-event risk index + city-wide percolation risk
  post_event.py            prediction log, history replay, drift tracking
  explain.py               SHAP waterfall + feature importance
  vulnerability.py         junction fragility index
  similarity.py            TF-IDF event similarity
  hotspot_detection.py     DBSCAN spatial clustering
  resources.py             context-aware resource recommendation
  digital_twin.py          multi-scenario simulator
  knowledge_graph.py       event relationship graph
data/                      dataset.csv, junction_vulnerability.csv, junction_centrality.csv
models/                    trained artifacts + metrics.json
```

---

## Known limitations

**Resolution duration is intrinsically hard to predict** in this data. In-distribution AUC for "will it exceed 60 min?" is ~0.61 and near-random out-of-time, because the resolution target is largely censored. We surface resolution as a historical-anchored estimate with a duration band and lean on the cascade-risk model for decisions.

**Impact is a composite-severity index**, not a ground-truth label — ~70% of rows have no labelled severity. The classifier learns and generalises from the composite with calibrated confidence.

**The road graph is reconstructed** from event geolocations and corridor membership (kNN + shared-corridor edges), not a full OSM import. This is a deliberate trade-off for a zero-download, reproducible demo.

---

## Roadmap

- XGBoost AFT → `lifelines` Weibull/Log-Logistic with Kaplan-Meier curves per cause
- Full OSMnx road import for true edge betweenness
- LLM "Traffic Commander" copilot grounded on model outputs (RAG)
- Reinforcement-learning diversion optimiser