"""
Servo-AI - Meals / Station Routes
"""
import logging
from fastapi import APIRouter, HTTPException

from app.config import STATIONS, STATION_MAP

logger = logging.getLogger("servo_ai.routes.meals")

router = APIRouter(prefix="/api/meals", tags=["Meals"])


@router.get(
    "",
    summary="List All Meal Stations",
    description="Returns information for all canteen meal stations including timings, menu, and share percentages.",
)
def list_stations():
    """Returns all meal stations with their configuration."""
    result = []
    for st in STATIONS:
        result.append({
            "id": st["id"],
            "name": st["name"],
            "time": st["time"],
            "daily_share": st["daily_share"],
            "peak_window": st["peak_window"],
            "menu": st["menu"],
        })
    return result


@router.get(
    "/{station}",
    summary="Get Station Details",
    description="Returns detailed information about a specific meal station.",
)
def get_station(station: str):
    """Returns details for a specific station by ID."""
    if station not in STATION_MAP:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "Station not found",
                "message": f"Station '{station}' not found. Valid stations: {list(STATION_MAP.keys())}",
            },
        )

    st = STATION_MAP[station]
    return {
        "id": st["id"],
        "name": st["name"],
        "time": st["time"],
        "daily_share": st["daily_share"],
        "peak_window": st["peak_window"],
        "menu": st["menu"],
    }


@router.get(
    "/{station}/menu",
    summary="Get Station Menu",
    description="Returns the menu items for a specific meal station.",
)
def get_station_menu(station: str):
    """Returns the menu items for a specific station."""
    if station not in STATION_MAP:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "Station not found",
                "message": f"Station '{station}' not found. Valid stations: {list(STATION_MAP.keys())}",
            },
        )

    st = STATION_MAP[station]
    return {
        "station": st["id"],
        "station_name": st["name"],
        "time": st["time"],
        "menu": st["menu"],
    }
