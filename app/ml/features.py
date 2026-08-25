"""
Canteen Pulse - Feature Engineering & Transformation
"""
import pandas as pd
import numpy as np
from datetime import date, timedelta
from typing import List, Dict, Any, Tuple

FEATURE_COLUMNS = [
    "day_of_week",
    "is_weekend",
    "is_holiday",
    "is_exam_period",
    "is_special_event",
    "temperature_c",
    "rainfall_mm",
    "humidity_pct",
    "rolling_avg_7d",
    "rolling_avg_28d",
    "month_sin",
    "month_cos",
    "day_sin",
    "day_cos"
]

def engineer_features_df(records_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms raw daily records dataframe into ML-ready feature matrices with lags & cyclical time encodings.
    """
    df = records_df.copy()
    df["record_date"] = pd.to_datetime(df["record_date"])
    df = df.sort_values("record_date").reset_index(drop=True)
    
    # Target actual meals (or predicted if actual is missing)
    df["target_meals"] = df["actual_meals"].fillna(df["predicted_meals"])
    
    # Rolling averages (using target history)
    df["rolling_avg_7d"] = df["target_meals"].shift(1).rolling(window=7, min_periods=1).mean().fillna(380.0)
    df["rolling_avg_28d"] = df["target_meals"].shift(1).rolling(window=28, min_periods=1).mean().fillna(380.0)
    
    # Cyclical date encodings
    months = df["record_date"].dt.month
    day_of_year = df["record_date"].dt.dayofyear
    
    df["month_sin"] = np.sin(2 * np.pi * months / 12.0)
    df["month_cos"] = np.cos(2 * np.pi * months / 12.0)
    df["day_sin"] = np.sin(2 * np.pi * day_of_year / 365.25)
    df["day_cos"] = np.cos(2 * np.pi * day_of_year / 365.25)
    
    # Booleans to numeric
    for col in ["is_weekend", "is_holiday", "is_exam_period", "is_special_event"]:
        if col in df.columns:
            df[col] = df[col].astype(int)
        else:
            df[col] = 0
            
    # Weather defaults
    if "temperature_c" not in df.columns:
        df["temperature_c"] = 28.0
    if "rainfall_mm" not in df.columns:
        df["rainfall_mm"] = 0.0
    if "humidity_pct" not in df.columns:
        df["humidity_pct"] = 55.0
        
    return df

def build_single_day_features(
    record_date: date,
    is_holiday: bool = False,
    is_exam: bool = False,
    is_special: bool = False,
    temp_c: float = 28.0,
    rainfall_mm: float = 0.0,
    humidity_pct: float = 55.0,
    rolling_avg_7d: float = 395.0,
    rolling_avg_28d: float = 390.0
) -> pd.DataFrame:
    """Builds a single-row feature vector for ad-hoc / what-if scenario prediction."""
    dow = record_date.weekday()
    is_wknd = 1 if dow in [5, 6] else 0
    month = record_date.month
    day_of_year = record_date.timetuple().tm_yday
    
    row = {
        "day_of_week": dow,
        "is_weekend": is_wknd,
        "is_holiday": 1 if is_holiday else 0,
        "is_exam_period": 1 if is_exam else 0,
        "is_special_event": 1 if is_special else 0,
        "temperature_c": float(temp_c),
        "rainfall_mm": float(rainfall_mm),
        "humidity_pct": float(humidity_pct),
        "rolling_avg_7d": float(rolling_avg_7d),
        "rolling_avg_28d": float(rolling_avg_28d),
        "month_sin": np.sin(2 * np.pi * month / 12.0),
        "month_cos": np.cos(2 * np.pi * month / 12.0),
        "day_sin": np.sin(2 * np.pi * day_of_year / 365.25),
        "day_cos": np.cos(2 * np.pi * day_of_year / 365.25)
    }
    
    return pd.DataFrame([row])[FEATURE_COLUMNS]
