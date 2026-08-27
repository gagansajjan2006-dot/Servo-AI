"""
Servo-AI - CRUD Operations Layer
Encapsulates all SQLAlchemy database queries used by route handlers.
"""
import logging
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models import (
    User, MealDemand, Prediction, FoodWaste, Feedback,
    DailyRecord, ModelTrainingLog
)

logger = logging.getLogger("servo_ai.crud")


# ==========================================
# User CRUD
# ==========================================

def create_user(db: Session, name: str, email: str, role: str = "staff") -> User:
    user = User(name=name, email=email, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


# ==========================================
# MealDemand CRUD
# ==========================================

def create_meal_demand(db: Session, data: Dict[str, Any]) -> MealDemand:
    record = MealDemand(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def create_meal_demands_bulk(db: Session, records: List[Dict[str, Any]]) -> int:
    objects = [MealDemand(**r) for r in records]
    db.bulk_save_objects(objects)
    db.commit()
    return len(objects)


def get_meal_demands(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    station: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[MealDemand]:
    query = db.query(MealDemand)
    if station:
        query = query.filter(MealDemand.station == station)
    if start_date:
        query = query.filter(MealDemand.date >= start_date)
    if end_date:
        query = query.filter(MealDemand.date <= end_date)
    return query.order_by(desc(MealDemand.date)).offset(skip).limit(limit).all()


def get_meal_demands_by_date(db: Session, target_date: date) -> List[MealDemand]:
    return (
        db.query(MealDemand)
        .filter(MealDemand.date == target_date)
        .order_by(MealDemand.station, MealDemand.menu_item)
        .all()
    )


def get_meal_demand_count(db: Session) -> int:
    return db.query(MealDemand).count()


def get_all_meal_demands_df_data(db: Session) -> List[MealDemand]:
    """Returns all meal demand records for ML training."""
    return db.query(MealDemand).order_by(MealDemand.date).all()


# ==========================================
# Prediction CRUD
# ==========================================

def create_prediction(db: Session, data: Dict[str, Any]) -> Prediction:
    record = Prediction(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_predictions_by_date(db: Session, target_date: date) -> List[Prediction]:
    return (
        db.query(Prediction)
        .filter(Prediction.prediction_date == target_date)
        .all()
    )


# ==========================================
# FoodWaste CRUD
# ==========================================

def create_food_waste(db: Session, data: Dict[str, Any]) -> FoodWaste:
    record = FoodWaste(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_food_waste_records(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    station: Optional[str] = None,
) -> List[FoodWaste]:
    query = db.query(FoodWaste)
    if station:
        query = query.filter(FoodWaste.station == station)
    return query.order_by(desc(FoodWaste.date)).offset(skip).limit(limit).all()


def get_food_waste_summary(db: Session) -> Dict[str, Any]:
    """Aggregated food waste summary with top 5 wasted items."""
    totals = db.query(
        func.sum(FoodWaste.prepared_quantity).label("total_prepared"),
        func.sum(FoodWaste.sold_quantity).label("total_sold"),
        func.sum(FoodWaste.wasted_quantity).label("total_wasted"),
    ).first()

    total_prepared = float(totals.total_prepared or 0)
    total_sold = float(totals.total_sold or 0)
    total_wasted = float(totals.total_wasted or 0)
    avg_waste_pct = round((total_wasted / total_prepared * 100), 2) if total_prepared > 0 else 0.0

    # Top 5 wasted items
    top_items = (
        db.query(
            FoodWaste.menu_item,
            FoodWaste.station,
            func.sum(FoodWaste.wasted_quantity).label("total_wasted"),
            func.sum(FoodWaste.prepared_quantity).label("total_prepared"),
            func.avg(FoodWaste.waste_percentage).label("avg_waste_pct"),
        )
        .group_by(FoodWaste.menu_item, FoodWaste.station)
        .order_by(desc("total_wasted"))
        .limit(5)
        .all()
    )

    top_wasted_items = [
        {
            "menu_item": item.menu_item,
            "station": item.station,
            "total_wasted": round(float(item.total_wasted), 1),
            "total_prepared": round(float(item.total_prepared), 1),
            "average_waste_percentage": round(float(item.avg_waste_pct), 2),
        }
        for item in top_items
    ]

    return {
        "total_prepared": round(total_prepared, 1),
        "total_sold": round(total_sold, 1),
        "total_wasted": round(total_wasted, 1),
        "average_waste_percentage": avg_waste_pct,
        "top_wasted_items": top_wasted_items,
    }


# ==========================================
# Feedback CRUD
# ==========================================

def create_feedback(db: Session, data: Dict[str, Any]) -> Feedback:
    record = Feedback(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ==========================================
# Analytics Queries
# ==========================================

def get_dashboard_stats(db: Session) -> Dict[str, Any]:
    """Computes aggregated dashboard statistics from real data."""
    today = date.today()

    # Today's actual demand
    today_demand_result = (
        db.query(func.sum(MealDemand.actual_quantity))
        .filter(MealDemand.date == today)
        .scalar()
    )
    today_demand = int(today_demand_result or 0)

    # Today's predicted demand
    today_predicted_result = (
        db.query(func.sum(Prediction.predicted_quantity))
        .filter(Prediction.prediction_date == today)
        .scalar()
    )
    predicted_demand = int(today_predicted_result or 0)

    # If no predictions stored for today, use most recent day with data
    if predicted_demand == 0 and today_demand == 0:
        latest_date = db.query(func.max(MealDemand.date)).scalar()
        if latest_date:
            today_demand = int(
                db.query(func.sum(MealDemand.actual_quantity))
                .filter(MealDemand.date == latest_date)
                .scalar() or 0
            )

    # Average waste percentage
    waste_summary = get_food_waste_summary(db)
    avg_waste_pct = waste_summary["average_waste_percentage"]

    # Food saved estimate (difference between predicted and wasted)
    food_saved = int(waste_summary["total_prepared"] - waste_summary["total_sold"] - waste_summary["total_wasted"]) if waste_summary["total_prepared"] > 0 else 0
    food_saved = max(0, int(waste_summary["total_wasted"] * 0.3))  # Estimate: 30% reduction from AI

    # Peak station
    peak_station_result = (
        db.query(
            MealDemand.station,
            func.sum(MealDemand.actual_quantity).label("total"),
        )
        .group_by(MealDemand.station)
        .order_by(desc("total"))
        .first()
    )
    peak_station = peak_station_result.station if peak_station_result else "lunch"

    # Peak menu item
    peak_item_result = (
        db.query(
            MealDemand.menu_item,
            func.sum(MealDemand.actual_quantity).label("total"),
        )
        .group_by(MealDemand.menu_item)
        .order_by(desc("total"))
        .first()
    )
    peak_menu_item = peak_item_result.menu_item if peak_item_result else "Chicken Biryani"

    return {
        "today_demand": today_demand,
        "predicted_demand": predicted_demand,
        "average_waste_percentage": avg_waste_pct,
        "food_saved_estimate": food_saved,
        "peak_station": peak_station,
        "peak_menu_item": peak_menu_item,
    }


def get_weekly_analytics(db: Session) -> Dict[str, Any]:
    """Returns 7-day demand trend."""
    today = date.today()
    start = today - timedelta(days=6)

    records = (
        db.query(
            MealDemand.date,
            func.sum(MealDemand.actual_quantity).label("actual"),
            func.sum(MealDemand.predicted_quantity).label("predicted"),
        )
        .filter(MealDemand.date >= start, MealDemand.date <= today)
        .group_by(MealDemand.date)
        .order_by(MealDemand.date)
        .all()
    )

    # Get waste data for the same period
    waste_by_date = {}
    waste_records = (
        db.query(
            FoodWaste.date,
            func.avg(FoodWaste.waste_percentage).label("avg_waste"),
        )
        .filter(FoodWaste.date >= start, FoodWaste.date <= today)
        .group_by(FoodWaste.date)
        .all()
    )
    for wr in waste_records:
        waste_by_date[wr.date] = round(float(wr.avg_waste), 1)

    trend = []
    total_meals = 0
    for r in records:
        actual = int(r.actual or 0)
        total_meals += actual
        trend.append({
            "date": r.date.isoformat(),
            "day_name": r.date.strftime("%A"),
            "actual_meals": actual,
            "predicted_meals": int(r.predicted or 0),
            "waste_percentage": waste_by_date.get(r.date),
        })

    avg_daily = round(total_meals / max(1, len(records)), 1)

    return {
        "start_date": start.isoformat(),
        "end_date": today.isoformat(),
        "total_meals": total_meals,
        "average_daily_meals": avg_daily,
        "trend": trend,
    }


def get_monthly_analytics(db: Session) -> Dict[str, Any]:
    """Returns month-over-month summary."""
    # Get demand grouped by month
    demand_by_month = (
        db.query(
            func.strftime("%Y-%m", MealDemand.date).label("month"),
            func.sum(MealDemand.actual_quantity).label("total_demand"),
            func.avg(MealDemand.actual_quantity).label("avg_daily"),
        )
        .group_by("month")
        .order_by("month")
        .all()
    )

    # Get waste grouped by month
    waste_by_month_raw = (
        db.query(
            func.strftime("%Y-%m", FoodWaste.date).label("month"),
            func.sum(FoodWaste.wasted_quantity).label("total_waste"),
        )
        .group_by("month")
        .all()
    )
    waste_map = {w.month: float(w.total_waste or 0) for w in waste_by_month_raw}

    # Get prediction accuracy by month
    accuracy_by_month_raw = (
        db.query(
            func.strftime("%Y-%m", MealDemand.date).label("month"),
            func.avg(MealDemand.actual_quantity).label("avg_actual"),
            func.avg(MealDemand.predicted_quantity).label("avg_predicted"),
        )
        .filter(MealDemand.predicted_quantity.isnot(None))
        .group_by("month")
        .all()
    )
    accuracy_map = {}
    for a in accuracy_by_month_raw:
        if a.avg_actual and a.avg_predicted and float(a.avg_actual) > 0:
            mape = abs(float(a.avg_actual) - float(a.avg_predicted)) / float(a.avg_actual) * 100
            accuracy_map[a.month] = round(max(0, 100 - mape), 1)
        else:
            accuracy_map[a.month] = 0.0

    months = []
    for d in demand_by_month:
        months.append({
            "month": d.month,
            "total_demand": int(d.total_demand or 0),
            "avg_daily_demand": round(float(d.avg_daily or 0), 1),
            "total_waste_kg": round(waste_map.get(d.month, 0), 1),
            "accuracy_pct": accuracy_map.get(d.month, 0.0),
        })

    return {"months": months}


def get_station_analytics(db: Session) -> List[Dict[str, Any]]:
    """Per-station analytics."""
    from app.config import STATION_MAP

    stations_data = (
        db.query(
            MealDemand.station,
            func.sum(MealDemand.actual_quantity).label("total_demand"),
        )
        .group_by(MealDemand.station)
        .all()
    )

    grand_total = sum(float(s.total_demand or 0) for s in stations_data)

    # Waste per station
    waste_by_station = {}
    waste_rows = (
        db.query(
            FoodWaste.station,
            func.avg(FoodWaste.waste_percentage).label("avg_waste"),
        )
        .group_by(FoodWaste.station)
        .all()
    )
    for wr in waste_rows:
        waste_by_station[wr.station] = round(float(wr.avg_waste or 0), 1)

    # Top item per station
    result = []
    for s in stations_data:
        top_item_row = (
            db.query(
                MealDemand.menu_item,
                func.sum(MealDemand.actual_quantity).label("item_total"),
            )
            .filter(MealDemand.station == s.station)
            .group_by(MealDemand.menu_item)
            .order_by(desc("item_total"))
            .first()
        )

        station_info = STATION_MAP.get(s.station, {})
        result.append({
            "station_id": s.station,
            "station_name": station_info.get("name", s.station.title()),
            "total_demand": int(s.total_demand or 0),
            "share_pct": round(float(s.total_demand or 0) / max(1, grand_total) * 100, 1),
            "average_waste_pct": waste_by_station.get(s.station, 0.0),
            "top_item": top_item_row.menu_item if top_item_row else "N/A",
        })

    return result


def get_menu_item_analytics(db: Session) -> List[Dict[str, Any]]:
    """Per-menu-item analytics with waste and ratings."""
    items = (
        db.query(
            MealDemand.menu_item,
            MealDemand.station,
            func.sum(MealDemand.actual_quantity).label("total_sold"),
        )
        .group_by(MealDemand.menu_item, MealDemand.station)
        .order_by(desc("total_sold"))
        .all()
    )

    # Waste per item
    waste_map = {}
    waste_rows = (
        db.query(
            FoodWaste.menu_item,
            func.sum(FoodWaste.prepared_quantity).label("total_prepared"),
            func.sum(FoodWaste.wasted_quantity).label("total_wasted"),
            func.avg(FoodWaste.waste_percentage).label("avg_waste"),
        )
        .group_by(FoodWaste.menu_item)
        .all()
    )
    for wr in waste_rows:
        waste_map[wr.menu_item] = {
            "total_prepared": round(float(wr.total_prepared or 0), 1),
            "total_wasted": round(float(wr.total_wasted or 0), 1),
            "waste_pct": round(float(wr.avg_waste or 0), 1),
        }

    # Ratings per item
    rating_map = {}
    rating_rows = (
        db.query(
            Feedback.menu_item,
            func.avg(Feedback.rating).label("avg_rating"),
        )
        .group_by(Feedback.menu_item)
        .all()
    )
    for rr in rating_rows:
        rating_map[rr.menu_item] = round(float(rr.avg_rating or 0), 1)

    result = []
    for item in items:
        w = waste_map.get(item.menu_item, {})
        result.append({
            "menu_item": item.menu_item,
            "station": item.station,
            "total_sold": round(float(item.total_sold or 0), 1),
            "total_prepared": w.get("total_prepared", 0),
            "total_wasted": w.get("total_wasted", 0),
            "waste_pct": w.get("waste_pct", 0),
            "avg_rating": rating_map.get(item.menu_item),
        })

    return result


# ==========================================
# Model Training Log
# ==========================================

def get_latest_training_log(db: Session) -> Optional[ModelTrainingLog]:
    return (
        db.query(ModelTrainingLog)
        .order_by(desc(ModelTrainingLog.trained_at))
        .first()
    )


def create_training_log(db: Session, data: Dict[str, Any]) -> ModelTrainingLog:
    log = ModelTrainingLog(**data)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
