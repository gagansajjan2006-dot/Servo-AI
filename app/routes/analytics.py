"""
Servo-AI - Analytics Routes
"""
import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import CANTEEN_SETTINGS
from app.schemas import DashboardAnalyticsResponse
from app import crud

logger = logging.getLogger("servo_ai.routes.analytics")

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get(
    "/dashboard",
    response_model=DashboardAnalyticsResponse,
    summary="Dashboard Overview",
    description="Returns aggregated dashboard statistics for the canteen operations command center.",
)
def dashboard(db: Session = Depends(get_db)):
    """Returns comprehensive dashboard statistics from real data."""
    stats = crud.get_dashboard_stats(db)

    return {
        "today_demand": stats["today_demand"],
        "predicted_demand": stats["predicted_demand"],
        "average_waste_percentage": stats["average_waste_percentage"],
        "food_saved_estimate": stats["food_saved_estimate"],
        "peak_station": stats["peak_station"],
        "peak_menu_item": stats["peak_menu_item"],
        "students": CANTEEN_SETTINGS["student_population"],
        "faculty_staff": CANTEEN_SETTINGS["faculty_staff_population"],
        "seating_capacity": CANTEEN_SETTINGS["seating_capacity"],
    }


@router.get(
    "/weekly",
    summary="Weekly Analytics",
    description="Returns a 7-day demand trend with actual vs predicted meals and waste data.",
)
def weekly_analytics(db: Session = Depends(get_db)):
    """Returns 7-day demand trend."""
    return crud.get_weekly_analytics(db)


@router.get(
    "/monthly",
    summary="Monthly Analytics",
    description="Returns month-over-month demand summary with waste and accuracy metrics.",
)
def monthly_analytics(db: Session = Depends(get_db)):
    """Returns monthly demand summary."""
    return crud.get_monthly_analytics(db)


@router.get(
    "/stations",
    summary="Station Analytics",
    description="Returns per-station demand analytics including share, waste, and top items.",
)
def station_analytics(db: Session = Depends(get_db)):
    """Returns analytics breakdown by station."""
    return crud.get_station_analytics(db)


@router.get(
    "/menu-items",
    summary="Menu Item Analytics",
    description="Returns per-menu-item analytics including demand, waste, and ratings.",
)
def menu_item_analytics(db: Session = Depends(get_db)):
    """Returns analytics breakdown by menu item."""
    return crud.get_menu_item_analytics(db)
