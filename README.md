# CascadeIQ — Event Impact Forecasting & Response Intelligence System

**Gridlock-Flipkart 2.0 Hackathon — Theme 2: Event-Driven Congestion**

> **Cities don't fail because of events. They fail because of cascades.**
>
> CascadeIQ predicts how disruptions spread, how much time authorities have before escalation, and the exact decision window where intervention could have prevented city-wide failure.

---

## Problem Statement

Traffic authorities manage both **planned events** (sports matches, festivals, VIP movement, processions, construction) and **unplanned events** (vehicle breakdowns, accidents, water logging, tree falls, protests). These events frequently evolve into severe congestion because of delayed intervention, poor situational awareness, resource bottlenecks, and escalating secondary effects.

Current systems are reactive — they identify traffic problems only after they have already developed. Authorities cannot reliably answer:

- Which event is likely to create the highest traffic impact?
- Which junctions are most vulnerable during an event?
- How long will the disruption last?
- How many officers and barricades should be deployed?
- Which corridors need proactive monitoring?
- What can be learned from previous similar events?

Most decisions are based on experience rather than historical evidence.

---

## Core Insight

Most systems think: `Event → Congestion`

Reality is: `Event → Local Disruption → Network Stress → Junction Overload → Spillback → Escalation → City-Wide Gridlock`

The congestion itself is not the problem — **the escalation is**. CascadeIQ is designed to predict, analyze, and prevent escalation before it happens.

---

## Solution Overview

CascadeIQ is an AI-powered platform that learns from 8,173 historical traffic events and helps authorities forecast the operational impact of future events. Instead of simply recording incidents, the system predicts impact level, resolution duration, resource requirements, vulnerable junctions, and optimal response actions.

### System Architecture

```
Historical Events
       ↓
  Impact Prediction Model  ─── XGBoost Classifier (75.7% accuracy)
       ↓
  Resolution Time Model    ─── XGBoost Regressor (109.5 min MAE)
       ↓
  Cascade Risk Model       ─── XGBoost Classifier (93.1% accuracy, 0.958 AUC-ROC)
       ↓
  Junction Vulnerability   ─── Multi-factor Risk Index (294 junctions)
       ↓
  Hotspot Detection        ─── DBSCAN Spatial Clustering
       ↓
  Event Similarity Engine  ─── TF-IDF Vector Search
       ↓
  Resource Recommendation  ─── Context-Aware Allocation Engine
       ↓
  Cascade Autopsy          ─── Counterfactual Simulation
       ↓
  Streamlit Dashboard      ─── Interactive Decision Support
```

---

## Modules

### 1. Event Impact Prediction
Forecasts operational impact of an event before it escalates.

- **Inputs:** Event type, cause, priority, corridor, zone, road closure, time of day
- **Outputs:** Low / Medium / High / Critical impact with confidence score
- **Model:** XGBoost Classifier with 29 engineered features (time features, target encodings, historical statistics)
- **Accuracy:** 75.7%

### 2. Resolution Time Prediction
Estimates how long traffic disruption will last.

- **Inputs:** Same feature set as impact prediction
- **Outputs:** Expected resolution time in minutes
- **Model:** XGBoost Regressor with log-transformed target
- **MAE:** 109.5 minutes

### 3. Cascade Risk Assessment
Predicts whether an event will escalate into a critical gridlock situation.

- **Outputs:** Cascade probability (%), risk level
- **Model:** XGBoost Binary Classifier
- **Accuracy:** 93.1% | **AUC-ROC:** 0.958

### 4. Junction Vulnerability Analysis
Identifies junctions most at risk during events using a multi-factor risk index.

- **Factors:** Event frequency, average resolution time, high-priority ratio, road closure frequency, impact severity
- **Outputs:** Risk score (/10), risk category (Low/Medium/High/Critical)
- **Coverage:** 294 junctions across Bengaluru

### 5. Hotspot Detection
Uses DBSCAN spatial clustering to identify recurring event hotspots by cause type.

- **Clusters detected:** Vehicle breakdown (263), water logging (25), pot holes (27), construction (11), accident (7), and more
- **Outputs:** Interactive map with hotspot clusters

### 6. Event Similarity Search
Finds top-5 historical events most similar to any given event using TF-IDF vector search.

- **Similarity dimensions:** Event cause, corridor, zone, junction, type, priority
- **Outputs:** Similarity score, historical impact, resolution time, resources used

### 7. Resource Recommendation Engine
Recommends optimal resource deployment based on event context.

| Impact Level | Officers | Barricades | Monitoring | Diversion |
|-------------|----------|------------|------------|-----------|
| Low | 2 | 2 | Observation Only | Not Required |
| Medium | 5 | 6 | Normal | Standby |
| High | 10 | 14 | Immediate | Required |
| Critical | 15 | 20 | Immediate | Required |

Modifiers applied for: event cause, peak hours (20% increase), road closure (50% more barricades), major corridors (10% increase).

### 8. Cascade Autopsy (Counterfactual Simulation)
The flagship feature — identifies the exact decision window where intervention could have prevented escalation.

- **Method:** Binary search over intervention timing to find the Point of No Return
- **Outputs:** Point of No Return timestamp, Decision Window (minutes), Potential Delay Saved, Reality vs Counterfactual timeline

---

## Dataset

The dataset contains **8,173 events** with 46 columns capturing:

| Category | Attributes |
|----------|-----------|
| **Event Characteristics** | event_type, event_cause, priority, requires_road_closure |
| **Location Intelligence** | latitude, longitude, corridor, zone, junction, police_station |
| **Time Intelligence** | start_datetime, end_datetime, resolved_datetime, closed_datetime |
| **Operational Outcomes** | status, closure information, resolution duration |

### Key Statistics

- **7706** unplanned events | **467** planned events
- **5030** high priority | **3141** low priority
- **22** corridors | **10** zones | **294** junctions
- **7095** closed | **1007** active | **71** resolved

---

## Technical Stack

| Layer | Technology |
|-------|-----------|
| **Data Processing** | Pandas, NumPy |
| **Machine Learning** | XGBoost, Scikit-Learn |
| **Feature Engineering** | Cyclical time encoding, Target encoding, Historical aggregates |
| **Spatial Analysis** | DBSCAN Clustering |
| **Similarity Search** | TF-IDF Vectorization, Cosine Similarity |
| **Frontend** | Streamlit, Plotly |
| **Explainability** | SHAP (integrated) |
| **Package Management** | Poetry |

---

## Project Structure

```
cascadeiq/
├── app.py                          # Streamlit dashboard (7 interactive modules)
├── train.py                        # End-to-end training pipeline
├── pyproject.toml                  # Poetry project configuration
├── requirements.txt                # pip dependencies
├── README.md                       # This file
├── .gitignore
├── data/
│   ├── dataset.csv                 # 8,173 historical events
│   └── junction_vulnerability.csv  # Precomputed junction risk scores
├── models/                         # Trained model artifacts
│   ├── impact_classifier.pkl
│   ├── resolution_regressor.pkl
│   ├── cascade_classifier.pkl
│   ├── similarity.pkl
│   ├── hotspots.pkl
│   └── metrics.json
└── src/
    ├── feature_engineering.py      # 29 engineered features + target creation
    ├── models.py                   # XGBoost training & evaluation
    ├── hotspot_detection.py        # DBSCAN spatial clustering
    ├── vulnerability.py            # Junction Risk Index calculation
    ├── similarity.py               # TF-IDF event similarity search
    ├── resources.py                # Context-aware resource recommendation
    └── cascade_autopsy.py          # Counterfactual simulation engine
```

---

## Setup & Installation

### Prerequisites

- Python >= 3.10, < 3.12
- Poetry (recommended) or pip

### Using Poetry (Recommended)

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Train models
poetry run python train.py

# Launch the dashboard
poetry run streamlit run app.py
```

### Using pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Train models
poetry run python train.py

# Launch dashboard
poetry run streamlit run app.py
```

---

## Usage

### Dashboard Navigation

1. **Dashboard Overview** — Key metrics, event distribution charts, time series, top vulnerable junctions
2. **Event Impact Prediction** — Input event parameters and get instant prediction with confidence, resolution time, cascade risk, and resource recommendations
3. **Hotspot Analysis** — View DBSCAN spatial clusters by event cause on interactive maps
4. **Junction Vulnerability** — Browse and filter all 294 junctions by risk score
5. **Event Similarity Search** — Find top-5 historical events matching any event profile
6. **Cascade Autopsy** — Select any historical event and run counterfactual analysis to discover the Point of No Return
7. **Resource Recommendation** — Get optimized officer, barricade, and diversion recommendations

---

## Model Performance

| Model | Metric | Score |
|-------|--------|-------|
| **Impact Classifier** | Accuracy | **75.7%** |
| **Cascade Classifier** | Accuracy | **93.1%** |
| **Cascade Classifier** | AUC-ROC | **0.958** |
| **Resolution Regressor** | MAE | **109.5 min** |

All models validated using **time-aware train/test split** (80/20 chronological) to avoid temporal leakage.

---

## Why CascadeIQ Is Different

| Dimension | Traditional Systems | CascadeIQ |
|-----------|-------------------|-----------|
| Focus | Congestion detection | **Escalation prediction** |
| Timing | Reactive (after) | **Preventive (before)** |
| Decision Metric | Risk level | **Time-To-Failure (minutes)** |
| Resource Planning | Manual | **Data-driven recommendations** |
| Post-Event Analysis | None | **Cascade Autopsy with Point of No Return** |
| Institutional Memory | Lost | **Similarity search across 8K events** |
| Explainability | None | **Counterfactual simulation** |

---

## Future Enhancements

- Traffic Digital Twin Simulator for scenario comparison
- Reinforcement Learning-based diversion optimization
- LLM-powered Traffic Commander for conversational queries
- Real-time integration with traffic sensors and CCTV feeds
- Knowledge Graph for multi-dimensional event relationship analysis