import pandas as pd
import numpy as np
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

from xgboost import XGBClassifier, XGBRegressor
from sklearn.model_selection import cross_val_score, StratifiedKFold, TimeSeriesSplit
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             mean_absolute_error, mean_squared_error, r2_score,
                             roc_auc_score, precision_recall_fscore_support)
import joblib

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')


def train_impact_classifier(X, y, use_time_aware_split=True):
    params = {
        'n_estimators': 500,
        'max_depth': 8,
        'learning_rate': 0.05,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'min_child_weight': 3,
        'gamma': 0.1,
        'reg_alpha': 0.1,
        'reg_lambda': 1.0,
        'eval_metric': 'mlogloss',
        'random_state': 42,
        'n_jobs': -1
    }

    model = XGBClassifier(**params)

    if use_time_aware_split and len(X) > 100:
        try:
            tscv = TimeSeriesSplit(n_splits=3)
            cv_scores = cross_val_score(model, X, y, cv=tscv, scoring='accuracy')
            print(f"TimeSeries CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        except:
            pass

    model.fit(X, y)
    return model


def train_resolution_regressor(X, y):
    y_log = np.log1p(y)

    params = {
        'n_estimators': 500,
        'max_depth': 6,
        'learning_rate': 0.05,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'min_child_weight': 2,
        'gamma': 0.1,
        'reg_alpha': 0.5,
        'reg_lambda': 1.0,
        'eval_metric': 'mae',
        'random_state': 42,
        'n_jobs': -1
    }

    model = XGBRegressor(**params)

    if len(X) > 100:
        try:
            tscv = TimeSeriesSplit(n_splits=3)
            cv_scores = cross_val_score(model, X, y_log, cv=tscv, scoring='neg_mean_absolute_error')
            print(f"TimeSeries CV MAE (log): {-cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        except:
            pass

    model.fit(X, y_log)
    return model


def predict_resolution(model, X):
    y_log_pred = model.predict(X)
    return np.expm1(y_log_pred)


def train_cascade_classifier(X, y):
    params = {
        'n_estimators': 300,
        'max_depth': 6,
        'learning_rate': 0.05,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'eval_metric': 'logloss',
        'random_state': 42,
        'scale_pos_weight': 1.5,
        'n_jobs': -1
    }

    model = XGBClassifier(**params)

    if len(X) > 100:
        tscv = TimeSeriesSplit(n_splits=3)
        cv_scores = cross_val_score(model, X, y, cv=tscv, scoring='roc_auc')
        print(f"Cascade CV AUC-ROC: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    model.fit(X, y)
    return model


def evaluate_classifier(model, X_test, y_test, label='Classifier'):
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None

    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)

    print(f"\n=== {label} ===")
    print(f"Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred))

    if y_proba is not None and len(np.unique(y_test)) == 2:
        auc = roc_auc_score(y_test, y_proba[:, 1])
        print(f"AUC-ROC: {auc:.4f}")

    return acc, report


def evaluate_regressor(model, X_test, y_test, label='Regressor'):
    y_pred = predict_resolution(model, X_test)
    y_test = np.array(y_test)
    valid_mask = np.isfinite(y_test) & np.isfinite(y_pred)
    if valid_mask.sum() < 10:
        print(f"\n=== {label} === Not enough valid samples")
        return -1, -1, -1
    y_test_f = y_test[valid_mask]
    y_pred_f = y_pred[valid_mask]
    mae = mean_absolute_error(y_test_f, y_pred_f)
    rmse = np.sqrt(mean_squared_error(y_test_f, y_pred_f))
    r2 = r2_score(y_test_f, y_pred_f)

    print(f"\n=== {label} ===")
    print(f"MAE: {mae:.2f} mins")
    print(f"RMSE: {rmse:.2f} mins")
    print(f"R2: {r2:.4f}")

    return mae, rmse, r2


def save_model(model, name):
    path = os.path.join(MODELS_DIR, f'{name}.pkl')
    joblib.dump(model, path)
    print(f"Model saved to {path}")
    return path


def load_model(name):
    path = os.path.join(MODELS_DIR, f'{name}.pkl')
    if os.path.exists(path):
        return joblib.load(path)
    return None
