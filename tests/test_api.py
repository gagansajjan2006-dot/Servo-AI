"""
Servo-AI - Comprehensive API Test Suite
Validates all endpoints across Health, Predictions, Meals, Demand, Waste, Analytics, Recommendations, ML, and Settings.
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, SessionLocal
from app.seed import seed_database
from app.ml.model_manager import model_manager

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_test_data():
    """Initializes the DB, seeds realistic data, and trains model before tests."""
    init_db()
    seed_database()
    db = SessionLocal()
    try:
        model_manager.retrain(db)
    finally:
        db.close()


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["model"] in ("loaded", "not_loaded")


def test_list_meals():
    res = client.get("/api/meals")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 4
    station_ids = [s["id"] for s in data]
    assert "breakfast" in station_ids
    assert "lunch" in station_ids
    assert "snacks" in station_ids
    assert "dinner" in station_ids


def test_get_single_station():
    res = client.get("/api/meals/lunch")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "lunch"
    assert data["name"] == "Midday Lunch Line"
    assert "Chicken Biryani" in data["menu"]


def test_get_station_menu():
    res = client.get("/api/meals/breakfast/menu")
    assert res.status_code == 200
    data = res.json()
    assert data["station"] == "breakfast"
    assert "Masala Dosa" in data["menu"]


def test_ml_status():
    res = client.get("/api/ml/status")
    assert res.status_code == 200
    data = res.json()
    assert data["model_name"] == "RandomForestRegressor"
    assert data["is_trained"] is True
    assert len(data["features"]) > 0


def test_predict_single_item():
    payload = {
        "date": "2026-08-30",
        "station": "lunch",
        "menu_item": "Chicken Biryani",
        "temperature": 29.5,
        "weather": "Rainy",
        "is_holiday": False,
        "student_attendance": 3600,
        "faculty_attendance": 400,
        "confidence": 0.95,
    }
    res = client.post("/api/predictions/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["station"] == "lunch"
    assert data["menu_item"] == "Chicken Biryani"
    assert data["predicted_quantity"] > 0
    assert data["lower_bound"] <= data["predicted_quantity"] <= data["upper_bound"]


def test_daily_forecast():
    res = client.get("/api/predictions/daily?target_date=2026-08-30")
    assert res.status_code == 200
    data = res.json()
    assert data["total_expected_meals"] > 0
    assert len(data["stations"]) == 4


def test_create_and_get_demand():
    payload = {
        "date": "2026-08-25",
        "station": "breakfast",
        "menu_item": "Poha",
        "actual_quantity": 140.0,
        "weather": "Sunny",
        "temperature": 27.0,
        "is_holiday": False,
        "is_weekend": False,
        "student_attendance": 3500,
        "faculty_attendance": 380,
    }
    res = client.post("/api/demand", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["actual_quantity"] == 140.0

    # Retrieve by date
    res2 = client.get("/api/demand/2026-08-25")
    assert res2.status_code == 200
    records = res2.json()
    assert len(records) > 0


def test_demand_csv_upload():
    csv_data = (
        "date,station,menu_item,actual_quantity,weather,temperature,is_holiday,is_weekend\n"
        "2026-08-26,lunch,Rajma Chawal,195,Sunny,30.0,false,false\n"
        "2026-08-26,dinner,Veg Pulao,120,Clear,26.0,false,false\n"
    )
    files = {"file": ("test_demand.csv", csv_data.encode("utf-8"), "text/csv")}
    res = client.post("/api/demand/upload", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["records_imported"] == 2


def test_create_and_summarize_waste():
    payload = {
        "date": "2026-08-25",
        "station": "lunch",
        "menu_item": "Executive Thali",
        "prepared_quantity": 250.0,
        "sold_quantity": 230.0,
    }
    res = client.post("/api/waste", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["wasted_quantity"] == 20.0
    assert data["waste_percentage"] == 8.0

    res2 = client.get("/api/waste/summary")
    assert res2.status_code == 200
    summary = res2.json()
    assert summary["total_prepared"] > 0
    assert len(summary["top_wasted_items"]) > 0


def test_analytics_dashboard():
    res = client.get("/api/analytics/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "students" in data
    assert "seating_capacity" in data
    assert "peak_station" in data


def test_analytics_weekly():
    res = client.get("/api/analytics/weekly")
    assert res.status_code == 200
    data = res.json()
    assert "trend" in data
    assert "total_meals" in data


def test_analytics_monthly():
    res = client.get("/api/analytics/monthly")
    assert res.status_code == 200
    data = res.json()
    assert "months" in data


def test_analytics_stations():
    res = client.get("/api/analytics/stations")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 4


def test_analytics_menu_items():
    res = client.get("/api/analytics/menu-items")
    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0


def test_recommendations():
    res = client.get("/api/recommendations")
    assert res.status_code == 200
    data = res.json()
    assert "recommendations" in data
    assert data["count"] >= 0


def test_settings():
    res = client.get("/api/settings")
    assert res.status_code == 200
    data = res.json()
    assert data["student_population"] == 4200
    assert len(data["stations"]) == 4


def test_dashboard_today_forecast():
    res = client.get("/api/predict/today")
    assert res.status_code == 200
    data = res.json()
    assert "hero" in data
    assert "stations" in data
    assert "weather" in data
    assert data["hero"]["predicted_count"] > 0


def test_dashboard_range_forecast():
    res = client.get("/api/predict/range?days=7")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 7


def test_dashboard_menu_today():
    res = client.get("/api/menu/today")
    assert res.status_code == 200
    data = res.json()
    assert "shifts" in data
    assert data["total_menu_items"] > 0


def test_dashboard_procurement():
    res = client.get("/api/procurement/today?buffer=5")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert data["items_count"] > 0


def test_dashboard_history_metrics():
    res = client.get("/api/history/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "monthly_accuracy_pct" in data
    assert "r2_score" in data


def test_dashboard_history_calendar():
    res = client.get("/api/history/calendar?weeks=4")
    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0


def test_dashboard_assistant_ask():
    res = client.post("/api/assistant/ask", json={"query": "Why is today higher?"})
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert len(data["reply"]) > 0


def test_batch_csv_prediction_endpoint():
    csv_data = (
        "date,temperature_c,rainfall_mm,humidity_pct,is_holiday,is_exam,is_special,rolling_avg_7d,rolling_avg_28d\n"
        "2026-09-01,29.5,0.0,52,0,0,0,410,405\n"
        "2026-09-02,30.0,0.0,50,0,0,0,412,406\n"
        "2026-09-03,26.0,18.5,85,0,0,0,408,405\n"
    )
    files = {"file": ("test_input.csv", csv_data.encode("utf-8"), "text/csv")}
    res = client.post("/api/predictions/batch-csv?buffer=7.5", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "summary" in data
    assert data["summary"]["total_rows_processed"] == 3
    assert data["summary"]["total_predicted_meals"] > 0
    assert data["summary"]["safety_buffer_pct"] == 7.5
    assert len(data["predictions"]) == 3
    
    first_pred = data["predictions"][0]
    assert first_pred["date"] == "2026-09-01"
    assert first_pred["predicted_meals"] > 0
    assert first_pred["breakfast_covers"] > 0
    assert first_pred["lunch_covers"] > 0
    assert first_pred["snacks_covers"] > 0
    assert first_pred["dinner_covers"] > 0
    assert first_pred["lower_bound_95ci"] <= first_pred["predicted_meals"] <= first_pred["upper_bound_95ci"]
    assert "rice_staple_kg" in first_pred
    assert "dal_staple_kg" in first_pred
    assert first_pred["total_ingredient_cost_inr"] > 0


def test_batch_csv_download_endpoint():
    csv_data = (
        "date,temperature_c,rainfall_mm,humidity_pct,is_holiday,is_exam,is_special,rolling_avg_7d,rolling_avg_28d\n"
        "2026-09-01,29.5,0.0,52,0,0,0,410,405\n"
    )
    files = {"file": ("test_input.csv", csv_data.encode("utf-8"), "text/csv")}
    res = client.post("/api/predictions/batch-csv/download?buffer=5.0", files=files)
    assert res.status_code == 200
    assert "text/csv" in res.headers.get("content-type", "")
    content = res.text
    assert "PREDICTED_MEALS" in content
    assert "CONFIDENCE_LOWER_95" in content
    assert "BREAKFAST_MEALS" in content
    assert "LUNCH_MEALS" in content
    assert "RICE_REQUISITION" in content
    assert "ESTIMATED_GROCERY_COST" in content


def test_sample_csv_template_endpoint():
    res = client.get("/api/predictions/sample-csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers.get("content-type", "")
    content = res.text
    assert "date,temperature_c,rainfall_mm" in content
    assert "2026-09-01" in content


def test_batch_csv_errors():
    # Empty file
    files = {"file": ("empty.csv", b"", "text/csv")}
    res = client.post("/api/predictions/batch-csv", files=files)
    assert res.status_code == 400

    # Non-CSV extension
    files2 = {"file": ("test.txt", b"some text", "text/plain")}
    res2 = client.post("/api/predictions/batch-csv", files=files2)
    assert res2.status_code == 400


