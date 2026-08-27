"""
Servo-AI - Database Engine, Session Factory & Schema Initialization
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import DATABASE_URL, IS_SERVERLESS
from app.models import (
    Base, User, MealDemand, Prediction, FoodWaste, Feedback,
    DailyRecord, AcademicCalendar, RecipeRatio, ManagerCorrection,
    ModelTrainingLog, MenuItem
)

logger = logging.getLogger("servo_ai.database")

# Configure SQLite engine with proper concurrency flags
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all database tables automatically on startup"""
    try:
        logger.info(f"Initializing database schema using URL: {DATABASE_URL}")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified / created successfully.")
    except Exception as e:
        logger.error(f"Error during init_db: {e}")
        raise e


def get_db():
    """FastAPI Dependency for database session management"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
