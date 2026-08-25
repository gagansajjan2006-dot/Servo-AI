"""
Canteen Pulse - Automated Test Suite
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db
from app.seed_data import seed_database

client = TestClient(app)

def test_startup_and_health():
    init_db()
    seed_database()
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"

def test_today_prediction():
    res = client.get("/api/predict/today")
    assert res.status_code == 200
    data = res.json()
    assert "hero" in data
    assert data["hero"]["predicted_count"] > 50
    assert data["hero"]["confidence_lower"] < data["hero"]["confidence_upper"]
    assert len(data["stations"]) == 4
    assert len(data["reason_chips"]) > 0

def test_range_prediction():
    res = client.get("/api/predict/range?days=14")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 14
    assert data[0]["is_today"] is True

def test_scenario_simulation():
    res = client.post("/api/predict/scenario", json={
        "day_of_week": 0,
        "weather_condition": "Rainy",
        "temperature_c": 22.0,
        "rainfall_mm": 35.0,
        "is_holiday": False,
        "is_exam": True,
        "is_fest": False
    })
    assert res.status_code == 200
    data = res.json()
    assert data["predicted_meals"] > 100
    assert len(data["stations"]) == 4

def test_procurement_calculation():
    res = client.get("/api/procurement/today?buffer=10.0")
    assert res.status_code == 200
    data = res.json()
    assert data["safety_buffer_pct"] == 10.0
    assert len(data["items"]) >= 10
    assert data["total_estimated_cost"] > 0

def test_calendar_heatmap():
    res = client.get("/api/history/calendar?weeks=52")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 300

def test_history_metrics():
    res = client.get("/api/history/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "monthly_accuracy_pct" in data
    assert data["monthly_accuracy_pct"] > 80.0

def test_assistant_ask():
    res = client.post("/api/assistant/ask", json={"query": "Why is today higher than usual?"})
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert len(data["reply"]) > 20

def test_model_retrain():
    res = client.post("/api/admin/retrain")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "metrics" in data
    assert data["metrics"]["r2_score"] > 0.5

def test_menu_today():
    res = client.get("/api/menu/today")
    assert res.status_code == 200
    data = res.json()
    assert "shifts" in data
    assert "lunch" in data["shifts"]
    assert len(data["shifts"]["lunch"]["items"]) > 0
    assert data["total_estimated_revenue"] > 0
    assert data["overall_gross_margin_pct"] > 50

def test_menu_dish_status_update():
    # First get today menu to get a dish id
    menu_res = client.get("/api/menu/today")
    assert menu_res.status_code == 200
    dish_id = menu_res.json()["shifts"]["lunch"]["items"][0]["id"]

    patch_res = client.patch(f"/api/menu/{dish_id}/status", json={"status": "low_stock"})
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "low_stock"

def test_add_menu_item():
    post_res = client.post("/api/menu/item", json={
        "dish_name": "Chef Special Paneer Tikka Platter",
        "shift": "dinner",
        "category": "Tandoor Special",
        "price": 120.0,
        "cost_per_portion": 45.0,
        "portion_share_pct": 0.35,
        "chef_station": "Tandoor Line",
        "dietary": "Veg",
        "calories": 480,
        "allergens": "Dairy",
        "status": "ready"
    })
    assert post_res.status_code == 200
    assert post_res.json()["status"] == "success"
    assert "id" in post_res.json()

def test_serve_index_html():
    res = client.get("/")
    assert res.status_code == 200
    assert "Servo AI" in res.text or "<html" in res.text

def test_vercel_entrypoint():
    from api.index import app as vercel_app
    vclient = TestClient(vercel_app)
    res = vclient.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


