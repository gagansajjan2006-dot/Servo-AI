"""
Canteen Pulse - Database Models & Session Management
"""
from datetime import datetime, date
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean, Date, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DailyRecord(Base):
    """Historical and planned daily canteen records"""
    __tablename__ = "daily_records"

    id = Column(Integer, primary_key=True, index=True)
    record_date = Column(Date, unique=True, index=True, nullable=False)
    
    # Context & Features
    day_of_week = Column(Integer)  # 0 = Monday, 6 = Sunday
    day_name = Column(String(16))
    is_weekend = Column(Boolean, default=False)
    is_holiday = Column(Boolean, default=False)
    holiday_name = Column(String(128), nullable=True)
    is_exam_period = Column(Boolean, default=False)
    exam_name = Column(String(128), nullable=True)
    is_special_event = Column(Boolean, default=False)
    event_name = Column(String(128), nullable=True)
    
    # Weather
    weather_condition = Column(String(32), default="Clear")  # Sunny, Rainy, Cloudy, Stormy, Cold
    temperature_c = Column(Float, default=28.0)
    rainfall_mm = Column(Float, default=0.0)
    humidity_pct = Column(Float, default=55.0)
    
    # Model Predictions
    predicted_meals = Column(Integer, nullable=True)
    confidence_lower = Column(Integer, nullable=True)
    confidence_upper = Column(Integer, nullable=True)
    predicted_breakfast = Column(Integer, nullable=True)
    predicted_lunch = Column(Integer, nullable=True)
    predicted_snacks = Column(Integer, nullable=True)
    predicted_dinner = Column(Integer, nullable=True)
    feature_importance_json = Column(JSON, nullable=True)  # Explainability reason chips
    
    # Actual Operational Records
    actual_meals = Column(Integer, nullable=True)
    actual_breakfast = Column(Integer, nullable=True)
    actual_lunch = Column(Integer, nullable=True)
    actual_snacks = Column(Integer, nullable=True)
    actual_dinner = Column(Integer, nullable=True)
    
    # Manager Review & Notes
    manager_logged_at = Column(DateTime, nullable=True)
    manager_notes = Column(Text, nullable=True)
    anomaly_flag = Column(Boolean, default=False)
    anomaly_reason = Column(String(256), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AcademicCalendar(Base):
    """Holidays, Exam Schedules & Special Events"""
    __tablename__ = "academic_calendar"

    id = Column(Integer, primary_key=True, index=True)
    event_date = Column(Date, index=True, nullable=False)
    event_type = Column(String(32))  # 'holiday', 'exam', 'fest', 'placement', 'sports'
    title = Column(String(128), nullable=False)
    impact_multiplier = Column(Float, default=1.0)  # e.g., 0.1 for closed, 1.25 for fest
    description = Column(String(256), nullable=True)


class RecipeRatio(Base):
    """Raw ingredient ratio per meal type (in grams or ml per meal)"""
    __tablename__ = "recipe_ratios"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(32))  # 'lunch_dinner', 'breakfast', 'snacks', 'beverage'
    ingredient_name = Column(String(64), nullable=False)
    unit = Column(String(16), default="kg")  # kg, litres, units, packets
    qty_per_100_meals = Column(Float, nullable=False)  # Quantity required per 100 meals
    current_unit_price = Column(Float, default=0.0)  # INR/USD per unit
    notes = Column(String(128), nullable=True)


class ManagerCorrection(Base):
    """Audit log of manager overrides and actuals adjustments"""
    __tablename__ = "manager_corrections"

    id = Column(Integer, primary_key=True, index=True)
    record_date = Column(Date, index=True, nullable=False)
    original_prediction = Column(Integer)
    adjusted_count = Column(Integer)
    correction_type = Column(String(32))  # 'actual_log', 'manual_override'
    reason = Column(String(256))
    created_at = Column(DateTime, default=datetime.utcnow)


class ModelTrainingLog(Base):
    """History of model retraining runs"""
    __tablename__ = "model_training_logs"

    id = Column(Integer, primary_key=True, index=True)
    trained_at = Column(DateTime, default=datetime.utcnow)
    sample_count = Column(Integer)
    mae = Column(Float)
    rmse = Column(Float)
    r2_score = Column(Float)
    mape = Column(Float)
    accuracy_pct = Column(Float)
    feature_importances = Column(JSON)
    model_version = Column(String(32), default="v1.0-gbdt")
    notes = Column(String(256), nullable=True)


class MenuItem(Base):
    """Canteen Menu Items & Station Portions"""
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    dish_name = Column(String(128), nullable=False)
    shift = Column(String(32), index=True, nullable=False)  # 'breakfast', 'lunch', 'snacks', 'dinner'
    category = Column(String(64), default="Main Course")  # 'Main Course', 'Breads & Rice', 'Beverage', 'Snack', 'Dessert'
    price = Column(Float, default=60.0)
    cost_per_portion = Column(Float, default=24.0)
    portion_share_pct = Column(Float, default=0.50)  # Share of diners ordering this item in this shift
    chef_station = Column(String(64), default="Main Steam Line")  # 'Griddle', 'Curry Line', 'Beverage Bar', 'Tandoor'
    dietary = Column(String(32), default="Veg")  # 'Veg', 'Non-Veg', 'Jain', 'High Protein'
    calories = Column(Integer, default=350)
    allergens = Column(String(128), default="Gluten, Dairy")
    status = Column(String(32), default="ready")  # 'ready', 'preparing', 'low_stock', 'sold_out'
    is_active = Column(Boolean, default=True)
    day_of_week = Column(Integer, nullable=True)  # Null = Daily, or 0-6 for specific days


def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
