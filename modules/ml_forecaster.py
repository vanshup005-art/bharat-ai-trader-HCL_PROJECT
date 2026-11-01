"""
Machine Learning Forecasting & Market Anomaly Detection Engine.
Uses Random Forest for directional classification and Isolation Forest for anomaly radar.
"""
from typing import Dict, Tuple, List, Optional, Any
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import accuracy_score


def prepare_ml_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer quantitative features for ML trend classification."""
    data = df.copy()

    # Target: 1-day ahead direction (1 if tomorrow's Close > today's Close else 0)
    data["Target_1D"] = (data["Close"].shift(-1) > data["Close"]).astype(int)
    # Target: 5-day ahead direction
    data["Target_5D"] = (data["Close"].shift(-5) > data["Close"]).astype(int)

    # Returns & Momentum Lags
    data["Return_1D"] = data["Close"].pct_change().fillna(0)
    data["Return_5D"] = data["Close"].pct_change(5).fillna(0)
    data["Return_10D"] = data["Close"].pct_change(10).fillna(0)
    data["Return_20D"] = data["Close"].pct_change(20).fillna(0)

    # Volatility & Momentum
    data["Vol_10D"] = data["Return_1D"].rolling(10, min_periods=1).std().fillna(0)
    data["Vol_Ratio"] = data["Volume"] / (data["Volume"].rolling(20, min_periods=1).mean() + 1e-9)

    # Distance to moving averages
    data["Dist_SMA20"] = (data["Close"] - data["SMA_20"]) / (data["SMA_20"] + 1e-9)
    data["Dist_SMA50"] = (data["Close"] - data["SMA_50"]) / (data["SMA_50"] + 1e-9)
    data["Dist_SMA200"] = (data["Close"] - data["SMA_200"]) / (data["SMA_200"] + 1e-9)

    # Bollinger Band Relative Position (0 = at lower band, 1 = at upper band)
    bb_width = data["BB_Upper"] - data["BB_Lower"] + 1e-9
    data["BB_Pos"] = (data["Close"] - data["BB_Lower"]) / bb_width

    # Normalized RSI & MACD
    data["RSI_Norm"] = (data["RSI"] - 50) / 50.0
    data["MACD_Norm"] = data["MACD"] / (data["Close"] + 1e-9)
    data["MACD_Hist_Norm"] = data["MACD_Hist"] / (data["Close"] + 1e-9)

    return data


FEATURE_COLUMNS = [
    "Return_1D", "Return_5D", "Return_10D", "Vol_10D", "Vol_Ratio",
    "Dist_SMA20", "Dist_SMA50", "BB_Pos", "RSI_Norm", "MACD_Norm", "MACD_Hist_Norm"
]


def train_and_forecast_trend(
    df: pd.DataFrame,
    horizon: str = "1D"
) -> Dict[str, Any]:
    """
    Train a Random Forest classifier on historical feature vectors to forecast
    the probability of upward/downward movement over the specified horizon.
    """
    data = prepare_ml_features(df)
    target_col = "Target_1D" if horizon == "1D" else "Target_5D"

    clean = data.dropna(subset=FEATURE_COLUMNS + [target_col])
    if len(clean) < 60:
        return {
            "error": "Insufficient historical data points (minimum 60 trading bars required for statistical stability)."
        }

    # Time-series split (last 20% for out-of-sample validation)
    split_idx = int(len(clean) * 0.8)
    train_data = clean.iloc[:split_idx]
    test_data = clean.iloc[split_idx:]

    X_train = train_data[FEATURE_COLUMNS]
    y_train = train_data[target_col]
    X_test = test_data[FEATURE_COLUMNS]
    y_test = test_data[target_col]

    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        min_samples_split=6,
        random_state=42
    )
    clf.fit(X_train, y_train)

    test_preds = clf.predict(X_test)
    accuracy = float(accuracy_score(y_test, test_preds))

    # Inference on the most recent bar
    latest_feature_vector = data[FEATURE_COLUMNS].iloc[[-1]].fillna(0)
    latest_probs = clf.predict_proba(latest_feature_vector)[0]

    # Robust probability mapping based on clf.classes_
    classes = list(clf.classes_)
    if 1 in classes:
        prob_up = float(latest_probs[classes.index(1)])
    else:
        prob_up = 0.0

    if 0 in classes:
        prob_down = float(latest_probs[classes.index(0)])
    else:
        prob_down = 1.0 - prob_up

    # Feature Importance breakdown
    importances = [
        {"feature": feat, "importance": round(float(imp), 4)}
        for feat, imp in zip(FEATURE_COLUMNS, clf.feature_importances_)
    ]
    importances = sorted(importances, key=lambda x: x["importance"], reverse=True)

    if prob_up > 0.58:
        recommendation = "BULLISH ACCUMULATION 📈"
        eli5_rec = "The AI model predicts a strong likelihood of upward price momentum based on historical indicator alignment."
    elif prob_down > 0.58:
        recommendation = "BEARISH CAUTION 📉"
        eli5_rec = "The AI model detects downward pressure and recommends defensive posturing or waiting on the sidelines."
    else:
        recommendation = "NEUTRAL / RANGE-BOUND ⚖️"
        eli5_rec = "The forces of buyers and sellers are closely balanced. Expect price to oscillate within recent support and resistance."

    return {
        "horizon": horizon,
        "prob_up": round(prob_up * 100, 1),
        "prob_down": round(prob_down * 100, 1),
        "validation_accuracy": round(accuracy * 100, 1),
        "recommendation": recommendation,
        "eli5_recommendation": eli5_rec,
        "top_features": importances[:6],
        "model_type": "Random Forest Classifier (Ensemble)",
        "train_samples": len(train_data),
        "test_samples": len(test_data)
    }


def detect_market_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect statistical price and volume anomalies using Isolation Forest & Z-Scores.
    Flags unusual institutional volume spikes, abnormal volatility shocks, and flash deviations.
    """
    data = df.copy()

    ret = data["Close"].pct_change().fillna(0)
    vol = data["Volume"].fillna(0)

    ret_mean = ret.rolling(30, min_periods=5).mean().fillna(0)
    ret_std = ret.rolling(30, min_periods=5).std().fillna(1e-9)
    data["Return_ZScore"] = (ret - ret_mean) / ret_std

    vol_mean = vol.rolling(30, min_periods=5).mean().fillna(1)
    vol_std = vol.rolling(30, min_periods=5).std().fillna(1e-9)
    data["Volume_ZScore"] = (vol - vol_mean) / vol_std

    features = data[["Return_ZScore", "Volume_ZScore"]].fillna(0)

    iso = IsolationForest(contamination=0.035, random_state=42)
    preds = iso.fit_predict(features)
    data["Is_Anomaly"] = preds == -1

    def classify_anomaly(row):
        if not row["Is_Anomaly"]:
            return "Normal"
        if row["Volume_ZScore"] > 2.5 and row["Return_ZScore"] > 1.8:
            return "Institutional Buying Surge 🚀"
        elif row["Volume_ZScore"] > 2.5 and row["Return_ZScore"] < -1.8:
            return "Heavy Distribution / Selloff 💥"
        elif row["Volume_ZScore"] > 2.5:
            return "Abnormal Volume Churn ⚠️"
        elif abs(row["Return_ZScore"]) > 2.5:
            return "Extreme Volatility Shock ⚡"
        else:
            return "Statistical Outlier 🔍"

    data["Anomaly_Type"] = data.apply(classify_anomaly, axis=1)
    return data
