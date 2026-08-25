"""
Canteen Pulse - Explainability Layer (Reason Chips Engine)
Translates model feature attributions, weather deltas, and calendar context into human-readable reason chips.
"""
from typing import List, Dict, Any
import numpy as np

def generate_reason_chips(
    features_dict: Dict[str, Any],
    predicted_count: int,
    baseline_avg: float = 380.0
) -> List[Dict[str, Any]]:
    """
    Computes feature contribution deltas and translates them into crisp, kitchen-friendly reason chips.
    """
    chips = []
    
    dow = features_dict.get("day_of_week", 0)
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dname = day_names[dow]
    
    dow_baselines = {0: 425, 1: 412, 2: 405, 3: 398, 4: 375, 5: 220, 6: 165}
    base = dow_baselines.get(dow, 380)
    
    # 1. Day of Week Effect
    dow_diff_pct = round(((base - baseline_avg) / baseline_avg) * 100, 1)
    if dow in [0, 1]:
        chips.append({
            "icon": "calendar",
            "text": f"📅 {dname} Peak (+{dow_diff_pct}%)",
            "type": "positive",
            "category": "calendar",
            "delta_pct": dow_diff_pct
        })
    elif dow in [5, 6]:
        chips.append({
            "icon": "calendar",
            "text": f"📅 Weekend Shift ({dow_diff_pct}%)",
            "type": "negative",
            "category": "calendar",
            "delta_pct": dow_diff_pct
        })
    elif dow == 4:
        chips.append({
            "icon": "calendar",
            "text": f"📅 Friday Taper ({dow_diff_pct}%)",
            "type": "neutral",
            "category": "calendar",
            "delta_pct": dow_diff_pct
        })
    else:
        chips.append({
            "icon": "calendar",
            "text": f"📅 {dname} Midweek Steady",
            "type": "neutral",
            "category": "calendar",
            "delta_pct": dow_diff_pct
        })

    # 2. Weather Effect
    rain = features_dict.get("rainfall_mm", 0.0)
    temp = features_dict.get("temperature_c", 28.0)
    
    if rain > 20.0:
        chips.append({
            "icon": "cloud-rain",
            "text": f"🌧️ Heavy Rain (+9% Snack/Soup Surge)",
            "type": "positive",
            "category": "weather",
            "delta_pct": 9.0
        })
    elif rain > 5.0:
        chips.append({
            "icon": "cloud-drizzle",
            "text": f"🌦️ Light Rain (+5% Hot Beverages)",
            "type": "positive",
            "category": "weather",
            "delta_pct": 5.0
        })
    elif temp > 33.0:
        chips.append({
            "icon": "sun",
            "text": f"☀️ High Heat {temp}°C (+15% Cold Drinks)",
            "type": "neutral",
            "category": "weather",
            "delta_pct": 6.0
        })
    elif temp < 18.0:
        chips.append({
            "icon": "thermometer-snowflake",
            "text": f"❄️ Cool Weather {temp}°C (+8% Hot Breakfast)",
            "type": "positive",
            "category": "weather",
            "delta_pct": 8.0
        })

    # 3. Academic Calendar / Event Effect
    is_hol = bool(features_dict.get("is_holiday", False))
    is_ex = bool(features_dict.get("is_exam_period", False))
    is_sp = bool(features_dict.get("is_special_event", False))
    
    if is_hol:
        chips.append({
            "icon": "coffee",
            "text": f"🎉 Campus Holiday (-75% Mess Mode)",
            "type": "negative",
            "category": "event",
            "delta_pct": -75.0
        })
    elif is_ex:
        chips.append({
            "icon": "book-open",
            "text": f"📚 Exam Schedule (+16% Extended Study)",
            "type": "positive",
            "category": "event",
            "delta_pct": 16.0
        })
    elif is_sp:
        chips.append({
            "icon": "trophy",
            "text": f"⭐ Campus Fest / Event (+28% Volume)",
            "type": "positive",
            "category": "event",
            "delta_pct": 28.0
        })

    # 4. Historical Trend baseline chip
    roll7 = features_dict.get("rolling_avg_7d", baseline_avg)
    chips.append({
        "icon": "trending-up",
        "text": f"📈 7-Day Baseline: ~{int(round(roll7))} meals",
        "type": "neutral",
        "category": "trend",
        "delta_pct": 0.0
    })

    return chips
