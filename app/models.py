"""
Servo-AI - SQLAlchemy Database Models
Defines User, MealDemand, Prediction, FoodWaste, Feedback, DailyRecord, and Operational tables.
"""
from datetime import datetime, date, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Date, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def utc_now():
    """Returns timezone-aware UTC datetime"""
    return datetime.now(timezone.utc)


class User(Base):
    """Users of the system (admin, staff, manager)"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    role = Column(String(32), default="staff", nullable=False)  # admin, staff, manager
    created_at = Column(DateTime, default=utc_now)


class MealDemand(Base):
    """Historical and actual meal demand records"""
    __tablename__ = "meal_demand"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True, nullable=False)
    station = Column(String(32), index=True, nullable=False)  # breakfast, lunch, snacks, dinner
    menu_item = Column(String(128), index=True, nullable=False)
    predicted_quantity = Column(Float, nullable=True)
    actual_quantity = Column(Float, nullable=False)
    weather = Column(String(32), default="Clear")  # Clear, Sunny, Rainy, Cloudy, Cold, Stormy
    temperature = Column(Float, default=28.0)
    is_holiday = Column(Boolean, default=False)
    is_weekend = Column(Boolean, default=False)
    student_attendance = Column(Integer, default=3500)
    faculty_attendance = Column(Integer, default=380)
    created_at = Column(DateTime, default=utc_now)


class Prediction(Base):
    """Persisted forecast snapshots with statistical bounds"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    prediction_date = Column(Date, index=True, nullable=False)
    station = Column(String(32), index=True, nullable=False)
    menu_item = Column(String(128), index=True, nullable=False)
    predicted_quantity = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=False)
    upper_bound = Column(Float, nullable=False)
    confidence = Column(Float, default=0.95)
    created_at = Column(DateTime, default=utc_now)


class FoodWaste(Base):
    """Daily food waste tracking and post-service audits"""
    __tablename__ = "food_waste"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True, nullable=False)
    station = Column(String(32), index=True, nullable=False)
    menu_item = Column(String(128), index=True, nullable=False)
    prepared_quantity = Column(Float, nullable=False)
    sold_quantity = Column(Float, nullable=False)
    wasted_quantity = Column(Float, nullable=False)
    waste_percentage = Column(Float, nullable=False)
    created_at = Column(DateTime, default=utc_now)


class Feedback(Base):
    """Diner satisfaction and qualitative feedback ratings"""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True, nullable=False)
    station = Column(String(32), index=True, nullable=False)
    menu_item = Column(String(128), index=True, nullable=False)
    rating = Column(Integer, nullable=False)  # 1 to 5
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)


class DailyRecord(Base):
    """Historical aggregated daily operational records"""
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
    weather_condition = Column(String(32), default="Clear")
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
    feature_importance_json = Column(JSON, nullable=True)

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

    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)


class AcademicCalendar(Base):
    """Holidays, Exam Schedules & Special Events"""
    __tablename__ = "academic_calendar"

    id = Column(Integer, primary_key=True, index=True)
    event_date = Column(Date, index=True, nullable=False)
    event_type = Column(String(32))  # 'holiday', 'exam', 'fest', 'placement', 'sports'
    title = Column(String(128), nullable=False)
    impact_multiplier = Column(Float, default=1.0)
    description = Column(String(256), nullable=True)


class RecipeRatio(Base):
    """Raw ingredient ratio per meal type (in grams or ml per meal)"""
    __tablename__ = "recipe_ratios"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(32))
    ingredient_name = Column(String(64), nullable=False)
    unit = Column(String(16), default="kg")
    qty_per_100_meals = Column(Float, nullable=False)
    current_unit_price = Column(Float, default=0.0)
    notes = Column(String(128), nullable=True)


class ManagerCorrection(Base):
    """Audit log of manager overrides and actuals adjustments"""
    __tablename__ = "manager_corrections"

    id = Column(Integer, primary_key=True, index=True)
    record_date = Column(Date, index=True, nullable=False)
    original_prediction = Column(Integer)
    adjusted_count = Column(Integer)
    correction_type = Column(String(32))
    reason = Column(String(256))
    created_at = Column(DateTime, default=utc_now)


class ModelTrainingLog(Base):
    """History of model retraining runs"""
    __tablename__ = "model_training_logs"

    id = Column(Integer, primary_key=True, index=True)
    trained_at = Column(DateTime, default=utc_now)
    sample_count = Column(Integer)
    mae = Column(Float)
    rmse = Column(Float)
    r2_score = Column(Float)
    mape = Column(Float)
    accuracy_pct = Column(Float)
    feature_importances = Column(JSON)
    model_version = Column(String(32), default="v1.0-rf")
    notes = Column(String(256), nullable=True)


class MenuItem(Base):
    """Canteen Menu Items & Station Portions"""
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    dish_name = Column(String(128), nullable=False)
    shift = Column(String(32), index=True, nullable=False)  # 'breakfast', 'lunch', 'snacks', 'dinner'
    category = Column(String(64), default="Main Course")
    price = Column(Float, default=60.0)
    cost_per_portion = Column(Float, default=24.0)
    portion_share_pct = Column(Float, default=0.50)
    chef_station = Column(String(64), default="Main Steam Line")
    dietary = Column(String(32), default="Veg")
    calories = Column(Integer, default=350)
    allergens = Column(String(128), default="Gluten, Dairy")
    status = Column(String(32), default="ready")
    is_active = Column(Boolean, default=True)
    day_of_week = Column(Integer, nullable=True)
