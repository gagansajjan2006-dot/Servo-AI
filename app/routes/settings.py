"""
Servo-AI - Settings Routes
"""
import logging
from fastapi import APIRouter

from app.config import CANTEEN_SETTINGS, STATIONS
from app.schemas import CanteenSettingsResponse

logger = logging.getLogger("servo_ai.routes.settings")

router = APIRouter(prefix="/api", tags=["Settings"])


@router.get(
    "/settings",
    response_model=CanteenSettingsResponse,
    summary="Canteen Settings",
    description="Returns the current canteen configuration including station details.",
)
def get_settings():
    """Returns canteen settings and station configuration."""
    station_items = []
    for st in STATIONS:
        station_items.append({
            "id": st["id"],
            "name": st["name"],
            "time": st["time"],
            "daily_share": st["daily_share"],
            "peak_window": st["peak_window"],
            "menu": st["menu"],
        })

    return {
        "name": CANTEEN_SETTINGS["name"],
        "campus": CANTEEN_SETTINGS["campus"],
        "student_population": CANTEEN_SETTINGS["student_population"],
        "faculty_staff_population": CANTEEN_SETTINGS["faculty_staff_population"],
        "seating_capacity": CANTEEN_SETTINGS["seating_capacity"],
        "confidence_level": CANTEEN_SETTINGS["confidence_level"],
        "stations": station_items,
    }
