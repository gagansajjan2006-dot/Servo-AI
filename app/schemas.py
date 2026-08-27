"""
Servo-AI - Pydantic Request & Response Schemas
Validates all incoming payload data and guarantees structured, typed API responses.
"""
from datetime import date as PyDate, datetime as PyDateTime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ==========================================
# Generic & Error Response Schemas
# ==========================================
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str


class StandardResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None


# ==========================================
# User Schemas
# ==========================================
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=128, examples=["Chef Vikram"])
    email: str = Field(..., min_length=5, max_length=128, examples=["vikram.chef@canteen.edu"])
    role: str = Field("staff", examples=["manager"])  # admin, staff, manager


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: PyDateTime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Meal Demand Schemas
# ==========================================
class MealDemandBase(BaseModel):
    date: PyDate = Field(..., examples=["2026-08-28"])
    station: str = Field(..., examples=["lunch"])
    menu_item: str = Field(..., examples=["Chicken Biryani"])
    predicted_quantity: Optional[float] = Field(None, examples=[820.0])
    actual_quantity: float = Field(..., ge=0, examples=[815.0])
    weather: str = Field("Clear", examples=["Clear"])
    temperature: float = Field(28.0, examples=[28.5])
    is_holiday: bool = Field(False, examples=[False])
    is_weekend: bool = Field(False, examples=[False])
    student_attendance: int = Field(3500, ge=0, examples=[3500])
    faculty_attendance: int = Field(380, ge=0, examples=[380])


class MealDemandCreate(MealDemandBase):
    pass


class MealDemandBulkCreate(BaseModel):
    records: List[MealDemandCreate]


class MealDemandResponse(MealDemandBase):
    id: int
    created_at: PyDateTime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Prediction Schemas
# ==========================================
class PredictionRequest(BaseModel):
    date: PyDate = Field(..., examples=["2026-08-28"])
    station: str = Field(..., examples=["lunch"])
    menu_item: str = Field(..., examples=["Chicken Biryani"])
    temperature: float = Field(28.0, examples=[28.0])
    weather: str = Field("cloudy", examples=["cloudy"])
    is_holiday: bool = Field(False, examples=[False])
    student_attendance: int = Field(3500, ge=0, examples=[3500])
    faculty_attendance: int = Field(380, ge=0, examples=[380])
    confidence: Optional[float] = Field(0.95, ge=0.5, le=0.99, examples=[0.95])


class PredictionResponse(BaseModel):
    station: str = Field(..., examples=["lunch"])
    menu_item: str = Field(..., examples=["Chicken Biryani"])
    predicted_quantity: float = Field(..., examples=[820.0])
    lower_bound: float = Field(..., examples=[750.0])
    upper_bound: float = Field(..., examples=[890.0])
    confidence: float = Field(0.95, examples=[0.95])
    date: Optional[PyDate] = None


class StationForecastItem(BaseModel):
    station: str = Field(..., examples=["lunch"])
    station_name: Optional[str] = Field(None, examples=["Midday Lunch Line"])
    expected_demand: int = Field(..., examples=[1360])
    lower_bound: Optional[int] = None
    upper_bound: Optional[int] = None
    peak_window: Optional[str] = None
    menu: Optional[List[str]] = None


class DailyForecastResponse(BaseModel):
    date: PyDate = Field(..., examples=["2026-08-28"])
    total_expected_meals: int = Field(..., examples=[3100])
    confidence_lower: Optional[int] = None
    confidence_upper: Optional[int] = None
    stations: List[StationForecastItem]


class BatchCSVPredictionRow(BaseModel):
    row_index: int
    date: str
    day_name: str
    predicted_meals: int
    lower_bound_95ci: int
    upper_bound_95ci: int
    trend: str
    breakfast_covers: int
    lunch_covers: int
    snacks_covers: int
    dinner_covers: int
    rice_staple_kg: str
    dal_staple_kg: str
    veggies_kg: str
    milk_litres: str
    cooking_oil_litres: str
    total_ingredient_cost_inr: float
    primary_reason: str
    all_reasons: str
    input_temperature_c: float
    input_rainfall_mm: float
    input_is_holiday: bool
    input_is_exam: bool
    input_is_special: bool


class BatchCSVForecastSummary(BaseModel):
    total_rows_processed: int
    total_predicted_meals: int
    average_daily_meals: float
    total_estimated_procurement_cost: float
    safety_buffer_pct: float
    model_architecture: str
    processed_at: str


class BatchCSVForecastResponse(BaseModel):
    success: bool = True
    summary: BatchCSVForecastSummary
    predictions: List[BatchCSVPredictionRow]
    columns: Optional[List[str]] = None


# ==========================================
# Food Waste Schemas
# ==========================================
class FoodWasteCreate(BaseModel):
    date: PyDate = Field(..., examples=["2026-08-28"])
    station: str = Field(..., examples=["lunch"])
    menu_item: str = Field(..., examples=["Chicken Biryani"])
    prepared_quantity: float = Field(..., gt=0, examples=[850.0])
    sold_quantity: float = Field(..., ge=0, examples=[815.0])


class FoodWasteResponse(BaseModel):
    id: int
    date: PyDate
    station: str
    menu_item: str
    prepared_quantity: float
    sold_quantity: float
    wasted_quantity: float
    waste_percentage: float
    created_at: PyDateTime

    model_config = ConfigDict(from_attributes=True)


class TopWasteItem(BaseModel):
    menu_item: str
    station: str
    total_wasted: float
    total_prepared: float
    average_waste_percentage: float


class FoodWasteSummary(BaseModel):
    total_prepared: float
    total_sold: float
    total_wasted: float
    average_waste_percentage: float
    top_wasted_items: List[TopWasteItem]


# ==========================================
# Feedback Schemas
# ==========================================
class FeedbackCreate(BaseModel):
    date: PyDate = Field(..., examples=["2026-08-28"])
    station: str = Field(..., examples=["lunch"])
    menu_item: str = Field(..., examples=["Chicken Biryani"])
    rating: int = Field(..., ge=1, le=5, examples=[5])
    comments: Optional[str] = Field(None, examples=["Biryani was fresh and flavor was excellent!"])


class FeedbackResponse(BaseModel):
    id: int
    date: PyDate
    station: str
    menu_item: str
    rating: int
    comments: Optional[str]
    created_at: PyDateTime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Dashboard & Analytics Schemas
# ==========================================
class DashboardAnalyticsResponse(BaseModel):
    today_demand: int = Field(..., examples=[3100])
    predicted_demand: int = Field(..., examples=[3250])
    average_waste_percentage: float = Field(..., examples=[8.4])
    food_saved_estimate: int = Field(..., examples=[215])
    peak_station: str = Field(..., examples=["lunch"])
    peak_menu_item: str = Field(..., examples=["Chicken Biryani"])
    students: int = Field(4200, examples=[4200])
    faculty_staff: int = Field(450, examples=[450])
    seating_capacity: int = Field(600, examples=[600])


class DayDemandPoint(BaseModel):
    date: str
    day_name: str
    actual_meals: Optional[int] = None
    predicted_meals: Optional[int] = None
    waste_percentage: Optional[float] = None


class WeeklyAnalyticsResponse(BaseModel):
    start_date: str
    end_date: str
    total_meals: int
    average_daily_meals: float
    trend: List[DayDemandPoint]


class MonthSummaryPoint(BaseModel):
    month: str
    total_demand: int
    avg_daily_demand: float
    total_waste_kg: float
    accuracy_pct: float


class MonthlyAnalyticsResponse(BaseModel):
    months: List[MonthSummaryPoint]


class StationAnalyticsItem(BaseModel):
    station_id: str
    station_name: str
    total_demand: int
    share_pct: float
    average_waste_pct: float
    top_item: str


class MenuItemAnalyticsItem(BaseModel):
    menu_item: str
    station: str
    total_sold: float
    total_prepared: float
    total_wasted: float
    waste_pct: float
    avg_rating: Optional[float] = None


# ==========================================
# AI Recommendations Schemas
# ==========================================
class RecommendationItem(BaseModel):
    id: str
    type: str = Field("adjustment", examples=["adjustment"])  # adjustment, alert, operational, efficiency
    title: str = Field(..., examples=["Portion Optimization"])
    message: str = Field(..., examples=["Increase Chicken Biryani preparation by 12%."])
    impact: str = Field("medium", examples=["high"])  # low, medium, high
    category: str = Field("kitchen", examples=["procurement"])  # kitchen, procurement, station, waste
    confidence: float = Field(0.95, examples=[0.92])


class RecommendationsResponse(BaseModel):
    generated_at: PyDateTime
    count: int
    recommendations: List[RecommendationItem]


# ==========================================
# ML Training & Status Schemas
# ==========================================
class TrainModelRequest(BaseModel):
    min_samples: Optional[int] = Field(10, ge=5)


class TrainModelResponse(BaseModel):
    status: str = Field("success", examples=["success"])
    model: str = Field("RandomForestRegressor", examples=["RandomForestRegressor"])
    mae: float = Field(..., examples=[42.3])
    mse: float = Field(..., examples=[3100.5])
    rmse: float = Field(..., examples=[55.68])
    r2_score: float = Field(..., examples=[0.94])
    training_rows: int = Field(..., examples=[1250])
    feature_importances: Optional[Dict[str, float]] = None


class ModelStatusResponse(BaseModel):
    status: str
    model_name: str
    is_trained: bool
    last_trained: Optional[str]
    total_samples: int
    mae: Optional[float]
    rmse: Optional[float]
    r2_score: Optional[float]
    features: List[str]


# ==========================================
# Settings Schemas
# ==========================================
class MealStationItem(BaseModel):
    id: str
    name: str
    time: str
    daily_share: float
    peak_window: str
    menu: List[str]


class CanteenSettingsResponse(BaseModel):
    name: str
    campus: str
    student_population: int
    faculty_staff_population: int
    seating_capacity: int
    confidence_level: float
    stations: List[MealStationItem]


class SettingsUpdate(BaseModel):
    name: Optional[str] = None
    campus: Optional[str] = None
    student_population: Optional[int] = None
    faculty_staff_population: Optional[int] = None
    seating_capacity: Optional[int] = None
    confidence_level: Optional[float] = None
