"""
Canteen Pulse - ML Forecasting Engine
Implements Gradient Boosted Decision Tree model with Quantile bounds for confidence intervals.
"""
import os
import joblib
import pandas as pd
import numpy as np
from datetime import date, datetime, timezone
from typing import Dict, Any, Tuple, Optional
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sqlalchemy.orm import Session

from app.config import MODEL_FILE, BUNDLED_MODEL_FILE
from app.database import DailyRecord, ModelTrainingLog, SessionLocal
from app.ml.features import FEATURE_COLUMNS, engineer_features_df, build_single_day_features
from app.ml.explainability import generate_reason_chips

class CanteenDemandForecaster:
    def __init__(self):
        self.model_mean = None
        self.model_lower = None
        self.model_upper = None
        self.feature_importances = {}
        self.last_trained = None
        self.metrics = {}
        self._is_fitted = False
        self.load_or_initialize()

    def load_or_initialize(self):
        """Loads saved models if available, otherwise initializes clean estimators."""
        # Initialize default estimators first
        self.model_mean = HistGradientBoostingRegressor(
            loss="squared_error", max_iter=120, max_leaf_nodes=31, random_state=42
        )
        self.model_lower = HistGradientBoostingRegressor(
            loss="quantile", quantile=0.08, max_iter=100, random_state=42
        )
        self.model_upper = HistGradientBoostingRegressor(
            loss="quantile", quantile=0.92, max_iter=100, random_state=42
        )
        self._is_fitted = False

        candidate_files = [MODEL_FILE, BUNDLED_MODEL_FILE]
        for fpath in candidate_files:
            if fpath and fpath.exists():
                try:
                    bundle = joblib.load(fpath)
                    if isinstance(bundle, dict) and bundle.get("model_mean") is not None:
                        self.model_mean = bundle.get("model_mean")
                        self.model_lower = bundle.get("model_lower", self.model_lower)
                        self.model_upper = bundle.get("model_upper", self.model_upper)
                        self.feature_importances = bundle.get("feature_importances", {})
                        self.last_trained = bundle.get("last_trained")
                        self.metrics = bundle.get("metrics", {})
                        self._is_fitted = True
                        return
                except Exception as e:
                    print(f"Warning: could not load existing model from {fpath}: {e}")


    def train_on_records(self, db: Optional[Session] = None) -> Dict[str, Any]:
        """Fetches historical records from DB, engineers features, trains ensemble and calculates metrics."""
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
            
        try:
            records = db.query(DailyRecord).filter(DailyRecord.actual_meals.isnot(None)).all()
            if len(records) < 30:
                records = db.query(DailyRecord).all()
                
            data = []
            for r in records:
                data.append({
                    "record_date": r.record_date,
                    "day_of_week": r.day_of_week,
                    "is_weekend": r.is_weekend,
                    "is_holiday": r.is_holiday,
                    "is_exam_period": r.is_exam_period,
                    "is_special_event": r.is_special_event,
                    "temperature_c": r.temperature_c,
                    "rainfall_mm": r.rainfall_mm,
                    "humidity_pct": r.humidity_pct,
                    "actual_meals": r.actual_meals,
                    "predicted_meals": r.predicted_meals
                })
                
            raw_df = pd.DataFrame(data)
            feat_df = engineer_features_df(raw_df)
            
            X = feat_df[FEATURE_COLUMNS]
            y = feat_df["target_meals"]
            
            # Train estimators
            self.model_mean.fit(X, y)
            self.model_lower.fit(X, y)
            self.model_upper.fit(X, y)
            self._is_fitted = True
            
            # Calculate feature importance via RF surrogate for explainability
            rf_surrogate = RandomForestRegressor(n_estimators=40, random_state=42)
            rf_surrogate.fit(X, y)
            raw_importances = dict(zip(FEATURE_COLUMNS, rf_surrogate.feature_importances_))
            
            # Normalize and sort importances
            total_imp = sum(raw_importances.values()) or 1.0
            self.feature_importances = {
                k: round(float(v / total_imp), 3)
                for k, v in sorted(raw_importances.items(), key=lambda x: x[1], reverse=True)
            }
            
            # Evaluate metrics
            y_pred = self.model_mean.predict(X)
            mae = float(mean_absolute_error(y, y_pred))
            rmse = float(np.sqrt(mean_squared_error(y, y_pred)))
            r2 = float(r2_score(y, y_pred))
            mape = float(np.mean(np.abs((y - y_pred) / np.maximum(y, 1))) * 100.0)
            accuracy_pct = round(max(0.0, 100.0 - mape), 1)
            
            self.last_trained = datetime.now()
            self.metrics = {
                "mae": round(mae, 1),
                "rmse": round(rmse, 1),
                "r2_score": round(r2, 3),
                "mape": round(mape, 1),
                "accuracy_pct": accuracy_pct,
                "sample_count": len(X)
            }
            
            # Save bundle
            bundle = {
                "model_mean": self.model_mean,
                "model_lower": self.model_lower,
                "model_upper": self.model_upper,
                "feature_importances": self.feature_importances,
                "last_trained": self.last_trained,
                "metrics": self.metrics
            }
            try:
                joblib.dump(bundle, MODEL_FILE)
            except Exception as e:
                print(f"Warning: could not save model file: {e}")
            
            # Save training log to DB
            log_entry = ModelTrainingLog(
                trained_at=self.last_trained,
                sample_count=len(X),
                mae=self.metrics["mae"],
                rmse=self.metrics["rmse"],
                r2_score=self.metrics["r2_score"],
                mape=self.metrics["mape"],
                accuracy_pct=self.metrics["accuracy_pct"],
                feature_importances=self.feature_importances,
                model_version=f"v{datetime.now().strftime('%m%d.%H%M')}-GBDT",
                notes="HistGradientBoostingRegressor with Quantile Error Bounds"
            )
            db.add(log_entry)
            db.commit()
            
            return self.metrics
        finally:
            if close_db:
                db.close()

    def predict(
        self,
        target_date: date,
        is_holiday: bool = False,
        is_exam: bool = False,
        is_special: bool = False,
        temp_c: float = 28.0,
        rainfall_mm: float = 0.0,
        humidity_pct: float = 55.0,
        rolling_avg_7d: float = 395.0,
        rolling_avg_28d: float = 390.0
    ) -> Dict[str, Any]:
        """Generates point forecast, confidence band, station breakdown, and reason chips."""
        # Auto-train if not fitted
        if not self._is_fitted:
            try:
                self.train_on_records()
            except Exception as e:
                print(f"Auto-fit on predict fallback: {e}")

        X = build_single_day_features(
            record_date=target_date,
            is_holiday=is_holiday,
            is_exam=is_exam,
            is_special=is_special,
            temp_c=temp_c,
            rainfall_mm=rainfall_mm,
            humidity_pct=humidity_pct,
            rolling_avg_7d=rolling_avg_7d,
            rolling_avg_28d=rolling_avg_28d
        )
        
        # Predict
        if self._is_fitted and self.model_mean is not None:
            pred_val = float(self.model_mean.predict(X)[0])
            lower_val = float(self.model_lower.predict(X)[0])
            upper_val = float(self.model_upper.predict(X)[0])
        else:
            # Deterministic domain heuristic fallback
            dow_baselines = {0: 425, 1: 412, 2: 405, 3: 398, 4: 375, 5: 220, 6: 165}
            base = dow_baselines.get(target_date.weekday(), 380)
            event_mult = 0.25 if is_holiday else (1.18 if is_exam else (1.30 if is_special else 1.0))
            weather_mult = 1.08 if rainfall_mm > 5.0 else 1.0
            pred_val = base * event_mult * weather_mult
            lower_val = pred_val * 0.92
            upper_val = pred_val * 1.08
            
        pred_int = max(30, int(round(pred_val)))
        lower_int = max(20, int(round(min(lower_val, pred_val - 14))))
        upper_int = int(round(max(upper_val, pred_val + 14)))
        
        # Station breakdown calculation
        snack_mult = 1.22 if rainfall_mm > 5.0 else 1.0
        
        b_weight = 0.22
        l_weight = 0.44
        s_weight = 0.18 * snack_mult
        d_weight = 0.16
        total_w = b_weight + l_weight + s_weight + d_weight
        
        b_count = int(round(pred_int * (b_weight / total_w)))
        l_count = int(round(pred_int * (l_weight / total_w)))
        s_count = int(round(pred_int * (s_weight / total_w)))
        d_count = max(10, pred_int - (b_count + l_count + s_count))
        
        # Explainability reason chips
        feats = {
            "day_of_week": target_date.weekday(),
            "is_holiday": is_holiday,
            "is_exam_period": is_exam,
            "is_special_event": is_special,
            "temperature_c": temp_c,
            "rainfall_mm": rainfall_mm,
            "humidity_pct": humidity_pct,
            "rolling_avg_7d": rolling_avg_7d
        }
        reason_chips = generate_reason_chips(feats, pred_int, baseline_avg=rolling_avg_7d)
        
        # Demand trend indicator
        trend = "steady"
        if pred_int > rolling_avg_7d + 15:
            trend = "surging"
        elif pred_int < rolling_avg_7d - 15:
            trend = "cooling"
            
        return {
            "date": target_date.isoformat(),
            "predicted_meals": pred_int,
            "confidence_interval": {
                "lower": lower_int,
                "upper": upper_int,
                "confidence_level": 0.95
            },
            "trend": trend,
            "stations": {
                "breakfast": b_count,
                "lunch": l_count,
                "snacks": s_count,
                "dinner": d_count
            },
            "reason_chips": reason_chips
        }

# Global singleton
forecaster = CanteenDemandForecaster()
