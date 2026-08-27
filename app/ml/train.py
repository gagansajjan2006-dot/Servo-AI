"""
Servo-AI - ML Training Pipeline
Trains a RandomForestRegressor on historical MealDemand data.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
from sqlalchemy.orm import Session

from app.models import MealDemand
from app.crud import get_all_meal_demands_df_data, create_training_log

logger = logging.getLogger("servo_ai.train")

# Feature columns used by the model
FEATURE_COLUMNS = [
    "day_of_week",
    "month",
    "station_encoded",
    "menu_item_encoded",
    "temperature",
    "weather_encoded",
    "is_weekend",
    "is_holiday",
    "student_attendance",
    "faculty_attendance",
    "previous_day_demand",
    "previous_week_demand",
]


def _build_training_dataframe(records) -> pd.DataFrame:
    """Converts MealDemand ORM records into a training-ready DataFrame."""
    data = []
    for r in records:
        data.append({
            "date": r.date,
            "station": r.station,
            "menu_item": r.menu_item,
            "actual_quantity": r.actual_quantity,
            "predicted_quantity": r.predicted_quantity,
            "weather": r.weather or "Clear",
            "temperature": r.temperature or 28.0,
            "is_holiday": 1 if r.is_holiday else 0,
            "is_weekend": 1 if r.is_weekend else 0,
            "student_attendance": r.student_attendance or 3500,
            "faculty_attendance": r.faculty_attendance or 380,
        })

    df = pd.DataFrame(data)
    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["station", "menu_item", "date"]).reset_index(drop=True)

    # Time features
    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month

    # Lag features: previous day and previous week demand (per station+item group)
    df["previous_day_demand"] = (
        df.groupby(["station", "menu_item"])["actual_quantity"]
        .shift(1)
        .fillna(df["actual_quantity"].mean())
    )
    df["previous_week_demand"] = (
        df.groupby(["station", "menu_item"])["actual_quantity"]
        .shift(7)
        .fillna(df["actual_quantity"].mean())
    )

    return df


def train_demand_model(db: Session, manager) -> Dict[str, Any]:
    """
    Full training pipeline:
    1. Load MealDemand data
    2. Clean & encode
    3. Train RandomForestRegressor
    4. Evaluate
    5. Save model
    6. Return metrics
    """
    logger.info("Starting demand forecasting model training pipeline...")
    records = get_all_meal_demands_df_data(db)

    if len(records) < 10:
        logger.error(f"Insufficient training data: {len(records)} records found, minimum 10 required.")
        raise ValueError(
            f"Insufficient training data: {len(records)} records found, "
            f"minimum 10 required."
        )

    logger.info(f"Step 1/5: Loaded {len(records)} records from database. Building feature matrix...")
    df = _build_training_dataframe(records)

    # Encode categorical variables
    logger.info("Step 2/5: Encoding categorical features & generating lag demand variables...")
    station_encoder = LabelEncoder()
    item_encoder = LabelEncoder()
    weather_encoder = LabelEncoder()

    df["station_encoded"] = station_encoder.fit_transform(df["station"])
    df["menu_item_encoded"] = item_encoder.fit_transform(df["menu_item"])
    df["weather_encoded"] = weather_encoder.fit_transform(df["weather"])

    # Clean missing values
    df = df.dropna(subset=["actual_quantity"])
    df[FEATURE_COLUMNS] = df[FEATURE_COLUMNS].fillna(0)

    X = df[FEATURE_COLUMNS].values
    y = df["actual_quantity"].values

    # Train Random Forest
    logger.info(
        f"Step 3/5: Training RandomForestRegressor (n_estimators=100, max_depth=15) on {len(X)} samples with {len(FEATURE_COLUMNS)} features..."
    )
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X, y)

    # Evaluate
    logger.info("Step 4/5: Evaluating model performance and computing feature importances...")
    y_pred = model.predict(X)
    mae = float(mean_absolute_error(y, y_pred))
    mse = float(mean_squared_error(y, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y, y_pred))
    residual_std = float(np.std(y - y_pred))
    mape = float(np.mean(np.abs((y - y_pred) / np.maximum(y, 1))) * 100)
    accuracy_pct = float(max(0, 100 - mape))

    # Feature importances
    feature_importances = dict(
        zip(FEATURE_COLUMNS, [round(float(fi), 4) for fi in model.feature_importances_])
    )

    logger.info(
        f"Model Evaluation Metrics -> R2: {r2:.4f} | MAE: {mae:.2f} | RMSE: {rmse:.2f} | MAPE: {mape:.1f}% | Accuracy: {accuracy_pct:.1f}%"
    )

    # Save metadata
    now_utc = datetime.now(timezone.utc)
    model_version = f"v{now_utc.strftime('%m%d.%H%M')}-RF"
    metadata = {
        "residual_std": residual_std,
        "feature_names": FEATURE_COLUMNS,
        "label_encoders": {
            "station": station_encoder,
            "menu_item": item_encoder,
            "weather": weather_encoder,
        },
        "metrics": {
            "mae": round(mae, 2),
            "mse": round(mse, 2),
            "rmse": round(rmse, 2),
            "r2_score": round(r2, 4),
            "mape": round(mape, 1),
            "accuracy_pct": round(accuracy_pct, 1),
        },
        "last_trained": now_utc.isoformat(),
        "training_rows": len(X),
        "feature_importances": feature_importances,
        "model_version": model_version,
    }

    # Save via model manager
    logger.info("Step 5/5: Persisting model artifacts and updating database training audit log...")
    manager.save_model(model, metadata)

    # Log to database
    try:
        create_training_log(db, {
            "trained_at": now_utc,
            "sample_count": len(X),
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "r2_score": round(r2, 4),
            "mape": round(mape, 1),
            "accuracy_pct": round(accuracy_pct, 1),
            "feature_importances": feature_importances,
            "model_version": model_version,
            "notes": "RandomForestRegressor trained via Servo-AI pipeline",
        })
        logger.info(f"Training audit log recorded successfully: version={model_version}")
    except Exception as e:
        logger.warning(f"Could not save training log to database: {e}")

    logger.info("Demand forecasting model training pipeline completed successfully!")

    return {
        "status": "success",
        "model": "RandomForestRegressor",
        "model_version": model_version,
        "mae": round(mae, 2),
        "mse": round(mse, 2),
        "rmse": round(rmse, 2),
        "r2_score": round(r2, 4),
        "mape": round(mape, 1),
        "accuracy_pct": round(accuracy_pct, 1),
        "training_rows": len(X),
        "feature_importances": feature_importances,
    }


if __name__ == "__main__":
    import sys
    from app.database import init_db, SessionLocal
    from app.ml.model_manager import model_manager

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    init_db()
    db = SessionLocal()
    try:
        print("\n" + "=" * 65)
        print("  SERVO-AI: DEMAND FORECASTING ML TRAINING PIPELINE")
        print("=" * 65 + "\n")
        result = train_demand_model(db, model_manager)
        print("\n" + "-" * 65)
        print("  TRAINING COMPLETED SUCCESSFULLY")
        print("-" * 65)
        print(f"  Model Architecture : {result.get('model')}")
        print(f"  Model Version      : {result.get('model_version')}")
        print(f"  Training Samples   : {result.get('training_rows'):,} records")
        print(f"  Accuracy           : {result.get('accuracy_pct')}%")
        print(f"  R² Score           : {result.get('r2_score')}")
        print(f"  Mean Abs Error     : {result.get('mae')} meals")
        print(f"  Root Mean Sq Error : {result.get('rmse')} meals")
        print(f"  MAPE               : {result.get('mape')}%")
        print("\n  Top Feature Importance Ranking:")
        sorted_features = sorted(result.get("feature_importances", {}).items(), key=lambda x: x[1], reverse=True)
        for idx, (feat, imp) in enumerate(sorted_features[:6], 1):
            bar = "█" * int(imp * 30)
            print(f"    {idx}. {feat:<24} {imp * 100:>5.1f}%  {bar}")
        print("=" * 65 + "\n")
    except Exception as exc:
        print(f"\n[ERROR] Training failed: {exc}\n", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()

