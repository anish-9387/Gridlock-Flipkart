"""
Gridlock-Flipkart 2.0 — CascadeIQ Training Pipeline
Trains impact classifier, resolution regressor, cascade classifier,
similarity engine, hotspot detector, and junction vulnerability.
"""

import pandas as pd
import numpy as np
import os
import sys
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import accuracy_score, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib

from src.feature_engineering import (
    engineer_features, compute_resolution_time, create_impact_target,
    ENGINEERED_FEATURE_COLS, parse_datetime
)
from src.models import (
    train_impact_classifier, train_resolution_regressor, train_cascade_classifier,
    evaluate_classifier, evaluate_regressor, save_model, load_model,
    predict_resolution
)
from src.hotspot_detection import detect_hotspots_by_cause, save_hotspot_models
from src.vulnerability import compute_junction_vulnerability
from src.similarity import train_similarity_engine, save_similarity_engine
import pickle

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'dataset.csv')
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)


def main():
    print("=" * 60)
    print("  CascadeIQ — Training Pipeline")
    print("  Gridlock-Flipkart 2.0 Hackathon")
    print("=" * 60)

    print("\n[1/8] Loading dataset...")
    df = pd.read_csv(DATA_PATH, low_memory=False)
    print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")

    print("\n[2/8] Engineering features...")
    X, y_resolution, y_impact, target_encoders, scaler, feature_cols = engineer_features(
        df, is_train=True
    )
    target_encoders['scaler'] = scaler
    print(f"  Feature matrix: {X.shape}")
    print(f"  Features: {feature_cols}")
    print(f"  Impact distribution: {pd.Series(y_impact).value_counts().to_dict()}")

    print("\n[3/8] Computing cascade target...")
    resolution_q75 = y_resolution.quantile(0.75)
    y_cascade = (
        (y_resolution > resolution_q75) &
        (y_impact >= 2)
    ).astype(int)
    print(f"  Cascade events: {y_cascade.sum()} / {len(y_cascade)}")
    print(f"  Resolution 75th percentile: {resolution_q75:.1f} mins")

    print("\n[4/8] Splitting data (time-aware split)...")
    df_with_features = df.copy()
    df_with_features['resolution_minutes'] = y_resolution
    df_with_features['impact_level'] = y_impact
    dates = parse_datetime(df_with_features, 'start_datetime')
    sorted_idx = dates.argsort().values
    split_idx = int(len(sorted_idx) * 0.8)
    train_idx = sorted_idx[:split_idx]
    test_idx = sorted_idx[split_idx:]

    X_train, X_test = X[train_idx], X[test_idx]
    y_impact_train, y_impact_test = y_impact.iloc[train_idx], y_impact.iloc[test_idx]
    y_res_train, y_res_test = y_resolution.iloc[train_idx], y_resolution.iloc[test_idx]
    y_cascade_train, y_cascade_test = y_cascade.iloc[train_idx], y_cascade.iloc[test_idx]

    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")
    print(f"  Train period: {dates.iloc[train_idx].min()} to {dates.iloc[train_idx].max()}")
    print(f"  Test period: {dates.iloc[test_idx].min()} to {dates.iloc[test_idx].max()}")

    print("\n[5/8] Training models...")

    print("  >> Impact Classifier...")
    impact_model = train_impact_classifier(X_train, y_impact_train)
    impact_acc, _ = evaluate_classifier(impact_model, X_test, y_impact_test, 'Impact Classifier')
    save_model(impact_model, 'impact_classifier')

    print("  >> Resolution Time Regressor...")
    res_train_mask = y_res_train.notna() & (y_res_train > 0) & (y_res_train < 1440)
    res_test_mask = y_res_test.notna() & (y_res_test > 0) & (y_res_test < 1440)
    if res_train_mask.sum() > 100:
        res_model = train_resolution_regressor(
            X_train[res_train_mask.values], y_res_train[res_train_mask].values
        )
        res_mae, res_rmse, res_r2 = evaluate_regressor(
            res_model, X_test[res_test_mask.values], y_res_test[res_test_mask].values,
            'Resolution Regressor'
        )
        save_model(res_model, 'resolution_regressor')
    else:
        print("  WARNING: Not enough valid resolution data for regressor training")
        res_mae, res_rmse, res_r2 = -1, -1, -1

    print("  >> Cascade Probability Classifier...")
    cascade_model = train_cascade_classifier(X_train, y_cascade_train)
    cascade_acc, _ = evaluate_classifier(cascade_model, X_test, y_cascade_test, 'Cascade Classifier')
    save_model(cascade_model, 'cascade_classifier')

    print("\n[6/8] Building junction vulnerability index...")
    df_vuln = df_with_features.copy()
    df_vuln['priority_High'] = (df_vuln['priority'].str.lower().str.strip() == 'high').astype(int)
    df_vuln['requires_road_closure'] = df_vuln['requires_road_closure'].astype(int)
    junction_vulnerability = compute_junction_vulnerability(df_vuln)
    junction_vulnerability.to_csv(os.path.join(DATA_DIR, 'junction_vulnerability.csv'), index=False)
    print(f"  Computed risk scores for {len(junction_vulnerability)} junctions")
    print(f"  Top 5 fragile junctions:")
    for _, row in junction_vulnerability.head(5).iterrows():
        print(f"    {row['junction']}: {row['risk_score']}/10 ({row['risk_category']})")

    print("\n[7/8] Training similarity engine...")
    similarity_df = df_with_features.dropna(subset=['start_datetime'])
    vectorizer, tfidf_matrix, event_data = train_similarity_engine(similarity_df)
    save_similarity_engine(vectorizer, tfidf_matrix, event_data)
    print(f"  Similarity engine trained on {len(event_data)} events")

    print("\n[8/8] Detecting event hotspots...")
    hotspots = detect_hotspots_by_cause(df_with_features)
    save_hotspot_models(hotspots)
    print(f"  Detected hotspots for {len(hotspots)} event causes")
    for cause, h in hotspots.items():
        print(f"    {cause}: {len(h)} hotspot clusters")

    print("\n" + "=" * 60)
    print("  Training Complete!")
    print("=" * 60)
    print(f"\n  Model Performance Summary:")
    print(f"  Impact Classifier Accuracy:   {impact_acc:.3f}")
    print(f"  Resolution Regressor MAE:     {res_mae:.1f} mins")
    print(f"  Resolution Regressor R2:      {res_r2:.3f}")
    print(f"  Cascade Classifier Accuracy:  {cascade_acc:.3f}")
    print(f"\n  All models saved to: {MODELS_DIR}")

    metrics = {
        'impact_accuracy': float(f"{impact_acc:.4f}"),
        'resolution_mae': float(f"{res_mae:.1f}"),
        'resolution_r2': float(f"{res_r2:.4f}"),
        'cascade_accuracy': float(f"{cascade_acc:.4f}"),
        'train_samples': len(X_train),
        'test_samples': len(X_test)
    }
    with open(os.path.join(MODELS_DIR, 'metrics.json'), 'w') as f:
        import json
        json.dump(metrics, f, indent=2)

    return metrics


if __name__ == '__main__':
    main()
