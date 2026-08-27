"""
Servo-AI - Database Seed Script
Generates realistic demo data for MealDemand, FoodWaste, and Feedback tables.

Usage:
    python -m app.seed
"""
import random
import math
import logging
import sys
from datetime import date, timedelta, datetime
from pathlib import Path

# Ensure root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.database import init_db, SessionLocal
from app.models import MealDemand, FoodWaste, Feedback, Prediction
from app.config import STATIONS, CANTEEN_SETTINGS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("servo_ai.seed")

# ==========================================
# Realistic variation parameters
# ==========================================

WEATHER_OPTIONS = ["Clear", "Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Stormy"]
WEATHER_WEIGHTS = [0.25, 0.20, 0.20, 0.20, 0.10, 0.05]

COMMENT_TEMPLATES = [
    "Very fresh and tasty today!",
    "Good portion size, well cooked.",
    "Could use more spice.",
    "Excellent quality as always.",
    "A bit cold when served.",
    "Best dish on the menu today!",
    "Average taste, nothing special.",
    "Loved the flavor, please serve more often.",
    "Too oily for my liking.",
    "Perfect balance of flavors.",
]

# Holiday dates (relative to seed range)
HOLIDAY_OFFSETS = {7, 14, 21, 35}  # Days from start that are holidays


def _generate_base_demand(station_share: float, day_of_week: int, is_holiday: bool, is_weekend: bool) -> float:
    """Generate realistic base demand for a station."""
    total_pop = CANTEEN_SETTINGS["student_population"] + CANTEEN_SETTINGS["faculty_staff_population"]

    # Weekday participation rates
    weekday_rates = {
        0: 0.70, 1: 0.68, 2: 0.66, 3: 0.67, 4: 0.62,
        5: 0.35, 6: 0.28
    }
    participation = weekday_rates.get(day_of_week, 0.65)

    if is_holiday:
        participation *= 0.20

    base = total_pop * participation * station_share
    return base


def seed_meal_demand(db, num_weeks: int = 8):
    """Seeds MealDemand table with realistic per-item demand data."""
    existing = db.query(MealDemand).count()
    if existing > 500:
        logger.info(f"MealDemand already has {existing} records. Skipping seed.")
        return existing

    logger.info(f"Seeding {num_weeks} weeks of MealDemand data...")

    today = date.today()
    start_date = today - timedelta(weeks=num_weeks)
    total_days = (today - start_date).days + 1

    records = []
    for day_offset in range(total_days):
        current_date = start_date + timedelta(days=day_offset)
        dow = current_date.weekday()
        is_weekend = dow >= 5
        is_holiday = day_offset in HOLIDAY_OFFSETS

        # Weather for the day
        weather = random.choices(WEATHER_OPTIONS, weights=WEATHER_WEIGHTS, k=1)[0]
        day_of_year = current_date.timetuple().tm_yday
        # Seasonal temperature
        base_temp = 26.0 + 6.0 * math.sin(day_of_year / 365.0 * 2 * math.pi)
        temperature = round(base_temp + random.uniform(-3, 4), 1)

        if "Rain" in weather or "Storm" in weather:
            temperature = round(temperature - random.uniform(2, 5), 1)

        # Attendance variation
        if is_holiday:
            student_att = random.randint(400, 900)
            faculty_att = random.randint(50, 120)
        elif is_weekend:
            student_att = random.randint(1200, 2200)
            faculty_att = random.randint(80, 180)
        else:
            student_att = random.randint(3000, 4000)
            faculty_att = random.randint(320, 430)

        # Weather multiplier
        weather_mult = 1.0
        if "Rain" in weather:
            weather_mult = 1.06
        elif "Storm" in weather:
            weather_mult = 0.85
        elif temperature > 35:
            weather_mult = 0.95

        for station in STATIONS:
            station_id = station["id"]
            station_share = station["daily_share"]
            menu_items = station["menu"]

            station_demand = _generate_base_demand(station_share, dow, is_holiday, is_weekend)
            station_demand *= weather_mult

            # Distribute across menu items with realistic variation
            num_items = len(menu_items)
            # Generate random shares that sum to ~1.0
            raw_shares = [random.uniform(0.12, 0.35) for _ in range(num_items)]
            total_share = sum(raw_shares)
            item_shares = [s / total_share for s in raw_shares]

            for i, item_name in enumerate(menu_items):
                item_demand = station_demand * item_shares[i]
                # Add noise
                noise = random.gauss(0, item_demand * 0.08)
                actual = max(5, int(round(item_demand + noise)))

                # Predicted quantity (model simulation — slightly off from actual)
                pred_noise = random.gauss(0, actual * 0.06)
                predicted = max(5, int(round(actual + pred_noise)))

                records.append(MealDemand(
                    date=current_date,
                    station=station_id,
                    menu_item=item_name,
                    predicted_quantity=predicted,
                    actual_quantity=actual,
                    weather=weather,
                    temperature=temperature,
                    is_holiday=is_holiday,
                    is_weekend=is_weekend,
                    student_attendance=student_att,
                    faculty_attendance=faculty_att,
                ))

    db.bulk_save_objects(records)
    db.commit()
    logger.info(f"Seeded {len(records)} MealDemand records.")
    return len(records)


def seed_food_waste(db, num_weeks: int = 8):
    """Seeds FoodWaste table from existing MealDemand data."""
    existing = db.query(FoodWaste).count()
    if existing > 200:
        logger.info(f"FoodWaste already has {existing} records. Skipping seed.")
        return existing

    # Get demand data to derive waste from
    demands = db.query(MealDemand).all()
    if not demands:
        logger.warning("No MealDemand data to derive waste from. Seed demand first.")
        return 0

    logger.info("Seeding FoodWaste data...")

    records = []
    # Group by date+station+item, sample a subset for waste tracking
    seen = set()
    for d in demands:
        key = (d.date, d.station, d.menu_item)
        if key in seen:
            continue
        seen.add(key)

        # Not every item has waste tracked every day — sample ~60%
        if random.random() > 0.60:
            continue

        actual = d.actual_quantity
        # Prepared is typically 5-20% more than actual sold
        overprep_pct = random.uniform(0.03, 0.18)
        prepared = int(round(actual * (1 + overprep_pct)))
        sold = actual
        wasted = prepared - sold
        waste_pct = round((wasted / prepared) * 100, 2) if prepared > 0 else 0

        records.append(FoodWaste(
            date=d.date,
            station=d.station,
            menu_item=d.menu_item,
            prepared_quantity=prepared,
            sold_quantity=sold,
            wasted_quantity=wasted,
            waste_percentage=waste_pct,
        ))

    db.bulk_save_objects(records)
    db.commit()
    logger.info(f"Seeded {len(records)} FoodWaste records.")
    return len(records)


def seed_feedback(db, num_weeks: int = 8):
    """Seeds Feedback table with realistic ratings."""
    existing = db.query(Feedback).count()
    if existing > 100:
        logger.info(f"Feedback already has {existing} records. Skipping seed.")
        return existing

    demands = db.query(MealDemand).all()
    if not demands:
        logger.warning("No MealDemand data for feedback. Seed demand first.")
        return 0

    logger.info("Seeding Feedback data...")

    records = []
    seen = set()
    for d in demands:
        key = (d.date, d.station, d.menu_item)
        if key in seen:
            continue
        seen.add(key)

        # ~30% of items get feedback on any given day
        if random.random() > 0.30:
            continue

        rating = random.choices([1, 2, 3, 4, 5], weights=[2, 5, 15, 40, 38], k=1)[0]
        comment = random.choice(COMMENT_TEMPLATES) if random.random() > 0.4 else None

        records.append(Feedback(
            date=d.date,
            station=d.station,
            menu_item=d.menu_item,
            rating=rating,
            comments=comment,
        ))

    db.bulk_save_objects(records)
    db.commit()
    logger.info(f"Seeded {len(records)} Feedback records.")
    return len(records)


def seed_database():
    """Main seed entry point."""
    logger.info("=" * 60)
    logger.info("Servo AI - Database Seed Script")
    logger.info("=" * 60)

    init_db()
    db = SessionLocal()

    try:
        demand_count = seed_meal_demand(db)
        waste_count = seed_food_waste(db)
        feedback_count = seed_feedback(db)

        # Also run the legacy seeder for DailyRecord compatibility
        try:
            from app.seed_data import seed_database as legacy_seed
            legacy_seed()
        except Exception as e:
            logger.warning(f"Legacy seed (DailyRecord) skipped: {e}")

        logger.info("=" * 60)
        logger.info(f"Seed complete!")
        logger.info(f"  MealDemand:  {demand_count} records")
        logger.info(f"  FoodWaste:   {waste_count} records")
        logger.info(f"  Feedback:    {feedback_count} records")
        logger.info("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
