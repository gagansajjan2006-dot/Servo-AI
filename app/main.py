"""
Servo AI - FastAPI Main Application
AI-Powered Campus Canteen Demand Forecasting System
"""
import sys
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import CANTEEN_SETTINGS, FRONTEND_URL, ENVIRONMENT
from app.database import init_db, engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("servo_ai")

STATIC_DIR = Path(__file__).resolve().parent / "static"

_db_initialized = False


def ensure_initialized():
    """Initialize database tables on first request. Never train model at startup."""
    global _db_initialized
    if not _db_initialized:
        try:
            init_db()
            logger.info("Database tables initialized successfully.")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
        _db_initialized = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler — startup and shutdown."""
    logger.info("Starting Servo AI - Campus Canteen Demand Forecasting System")
    ensure_initialized()

    # Attempt to load pre-trained models (non-blocking)
    try:
        from app.ml.model_manager import model_manager
        model_manager.load_model()
        if model_manager.is_loaded:
            logger.info("Pre-trained ML model loaded successfully.")
    except Exception as e:
        logger.warning(f"model_manager loading skipped: {e}")

    try:
        from app.ml.model import forecaster
        forecaster.load_or_initialize()
        if not forecaster._is_fitted:
            forecaster.train_on_records()
        logger.info("GBDT Forecaster engine ready.")
    except Exception as e:
        logger.warning(f"Forecaster engine startup: {e}")

    yield
    logger.info("Servo AI shutting down.")


# ==========================================
# FastAPI Application
# ==========================================
app = FastAPI(
    title="🔥 Servo AI API",
    description=(
        "AI-Powered Campus Canteen Demand Forecasting System.\n\n"
        f"**Canteen:** {CANTEEN_SETTINGS['name']}\n\n"
        f"**Campus:** {CANTEEN_SETTINGS['campus']}\n\n"
        "Predicts meal demand across breakfast, lunch, snacks, and dinner stations "
        "using machine learning, historical data analysis, and weather/calendar context."
    ),
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ==========================================
# Middleware
# ==========================================

# Lazy DB init middleware (for serverless cold starts)
@app.middleware("http")
async def db_init_middleware(request: Request, call_next):
    if not _db_initialized:
        ensure_initialized()
    return await call_next(request)


# CORS Configuration
origins = [o.strip() for o in FRONTEND_URL.split(",") if o.strip()]
if ENVIRONMENT == "development" and not origins:
    origins = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:8000", "http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Global Exception Handlers
# ==========================================

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.warning(f"ValueError: {exc}")
    return JSONResponse(
        status_code=400,
        content={"success": False, "error": "Validation error", "message": str(exc)},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}")
    detail = str(exc) if ENVIRONMENT == "development" else "An internal error occurred."
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error", "message": detail},
    )


# ==========================================
# Register Route Modules
# ==========================================
from app.routes.dashboard import router as dashboard_router
from app.routes.health import router as health_router
from app.routes.predictions import router as predictions_router
from app.routes.meals import router as meals_router
from app.routes.demand import router as demand_router
from app.routes.waste import router as waste_router
from app.routes.analytics import router as analytics_router
from app.routes.recommendations import router as recommendations_router
from app.routes.ml import router as ml_router
from app.routes.settings import router as settings_router

app.include_router(dashboard_router)
app.include_router(health_router)
app.include_router(predictions_router)
app.include_router(meals_router)
app.include_router(demand_router)
app.include_router(waste_router)
app.include_router(analytics_router)
app.include_router(recommendations_router)
app.include_router(ml_router)
app.include_router(settings_router)



# ==========================================
# Root & Static Files
# ==========================================

@app.get("/health", include_in_schema=False)
def root_health():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def serve_root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "message": "Servo AI API is running",
        "service": "Servo AI - Campus Canteen Demand Forecasting",
        "version": "3.0.0",
        "docs": "/docs",
    }


@app.get("/api", include_in_schema=False)
def serve_api():
    return {
        "message": "Servo AI API is running",
        "service": "Servo AI - Campus Canteen Demand Forecasting",
        "version": "3.0.0",
        "docs": "/docs",
    }


@app.get("/favicon.ico", include_in_schema=False)
@app.get("/favicon.png", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


# Mount static files if directory exists
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
