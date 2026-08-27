"""
Servo-AI - Demand Routes (Historical Data)
"""
import logging
from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import MealDemandCreate, MealDemandResponse
from app.config import STATION_MAP
from app.utils.helpers import parse_demand_csv
from app import crud

logger = logging.getLogger("servo_ai.routes.demand")

router = APIRouter(prefix="/api/demand", tags=["Demand"])


@router.post(
    "",
    response_model=MealDemandResponse,
    summary="Record Meal Demand",
    description="Records a historical or actual meal demand entry.",
)
def create_demand(record: MealDemandCreate, db: Session = Depends(get_db)):
    """Create a single meal demand record."""
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

    data = record.model_dump() if hasattr(record, "model_dump") else record.dict()
    result = crud.create_meal_demand(db, data)
    return result


@router.get(
    "",
    response_model=List[MealDemandResponse],
    summary="List Demand Records",
    description="Returns historical demand records with optional filters.",
)
def list_demand(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    station: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List meal demand records with pagination and optional filters."""
    try:
        sd = date.fromisoformat(start_date) if start_date else None
        ed = date.fromisoformat(end_date) if end_date else None
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"success": False, "error": "Invalid date", "message": str(e)})

    return crud.get_meal_demands(db, skip=skip, limit=limit, station=station, start_date=sd, end_date=ed)


@router.get(
    "/{target_date}",
    response_model=List[MealDemandResponse],
    summary="Get Demand by Date",
    description="Returns all demand records for a specific date.",
)
def get_demand_by_date(target_date: str, db: Session = Depends(get_db)):
    """Get all demand records for a specific date."""
    try:
        d = date.fromisoformat(target_date)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "Invalid date", "message": f"Cannot parse '{target_date}'. Use YYYY-MM-DD."},
        )

    records = crud.get_meal_demands_by_date(db, d)
    if not records:
        raise HTTPException(
            status_code=404,
            detail={"success": False, "error": "No data", "message": f"No demand records found for {target_date}"},
        )
    return records


@router.post(
    "/upload",
    summary="Upload Demand CSV",
    description="Upload a CSV file with historical demand data. Required columns: date, station, menu_item, actual_quantity.",
)
async def upload_demand_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and process a CSV file with historical meal demand data."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "Invalid file", "message": "Only .csv files are accepted."},
        )

    try:
        content = await file.read()
        records = parse_demand_csv(content)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "Invalid CSV", "message": str(e)},
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "CSV parse error", "message": str(e)},
        )

    # Validate stations
    valid_stations = set(STATION_MAP.keys())
    for r in records:
        if r["station"] not in valid_stations:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Invalid station in CSV",
                    "message": f"Row contains station '{r['station']}'. Valid: {list(valid_stations)}",
                },
            )

    try:
        count = crud.create_meal_demands_bulk(db, records)
        logger.info(f"CSV upload: {count} demand records inserted from {file.filename}")
        return {
            "success": True,
            "message": f"Successfully imported {count} demand records.",
            "records_imported": count,
        }
    except Exception as e:
        logger.error(f"CSV import failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Import failed", "message": str(e)},
        )
