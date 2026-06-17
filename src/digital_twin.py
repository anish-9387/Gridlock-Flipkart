import pandas as pd
import numpy as np
from datetime import datetime

from src.feature_engineering import engineer_features
from src.models import predict_resolution
from src.resources import recommend_resources


def run_scenario(params, impact_model, res_model, cascade_model, encoders):
    input_data = pd.DataFrame([{
        'event_type': params['event_type'],
        'event_cause': params['event_cause'],
        'priority': params['priority'],
        'requires_road_closure': params['requires_road_closure'],
        'corridor': params['corridor'],
        'zone': params['zone'],
        'junction': params['junction'] if params['junction'] != 'Unknown' else 'unknown',
        'start_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'resolved_datetime': None,
        'closed_datetime': None,
        'police_station': 'unknown',
        'status': 'active',
        'latitude': 12.97,
        'longitude': 77.59
    }])

    X_input, _, _, _, _ = engineer_features(
        input_data, is_train=False, target_encoders=encoders
    )

    impact_pred = int(impact_model.predict(X_input)[0])
    impact_proba = impact_model.predict_proba(X_input)[0]
    impact_confidence = float(max(impact_proba) * 100)

    res_pred = float(predict_resolution(res_model, X_input)[0])

    cascade_pred = int(cascade_model.predict(X_input)[0])
    cascade_proba = float(cascade_model.predict_proba(X_input)[0][1] * 100)

    resources = recommend_resources(
        impact_pred, params['event_cause'], params['requires_road_closure'],
        params['corridor'], params['hour']
    )

    return {
        'name': params.get('name', 'Unnamed'),
        'event_cause': params['event_cause'],
        'priority': params['priority'],
        'corridor': params['corridor'],
        'zone': params['zone'],
        'junction': params['junction'],
        'hour': params['hour'],
        'requires_road_closure': params['requires_road_closure'],
        'impact_level': impact_pred,
        'impact_label': {0: 'Low', 1: 'Medium', 2: 'High', 3: 'Critical'}[impact_pred],
        'impact_confidence': impact_confidence,
        'resolution_minutes': res_pred,
        'cascade_risk': cascade_pred,
        'cascade_probability': cascade_proba,
        'officers': resources['officers'],
        'barricades': resources['barricades'],
        'monitoring': resources['monitoring'],
        'diversion': resources['diversion']
    }


def compare_scenarios(scenarios, impact_model, res_model, cascade_model, encoders):
    return [run_scenario(s, impact_model, res_model, cascade_model, encoders) for s in scenarios]


def scenarios_to_dataframe(results):
    rows = []
    for r in results:
        rows.append({
            'Scenario': r['name'],
            'Cause': r['event_cause'],
            'Junction': r['junction'],
            'Corridor': r['corridor'],
            'Hour': f"{r['hour']}:00",
            'Road Closure': 'Yes' if r['requires_road_closure'] else 'No',
            'Impact Level': r['impact_label'],
            'Confidence': f"{r['impact_confidence']:.1f}%",
            'Resolution (min)': f"{r['resolution_minutes']:.0f}",
            'Cascade Risk': 'High' if r['cascade_risk'] else 'Low',
            'Cascade Prob.': f"{r['cascade_probability']:.1f}%",
            'Officers': r['officers'],
            'Barricades': r['barricades'],
            'Monitoring': r['monitoring'],
            'Diversion': r['diversion']
        })
    return pd.DataFrame(rows)
