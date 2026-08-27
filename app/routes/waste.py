"""
Servo-AI - Food Waste Routes
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import FoodWasteCreate, FoodWasteResponse, FoodWasteSummary
from app.config import STATION_MAP
from app import crud

logger = logging.getLogger("servo_ai.routes.waste")

router = APIRouter(prefix="/api/waste", tags=["Waste"])


@router.post(
    "",
    response_model=FoodWasteResponse,
    summary="Log Food Waste",
    description="Records a food waste entry. Wasted quantity and waste percentage are calculated automatically.",
)
def create_waste(record: FoodWasteCreate, db: Session = Depends(get_db)):
    """Log a food waste record with auto-calculated waste metrics."""
    # Validate station
    if record.station not in STATION_MAP:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "Invalid station",
                "message": f"Station '{record.station}' not valid. Options: {list(STATION_MAP.keys())}",
            },
        )

    if record.sold_quantity > record.prepared_quantity:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "Invalid quantities",
                "message": "sold_quantity cannot exceed prepared_quantity.",
            },
        )

    wasted = record.prepared_quantity - record.sold_quantity
    waste_pct = round((wasted / record.prepared_quantity) * 100, 2) if record.prepared_quantity > 0 else 0.0

    data = record.model_dump() if hasattr(record, "model_dump") else record.dict()
    data["wasted_quantity"] = wasted
    data["waste_percentage"] = waste_pct

    result = crud.create_food_waste(db, data)
    return result


@router.get(
    "",
    response_model=List[FoodWasteResponse],
    summary="List Waste Records",
    description="Returns food waste records with optional station filter.",
)
def list_waste(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    station: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List food waste records."""
    return crud.get_food_waste_records(db, skip=skip, limit=limit, station=station)


@router.get(
    "/summary",
    response_model=FoodWasteSummary,
    summary="Waste Summary",
    description="Returns aggregated food waste statistics including totals and top 5 wasted items.",
)
def waste_summary(db: Session = Depends(get_db)):
    """Returns food waste summary with totals and top wasted items."""
    summary = crud.get_food_waste_summary(db)

    if summary["total_prepared"] == 0:
        return {
            "total_prepared": 0,
            "total_sold": 0,
            "total_wasted": 0,
            "average_waste_percentage": 0.0,
            "top_wasted_items": [],
        }

    return summary
