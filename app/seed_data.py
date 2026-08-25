"""
Canteen Pulse - Seed Data Generator
Pre-seeds 365 days of realistic canteen sales data, academic events, weather logs, and recipe ratios.
"""
import random
import math
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session
from app.database import (
    engine, init_db, SessionLocal, DailyRecord, AcademicCalendar, RecipeRatio, ModelTrainingLog, MenuItem
)
from app.config import STATIONS

def seed_database():
    init_db()
    db: Session = SessionLocal()
    
    # Check if menu items need seeding
    if db.query(MenuItem).count() < 10:
        print("Seeding MenuItem catalog...")
        _seed_menu_items(db)

    # Check if already seeded with daily records
    if db.query(DailyRecord).count() > 300:
        print("Database already seeded with daily records.")
        db.close()
        return

    print("Seeding Servo AI database with 365+ days of rich historical operations...")

    # Clear existing
    db.query(DailyRecord).delete()
    db.query(AcademicCalendar).delete()
    db.query(RecipeRatio).delete()
    db.query(ModelTrainingLog).delete()
    db.commit()

    # 1. Recipe Ratios
    recipes = [
        {"category": "lunch_dinner", "ingredient_name": "Premium Sona Masoori Rice", "unit": "kg", "qty_per_100_meals": 14.0, "current_unit_price": 58.0, "notes": "Standard 140g per meal"},
        {"category": "lunch_dinner", "ingredient_name": "Toor Dal & Moong Pulses", "unit": "kg", "qty_per_100_meals": 5.5, "current_unit_price": 145.0, "notes": "55g dry dal per meal"},
        {"category": "lunch_dinner", "ingredient_name": "Fresh Mixed Vegetables", "unit": "kg", "qty_per_100_meals": 12.0, "current_unit_price": 42.0, "notes": "Seasonal greens, carrots, beans"},
        {"category": "lunch_dinner", "ingredient_name": "Paneer / Farm Fresh Chicken", "unit": "kg", "qty_per_100_meals": 8.5, "current_unit_price": 280.0, "notes": "High-protein mains"},
        {"category": "lunch_dinner", "ingredient_name": "Whole Wheat Flour (Atta)", "unit": "kg", "qty_per_100_meals": 7.5, "current_unit_price": 40.0, "notes": "For fresh Phulkas & Rotis"},
        {"category": "lunch_dinner", "ingredient_name": "Refined Sunflower Oil & Ghee", "unit": "litres", "qty_per_100_meals": 3.2, "current_unit_price": 135.0, "notes": "Cooking medium & seasoning"},
        {"category": "breakfast", "ingredient_name": "Idli / Dosa Rice & Urad Batter", "unit": "kg", "qty_per_100_meals": 11.0, "current_unit_price": 62.0, "notes": "Fermented batter mix"},
        {"category": "breakfast", "ingredient_name": "Thick Poha & Semolina", "unit": "kg", "qty_per_100_meals": 6.0, "current_unit_price": 48.0, "notes": "Quick morning staples"},
        {"category": "snacks", "ingredient_name": "Potatoes & Sweet Onions", "unit": "kg", "qty_per_100_meals": 9.5, "current_unit_price": 32.0, "notes": "Samosa, Vada Pav, Veg Cutlet filling"},
        {"category": "beverage", "ingredient_name": "Full Cream Dairy Milk", "unit": "litres", "qty_per_100_meals": 14.5, "current_unit_price": 64.0, "notes": "Chai, Filter Coffee & Curd"},
        {"category": "beverage", "ingredient_name": "Assam CTC Tea & Cardamom", "unit": "kg", "qty_per_100_meals": 1.2, "current_unit_price": 360.0, "notes": "Ginger Masala & Strong Chai"},
        {"category": "beverage", "ingredient_name": "Ground Robusta Coffee Beans", "unit": "kg", "qty_per_100_meals": 0.8, "current_unit_price": 520.0, "notes": "South Indian Filter Brew"}
    ]
    for r in recipes:
        db.add(RecipeRatio(**r))
    db.commit()

    # 2. Academic Calendar Events for the year
    today = date.today()
    start_date = today - timedelta(days=365)
    end_date = today + timedelta(days=30)

    academic_events = [
        # Past events relative to current anchor
        {"delta": -340, "type": "fest", "title": "Fresher's Welcome Carnival", "impact": 1.35, "desc": "High footfall from parents and new batches"},
        {"delta": -300, "type": "holiday", "title": "National Independence Holiday", "impact": 0.20, "desc": "Campus closed, hostel mess light load"},
        {"delta": -260, "type": "exam", "title": "Midterm Examination Week 1", "impact": 1.18, "desc": "Heavy library study sessions and night snacks surge"},
        {"delta": -220, "type": "fest", "title": "Inter-Collegiate Sports Meet", "impact": 1.28, "desc": "Visiting teams meal passes and energy drinks"},
        {"delta": -180, "type": "holiday", "title": "Diwali Festival Break", "impact": 0.15, "desc": "Hostels 85% empty"},
        {"delta": -130, "type": "exam", "title": "Fall Semester Final Exams", "impact": 1.22, "desc": "Intense exam rush & 24hr canteen access"},
        {"delta": -100, "type": "holiday", "title": "Winter Semester Break", "impact": 0.25, "desc": "Research scholars & staff only"},
        {"delta": -65, "type": "fest", "title": "Techno-Hackathon 36H", "impact": 1.32, "desc": "Midnight pizzas, sandwiches and continuous chai orders"},
        {"delta": -35, "type": "exam", "title": "Spring Midterm Exams", "impact": 1.15, "desc": "High lunch & dinner retention on campus"},
        {"delta": -12, "type": "fest", "title": "Alumni Homecoming Dinner", "impact": 1.20, "desc": "Evening dinner banquet and snacks"},
        # Upcoming events (Future)
        {"delta": 2, "type": "fest", "title": "Annual Tech & Robotics Expo", "impact": 1.30, "desc": "Expected 800+ external participants"},
        {"delta": 5, "type": "exam", "title": "Continuous Assessment Test 2", "impact": 1.14, "desc": "Pre-exam rush in late afternoons"},
        {"delta": 9, "type": "holiday", "title": "State Founders Day Holiday", "impact": 0.30, "desc": "Classes off, day scholars absent"},
        {"delta": 14, "type": "placement", "title": "Campus Placement Mega Day", "impact": 1.25, "desc": "Interview panels, recruiters & students lunch"},
        {"delta": 21, "type": "fest", "title": "Cultural Harmony Night", "impact": 1.40, "desc": "Massive dinner & street food counter rush"}
    ]

    event_map = {}
    for ev in academic_events:
        ev_date = today + timedelta(days=ev["delta"])
        event_map[ev_date] = ev
        db.add(AcademicCalendar(
            event_date=ev_date,
            event_type=ev["type"],
            title=ev["title"],
            impact_multiplier=ev["impact"],
            description=ev["desc"]
        ))
    db.commit()

    # 3. Generate 365 Days of Daily Records (Past + Today + 30 Days Future)
    curr_date = start_date
    records_to_add = []
    
    # Base parameters
    weekday_baselines = {
        0: 425,  # Monday - Peak attendance
        1: 412,  # Tuesday - High steady
        2: 405,  # Wednesday - Midweek steady
        3: 398,  # Thursday - High steady
        4: 375,  # Friday - Early weekend departures
        5: 220,  # Saturday - Hostelers & labs only
        6: 165   # Sunday - Brunch & hostel dinner only
    }

    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # History memory for rolling avg calculation
    history_counts = []

    while curr_date <= end_date:
        dow = curr_date.weekday()
        dname = day_names[dow]
        is_wknd = dow in [5, 6]
        
        # Check event
        event = event_map.get(curr_date)
        is_hol = False
        hol_name = None
        is_ex = False
        ex_name = None
        is_sp = False
        sp_name = None
        event_mult = 1.0

        if event:
            if event["type"] == "holiday":
                is_hol = True
                hol_name = event["title"]
                event_mult = event["impact"]
            elif event["type"] == "exam":
                is_ex = True
                ex_name = event["title"]
                event_mult = event["impact"]
            else:
                is_sp = True
                sp_name = event["title"]
                event_mult = event["impact"]

        # Weather simulation
        # Seasonal temp & rain
        day_of_year = curr_date.timetuple().tm_yday
        # Monsoon bump during days 160-250
        is_monsoon_season = 160 <= day_of_year <= 250
        rain_prob = 0.45 if is_monsoon_season else 0.15
        
        is_rainy = random.random() < rain_prob
        if is_rainy:
            rainfall = round(random.uniform(8.0, 48.0), 1)
            weather = "Rainy" if rainfall < 25.0 else "Heavy Rain"
            temp = round(random.uniform(22.0, 27.0), 1)
            humidity = round(random.uniform(75.0, 95.0), 1)
            weather_mult = 1.08  # Rain keeps students on campus + chai/pakoda boom
        else:
            rainfall = 0.0
            weather = random.choice(["Sunny", "Clear", "Partly Cloudy", "Mild Warm"])
            temp = round(26.0 + 8.0 * math.sin(day_of_year / 365.0 * 2 * math.pi) + random.uniform(-2, 3), 1)
            humidity = round(random.uniform(40.0, 68.0), 1)
            weather_mult = 1.0

        # Calculate synthetic ground-truth demand
        base_demand = weekday_baselines[dow]
        # Slight trend over time (+5% growth year over year)
        days_from_start = (curr_date - start_date).days
        trend_mult = 1.0 + (0.05 * (days_from_start / 365.0))
        
        expected_demand = base_demand * event_mult * weather_mult * trend_mult
        
        # Noise
        noise = random.gauss(0, 12)
        true_meals = max(40, int(round(expected_demand + noise)))
        
        # Predictor model simulation (deterministic with high precision & CI)
        pred_meals = int(round(expected_demand + random.gauss(0, 7)))
        ci_spread = int(round(pred_meals * 0.065 + 10))
        ci_lower = max(20, pred_meals - ci_spread)
        ci_upper = pred_meals + ci_spread
        
        # Station breakdowns
        # In rainy weather, snacks jump by 20%
        snack_boost = 1.22 if is_rainy else 1.0
        b_ratio = 0.22 / (1.0 + (snack_boost - 1.0) * 0.18)
        l_ratio = 0.44 / (1.0 + (snack_boost - 1.0) * 0.18)
        s_ratio = (0.18 * snack_boost) / (1.0 + (snack_boost - 1.0) * 0.18)
        d_ratio = 0.16 / (1.0 + (snack_boost - 1.0) * 0.18)

        pred_b = int(round(pred_meals * b_ratio))
        pred_l = int(round(pred_meals * l_ratio))
        pred_s = int(round(pred_meals * s_ratio))
        pred_d = max(10, pred_meals - (pred_b + pred_l + pred_s))

        # Explainability feature contributions (Reason Chips)
        reasons = []
        # Day contribution
        dow_delta = round(((base_demand - 350) / 350) * 100, 1)
        if dow_delta > 0:
            reasons.append({"icon": "calendar", "text": f"{dname} Baseline +{dow_delta}%", "type": "positive", "weight": abs(dow_delta)})
        elif dow_delta < 0:
            reasons.append({"icon": "calendar", "text": f"{dname} Drop {dow_delta}%", "type": "negative", "weight": abs(dow_delta)})

        # Weather contribution
        if is_rainy:
            reasons.append({"icon": "cloud-rain", "text": f"🌧️ {weather} +8% Snack Surge", "type": "positive", "weight": 8.0})
        elif temp > 33.0:
            reasons.append({"icon": "sun", "text": f"☀️ High Heat ({temp}°C) → Cool Beverage +12%", "type": "neutral", "weight": 6.0})

        # Event contribution
        if is_hol:
            reasons.append({"icon": "coffee", "text": f"🎉 {hol_name} (-75% Mess Only)", "type": "negative", "weight": 35.0})
        elif is_ex:
            reasons.append({"icon": "book-open", "text": f"📚 {ex_name} (+18% Study Rush)", "type": "positive", "weight": 18.0})
        elif is_sp:
            reasons.append({"icon": "trophy", "text": f"⭐ {sp_name} (+30% Footfall)", "type": "positive", "weight": 30.0})

        # History rolling average chip
        four_week_avg = int(sum(history_counts[-28:]) / len(history_counts[-28:])) if len(history_counts) >= 7 else base_demand
        reasons.append({"icon": "trending-up", "text": f"📈 4-Wk Rolling Avg: {four_week_avg} meals", "type": "neutral", "weight": 5.0})

        # Anomaly detection for past data
        anomaly_flag = False
        anomaly_reason = None
        actual_meals = None
        act_b, act_l, act_s, act_d = None, None, None, None
        manager_notes = None
        logged_at = None

        if curr_date <= today:
            actual_meals = true_meals
            # Inject 3 notable past anomalies for manager RCA demonstration
            if curr_date == today - timedelta(days=8):
                actual_meals = int(pred_meals * 0.72)  # -28% dip
                anomaly_flag = True
                anomaly_reason = "Unscheduled Water Main Repair in West Block caused early hostel closures"
                manager_notes = "Logged by Chef Raman: Low footfall at lunch due to water repair."
            elif curr_date == today - timedelta(days=22):
                actual_meals = int(pred_meals * 1.34)  # +34% spike
                anomaly_flag = True
                anomaly_reason = "Surprise inter-department debate tournament hosted in central hall"
                manager_notes = "Massive evening snack rush; sold out all 300 samosas."
            elif curr_date == today - timedelta(days=45):
                actual_meals = int(pred_meals * 0.65)
                anomaly_flag = True
                anomaly_reason = "Sudden flash rainstorm & localized power outage"
                manager_notes = "Dinner cook limited to backup gas stoves."

            act_b = int(round(actual_meals * b_ratio))
            act_l = int(round(actual_meals * l_ratio))
            act_s = int(round(actual_meals * s_ratio))
            act_d = max(10, actual_meals - (act_b + act_l + act_s))
            logged_at = datetime.combine(curr_date, datetime.min.time()) + timedelta(hours=22, minutes=30)
            history_counts.append(actual_meals)
        else:
            history_counts.append(pred_meals)

        record = DailyRecord(
            record_date=curr_date,
            day_of_week=dow,
            day_name=dname,
            is_weekend=is_wknd,
            is_holiday=is_hol,
            holiday_name=hol_name,
            is_exam_period=is_ex,
            exam_name=ex_name,
            is_special_event=is_sp,
            event_name=sp_name,
            weather_condition=weather,
            temperature_c=temp,
            rainfall_mm=rainfall,
            humidity_pct=humidity,
            predicted_meals=pred_meals,
            confidence_lower=ci_lower,
            confidence_upper=ci_upper,
            predicted_breakfast=pred_b,
            predicted_lunch=pred_l,
            predicted_snacks=pred_s,
            predicted_dinner=pred_d,
            feature_importance_json=reasons,
            actual_meals=actual_meals,
            actual_breakfast=act_b,
            actual_lunch=act_l,
            actual_snacks=act_s,
            actual_dinner=act_d,
            manager_logged_at=logged_at,
            manager_notes=manager_notes,
            anomaly_flag=anomaly_flag,
            anomaly_reason=anomaly_reason
        )
        records_to_add.append(record)
        curr_date += timedelta(days=1)

    db.bulk_save_objects(records_to_add)
    db.commit()

    # 4. Model Training Log
    initial_training = ModelTrainingLog(
        trained_at=datetime.utcnow() - timedelta(hours=4),
        sample_count=365,
        mae=11.4,
        rmse=15.8,
        r2_score=0.942,
        mape=3.1,
        accuracy_pct=96.9,
        feature_importances={
            "day_of_week": 0.38,
            "rolling_avg_7d": 0.22,
            "is_holiday": 0.16,
            "is_exam_period": 0.11,
            "rainfall_mm": 0.08,
            "temperature_c": 0.03,
            "is_special_event": 0.02
        },
        model_version="v2.4-GBDT-Ensemble",
        notes="Gradient Boosted Decision Trees with Quantile Loss for Confidence Intervals"
    )
    db.add(initial_training)
    db.commit()

    # 5. Menu Dishes Seeding
    _seed_menu_items(db)
    db.close()
    print("Database seeding completed successfully with full menu catalog!")

def _seed_menu_items(db: Session):
    db.query(MenuItem).delete()
    menu_dishes = [
        # BREAKFAST
        {"dish_name": "Crispy Masala Dosa with Sambar & Chutney", "shift": "breakfast", "category": "South Indian Griddle", "price": 45.0, "cost_per_portion": 16.0, "portion_share_pct": 0.45, "chef_station": "Griddle Line", "dietary": "Veg", "calories": 320, "allergens": "Dairy", "status": "ready"},
        {"dish_name": "Steamed Ghee Idli & Medu Vada Combo", "shift": "breakfast", "category": "Steamer Station", "price": 40.0, "cost_per_portion": 14.0, "portion_share_pct": 0.35, "chef_station": "Steam Line", "dietary": "Veg", "calories": 280, "allergens": "None", "status": "ready"},
        {"dish_name": "Indori Poha with Roasted Peanuts & Sev", "shift": "breakfast", "category": "Breakfast Staples", "price": 30.0, "cost_per_portion": 10.0, "portion_share_pct": 0.28, "chef_station": "Griddle Line", "dietary": "Veg", "calories": 250, "allergens": "Peanuts", "status": "ready"},
        {"dish_name": "Spiced Egg Bhurji & Butter Toast", "shift": "breakfast", "category": "Egg Station", "price": 50.0, "cost_per_portion": 20.0, "portion_share_pct": 0.22, "chef_station": "Egg Station", "dietary": "Non-Veg", "calories": 340, "allergens": "Eggs, Gluten, Dairy", "status": "ready"},
        {"dish_name": "Traditional South Indian Filter Coffee", "shift": "breakfast", "category": "Beverage Bar", "price": 20.0, "cost_per_portion": 7.0, "portion_share_pct": 0.58, "chef_station": "Beverage Bar", "dietary": "Veg", "calories": 95, "allergens": "Dairy", "status": "ready"},

        # LUNCH
        {"dish_name": "Grand Executive Thali (Paneer, Dal, Sabzi, Rice, 3 Rotis)", "shift": "lunch", "category": "Executive Platters", "price": 95.0, "cost_per_portion": 38.0, "portion_share_pct": 0.48, "chef_station": "Main Steam Line", "dietary": "Veg", "calories": 680, "allergens": "Gluten, Dairy", "status": "ready"},
        {"dish_name": "Hyderabadi Chicken Dum Biryani & Mirchi Salan", "shift": "lunch", "category": "Special Handi Line", "price": 140.0, "cost_per_portion": 55.0, "portion_share_pct": 0.36, "chef_station": "Handi Line", "dietary": "Non-Veg", "calories": 620, "allergens": "Dairy", "status": "ready"},
        {"dish_name": "Shahi Paneer Butter Masala with Butter Naan", "shift": "lunch", "category": "Curry Line", "price": 85.0, "cost_per_portion": 32.0, "portion_share_pct": 0.30, "chef_station": "Tandoor & Curry", "dietary": "Veg", "calories": 540, "allergens": "Gluten, Dairy, Nuts", "status": "ready"},
        {"dish_name": "Amritsari Rajma Masala & Jeera Rice Bowl", "shift": "lunch", "category": "Homestyle Bowls", "price": 65.0, "cost_per_portion": 22.0, "portion_share_pct": 0.24, "chef_station": "Main Steam Line", "dietary": "Veg", "calories": 460, "allergens": "None", "status": "ready"},
        {"dish_name": "Tempered Curd Rice with Pomegranate & Pickle", "shift": "lunch", "category": "Cooling Bowls", "price": 40.0, "cost_per_portion": 13.0, "portion_share_pct": 0.20, "chef_station": "Salad & Cold Bar", "dietary": "Veg", "calories": 290, "allergens": "Dairy, Mustard", "status": "ready"},
        {"dish_name": "Warm Gulab Jamun in Saffron Syrup (2 Pcs)", "shift": "lunch", "category": "Dessert Corner", "price": 30.0, "cost_per_portion": 11.0, "portion_share_pct": 0.28, "chef_station": "Dessert Station", "dietary": "Veg", "calories": 210, "allergens": "Gluten, Dairy", "status": "ready"},

        # EVENING SNACKS
        {"dish_name": "Fresh Kadak Adrak Masala Chai", "shift": "snacks", "category": "Tea Bar", "price": 15.0, "cost_per_portion": 4.5, "portion_share_pct": 0.78, "chef_station": "Tea Bar", "dietary": "Veg", "calories": 85, "allergens": "Dairy", "status": "ready"},
        {"dish_name": "Golden Punjabi Samosa with Mint & Saunth Chutney (2 Pcs)", "shift": "snacks", "category": "Fryer Line", "price": 25.0, "cost_per_portion": 8.0, "portion_share_pct": 0.62, "chef_station": "Fryer Station", "dietary": "Veg", "calories": 310, "allergens": "Gluten", "status": "ready"},
        {"dish_name": "Mumbai Batata Vada Pav with Fried Green Chutney", "shift": "snacks", "category": "Street Food Griddle", "price": 25.0, "cost_per_portion": 8.5, "portion_share_pct": 0.44, "chef_station": "Griddle Line", "dietary": "Veg", "calories": 290, "allergens": "Gluten", "status": "ready"},
        {"dish_name": "Flaky Vegetable Puff Pastry", "shift": "snacks", "category": "Bakehouse", "price": 25.0, "cost_per_portion": 9.0, "portion_share_pct": 0.32, "chef_station": "Bake House", "dietary": "Veg", "calories": 260, "allergens": "Gluten", "status": "ready"},
        {"dish_name": "Rich Cold Coffee with Chocolate Drizzle & Ice Cream", "shift": "snacks", "category": "Beverage Bar", "price": 45.0, "cost_per_portion": 17.0, "portion_share_pct": 0.38, "chef_station": "Beverage Bar", "dietary": "Veg", "calories": 240, "allergens": "Dairy", "status": "ready"},

        # DINNER
        {"dish_name": "Hostel Dinner Special (Yellow Dal Tadka, Aloo Gobhi, 4 Phulkas)", "shift": "dinner", "category": "Hostel Homestyle", "price": 75.0, "cost_per_portion": 28.0, "portion_share_pct": 0.52, "chef_station": "Hostel Steam Line", "dietary": "Veg", "calories": 520, "allergens": "Gluten, Dairy", "status": "ready"},
        {"dish_name": "Dhaba Style Egg Curry with Steamed Rice & Paratha", "shift": "dinner", "category": "Curry Line", "price": 85.0, "cost_per_portion": 32.0, "portion_share_pct": 0.32, "chef_station": "Curry Station", "dietary": "Non-Veg", "calories": 490, "allergens": "Eggs, Gluten, Dairy", "status": "ready"},
        {"dish_name": "Paneer Bhurji & Butter Tawa Paratha Combo", "shift": "dinner", "category": "Griddle Line", "price": 90.0, "cost_per_portion": 35.0, "portion_share_pct": 0.28, "chef_station": "Griddle Station", "dietary": "Veg", "calories": 540, "allergens": "Gluten, Dairy", "status": "ready"},
        {"dish_name": "Veg Dum Biryani with Cucumber Mint Raita", "shift": "dinner", "category": "Special Handi Line", "price": 95.0, "cost_per_portion": 34.0, "portion_share_pct": 0.22, "chef_station": "Handi Line", "dietary": "Veg", "calories": 510, "allergens": "Dairy", "status": "ready"}
    ]
    for d in menu_dishes:
        db.add(MenuItem(**d))
    db.commit()

if __name__ == "__main__":
    seed_database()
