"""
Servo-AI - Application Configuration
Portable configuration module supporting Windows, Linux, and serverless runtimes.
"""
import os
import sys
from pathlib import Path

# Base workspace directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Detect serverless / cloud function runtime (Vercel, AWS Lambda, etc.)
IS_SERVERLESS = bool(
    os.environ.get("VERCEL")
    or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
    or os.environ.get("NOW_REGION")
    or os.environ.get("LAMBDA_TASK_ROOT")
)

# Runtime data directory selection
if IS_SERVERLESS:
    DATA_DIR = Path("/tmp/servo_ai_data")
else:
    # Use environment override if set, otherwise default to local 'data' folder
    env_data_dir = os.environ.get("DATA_DIR")
    if env_data_dir:
        DATA_DIR = Path(env_data_dir).resolve()
    else:
        DATA_DIR = BASE_DIR / "data"

# Ensure data directory exists with fallback
try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
except (OSError, PermissionError):
    DATA_DIR = Path("/tmp/servo_ai_data")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database file & URL configuration
DB_PATH = DATA_DIR / "servo_ai.db"
DEFAULT_SQLITE_URL = f"sqlite:///{DB_PATH}"
DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_SQLITE_URL)

# Model directories and files
MODEL_DIR = DATA_DIR / "models"
try:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
except (OSError, PermissionError):
    MODEL_DIR = Path("/tmp/servo_ai_data/models")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_FILE = MODEL_DIR / "demand_forecaster.joblib"
BUNDLED_MODEL_FILE = BASE_DIR / "data" / "models" / "demand_forecaster.joblib"

# Ensure bundled model directory exists
try:
    (BASE_DIR / "data" / "models").mkdir(parents=True, exist_ok=True)
except (OSError, PermissionError):
    pass

# Environment & CORS configuration
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000,http://localhost:5173")

# Default Campus Dining & Kitchen Settings
CANTEEN_SETTINGS = {
    "name": "Grand Hall Central Dining & Kitchen",
    "campus": "Tech & Engineering Campus",
    "student_population": 4200,
    "faculty_staff_population": 450,
    "seating_capacity": 600,
    "confidence_level": 0.95,
    # Backward compatibility aliases
    "canteen_name": "Grand Hall Central Dining & Kitchen",
    "default_capacity": 600,
}

# Meal Stations configuration
STATIONS = [
    {
        "id": "breakfast",
        "name": "Breakfast Rush",
        "time": "07:30 - 10:00",
        "time_slot": "07:30 - 10:00",
        "daily_share": 0.22,
        "weight_pct": 0.22,
        "peak_window": "08:15 - 08:50",
        "menu": [
            "Masala Dosa",
            "Idli Sambar",
            "Poha",
            "Egg Toast",
            "Filter Coffee"
        ],
        "key_items": [
            "Masala Dosa",
            "Idli Sambar",
            "Poha",
            "Egg Toast",
            "Filter Coffee"
        ],
        "icon": "coffee"
    },
    {
        "id": "lunch",
        "name": "Midday Lunch Line",
        "time": "12:00 - 14:30",
        "time_slot": "12:00 - 14:30",
        "daily_share": 0.44,
        "weight_pct": 0.44,
        "peak_window": "12:30 - 13:45",
        "menu": [
            "Executive Thali",
            "Rajma Chawal",
            "Paneer Butter Masala",
            "Chicken Biryani",
            "Curd Rice"
        ],
        "key_items": [
            "Executive Thali",
            "Rajma Chawal",
            "Paneer Butter Masala",
            "Chicken Biryani",
            "Curd Rice"
        ],
        "icon": "utensils"
    },
    {
        "id": "snacks",
        "name": "Evening Tea & Snacks",
        "time": "16:00 - 18:00",
        "time_slot": "16:00 - 18:00",
        "daily_share": 0.18,
        "weight_pct": 0.18,
        "peak_window": "16:30 - 17:15",
        "menu": [
            "Adrak Masala Chai",
            "Samosa",
            "Veg Puff",
            "Vada Pav",
            "Cold Coffee"
        ],
        "key_items": [
            "Adrak Masala Chai",
            "Samosa",
            "Veg Puff",
            "Vada Pav",
            "Cold Coffee"
        ],
        "icon": "croissant"
    },
    {
        "id": "dinner",
        "name": "Hostel Dinner",
        "time": "19:30 - 22:00",
        "time_slot": "19:30 - 22:00",
        "daily_share": 0.16,
        "weight_pct": 0.16,
        "peak_window": "20:15 - 21:15",
        "menu": [
            "Dal Tadka & Roti",
            "Veg Pulao",
            "Egg Curry",
            "Mixed Veg",
            "Gulab Jamun"
        ],
        "key_items": [
            "Dal Tadka & Roti",
            "Veg Pulao",
            "Egg Curry",
            "Mixed Veg",
            "Gulab Jamun"
        ],
        "icon": "moon"
    }
]

# Quick lookup mapping station id -> station dict
STATION_MAP = {s["id"]: s for s in STATIONS}
