"""
Servo-AI - Prediction Routes
"""
import logging
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import PredictionRequest, PredictionResponse, DailyForecastResponse, BatchCSVForecastResponse
from app.ml.model_manager import model_manager
from app.ml.predict import predict_demand, predict_daily_forecast
from app.services.csv_service import csv_batch_forecaster, generate_sample_csv_content
from app.config import STATION_MAP
from app import crud

logger = logging.getLogger("servo_ai.routes.predictions")

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict Meal Demand",
    description="Generates an AI-powered demand prediction for a specific station and menu item.",
)
def predict(req: PredictionRequest, db: Session = Depends(get_db)):
    """Predict demand for a specific station/menu item on a given date."""
    # Validate station
    if req.station not in STATION_MAP:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "Invalid station",
                "message": f"Station '{req.station}' not found. Valid stations: {list(STATION_MAP.keys())}",
            },
        )

    # Validate menu item belongs to station
    station_menu = STATION_MAP[req.station]["menu"]
    if req.menu_item not in station_menu:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "Invalid menu item",
                "message": f"'{req.menu_item}' is not on the {req.station} menu. Valid items: {station_menu}",
            },
        )

    try:
        confidence = req.confidence if req.confidence else 0.95
        result = predict_demand(
            model_manager=model_manager,
            prediction_date=req.date,
            station=req.station,
            menu_item=req.menu_item,
            temperature=req.temperature,
            weather=req.weather,
            is_holiday=req.is_holiday,
            student_attendance=req.student_attendance,
            faculty_attendance=req.faculty_attendance,
            confidence_level=confidence,
        )

        # Store prediction in database
        try:
            crud.create_prediction(db, {
                "prediction_date": req.date,
                "station": req.station,
                "menu_item": req.menu_item,
                "predicted_quantity": result["predicted_quantity"],
                "lower_bound": result["lower_bound"],
                "upper_bound": result["upper_bound"],
                "confidence": confidence,
            })
        except Exception as e:
            logger.warning(f"Could not save prediction to DB: {e}")

        return result

    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Prediction failed",
                "message": str(e),
            },
        )


@router.get(
    "/daily",
    response_model=DailyForecastResponse,
    summary="Daily Forecast",
    description="Returns predicted demand for all meal stations (breakfast, lunch, snacks, dinner).",
)
def daily_forecast(
    target_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Returns the full daily forecast for all 4 stations."""
    try:
        if target_date:
            forecast_date = date.fromisoformat(target_date)
        else:
            forecast_date = date.today()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "Invalid date",
                "message": f"Cannot parse date '{target_date}'. Use YYYY-MM-DD format.",
            },
        )

    try:
        result = predict_daily_forecast(
            model_manager=model_manager,
            prediction_date=forecast_date,
        )
        return result
    except Exception as e:
        logger.error(f"Daily forecast failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Forecast failed",
                "message": str(e),
            },
        )


@router.post(
    "/batch-csv",
    response_model=BatchCSVForecastResponse,
    summary="Batch Predict from CSV File",
    description="Ingests a CSV file of dates/weather/academic conditions and produces rich ML demand predictions and procurement estimates.",
)
async def batch_predict_csv_endpoint(
    file: UploadFile = File(...),
    buffer: float = Query(5.0, ge=0.0, le=50.0, description="Pantry requisition safety buffer percentage"),
    db: Session = Depends(get_db),
):
    """Uploads a CSV file, runs the AI demand forecaster on every row, and returns full prediction records & summary."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "Invalid file format", "message": "Only .csv files are supported."},
        )

    try:
        content = await file.read()
        if not content or not content.strip():
            raise HTTPException(
                status_code=400,
                detail={"success": False, "error": "Empty file", "message": "Uploaded CSV file is empty."},
            )

        results = csv_batch_forecaster.process_csv(
            csv_source=content,
            safety_buffer_pct=buffer,
            db=db,
        )

        return {
            "success": True,
            "summary": results["summary"],
            "predictions": results["predictions"],
            "columns": results.get("columns", []),
        }

    except HTTPException:
        raise
    except ValueError as ve:
        logger.warning(f"Batch CSV validation error: {ve}")
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "Validation error", "message": str(ve)},
        )
    except Exception as e:
        logger.error(f"Batch CSV prediction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Batch prediction failed", "message": str(e)},
        )


@router.post(
    "/batch-csv/download",
    summary="Batch Predict and Download Enriched Output CSV",
    description="Takes an input CSV file and streams back the enriched CSV file with predicted meal covers, 95% confidence intervals, and grocery requisitions.",
)
async def batch_predict_download_csv_endpoint(
    file: UploadFile = File(...),
    buffer: float = Query(5.0, ge=0.0, le=50.0),
    db: Session = Depends(get_db),
):
    """Processes uploaded CSV and returns downloadable output CSV file."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "Invalid file", "message": "Only .csv files are accepted."},
        )

    try:
        content = await file.read()
        if not content or not content.strip():
            raise HTTPException(
                status_code=400,
                detail={"success": False, "error": "Empty file", "message": "Uploaded CSV is empty."},
            )

        results = csv_batch_forecaster.process_csv(
            csv_source=content,
            safety_buffer_pct=buffer,
            db=db,
        )

        output_csv_str = csv_batch_forecaster.export_output_csv(results)

        return Response(
            content=output_csv_str,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=predicted_canteen_forecast_output.csv",
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch CSV export failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Batch CSV export failed", "message": str(e)},
        )


@router.get(
    "/sample-csv",
    summary="Download Sample Input CSV Template",
    description="Returns a sample/template CSV file containing 14 days of realistic campus conditions ready for batch prediction.",
)
def get_sample_csv_template():
    """Generates and serves a realistic sample input CSV file."""
    sample_content = generate_sample_csv_content()
    return Response(
        content=sample_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=sample_canteen_forecast_input.csv",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )

