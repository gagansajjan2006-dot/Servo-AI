"""
Servo-AI - Machine Learning Routes
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import TrainModelResponse, ModelStatusResponse
from app.ml.model_manager import model_manager
from app.ml.train import FEATURE_COLUMNS
from app import crud

logger = logging.getLogger("servo_ai.routes.ml")

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])


@router.post(
    "/train",
    response_model=TrainModelResponse,
    summary="Train ML Model",
    description="Triggers a full model training pipeline on historical meal demand data.",
)
def train_model(db: Session = Depends(get_db)):
    """Train the demand forecasting model on historical data."""
    try:
        demand_count = crud.get_meal_demand_count(db)
        if demand_count < 10:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Insufficient data",
                    "message": f"Only {demand_count} demand records found. Need at least 10 to train.",
                },
            )

        logger.info(f"Starting model training with {demand_count} records...")
        metrics = model_manager.retrain(db)
        logger.info(f"Model training complete: {metrics}")
        return metrics

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "Training failed", "message": str(e)},
        )
    except Exception as e:
        logger.error(f"Model training error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": "Training failed", "message": str(e)},
        )


@router.get(
    "/status",
    response_model=ModelStatusResponse,
    summary="Model Status",
    description="Returns the current model status, training metrics, and feature list.",
)
def model_status(db: Session = Depends(get_db)):
    """Returns the current state of the ML model."""
    is_loaded = model_manager.is_loaded
    metadata = model_manager.metadata
    metrics = metadata.get("metrics", {})

    # Check latest training log from DB
    latest_log = crud.get_latest_training_log(db)

    return {
        "status": "ready" if is_loaded else "not_trained",
        "model_name": "RandomForestRegressor",
        "is_trained": is_loaded,
        "last_trained": metadata.get("last_trained") or (latest_log.trained_at.isoformat() if latest_log else None),
        "total_samples": metadata.get("training_rows", 0) or (latest_log.sample_count if latest_log else 0),
        "mae": metrics.get("mae") or (latest_log.mae if latest_log else None),
        "rmse": metrics.get("rmse") or (latest_log.rmse if latest_log else None),
        "r2_score": metrics.get("r2_score") or (latest_log.r2_score if latest_log else None),
        "features": FEATURE_COLUMNS,
    }
