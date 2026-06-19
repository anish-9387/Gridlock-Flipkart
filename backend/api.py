import os
import sys
import json
import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.feature_engineering import engineer_features
from src.models import load_model, predict_resolution
from src.vulnerability import compute_junction_vulnerability
from src.hotspot_detection import load_hotspot_models
from src.similarity import load_similarity_engine, find_similar_events
from src.resources import recommend_resources, IMPACT_RESOURCE_MAP
from src.cascade_autopsy import estimate_point_of_no_return, generate_timeline

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')

app = FastAPI(title="CascadeIQ API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models_cache = {}
data_cache = {}


def load_models():
    if not models_cache:
        models_cache['impact'] = load_model('impact_classifier')
        models_cache['resolution'] = load_model('resolution_regressor')
        models_cache['cascade'] = load_model('cascade_classifier')
        models_cache['sim_vec'], models_cache['sim_mat'], models_cache['sim_data'] = load_similarity_engine()
        models_cache['hotspots'] = load_hotspot_models()
    return models_cache


def load_dataset():
    if 'df' not in data_cache:
        path = os.path.join(DATA_DIR, 'dataset.csv')
        data_cache['df'] = pd.read_csv(path, low_memory=False)
    return data_cache['df']


def load_vulnerability():
    if 'vuln' not in data_cache:
        path = os.path.join(DATA_DIR, 'junction_vulnerability.csv')
        if os.path.exists(path):
            data_cache['vuln'] = pd.read_csv(path)
        else:
            df = load_dataset()
            X, y_res, y_impact, encoders, scaler, feat_cols = engineer_features(df, is_train=True)
            df_feat = df.copy()
            df_feat['resolution_minutes'] = y_res
            df_feat['impact_level'] = y_impact
            df_feat['priority_High'] = (df_feat['priority'].str.lower().str.strip() == 'high').astype(int)
            df_feat['requires_road_closure'] = df_feat['requires_road_closure'].astype(int)
            data_cache['vuln'] = compute_junction_vulnerability(df_feat)
    return data_cache['vuln']


def get_encoders():
    if 'encoders' not in data_cache:
        df = load_dataset()
        _, _, _, encoders, _, _ = engineer_features(df, is_train=True)
        data_cache['encoders'] = encoders
    return data_cache['encoders']


def get_feature_cols():
    if 'feat_cols' not in data_cache:
        from src.feature_engineering import ENGINEERED_FEATURE_COLS
        data_cache['feat_cols'] = ENGINEERED_FEATURE_COLS
    return data_cache['feat_cols']


class PredictionInput(BaseModel):
    event_type: str = "unplanned"
    event_cause: str = "vehicle_breakdown"
    priority: str = "Low"
    requires_road_closure: bool = False
    corridor: str = "Non-corridor"
    zone: str = "central zone 2"
    junction: str = "unknown"
    hour: int = 14
    latitude: float = 12.97
    longitude: float = 77.59


class SimilarityInput(BaseModel):
    event_cause: str = "vehicle_breakdown"
    corridor: str = "Non-corridor"
    zone: str = "central zone 2"
    junction: str = "unknown"
    event_type: str = "unplanned"
    priority: str = "Low"


class AutopsyInput(BaseModel):
    event_id: str


class ResourceInput(BaseModel):
    event_cause: str = "vehicle_breakdown"
    priority: str = "Low"
    corridor: str = "Non-corridor"
    hour: int = 14
    requires_road_closure: bool = False


def get_impact_label(level: int) -> str:
    return {0: 'Low', 1: 'Medium', 2: 'High', 3: 'Critical'}.get(level, 'Unknown')


def get_impact_color(level: int) -> str:
    return {0: '#22c55e', 1: '#eab308', 2: '#f97316', 3: '#ef4444'}.get(level, '#6b7280')


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "CascadeIQ API"}


@app.get("/api/dashboard/stats")
def dashboard_stats():
    df = load_dataset()
    X, y_res, y_impact, encoders, scaler, feat_cols = engineer_features(df, is_train=True)
    df_feat = df.copy()
    df_feat['resolution_minutes'] = y_res
    df_feat['impact_level'] = y_impact

    active_count = int((df['status'] == 'active').sum())
    high_impact_count = int((df_feat['impact_level'] >= 2).sum())
    total = len(df)

    vuln = load_vulnerability()
    top_junction = vuln.iloc[0]['junction'] if len(vuln) > 0 else "N/A"

    event_type_counts = df['event_type'].value_counts().to_dict()
    impact_counts = df_feat['impact_level'].value_counts().sort_index().to_dict()
    cause_counts = df['event_cause'].value_counts().head(8).to_dict()
    corridor_counts = df['corridor'].value_counts().head(10).to_dict()

    dates = pd.to_datetime(df['start_datetime'], utc=True, errors='coerce')
    daily_counts = dates.dt.date.value_counts().sort_index()
    time_series = {str(k): int(v) for k, v in daily_counts.head(60).items()}

    metrics_path = os.path.join(MODELS_DIR, 'metrics.json')
    metrics = {}
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            metrics = json.load(f)

    return {
        "total_events": total,
        "active_events": active_count,
        "high_impact_events": high_impact_count,
        "top_junction": top_junction,
        "junctions_count": int(df['junction'].nunique()),
        "zones_count": int(df['zone'].nunique()),
        "event_type_distribution": event_type_counts,
        "impact_distribution": {str(k): v for k, v in impact_counts.items()},
        "cause_distribution": cause_counts,
        "corridor_distribution": corridor_counts,
        "time_series": time_series,
        "metrics": metrics,
    }


@app.get("/api/dashboard/vulnerability")
def get_vulnerability(top_n: int = 20, min_events: int = 5):
    vuln = load_vulnerability()
    filtered = vuln[vuln['event_count'] >= min_events].head(top_n)
    cols = ['junction', 'risk_score', 'risk_category', 'event_count',
            'avg_resolution_minutes', 'high_priority_ratio', 'closure_ratio']
    return filtered[cols].to_dict(orient='records')


@app.post("/api/predict")
def predict(input_data: PredictionInput):
    models = load_models()
    encoders = get_encoders()
    impact_model = models['impact']
    res_model = models['resolution']
    cascade_model = models['cascade']

    input_df = pd.DataFrame([{
        'event_type': input_data.event_type,
        'event_cause': input_data.event_cause,
        'priority': input_data.priority,
        'requires_road_closure': input_data.requires_road_closure,
        'corridor': input_data.corridor,
        'zone': input_data.zone,
        'junction': input_data.junction,
        'start_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'police_station': 'unknown',
        'status': 'active',
        'latitude': input_data.latitude,
        'longitude': input_data.longitude,
    }])

    try:
        X_input, _, _, _ = engineer_features(
            input_df, is_train=False, target_encoders=encoders
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Feature engineering error: {str(e)}")

    impact_pred = int(impact_model.predict(X_input)[0])
    impact_proba = impact_model.predict_proba(X_input)[0].tolist()

    res_pred = float(predict_resolution(res_model, X_input)[0])

    cascade_pred = int(cascade_model.predict(X_input)[0])
    cascade_proba = cascade_model.predict_proba(X_input)[0].tolist()

    resources = recommend_resources(
        impact_pred, input_data.event_cause,
        input_data.requires_road_closure, input_data.corridor, input_data.hour
    )

    return {
        "impact_level": impact_pred,
        "impact_label": get_impact_label(impact_pred),
        "impact_color": get_impact_color(impact_pred),
        "impact_probabilities": impact_proba,
        "confidence": round(max(impact_proba) * 100, 1),
        "resolution_minutes": round(res_pred, 0),
        "cascade_prediction": cascade_pred,
        "cascade_probability": round(cascade_proba[1] * 100, 1),
        "cascade_label": "High" if cascade_pred == 1 else "Low",
        "resources": resources,
    }


@app.post("/api/similarity")
def similarity_search(input_data: SimilarityInput):
    models = load_models()
    vec = models.get('sim_vec')
    mat = models.get('sim_mat')
    ev_data = models.get('sim_data')

    if vec is None or mat is None or ev_data is None:
        raise HTTPException(status_code=503, detail="Similarity engine not available")

    query = {
        'event_cause': input_data.event_cause,
        'corridor': input_data.corridor,
        'zone': input_data.zone,
        'junction': input_data.junction,
        'event_type': input_data.event_type,
        'priority': input_data.priority,
        'police_station': 'unknown'
    }

    results = find_similar_events(query, vec, mat, ev_data, top_k=5)

    output = []
    for r in results:
        output.append({
            "event_id": r.get('id', ''),
            "event_cause": r.get('event_cause', ''),
            "corridor": r.get('corridor', ''),
            "zone": r.get('zone', ''),
            "junction": r.get('junction', ''),
            "priority": r.get('priority', ''),
            "impact_level": int(r.get('impact_level', 1)),
            "impact_label": get_impact_label(int(r.get('impact_level', 1))),
            "resolution_minutes": round(r.get('resolution_minutes', 0), 1),
            "similarity_score": r.get('similarity_score', 0),
        })

    return {"results": output}


@app.get("/api/hotspots")
def get_hotspots(cause: Optional[str] = None):
    models = load_models()
    hotspots = models.get('hotspots', {})

    if cause:
        if cause not in hotspots:
            raise HTTPException(status_code=404, detail=f"No hotspots for cause: {cause}")
        return {"cause": cause, "hotspots": hotspots[cause].to_dict(orient='records')}

    summary = {c: len(h) for c, h in hotspots.items()}
    return {"causes": summary}


@app.get("/api/events")
def get_events_for_autopsy(limit: int = 100):
    df = load_dataset()
    X, y_res, y_impact, encoders, scaler, feat_cols = engineer_features(df, is_train=True)
    df_feat = df.copy()
    df_feat['resolution_minutes'] = y_res
    df_feat['impact_level'] = y_impact

    resolved = df_feat[
        df_feat['status'].isin(['closed', 'resolved']) &
        (df_feat['resolution_minutes'] > 10) &
        (df_feat['resolution_minutes'] < 1440)
    ].head(limit)

    events = []
    for _, r in resolved.iterrows():
        events.append({
            "id": r.get('id', ''),
            "event_cause": r.get('event_cause', ''),
            "corridor": r.get('corridor', ''),
            "junction": r.get('junction', ''),
            "resolution_minutes": round(r.get('resolution_minutes', 0), 1),
            "priority": r.get('priority', ''),
            "impact_level": int(r.get('impact_level', 1)),
            "impact_label": get_impact_label(int(r.get('impact_level', 1))),
        })

    return {"events": events}


@app.post("/api/autopsy")
def run_autopsy(input_data: AutopsyInput):
    models = load_models()
    encoders = get_encoders()
    impact_model = models['impact']

    df = load_dataset()
    X, y_res, y_impact, _, scaler, feat_cols = engineer_features(df, is_train=True)
    df_feat = df.copy()
    df_feat['resolution_minutes'] = y_res
    df_feat['impact_level'] = y_impact

    event_row = df_feat[df_feat['id'] == input_data.event_id]
    if len(event_row) == 0:
        raise HTTPException(status_code=404, detail="Event not found")

    event_row = event_row.iloc[0].to_dict()

    autopsy = estimate_point_of_no_return(
        event_row, impact_model, engineer_features, encoders
    )

    timeline = generate_timeline(event_row, autopsy)

    return {
        "event": {
            "id": event_row.get('id', ''),
            "event_cause": event_row.get('event_cause', ''),
            "junction": event_row.get('junction', ''),
            "priority": event_row.get('priority', ''),
            "impact_label": get_impact_label(int(event_row.get('impact_level', 1))),
            "resolution_minutes": round(event_row.get('resolution_minutes', 0), 1),
        },
        "autopsy": autopsy,
        "timeline": timeline,
    }


@app.post("/api/resources")
def get_resources(input_data: ResourceInput):
    impact_level = 2 if input_data.priority == 'High' else 0
    if input_data.event_cause in ['public_event', 'procession']:
        impact_level = max(impact_level, 2)
    if input_data.requires_road_closure:
        impact_level = min(impact_level + 1, 3)

    resources = recommend_resources(
        impact_level, input_data.event_cause,
        input_data.requires_road_closure, input_data.corridor, input_data.hour
    )

    return {
        "impact_level": impact_level,
        "impact_label": get_impact_label(impact_level),
        "resources": resources,
        "reference_table": [
            {"impact": v['impact'], "officers": v['officers'],
             "barricades": v['barricades'], "monitoring": v['monitoring'],
             "diversion": v['diversion']}
            for v in IMPACT_RESOURCE_MAP.values()
        ]
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
