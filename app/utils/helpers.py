"""
Servo-AI - Helper Functions & Utilities
"""
import io
import csv
import math
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from scipy import stats


def get_z_score(confidence_level: float = 0.95) -> float:
    """Calculates normal distribution two-tailed critical z-score"""
    try:
        alpha = 1.0 - confidence_level
        return float(stats.norm.ppf(1.0 - alpha / 2.0))
    except Exception:
        # Standard fallback values
        if confidence_level >= 0.99:
            return 2.576
        elif confidence_level >= 0.95:
            return 1.960
        elif confidence_level >= 0.90:
            return 1.645
        return 1.960


def calculate_confidence_bounds(
    prediction: float,
    confidence_level: float = 0.95,
    residual_std: float = 25.0,
    min_floor: float = 0.0
) -> Tuple[float, float]:
    """Calculates lower and upper statistical confidence bounds."""
    z = get_z_score(confidence_level)
    margin = z * max(5.0, residual_std)
    lower = max(min_floor, round(prediction - margin, 1))
    upper = round(prediction + margin, 1)
    return lower, upper


def parse_demand_csv(file_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Parses and validates CSV content for historical meal demand.
    Expected headers: date, station, menu_item, actual_quantity, (optional: predicted_quantity, weather, temperature, is_holiday, is_weekend, student_attendance, faculty_attendance)
    """
    try:
        text = file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = file_bytes.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("CSV file is empty or has invalid header row.")

    # Normalize header names (lowercase, stripped)
    header_map = {col.strip().lower(): col for col in reader.fieldnames}
    required_cols = ["date", "station", "menu_item", "actual_quantity"]
    for col in required_cols:
        if col not in header_map:
            raise ValueError(f"Missing required CSV column: '{col}'. Required columns are: {', '.join(required_cols)}")

    records = []
    for idx, row in enumerate(reader, start=2):
        try:
            # Parse Date
            raw_date = row[header_map["date"]].strip()
            parsed_date = date.fromisoformat(raw_date)

            station = row[header_map["station"]].strip().lower()
            menu_item = row[header_map["menu_item"]].strip()
            actual_quantity = float(row[header_map["actual_quantity"]].strip())

            # Optional columns
            pred_col = header_map.get("predicted_quantity")
            predicted_quantity = float(row[pred_col].strip()) if (pred_col and row[pred_col].strip()) else None

            weather_col = header_map.get("weather")
            weather = row[weather_col].strip() if (weather_col and row[weather_col].strip()) else "Clear"

            temp_col = header_map.get("temperature") or header_map.get("temperature_c")
            temperature = float(row[temp_col].strip()) if (temp_col and row[temp_col].strip()) else 28.0

            holiday_col = header_map.get("is_holiday")
            is_holiday = row[holiday_col].strip().lower() in ("true", "1", "yes") if (holiday_col and row[holiday_col].strip()) else False

            weekend_col = header_map.get("is_weekend")
            is_weekend = row[weekend_col].strip().lower() in ("true", "1", "yes") if (weekend_col and row[weekend_col].strip()) else (parsed_date.weekday() >= 5)

            student_col = header_map.get("student_attendance")
            student_att = int(float(row[student_col].strip())) if (student_col and row[student_col].strip()) else 3500

            faculty_col = header_map.get("faculty_attendance")
            faculty_att = int(float(row[faculty_col].strip())) if (faculty_col and row[faculty_col].strip()) else 380

            records.append({
                "date": parsed_date,
                "station": station,
                "menu_item": menu_item,
                "predicted_quantity": predicted_quantity,
                "actual_quantity": actual_quantity,
                "weather": weather,
                "temperature": temperature,
                "is_holiday": is_holiday,
                "is_weekend": is_weekend,
                "student_attendance": student_att,
                "faculty_attendance": faculty_att
            })
        except Exception as e:
            raise ValueError(f"Error on CSV row {idx}: {e}")

    if not records:
        raise ValueError("CSV contains no valid data rows.")

    return records


def format_error(error: str, message: str) -> Dict[str, Any]:
    """Helper to return uniform error dictionaries"""
    return {
        "success": False,
        "error": error,
        "message": message
    }
