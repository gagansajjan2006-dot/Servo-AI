"""
Servo AI - App Configuration
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "servo_ai.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Model configuration
MODEL_DIR = DATA_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_FILE = MODEL_DIR / "demand_forecaster.joblib"

# Default Campus Dining & Kitchen Settings
CANTEEN_SETTINGS = {
    "canteen_name": "Grand Hall Central Dining & Kitchen",
    "campus": "Tech & Engineering Campus",
    "student_population": 4200,
    "faculty_staff_population": 450,
    "default_capacity": 600,
    "confidence_level": 0.95,
}

# Meal Stations configuration
STATIONS = [
    {
        "id": "breakfast",
        "name": "Breakfast Rush",
        "time_slot": "07:30 - 10:00",
        "weight_pct": 0.22,
        "peak_window": "08:15 - 08:50",
        "key_items": ["Masala Dosa", "Idli Sambar", "Poha", "Egg Toast", "Filter Coffee"],
        "icon": "coffee"
    },
    {
        "id": "lunch",
        "name": "Midday Lunch Line",
        "time_slot": "12:00 - 14:30",
        "weight_pct": 0.44,
        "peak_window": "12:30 - 13:45",
        "key_items": ["Executive Thali", "Rajma Chawal", "Paneer Butter Masala", "Chicken Biryani", "Curd Rice"],
        "icon": "utensils"
    },
    {
        "id": "snacks",
        "name": "Evening Tea & Snacks",
        "time_slot": "16:00 - 18:00",
        "weight_pct": 0.18,
        "peak_window": "16:30 - 17:15",
        "key_items": ["Adrak Masala Chai", "Samosa", "Veg Puff", "Vada Pav", "Cold Coffee"],
        "icon": "croissant"
    },
    {
        "id": "dinner",
        "name": "Hostel Dinner",
        "time_slot": "19:30 - 22:00",
        "weight_pct": 0.16,
        "peak_window": "20:15 - 21:15",
        "key_items": ["Dal Tadka & Roti", "Veg Pulao", "Egg Curry", "Mixed Veg", "Gulab Jamun"],
        "icon": "moon"
    }
]
