# CascadeIQ — Event Impact Forecasting & Response Intelligence System

**Gridlock-Flipkart 2.0 Hackathon · Theme 2: Event-Driven Congestion**

> **Cities don't fail because of events. They fail because of cascades.**
>
> CascadeIQ predicts how disruptions spread, how much time authorities have before
> escalation, and the exact decision window where intervention could have prevented
> city-wide failure — learned from **8,173 historical Bengaluru traffic events**.

---

## Why this project is different

Most teams build an "event → congestion" classifier. CascadeIQ models the real chain
— **event → local disruption → network stress → junction overload → spillback →
escalation → gridlock** — and is engineered for **honesty and correctness**, not just
a headline accuracy number:

- A **survival model** that handles the dataset's censored resolution times instead of
  trusting corrupt administrative timestamps.
- A **calibrated** cascade-risk model whose probabilities are trustworthy (Brier 0.24 → 0.04).
- A **road-network graph** with betweenness-centrality fragility and a percolation
  cascade tracker — a citable algorithm, not hand-waving.
- A **leakage-free** evaluation with an honest **Model Card** that states the limits.

---

## ⚡ Quickstart

```bash
pip install -r requirements.txt        # Python >= 3.10
python train.py                        # build network, train models, write metrics
streamlit run app.py                   # launch the 14-page dashboard
```
(Poetry also works: `poetry install && poetry run python train.py && poetry run streamlit run app.py`.)

---

## 🧠 Model performance (honest, chronological held-out test)

All metrics use a **time-aware split** (train Nov 2023→Mar 2024, test Mar→Apr 2024) with
encoders fit on the training slice only — **no leakage**. The `status` column is excluded
as a feature because it leaks the outcome.

| Model | Task | Technique | Result |
|---|---|---|---|
| **Cascade Classifier** | Will it escalate? | XGBoost + **isotonic calibration** | **ROC-AUC 0.91**, PR-AUC 0.64 (vs 0.08 base rate), **Brier 0.038** |
| **Impact Classifier** | Severity (Low→Critical) | XGBoost, composite-severity label | **71.3%** acc (vs 55.8% baseline), macro-F1 0.62 |
| **AFT Resolution** | How long? | XGBoost **`survival:aft`** (censoring-aware) | **MedAE 60 min** on reliable events |
| **Prolonged (>60 min)** | Quick vs long | XGBoost binary | in-dist AUC ~0.61 *(intrinsically weak — see limitations)* |

> The dashboard's **🧠 Model Card** page renders these live, including the cascade
> confusion matrix and the calibration story.

### Why the numbers are trustworthy (and what we fixed)

The raw dataset has two traps that inflate naive scores. We address both:

1. **Censored resolution times.** Only ~74 events have a real `resolved_datetime`; the
   rest fall back to `closed_datetime`, an *administrative* close (90th percentile ≈ 11.6
   days). Rather than trust or discard these, the AFT model treats admin-closes as
   **interval-censored** and still-active events as **right-censored** — the principled
   survival-analysis approach.
2. **Leakage.** The split happens *before* any fitting; label encoders, smoothed target
   encodings and the scaler see training data only.

---

## 🗺️ Architecture

```
8,173 historical events
        │
        ├─► Road Network Graph ─ NetworkX · 294 junctions · betweenness fragility · percolation
        │
        ├─► Feature Pipeline ─── 28 leak-safe features (cyclical time, smoothed target encoding, centrality)
        │
        ├─► Impact Classifier ───────── XGBoost (composite severity)
        ├─► AFT Resolution Model ─────── XGBoost survival:aft (handles censoring)
        ├─► Cascade Classifier ───────── XGBoost + isotonic calibration
        ├─► Time-To-Failure Estimator ── escalation pressure → decision window
        │
        └─► Streamlit Decision-Support Dashboard (14 modules)
```

---

## 📦 Modules (14 dashboard pages)

| # | Page | What it does |
|---|------|--------------|
| 1 | 📊 **Dashboard Overview** | KPIs, distributions, time series, fragility leaderboard |
| 2 | 🔮 **Event Impact Prediction** | Impact + calibrated cascade % + **Time-To-Failure** + **tree-SHAP** "why" |
| 3 | 🚨 **Early Warning System** | Pre-event 0–100 risk index, deployment **lead time**, live city percolation risk |
| 4 | 🛰️ **Network Propagation** | Cascade spread animation, betweenness fragility, collapse curve, **diversion routing** |
| 5 | 🕵️ **Cascade Autopsy** | Counterfactual levers (lift closure / shift off-peak) → preventable share + Point of No Return |
| 6 | 🛩️ **Traffic Black Box** | Event reconstruction, **root-cause analysis**, **avoidable-delay** accounting |
| 7 | ⚠️ **Junction Vulnerability** | Fragility index (vision-doc formula, centrality-based) |
| 8 | 📍 **Hotspot Analysis** | DBSCAN spatial clusters by cause |
| 9 | 🔍 **Event Similarity Search** | TF-IDF top-5 historical matches |
| 10 | 📋 **Resource Recommendation** | Officers / barricades / monitoring / diversion |
| 11 | 🔄 **Digital Twin Simulator** | Side-by-side what-if scenario comparison (impact, cascade, TTF, resources) |
| 12 | 🕸️ **Knowledge Graph** | Multi-dimensional event relationship graph |
| 13 | 📈 **Post-Event Learning** | Persistent prediction-vs-actual log, calibration curve, accuracy drift |
| 14 | 🧠 **Model Card** | Honest held-out metrics, methodology, and stated limitations |

### Signature features

- **Time-To-Failure (TTF)** — minutes until escalation + the decision window, the vision
  doc's headline metric, derived transparently from cascade probability, severity and
  junction fragility.
- **Network Propagation Engine** — a data-derived road graph (NetworkX), **betweenness
  centrality** fragility, a threshold/SIR **cascade spread** simulation, and a
  **percolation** connected-components tracker whose peak-cluster timestep is the
  published precursor to network collapse.
- **Counterfactual Cascade Autopsy** — quantifies how much escalation was preventable by
  lifting a road closure or shifting an event off peak hour.
- **Post-Event Learning loop** — the brief's "no post-event learning system" gap, closed:
  predictions are stored, matched to outcomes, and scored over time.
- **Explainability** — exact tree-SHAP per prediction via XGBoost's native `pred_contribs`
  (no extra dependency), surfaced as a driver waterfall.

---

## 📁 Project structure

```
app.py                     Streamlit dashboard (14 pages)
train.py                   Leakage-safe training pipeline (split → fit → honest eval → refit-all)
src/
  feature_engineering.py   Leak-safe features, composite impact, survival bounds, smoothed encoding
  models.py                XGBoost classifiers, AFT survival, isotonic calibration, native SHAP, metrics
  network.py               Road graph, betweenness fragility, cascade spread, percolation, diversion
  ttf.py                   Time-To-Failure / decision-window estimator
  cascade_autopsy.py       Counterfactual analysis + Point of No Return
  black_box.py             Reconstruction, root cause, avoidable delay
  early_warning.py         Pre-event risk index + city-wide percolation risk
  post_event.py            Persistent prediction log, history replay, learning summary, drift
  explain.py               SHAP driver text + Plotly waterfall/importance
  vulnerability.py         Junction fragility (centrality-based vision-doc formula)
  similarity.py            TF-IDF event similarity
  hotspot_detection.py     DBSCAN spatial clustering
  resources.py             Context-aware resource recommendation
  digital_twin.py          Multi-scenario simulator
  knowledge_graph.py       Event relationship graph
data/                      dataset.csv, junction_vulnerability.csv, junction_centrality.csv
models/                    trained artifacts + metrics.json
```

---

## ⚠️ Known limitations (stated up front)

- **Fine-grained resolution duration is intrinsically hard** in this data: in-distribution
  AUC for "will it exceed 60 min?" is ~0.61 and near-random out-of-time, because the
  resolution target is largely censored. We surface resolution as a *historical-anchored
  estimate* + duration band and lean on the (strong) cascade-risk model for decisions.
- **Impact** is a composite-severity index (it has no ground-truth label for ~70% of rows),
  learned and generalised by the classifier with calibrated confidence — not a physical
  measurement.
- The **road graph** is reconstructed from event geolocations + corridor membership
  (kNN + shared-corridor edges), not a full OSM import — a deliberate trade-off for a
  zero-download, reproducible demo.

---

## 🛣️ Roadmap

- XGBoost AFT → `lifelines` Weibull/Log-Logistic AFT with Kaplan-Meier survival curves per cause.
- Full OSMnx road import for true edge betweenness.
- LLM "Traffic Commander" copilot grounded (RAG) on the computed model outputs.
- Reinforcement-learning diversion optimiser.
