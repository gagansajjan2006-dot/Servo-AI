"""
Servo-AI - CSV Batch Forecasting & Processing Service
Ingests CSV files with calendar/weather/historical conditions and produces comprehensive demand predictions.
"""
import io
import logging
from datetime import date, datetime
from typing import Dict, Any, List, Optional, Union

import pandas as pd
from sqlalchemy.orm import Session

from app.ml.model import forecaster
from app.services.procurement_service import procurement_service
from app.database import SessionLocal

logger = logging.getLogger("servo_ai.csv_service")


# Standard column mappings to support flexible user CSV column names
COLUMN_ALIASES = {
    "date": ["date", "target_date", "record_date", "day", "forecast_date"],
    "temperature_c": ["temperature_c", "temp_c", "temperature", "temp", "temp_deg"],
    "rainfall_mm": ["rainfall_mm", "rain_mm", "rainfall", "rain", "precipitation_mm", "precipitation"],
    "humidity_pct": ["humidity_pct", "humidity", "hum_pct", "hum"],
    "is_holiday": ["is_holiday", "holiday", "is_vacation", "vacation"],
    "is_exam": ["is_exam", "is_exam_period", "exam", "exam_period", "finals"],
    "is_special": ["is_special", "is_special_event", "is_fest", "fest", "special_event", "event"],
    "rolling_avg_7d": ["rolling_avg_7d", "roll_7d", "prev_7d_avg", "7d_avg", "rolling_7d"],
    "rolling_avg_28d": ["rolling_avg_28d", "roll_28d", "prev_28d_avg", "28d_avg", "rolling_28d"],
}


def _normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Maps user-provided column names to standard internal column names."""
    col_map = {}
    lower_cols = {col.strip().lower(): col for col in df.columns}
    
    for standard_name, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias.lower() in lower_cols:
                col_map[lower_cols[alias.lower()]] = standard_name
                break
                
    renamed_df = df.rename(columns=col_map)
    return renamed_df


def _parse_bool(val: Any) -> bool:
    """Robust boolean parser for CSV values (handles 1/0, true/false, yes/no, T/F)."""
    if pd.isna(val) or val is None:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(int(val))
    str_val = str(val).strip().lower()
    return str_val in ["1", "true", "t", "yes", "y", "holiday", "exam", "fest", "event"]


def generate_sample_csv_content() -> str:
    """Generates a realistic 14-day sample input CSV string."""
    sample_rows = [
        "date,temperature_c,rainfall_mm,humidity_pct,is_holiday,is_exam,is_special,rolling_avg_7d,rolling_avg_28d,notes",
        "2026-09-01,29.5,0.0,52,0,0,0,410,405,Regular Tuesday - Standard classes",
        "2026-09-02,30.0,0.0,50,0,0,0,412,406,Regular Wednesday - Full attendance",
        "2026-09-03,26.0,18.5,85,0,0,0,408,405,Heavy Monsoon Storm - Expect hot snack spike",
        "2026-09-04,27.5,6.0,78,0,0,0,395,402,Friday Afternoon - Pre-weekend taper",
        "2026-09-05,28.0,0.0,60,0,0,0,240,380,Saturday - Hostel and weekend diners",
        "2026-09-06,29.0,0.0,55,0,0,0,180,375,Sunday - Low campus headcount",
        "2026-09-07,28.5,0.0,58,0,1,0,425,410,Monday - Midterm Exam Week Begins (+15% surge)",
        "2026-09-08,27.0,12.0,80,0,1,0,435,412,Tuesday - Midterms + Rainy afternoon",
        "2026-09-09,28.0,0.0,62,0,1,0,440,415,Wednesday - Midterms Peak study sessions",
        "2026-09-10,29.0,0.0,55,0,1,0,430,414,Thursday - Midterms final review",
        "2026-09-11,28.0,0.0,58,0,0,1,460,420,Friday - Annual Campus Cultural Fest (+35% rush)",
        "2026-09-12,27.5,0.0,60,0,0,1,380,418,Saturday - Cultural Fest Day 2 Visitors",
        "2026-09-13,29.0,0.0,50,1,0,0,95,390,Sunday - National Holiday / Campus Closed",
        "2026-09-14,28.5,0.0,55,0,0,0,415,408,Monday - Regular Academic Week Restart",
    ]
    return "\n".join(sample_rows)


class CSVBatchForecaster:
    """Processes input CSV data and outputs rich predictive meal forecasts and grocery lists."""

    def __init__(self):
        self.forecaster = forecaster

    def process_csv(
        self,
        csv_source: Union[str, bytes, io.StringIO, io.BytesIO, pd.DataFrame],
        safety_buffer_pct: float = 5.0,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Parses input CSV, generates predictions for each row, and returns structured data & DataFrame.
        """
        # Read into DataFrame
        if isinstance(csv_source, pd.DataFrame):
            raw_df = csv_source.copy()
        elif isinstance(csv_source, bytes):
            raw_df = pd.read_csv(io.BytesIO(csv_source))
        elif isinstance(csv_source, str):
            if "\n" in csv_source or "," in csv_source:
                raw_df = pd.read_csv(io.StringIO(csv_source))
            else:
                raw_df = pd.read_csv(csv_source)
        else:
            raw_df = pd.read_csv(csv_source)

        if raw_df.empty:
            raise ValueError("Input CSV is empty. Please provide at least one row of forecast conditions.")

        df = _normalize_column_names(raw_df)

        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        predictions_list = []
        enriched_rows = []

        try:
            today_default = date.today()

            for idx, row in df.iterrows():
                # Parse date
                raw_date = row.get("date")
                if pd.isna(raw_date) or not raw_date:
                    target_date = today_default
                else:
                    try:
                        target_date = pd.to_datetime(raw_date).date()
                    except Exception:
                        target_date = today_default

                # Parse weather & calendar parameters with safe fallbacks
                temp_c = float(row.get("temperature_c", 28.0) if not pd.isna(row.get("temperature_c")) else 28.0)
                rainfall_mm = float(row.get("rainfall_mm", 0.0) if not pd.isna(row.get("rainfall_mm")) else 0.0)
                humidity_pct = float(row.get("humidity_pct", 55.0) if not pd.isna(row.get("humidity_pct")) else 55.0)

                is_hol = _parse_bool(row.get("is_holiday", False))
                is_ex = _parse_bool(row.get("is_exam", False))
                is_sp = _parse_bool(row.get("is_special", False))

                roll7 = float(row.get("rolling_avg_7d", 395.0) if not pd.isna(row.get("rolling_avg_7d")) else 395.0)
                roll28 = float(row.get("rolling_avg_28d", 390.0) if not pd.isna(row.get("rolling_avg_28d")) else 390.0)

                # Run Servo AI ML Forecaster
                pred_result = self.forecaster.predict(
                    target_date=target_date,
                    is_holiday=is_hol,
                    is_exam=is_ex,
                    is_special=is_sp,
                    temp_c=temp_c,
                    rainfall_mm=rainfall_mm,
                    humidity_pct=humidity_pct,
                    rolling_avg_7d=roll7,
                    rolling_avg_28d=roll28
                )

                predicted_meals = pred_result["predicted_meals"]
                ci_lower = pred_result["confidence_interval"]["lower"]
                ci_upper = pred_result["confidence_interval"]["upper"]
                trend = pred_result["trend"]
                stations = pred_result["stations"]

                # Extract top reasons for explainability
                reasons = [r["text"] for r in pred_result.get("reason_chips", [])]
                reason_summary = " | ".join(reasons) if reasons else "Normal baseline operations"

                # Calculate pantry procurement estimates
                proc_data = procurement_service.calculate_procurement_for_meals(
                    db=db,
                    station_counts=stations,
                    safety_buffer_pct=safety_buffer_pct
                )

                # Key grocery staple items extraction
                staples_summary = {
                    "rice": "0 kg",
                    "dal": "0 kg",
                    "veggies": "0 kg",
                    "milk": "0 L",
                    "oil": "0 L"
                }
                for item in proc_data.get("items", []):
                    ing_name = item.get("ingredient_name", "").lower()
                    qty_str = f"{item['buffered_quantity']} {item['unit']}"
                    if "rice" in ing_name and staples_summary["rice"] == "0 kg":
                        staples_summary["rice"] = qty_str
                    elif ("dal" in ing_name or "pulse" in ing_name) and staples_summary["dal"] == "0 kg":
                        staples_summary["dal"] = qty_str
                    elif "veg" in ing_name and staples_summary["veggies"] == "0 kg":
                        staples_summary["veggies"] = qty_str
                    elif "milk" in ing_name and staples_summary["milk"] == "0 L":
                        staples_summary["milk"] = qty_str
                    elif ("oil" in ing_name or "ghee" in ing_name) and staples_summary["oil"] == "0 L":
                        staples_summary["oil"] = qty_str

                row_dict = {
                    "row_index": idx + 1,
                    "date": target_date.isoformat(),
                    "day_name": target_date.strftime("%A"),
                    "predicted_meals": predicted_meals,
                    "lower_bound_95ci": ci_lower,
                    "upper_bound_95ci": ci_upper,
                    "trend": trend,
                    "breakfast_covers": stations.get("breakfast", 0),
                    "lunch_covers": stations.get("lunch", 0),
                    "snacks_covers": stations.get("snacks", 0),
                    "dinner_covers": stations.get("dinner", 0),
                    "rice_staple_kg": staples_summary["rice"],
                    "dal_staple_kg": staples_summary["dal"],
                    "veggies_kg": staples_summary["veggies"],
                    "milk_litres": staples_summary["milk"],
                    "cooking_oil_litres": staples_summary["oil"],
                    "total_ingredient_cost_inr": proc_data.get("total_estimated_cost", 0.0),
                    "primary_reason": reasons[0] if reasons else "Normal Baseline",
                    "all_reasons": reason_summary,
                    "input_temperature_c": temp_c,
                    "input_rainfall_mm": rainfall_mm,
                    "input_is_holiday": is_hol,
                    "input_is_exam": is_ex,
                    "input_is_special": is_sp,
                }

                predictions_list.append(row_dict)

                # Append to flat tabular structure for output DataFrame
                enriched_record = dict(row)
                enriched_record.update({
                    "PREDICTED_MEALS": predicted_meals,
                    "CONFIDENCE_LOWER_95": ci_lower,
                    "CONFIDENCE_UPPER_95": ci_upper,
                    "DEMAND_TREND": trend.upper(),
                    "BREAKFAST_MEALS": stations.get("breakfast", 0),
                    "LUNCH_MEALS": stations.get("lunch", 0),
                    "SNACKS_MEALS": stations.get("snacks", 0),
                    "DINNER_MEALS": stations.get("dinner", 0),
                    "RICE_REQUISITION": staples_summary["rice"],
                    "DAL_REQUISITION": staples_summary["dal"],
                    "VEGETABLES_REQUISITION": staples_summary["veggies"],
                    "DAIRY_MILK_REQUISITION": staples_summary["milk"],
                    "ESTIMATED_GROCERY_COST": proc_data.get("total_estimated_cost", 0.0),
                    "EXPLAINABILITY_REASON": reasons[0] if reasons else "Normal baseline",
                })
                enriched_rows.append(enriched_record)

            output_df = pd.DataFrame(enriched_rows)

            # Overall summary metrics
            total_predicted_meals = sum(p["predicted_meals"] for p in predictions_list)
            avg_daily_meals = round(total_predicted_meals / max(1, len(predictions_list)), 1)
            total_est_cost = sum(p["total_ingredient_cost_inr"] for p in predictions_list)

            summary = {
                "total_rows_processed": len(predictions_list),
                "total_predicted_meals": total_predicted_meals,
                "average_daily_meals": avg_daily_meals,
                "total_estimated_procurement_cost": round(total_est_cost, 2),
                "safety_buffer_pct": safety_buffer_pct,
                "model_architecture": "HistGradientBoostingRegressor Ensemble + Quantile Bounds",
                "processed_at": datetime.now().isoformat(),
            }

            return {
                "success": True,
                "summary": summary,
                "predictions": predictions_list,
                "columns": list(output_df.columns),
                "output_dataframe": output_df,
            }

        finally:
            if close_db:
                db.close()

    def export_output_csv(self, result: Dict[str, Any]) -> str:
        """Exports the processed DataFrame as a CSV string."""
        if "output_dataframe" not in result or result["output_dataframe"].empty:
            return ""
        return result["output_dataframe"].to_csv(index=False)


# Global service singleton
csv_batch_forecaster = CSVBatchForecaster()
