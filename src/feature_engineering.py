import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.preprocessing import LabelEncoder, StandardScaler
import warnings
warnings.filterwarnings('ignore')


def parse_datetime(df, col):
    return pd.to_datetime(df[col], utc=True, errors='coerce')


def compute_resolution_time(df):
    resolved = parse_datetime(df, 'resolved_datetime')
    closed = parse_datetime(df, 'closed_datetime')
    start = parse_datetime(df, 'start_datetime')

    end = resolved.fillna(closed)
    resolution_minutes = (end - start).dt.total_seconds() / 60.0
    return resolution_minutes.clip(lower=0)


def extract_time_features(dt_series):
    features = pd.DataFrame(index=dt_series.index)
    features['hour'] = dt_series.dt.hour
    features['day_of_week'] = dt_series.dt.dayofweek
    features['month'] = dt_series.dt.month
    features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
    features['is_peak_hour'] = (
        ((features['hour'] >= 8) & (features['hour'] <= 10)) |
        ((features['hour'] >= 17) & (features['hour'] <= 20))
    ).astype(int)
    features['is_night'] = (features['hour'] < 6).astype(int)
    features['hour_sin'] = np.sin(2 * np.pi * features['hour'] / 24)
    features['hour_cos'] = np.cos(2 * np.pi * features['hour'] / 24)
    features['dow_sin'] = np.sin(2 * np.pi * features['day_of_week'] / 7)
    features['dow_cos'] = np.cos(2 * np.pi * features['day_of_week'] / 7)
    return features


def create_impact_target(df, resolution_minutes):
    has_valid_res = resolution_minutes.notna() & (resolution_minutes > 0)
    priority_high = (df['priority'].str.lower().str.strip() == 'high').values
    requires_closure = df['requires_road_closure'].astype(bool).values if 'requires_road_closure' in df.columns else np.zeros(len(df), dtype=bool)
    is_planned = (df['event_type'].str.lower().str.strip() == 'planned').values

    impact = np.ones(len(df), dtype=int)

    high_impact_causes = df['event_cause'].str.lower().str.strip().isin([
        'public_event', 'procession', 'vip_movement', 'accident', 'tree_fall',
        'water_logging', 'congestion', 'construction'
    ]).values

    low_impact_causes = df['event_cause'].str.lower().str.strip().isin([
        'pot_holes', 'vehicle_breakdown', 'road_conditions', 'others', 'debris'
    ]).values

    if has_valid_res.any():
        res = resolution_minutes.values
        low_res = has_valid_res & (res <= 60)
        medium_res = has_valid_res & (res > 60) & (res <= 180)
        high_res = has_valid_res & (res > 180) & (res <= 480)
        critical_res = has_valid_res & (res > 480)

        impact[critical_res] = 3
        impact[high_res] = 2
        impact[medium_res] = 1
        impact[low_res] = 0
    else:
        impact[priority_high & high_impact_causes & is_planned] = 3
        impact[priority_high & high_impact_causes & ~is_planned] = 2
        impact[priority_high & low_impact_causes] = 1
        impact[~priority_high & high_impact_causes] = 1
        impact[~priority_high] = 0

    impact[requires_closure] = np.minimum(impact[requires_closure] + 1, 3)

    return impact


ENGINEERED_FEATURE_COLS = [
    'hour', 'day_of_week', 'month', 'is_weekend', 'is_peak_hour', 'is_night',
    'hour_sin', 'hour_cos', 'dow_sin', 'dow_cos',
    'event_type_planned', 'event_type_unplanned',
    'requires_road_closure', 'priority_High', 'priority_Low',
    'cause_encoded', 'corridor_encoded', 'zone_encoded', 'junction_encoded',
    'cause_avg_resolution', 'cause_event_count',
    'corridor_avg_resolution', 'corridor_event_count',
    'zone_avg_resolution', 'zone_event_count',
    'junction_avg_resolution', 'junction_event_count',
    'police_station_encoded', 'status_encoded'
]


def engineer_features(df, is_train=True, target_encoders=None):
    df = df.copy()

    start_dt = parse_datetime(df, 'start_datetime')
    time_feats = extract_time_features(start_dt)
    for c in time_feats.columns:
        df[c] = time_feats[c]

    resolution_minutes = compute_resolution_time(df)
    df['resolution_minutes'] = resolution_minutes

    df['event_type_planned'] = (df['event_type'].str.lower().str.strip() == 'planned').astype(int)
    df['event_type_unplanned'] = 1 - df['event_type_planned']
    df['requires_road_closure'] = df['requires_road_closure'].astype(int)
    df['priority_High'] = (df['priority'].str.lower().str.strip() == 'high').astype(int)
    df['priority_Low'] = 1 - df['priority_High']

    df['event_cause'] = df['event_cause'].str.lower().str.strip().fillna('unknown')
    df['corridor'] = df['corridor'].str.lower().str.strip().fillna('unknown')
    df['zone'] = df['zone'].str.lower().str.strip().fillna('unknown')
    df['junction'] = df['junction'].str.lower().str.strip().fillna('unknown').str.replace(' ', '')
    df['police_station'] = df['police_station'].str.lower().str.strip().fillna('unknown')
    df['status'] = df['status'].str.lower().str.strip().fillna('unknown')

    le_cause = LabelEncoder()
    le_corridor = LabelEncoder()
    le_zone = LabelEncoder()
    le_junction = LabelEncoder()
    le_police = LabelEncoder()
    le_status = LabelEncoder()

    if is_train:
        df['cause_encoded'] = le_cause.fit_transform(df['event_cause'])
        df['corridor_encoded'] = le_corridor.fit_transform(df['corridor'])
        df['zone_encoded'] = le_zone.fit_transform(df['zone'])
        df['junction_encoded'] = le_junction.fit_transform(df['junction'])
        df['police_station_encoded'] = le_police.fit_transform(df['police_station'])
        df['status_encoded'] = le_status.fit_transform(df['status'])

        cause_stats = df.groupby('event_cause')['resolution_minutes'].agg(['mean', 'count']).rename(
            columns={'mean': 'cause_avg_resolution', 'count': 'cause_event_count'})
        corridor_stats = df.groupby('corridor')['resolution_minutes'].agg(['mean', 'count']).rename(
            columns={'mean': 'corridor_avg_resolution', 'count': 'corridor_event_count'})
        zone_stats = df.groupby('zone')['resolution_minutes'].agg(['mean', 'count']).rename(
            columns={'mean': 'zone_avg_resolution', 'count': 'zone_event_count'})
        junction_stats = df.groupby('junction')['resolution_minutes'].agg(['mean', 'count']).rename(
            columns={'mean': 'junction_avg_resolution', 'count': 'junction_event_count'})

        target_encoders = {
            'le_cause': le_cause, 'le_corridor': le_corridor, 'le_zone': le_zone,
            'le_junction': le_junction, 'le_police': le_police, 'le_status': le_status,
            'cause_stats': cause_stats, 'corridor_stats': corridor_stats,
            'zone_stats': zone_stats, 'junction_stats': junction_stats
        }

        df = df.merge(cause_stats, left_on='event_cause', right_index=True, how='left')
        df = df.merge(corridor_stats, left_on='corridor', right_index=True, how='left')
        df = df.merge(zone_stats, left_on='zone', right_index=True, how='left')
        df = df.merge(junction_stats, left_on='junction', right_index=True, how='left')
    else:
        le_cause.classes_ = target_encoders['le_cause'].classes_
        le_corridor.classes_ = target_encoders['le_corridor'].classes_
        le_zone.classes_ = target_encoders['le_zone'].classes_
        le_junction.classes_ = target_encoders['le_junction'].classes_
        le_police.classes_ = target_encoders['le_police'].classes_
        le_status.classes_ = target_encoders['le_status'].classes_

        df['cause_encoded'] = df['event_cause'].map(
            lambda x: le_cause.transform([x])[0] if x in le_cause.classes_ else -1)
        df['corridor_encoded'] = df['corridor'].map(
            lambda x: le_corridor.transform([x])[0] if x in le_corridor.classes_ else -1)
        df['zone_encoded'] = df['zone'].map(
            lambda x: le_zone.transform([x])[0] if x in le_zone.classes_ else -1)
        df['junction_encoded'] = df['junction'].map(
            lambda x: le_junction.transform([x])[0] if x in le_junction.classes_ else -1)
        df['police_station_encoded'] = df['police_station'].map(
            lambda x: le_police.transform([x])[0] if x in le_police.classes_ else -1)
        df['status_encoded'] = df['status'].map(
            lambda x: le_status.transform([x])[0] if x in le_status.classes_ else -1)

        cause_stats = target_encoders['cause_stats']
        corridor_stats = target_encoders['corridor_stats']
        zone_stats = target_encoders['zone_stats']
        junction_stats = target_encoders['junction_stats']

        df = df.merge(cause_stats, left_on='event_cause', right_index=True, how='left')
        df = df.merge(corridor_stats, left_on='corridor', right_index=True, how='left')
        df = df.merge(zone_stats, left_on='zone', right_index=True, how='left')
        df = df.merge(junction_stats, left_on='junction', right_index=True, how='left')

    for col in ['cause_avg_resolution', 'cause_event_count', 'corridor_avg_resolution',
                'corridor_event_count', 'zone_avg_resolution', 'zone_event_count',
                'junction_avg_resolution', 'junction_event_count']:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median() if is_train else 0)

    impact = create_impact_target(df, df['resolution_minutes'])
    df['impact_level'] = impact

    feature_cols = [c for c in ENGINEERED_FEATURE_COLS if c in df.columns]
    X = df[feature_cols].fillna(0)

    if is_train:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        return X_scaled, df['resolution_minutes'], df['impact_level'], target_encoders, scaler, feature_cols
    else:
        scaler = target_encoders.get('scaler')
        if scaler:
            X_scaled = scaler.transform(X)
        else:
            X_scaled = X.values
        return X_scaled, df['resolution_minutes'], df['impact_level'], target_encoders, feature_cols
