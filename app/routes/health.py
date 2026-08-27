"""
Servo-AI - Health Check Route
"""
import logging
from sqlalchemy import text
from fastapi import APIRouter

from app.database import engine
from app.ml.model_manager import model_manager

logger = logging.getLogger("servo_ai.routes.health")

router = APIRouter(prefix="/api", tags=["Health"])


@router.get(
    "/health",
    summary="System Health Check",
    description="Returns system health status including database connection and model load state.",
    response_description="Health status object",
)
def health_check():
    """Lightweight health check endpoint."""
    # Database check
    db_status = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    # Model check
    model_status = "loaded" if model_manager.is_loaded else "not_loaded"

    return {
        "status": "healthy",
        "database": db_status,
        "model": model_status,
    }
