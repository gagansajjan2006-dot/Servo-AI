"""
Servo-AI - ML Prediction Module
Generates demand predictions using the loaded model with confidence bounds.
"""
import logging
from datetime import date
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd

from app.config import CANTEEN_SETTINGS, STATION_MAP
from app.utils.helpers import calculate_confidence_bounds

logger = logging.getLogger("servo_ai.predict")


def predict_demand(
    model_manager,
    prediction_date: date,
    station: str,
    menu_item: str,
    temperature: float = 28.0,
    weather: str = "Clear",
    is_holiday: bool = False,
    student_attendance: int = 3500,
    faculty_attendance: int = 380,
    confidence_level: float = 0.95,
    previous_day_demand: Optional[float] = None,
    previous_week_demand: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Generates a demand prediction for a specific station/menu_item.
    Falls back to a baseline heuristic if no trained model is available.
    """
    model = model_manager.get_model()
    metadata = model_manager.metadata

    is_weekend = prediction_date.weekday() >= 5
    day_of_week = prediction_date.weekday()
    month = prediction_date.month

    if model is not None and metadata.get("label_encoders"):
        # Use trained ML model
        encoders = metadata["label_encoders"]

        # Safely encode categorical values
        try:
            station_enc = encoders["station"].transform([station])[0]
        except (ValueError, KeyError):
            station_enc = 0
        try:
            item_enc = encoders["menu_item"].transform([menu_item])[0]
        except (ValueError, KeyError):
            item_enc = 0
        try:
            weather_enc = encoders["weather"].transform([weather.capitalize()])[0]
        except (ValueError, KeyError):
            weather_enc = 0

        prev_day = previous_day_demand if previous_day_demand is not None else 200.0
        prev_week = previous_week_demand if previous_week_demand is not None else 200.0

        features = np.array([[
            day_of_week,
            month,
            station_enc,
            item_enc,
            temperature,
            weather_enc,
            1 if is_weekend else 0,
            1 if is_holiday else 0,
            student_attendance,
            faculty_attendance,
            prev_day,
            prev_week,
        ]])

        predicted = float(model.predict(features)[0])
        residual_std = metadata.get("residual_std", 25.0)

    else:
        # Fallback baseline model
        predicted = _baseline_predict(
            station=station,
            day_of_week=day_of_week,
            is_holiday=is_holiday,
            is_weekend=is_weekend,
            student_attendance=student_attendance,
            faculty_attendance=faculty_attendance,
            temperature=temperature,
            weather=weather,
        )
        residual_std = predicted * 0.08  # 8% uncertainty for baseline

    predicted = max(5, round(predicted))
    lower, upper = calculate_confidence_bounds(
        prediction=predicted,
        confidence_level=confidence_level,
        residual_std=residual_std,
        min_floor=0,
    )

    return {
        "station": station,
        "menu_item": menu_item,
        "predicted_quantity": predicted,
        "lower_bound": round(lower),
        "upper_bound": round(upper),
        "confidence": confidence_level,
        "date": prediction_date.isoformat(),
    }


def predict_daily_forecast(
    model_manager,
    prediction_date: date,
    temperature: float = 28.0,
    weather: str = "Clear",
    is_holiday: bool = False,
    student_attendance: int = 3500,
    faculty_attendance: int = 380,
) -> Dict[str, Any]:
    """
    Generates a full daily forecast for all 4 stations.
    Uses station daily_share percentages from configuration.
    """
    total_population = (
        CANTEEN_SETTINGS["student_population"]
        + CANTEEN_SETTINGS["faculty_staff_population"]
    )
    # Base daily meal estimate from attendance ratio
    attendance_ratio = (student_attendance + faculty_attendance) / max(1, total_population)

    # Weekday/weekend factor
    is_weekend = prediction_date.weekday() >= 5
    base_factor = 0.35 if is_weekend else 0.68
    if is_holiday:
        base_factor *= 0.25

    # Weather factor
    weather_lower = weather.lower()
    weather_mult = 1.0
    if "rain" in weather_lower or "storm" in weather_lower:
        weather_mult = 1.08
    elif temperature > 35:
        weather_mult = 0.95

    total_estimated = int(total_population * attendance_ratio * base_factor * weather_mult)

    stations = []
    for st_id, st_config in STATION_MAP.items():
        share = st_config["daily_share"]
        expected = int(total_estimated * share)
        stations.append({
            "station": st_id,
            "station_name": st_config["name"],
            "expected_demand": expected,
            "peak_window": st_config["peak_window"],
            "menu": st_config["menu"],
        })

    return {
        "date": prediction_date.isoformat(),
        "total_expected_meals": total_estimated,
        "stations": stations,
    }


def _baseline_predict(
    station: str,
    day_of_week: int,
    is_holiday: bool,
    is_weekend: bool,
    student_attendance: int,
    faculty_attendance: int,
    temperature: float,
    weather: str,
) -> float:
    """Deterministic baseline predictor when no ML model is available."""
    # Base demands per station per weekday
    station_bases = {
        "breakfast": {0: 160, 1: 155, 2: 150, 3: 148, 4: 140, 5: 85, 6: 65},
        "lunch":     {0: 320, 1: 310, 2: 305, 3: 300, 4: 285, 5: 170, 6: 130},
        "snacks":    {0: 135, 1: 130, 2: 125, 3: 123, 4: 115, 5: 70, 6: 55},
        "dinner":    {0: 120, 1: 115, 2: 112, 3: 110, 4: 105, 5: 65, 6: 50},
    }

    base = station_bases.get(station, station_bases["lunch"]).get(day_of_week, 200)

    # Attendance scaling
    normal_total = 3500 + 380
    actual_total = student_attendance + faculty_attendance
    att_ratio = actual_total / normal_total
    base *= att_ratio

    # Holiday/event effects
    if is_holiday:
        base *= 0.25

    # Weather effects
    weather_lower = weather.lower()
    if "rain" in weather_lower or "storm" in weather_lower:
        if station == "snacks":
            base *= 1.22
        else:
            base *= 1.05

    return max(5, base)
