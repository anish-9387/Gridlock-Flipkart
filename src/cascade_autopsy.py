import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor

from src.resources import IMPACT_RESOURCE_MAP


def build_counterfactual(event_row, minutes_shift=15):
    cf = event_row.copy()
    start = pd.to_datetime(event_row['start_datetime'], utc=True)
    resolved = pd.to_datetime(event_row['resolved_datetime'], utc=True) if pd.notna(
        event_row.get('resolved_datetime')) else None
    closed = pd.to_datetime(event_row['closed_datetime'], utc=True) if pd.notna(
        event_row.get('closed_datetime')) else None

    actual_resolution = None
    if resolved:
        actual_resolution = (resolved - start).total_seconds() / 60
    elif closed:
        actual_resolution = (closed - start).total_seconds() / 60

    if actual_resolution is None:
        return None

    new_resolved = start + timedelta(minutes=(actual_resolution - minutes_shift))
    cf['resolved_datetime'] = new_resolved.isoformat()
    cf['resolution_minutes'] = actual_resolution - minutes_shift

    return cf


def estimate_point_of_no_return(event_row, model, feature_fn, base_features, impact_percentile=0.75):
    start = pd.to_datetime(event_row['start_datetime'], utc=True)
    resolved = pd.to_datetime(event_row['resolved_datetime'], utc=True) if pd.notna(
        event_row.get('resolved_datetime')) else None
    closed = pd.to_datetime(event_row['closed_datetime'], utc=True) if pd.notna(
        event_row.get('closed_datetime')) else None

    actual_resolution = None
    if resolved:
        actual_resolution = (resolved - start).total_seconds() / 60
    elif closed:
        actual_resolution = (closed - start).total_seconds() / 60

    if actual_resolution is None or actual_resolution <= 5:
        return None

    impact_level = int(event_row.get('impact_level', 1))
    severity_threshold = IMPACT_RESOURCE_MAP.get(impact_level, {}).get('officers', 5)

    low, high = 0, int(actual_resolution)
    point_of_no_return = None

    for _ in range(10):
        mid = (low + high) // 2
        cf = build_counterfactual(event_row, mid)
        if cf is None:
            break

        cf_df = pd.DataFrame([cf])
        try:
            X_cf, _, _, _ = feature_fn(cf_df, is_train=False, target_encoders=base_features)
        except:
            break

        pred_impact = model.predict(X_cf)[0]

        if pred_impact <= impact_level - 1:
            point_of_no_return = mid
            high = mid - 1
        else:
            low = mid + 1

    if point_of_no_return is None:
        return None

    decision_window = actual_resolution - point_of_no_return
    delay_saved = actual_resolution * 0.6

    return {
        'point_of_no_return_minutes': point_of_no_return,
        'point_of_no_return_time': (start + timedelta(minutes=point_of_no_return)).strftime('%H:%M'),
        'decision_window_minutes': int(decision_window),
        'actual_resolution_minutes': int(actual_resolution),
        'potential_delay_saved': int(delay_saved),
        'cascade_prevented': True,
        'event_start': start.strftime('%H:%M'),
        'event_start_dt': start.isoformat()
    }


def generate_timeline(event_row, autopsy_result=None):
    start = pd.to_datetime(event_row['start_datetime'], utc=True)
    resolved = pd.to_datetime(event_row['resolved_datetime'], utc=True) if pd.notna(
        event_row.get('resolved_datetime')) else None
    closed = pd.to_datetime(event_row['closed_datetime'], utc=True) if pd.notna(
        event_row.get('closed_datetime')) else None
    end = resolved if resolved else closed

    timeline = [
        {'time': start.strftime('%H:%M'), 'event': 'Event Started', 'type': 'start'}
    ]

    if end:
        midpoint = start + (end - start) / 2
        timeline.append({
            'time': midpoint.strftime('%H:%M'),
            'event': 'Queue Building / Congestion Developing',
            'type': 'escalation'
        })
        timeline.append({
            'time': end.strftime('%H:%M'),
            'event': 'Event Resolved',
            'type': 'end'
        })

    if not end:
        timeline.append({
            'time': '--:--',
            'event': 'Still Active',
            'type': 'active'
        })

    if autopsy_result:
        ponr = autopsy_result.get('point_of_no_return_time')
        if ponr:
            timeline.append({
                'time': ponr,
                'event': '⚠ Point of No Return (Last Intervention Window)',
                'type': 'critical'
            })

    return timeline
