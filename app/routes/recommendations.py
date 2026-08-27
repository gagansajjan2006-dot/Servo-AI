"""
Servo-AI - AI Recommendations Route
Generates data-driven operational recommendations from prediction and historical data.
"""
import logging
from datetime import date, datetime, timedelta, timezone
from typing import List, Dict, Any
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models import MealDemand, FoodWaste, Prediction
from app.config import STATIONS, STATION_MAP, CANTEEN_SETTINGS
from app.schemas import RecommendationsResponse

logger = logging.getLogger("servo_ai.routes.recommendations")

router = APIRouter(prefix="/api", tags=["Recommendations"])


@router.get(
    "/recommendations",
    response_model=RecommendationsResponse,
    summary="AI Recommendations",
    description="Generates operational recommendations based on prediction data, waste patterns, and demand trends.",
)
def get_recommendations(db: Session = Depends(get_db)):
    """Generate data-driven recommendations from actual database values."""
    recommendations = []
    today = date.today()
    week_ago = today - timedelta(days=7)

    # 1. Analyze recent demand trends per menu item
    recent_demand = (
        db.query(
            MealDemand.menu_item,
            MealDemand.station,
            func.avg(MealDemand.actual_quantity).label("avg_demand"),
            func.avg(MealDemand.predicted_quantity).label("avg_predicted"),
        )
        .filter(MealDemand.date >= week_ago)
        .group_by(MealDemand.menu_item, MealDemand.station)
        .all()
    )

    for item in recent_demand:
        if item.avg_predicted and item.avg_predicted > 0 and item.avg_demand:
            diff_pct = ((item.avg_demand - item.avg_predicted) / item.avg_predicted) * 100

            if diff_pct > 8:
                recommendations.append({
                    "id": str(uuid.uuid4())[:8],
                    "type": "adjustment",
                    "title": "Increase Preparation",
                    "message": f"Increase {item.menu_item} preparation by {round(abs(diff_pct))}%. Actual demand has consistently exceeded predictions at the {item.station} station.",
                    "impact": "high" if diff_pct > 15 else "medium",
                    "category": "kitchen",
                    "confidence": 0.92,
                })
            elif diff_pct < -8:
                recommendations.append({
                    "id": str(uuid.uuid4())[:8],
                    "type": "adjustment",
                    "title": "Reduce Preparation",
                    "message": f"Reduce {item.menu_item} preparation by {round(abs(diff_pct))}%. Demand has been below predictions at the {item.station} station.",
                    "impact": "medium",
                    "category": "procurement",
                    "confidence": 0.88,
                })

    # 2. Station load analysis
    station_totals = (
        db.query(
            MealDemand.station,
            func.sum(MealDemand.actual_quantity).label("total"),
        )
        .filter(MealDemand.date >= week_ago)
        .group_by(MealDemand.station)
        .order_by(desc("total"))
        .all()
    )

    if station_totals:
        peak = station_totals[0]
        station_name = STATION_MAP.get(peak.station, {}).get("name", peak.station)
        recommendations.append({
            "id": str(uuid.uuid4())[:8],
            "type": "operational",
            "title": "Peak Station Alert",
            "message": f"{station_name} is the busiest station with {int(peak.total)} meals served this week. Ensure adequate staffing during peak window.",
            "impact": "high",
            "category": "station",
            "confidence": 0.95,
        })

    # 3. Food waste analysis
    waste_items = (
        db.query(
            FoodWaste.menu_item,
            FoodWaste.station,
            func.avg(FoodWaste.waste_percentage).label("avg_waste_pct"),
            func.sum(FoodWaste.wasted_quantity).label("total_wasted"),
        )
        .filter(FoodWaste.date >= week_ago)
        .group_by(FoodWaste.menu_item, FoodWaste.station)
        .having(func.avg(FoodWaste.waste_percentage) > 10)
        .order_by(desc("avg_waste_pct"))
        .limit(3)
        .all()
    )

    for wi in waste_items:
        recommendations.append({
            "id": str(uuid.uuid4())[:8],
            "type": "alert",
            "title": "High Waste Alert",
            "message": f"Food waste is high for {wi.menu_item} ({round(float(wi.avg_waste_pct), 1)}% average). Consider reducing preparation quantity by {round(float(wi.avg_waste_pct) * 0.5)}%.",
            "impact": "high",
            "category": "waste",
            "confidence": 0.90,
        })

    # 4. Tomorrow's demand trend
    yesterday = today - timedelta(days=1)
    yesterday_total = (
        db.query(func.sum(MealDemand.actual_quantity))
        .filter(MealDemand.date == yesterday)
        .scalar()
    )
    
    daily_totals = (
        db.query(func.sum(MealDemand.actual_quantity).label("day_sum"))
        .filter(MealDemand.date >= week_ago)
        .group_by(MealDemand.date)
        .all()
    )

    if yesterday_total and daily_totals:
        try:
            yesterday_val = float(yesterday_total)
            sums = [float(dt.day_sum or 0) for dt in daily_totals if dt.day_sum]
            week_val = sum(sums) / len(sums) if sums else 0.0
            if week_val > 0:
                if yesterday_val > week_val * 1.05:
                    recommendations.append({
                        "id": str(uuid.uuid4())[:8],
                        "type": "operational",
                        "title": "Demand Trend Rising",
                        "message": f"Demand is trending upward. Yesterday's total ({int(yesterday_val)} meals) exceeded the weekly average ({int(week_val)} meals). Prepare for potentially higher demand tomorrow.",
                        "impact": "medium",
                        "category": "kitchen",
                        "confidence": 0.85,
                    })
                elif yesterday_val < week_val * 0.95:
                    recommendations.append({
                        "id": str(uuid.uuid4())[:8],
                        "type": "operational",
                        "title": "Demand Trend Declining",
                        "message": f"Demand is trending downward. Yesterday's total ({int(yesterday_val)} meals) was below the weekly average ({int(week_val)} meals). Consider reducing preparation.",
                        "impact": "low",
                        "category": "kitchen",
                        "confidence": 0.80,
                    })
        except (TypeError, ValueError):
            pass

    # If no data-driven recommendations, provide operational defaults
    if not recommendations:
        recommendations.append({
            "id": str(uuid.uuid4())[:8],
            "type": "operational",
            "title": "Insufficient Data",
            "message": "Not enough historical data to generate specific recommendations. Seed or upload demand data to enable AI recommendations.",
            "impact": "low",
            "category": "kitchen",
            "confidence": 0.5,
        })

    return {
        "generated_at": datetime.now(timezone.utc),
        "count": len(recommendations),
        "recommendations": recommendations,
    }
