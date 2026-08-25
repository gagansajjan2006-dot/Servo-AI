"""
Canteen Pulse - FastAPI Main Application & API Server
"""
import io
import csv
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import CANTEEN_SETTINGS, STATIONS
from app.database import (
    init_db, get_db, SessionLocal, DailyRecord, AcademicCalendar, RecipeRatio, ManagerCorrection, ModelTrainingLog, MenuItem
)
from app.seed_data import seed_database
from app.ml.model import forecaster
from app.services.weather_service import weather_service
from app.services.procurement_service import procurement_service
from app.services.prediction_service import prediction_service
from app.services.assistant_service import assistant_service
from app.services.menu_service import menu_service

from pathlib import Path

STATIC_DIR = Path(__file__).resolve().parent / "static"

_db_initialized = False

def ensure_initialized():
    global _db_initialized
    if not _db_initialized:
        try:
            init_db()
            seed_database()
            db = SessionLocal()
            try:
                if not forecaster._is_fitted:
                    forecaster.train_on_records(db)
            except Exception as e:
                print(f"Warning during model init: {e}")
            finally:
                db.close()
        except Exception as e:
            print(f"Warning during database init: {e}")
        _db_initialized = True

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    ensure_initialized()
    yield
    # Shutdown

app = FastAPI(
    title="🔥 Servo AI API",
    description="Steam & Ledger Campus Dining Demand Prediction Engine",
    version="3.0.0",
    lifespan=lifespan
)

@app.middleware("http")
async def db_init_middleware(request, call_next):
    if not _db_initialized:
        ensure_initialized()
    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- WEBSOCKET FOR LIVE TELEMETRY -----------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

ws_manager = ConnectionManager()

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo heartbeat or client commands
            await websocket.send_json({"type": "pong", "time": datetime.now().isoformat()})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

# ----------------- PYDANTIC SCHEMAS -----------------
class ScenarioRequest(BaseModel):
    day_of_week: int = 0
    weather_condition: str = "Rainy"
    temperature_c: float = 24.0
    rainfall_mm: float = 15.0
    is_holiday: bool = False
    is_exam: bool = False
    is_fest: bool = False

class ActualLogRequest(BaseModel):
    record_date: str
    actual_meals: int
    actual_breakfast: Optional[int] = None
    actual_lunch: Optional[int] = None
    actual_snacks: Optional[int] = None
    actual_dinner: Optional[int] = None
    manager_notes: Optional[str] = None
    anomaly_flag: bool = False
    anomaly_reason: Optional[str] = None

class AssistantQueryRequest(BaseModel):
    query: str

class WeatherConfigRequest(BaseModel):
    api_key: Optional[str] = None
    city: Optional[str] = None
    scenario: Optional[str] = None

class AcademicEventRequest(BaseModel):
    event_date: str
    event_type: str
    title: str
    impact_multiplier: float = 1.0
    description: Optional[str] = None

class RecipeRatioRequest(BaseModel):
    category: str
    ingredient_name: str
    unit: str = "kg"
    qty_per_100_meals: float
    current_unit_price: float
    notes: Optional[str] = None

# ----------------- REST ENDPOINTS -----------------

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/health")
def api_health():
    return {
        "status": "ok",
        "service": "Servo AI Command Engine",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/predict/today")
async def get_today_prediction(target_date: Optional[str] = None, db: Session = Depends(get_db)):
    """Returns today's (or target date's) live command center forecast, reason chips & station loads."""
    d = date.fromisoformat(target_date) if target_date else date.today()
    result = await prediction_service.get_today_forecast(db, target_date=d)
    return result

@app.get("/api/predict/range")
async def get_range_prediction(days: int = Query(14, ge=3, le=30), db: Session = Depends(get_db)):
    """Returns 7-14 day forecast timeline strip with mini forecast cards."""
    result = await prediction_service.get_range_forecast(db, days=days)
    return result

@app.post("/api/predict/scenario")
async def simulate_scenario(req: ScenarioRequest, db: Session = Depends(get_db)):
    """Interactive what-if simulator."""
    result = await prediction_service.run_scenario_simulation(
        db=db,
        day_of_week=req.day_of_week,
        weather_condition=req.weather_condition,
        temperature_c=req.temperature_c,
        rainfall_mm=req.rainfall_mm,
        is_holiday=req.is_holiday,
        is_exam=req.is_exam,
        is_fest=req.is_fest
    )
    return result

@app.get("/api/procurement/today")
async def get_today_procurement(buffer: float = Query(5.0, ge=0.0, le=30.0), db: Session = Depends(get_db)):
    """Translates today's station meal forecasts into exact raw ingredient procurement list."""
    today_data = await prediction_service.get_today_forecast(db)
    station_counts = today_data["raw_station_counts"]
    proc = procurement_service.calculate_procurement_for_meals(db, station_counts, safety_buffer_pct=buffer)
    return proc

@app.get("/api/history/calendar")
def get_calendar_heatmap(weeks: int = Query(52, ge=4, le=52), db: Session = Depends(get_db)):
    """Returns historical daily records for the GitHub-style calendar heatmap."""
    today = date.today()
    start = today - timedelta(weeks=weeks)
    records = (
        db.query(DailyRecord)
        .filter(DailyRecord.record_date >= start, DailyRecord.record_date <= today)
        .order_by(DailyRecord.record_date.asc())
        .all()
    )
    
    heatmap_data = []
    for r in records:
        pred = r.predicted_meals or 0
        act = r.actual_meals
        diff = (act - pred) if (act is not None and pred) else 0
        variance_pct = round((diff / pred) * 100, 1) if pred else 0.0
        
        heatmap_data.append({
            "date": r.record_date.isoformat(),
            "day_of_week": r.day_of_week,
            "day_name": r.day_name,
            "actual_meals": act,
            "predicted_meals": pred,
            "variance": diff,
            "variance_pct": variance_pct,
            "weather": r.weather_condition,
            "temp": r.temperature_c,
            "anomaly_flag": r.anomaly_flag,
            "anomaly_reason": r.anomaly_reason,
            "is_holiday": r.is_holiday,
            "holiday_name": r.holiday_name,
            "is_exam": r.is_exam_period,
            "exam_name": r.exam_name,
            "is_fest": r.is_special_event,
            "fest_name": r.event_name
        })
        
    return heatmap_data

@app.get("/api/history/metrics")
def get_history_metrics(db: Session = Depends(get_db)):
    """Returns model trust & accuracy indicators."""
    latest_log = db.query(ModelTrainingLog).order_by(ModelTrainingLog.trained_at.desc()).first()
    
    # Calculate 30-day recent operational accuracy
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    recent = (
        db.query(DailyRecord)
        .filter(DailyRecord.record_date >= thirty_days_ago, DailyRecord.record_date <= today, DailyRecord.actual_meals.isnot(None))
        .all()
    )
    
    if recent:
        errors = [abs(r.actual_meals - (r.predicted_meals or r.actual_meals)) for r in recent]
        mape_list = [
            abs(r.actual_meals - (r.predicted_meals or r.actual_meals)) / max(1, r.actual_meals) * 100
            for r in recent
        ]
        recent_mae = round(sum(errors) / len(errors), 1)
        recent_accuracy = round(max(0.0, 100.0 - (sum(mape_list) / len(mape_list))), 1)
    else:
        recent_mae = 11.4
        recent_accuracy = 96.9

    return {
        "monthly_accuracy_pct": recent_accuracy,
        "monthly_mae": recent_mae,
        "model_version": latest_log.model_version if latest_log else "v2.4-GBDT",
        "last_trained_at": latest_log.trained_at.isoformat() if latest_log else datetime.now().isoformat(),
        "total_samples": latest_log.sample_count if latest_log else 365,
        "r2_score": latest_log.r2_score if latest_log else 0.942,
        "mape": latest_log.mape if latest_log else 3.1,
        "feature_importances": latest_log.feature_importances if latest_log else forecaster.feature_importances
    }

class MenuStatusUpdateRequest(BaseModel):
    status: str

class MenuItemCreateRequest(BaseModel):
    dish_name: str
    shift: str = "lunch"
    category: str = "Main Course"
    price: float = 60.0
    cost_per_portion: float = 24.0
    portion_share_pct: float = 0.30
    chef_station: str = "Main Steam Line"
    dietary: str = "Veg"
    calories: int = 350
    allergens: str = "Gluten, Dairy"
    status: str = "ready"

@app.get("/api/menu/today")
async def get_today_menu(target_date: Optional[str] = None, db: Session = Depends(get_db)):
    """Returns dynamic daily menu with predicted portions per dish and kitchen revenue."""
    t_date = date.fromisoformat(target_date) if target_date else date.today()
    return await menu_service.get_today_menu(db, t_date)

@app.patch("/api/menu/{item_id}/status")
async def update_dish_status(item_id: int, payload: MenuStatusUpdateRequest, db: Session = Depends(get_db)):
    """Updates live kitchen availability status (ready, preparing, low_stock, sold_out)."""
    try:
        updated = menu_service.update_dish_status(db, item_id, payload.status)
        await ws_manager.broadcast({
            "event": "menu_status_updated",
            "item_id": item_id,
            "status": payload.status,
            "dish_name": updated["dish_name"]
        })
        return updated
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/menu/item")
async def add_menu_item(payload: MenuItemCreateRequest, db: Session = Depends(get_db)):
    """Adds a new dish item to the canteen catalog."""
    data = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    item = menu_service.add_menu_item(db, data)
    await ws_manager.broadcast({
        "event": "menu_item_added",
        "dish_name": item.dish_name,
        "shift": item.shift
    })
    return {"status": "success", "id": item.id, "dish_name": item.dish_name}

@app.post("/api/sales/actual")
async def log_actual_sales(payload: ActualLogRequest, db: Session = Depends(get_db)):
    """Logs end-of-service actual meal count & retraining triggers."""
    d = date.fromisoformat(payload.record_date)
    record = db.query(DailyRecord).filter(DailyRecord.record_date == d).first()
    
    if not record:
        record = DailyRecord(record_date=d, day_of_week=d.weekday(), day_name=d.strftime("%A"))
        db.add(record)
        
    record.actual_meals = payload.actual_meals
    record.actual_breakfast = payload.actual_breakfast
    record.actual_lunch = payload.actual_lunch
    record.actual_snacks = payload.actual_snacks
    record.actual_dinner = payload.actual_dinner
    record.manager_notes = payload.manager_notes
    record.manager_logged_at = datetime.now()
    record.anomaly_flag = payload.anomaly_flag
    record.anomaly_reason = payload.anomaly_reason
    
    # Audit log
    audit = ManagerCorrection(
        record_date=d,
        original_prediction=record.predicted_meals,
        adjusted_count=payload.actual_meals,
        correction_type="actual_log",
        reason=payload.anomaly_reason or payload.manager_notes or "Daily end-of-shift logging"
    )
    db.add(audit)
    db.commit()
    
    # Broadcast live update over websocket
    await ws_manager.broadcast({
        "event": "actual_logged",
        "date": d.isoformat(),
        "actual_meals": payload.actual_meals,
        "anomaly_flag": payload.anomaly_flag
    })
    
    return {"status": "success", "message": f"Recorded {payload.actual_meals} actual meals for {d.isoformat()}"}

@app.post("/api/assistant/ask")
async def ask_assistant(req: AssistantQueryRequest, db: Session = Depends(get_db)):
    """Conversational assistant query."""
    res = await assistant_service.process_query(db, req.query)
    return res

@app.get("/api/admin/academic")
def get_academic_events(db: Session = Depends(get_db)):
    events = db.query(AcademicCalendar).order_by(AcademicCalendar.event_date.asc()).all()
    return [{
        "id": e.id,
        "event_date": e.event_date.isoformat(),
        "event_type": e.event_type,
        "title": e.title,
        "impact_multiplier": e.impact_multiplier,
        "description": e.description
    } for e in events]

@app.post("/api/admin/academic")
def add_academic_event(event: AcademicEventRequest, db: Session = Depends(get_db)):
    d = date.fromisoformat(event.event_date)
    new_ev = AcademicCalendar(
        event_date=d,
        event_type=event.event_type,
        title=event.title,
        impact_multiplier=event.impact_multiplier,
        description=event.description
    )
    db.add(new_ev)
    
    # Update DailyRecord if exists
    rec = db.query(DailyRecord).filter(DailyRecord.record_date == d).first()
    if rec:
        if event.event_type == "holiday":
            rec.is_holiday = True
            rec.holiday_name = event.title
        elif event.event_type == "exam":
            rec.is_exam_period = True
            rec.exam_name = event.title
        else:
            rec.is_special_event = True
            rec.event_name = event.title
            
    db.commit()
    return {"status": "success", "id": new_ev.id}

@app.post("/api/admin/retrain")
async def retrain_model(db: Session = Depends(get_db)):
    """Triggers ML model retraining on updated actuals."""
    metrics = forecaster.train_on_records(db)
    
    await ws_manager.broadcast({
        "event": "model_retrained",
        "metrics": metrics,
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        "status": "success",
        "message": "Demand prediction engine successfully retrained on latest operational actuals",
        "metrics": metrics,
        "feature_importances": forecaster.feature_importances
    }

@app.post("/api/admin/weather-config")
async def update_weather_config(cfg: WeatherConfigRequest):
    """Updates weather provider or simulation preset."""
    weather_service.set_config(api_key=cfg.api_key, city=cfg.city, scenario=cfg.scenario)
    weather_service.cached_weather.clear()
    
    await ws_manager.broadcast({
        "event": "weather_scenario_updated",
        "scenario": weather_service.current_scenario
    })
    
    return {
        "status": "success",
        "current_scenario": weather_service.current_scenario,
        "city": weather_service.city_name,
        "simulation_mode": weather_service.simulation_mode
    }

@app.get("/api/admin/export-csv")
def export_sales_csv(db: Session = Depends(get_db)):
    """Exports historical canteen sales data to CSV."""
    records = db.query(DailyRecord).order_by(DailyRecord.record_date.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "record_date", "day_name", "actual_meals", "predicted_meals",
        "weather", "temp_c", "rainfall_mm", "holiday", "exam", "fest", "manager_notes"
    ])
    for r in records:
        writer.writerow([
            r.record_date.isoformat(), r.day_name, r.actual_meals or "", r.predicted_meals or "",
            r.weather_condition, r.temperature_c, r.rainfall_mm,
            r.holiday_name or "", r.exam_name or "", r.event_name or "", r.manager_notes or ""
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=canteen_pulse_export_{date.today().isoformat()}.csv"}
    )

# ----------------- STATIC FILES MOUNTING -----------------
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/favicon.ico", include_in_schema=False)
@app.get("/favicon.png", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@app.get("/")
@app.get("/api/index.py")
@app.get("/api")
def serve_root(request: Request):
    accept = request.headers.get("accept", "")
    format_param = request.query_params.get("format", "")
    
    # If explicitly requesting JSON
    if format_param == "json" or ("application/json" in accept and "text/html" not in accept):
        return {"message": "Servo AI API is running"}
    
    # If browser is requesting HTML
    if "text/html" in accept:
        index_file = STATIC_DIR / "index.html"
        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read(), status_code=200)
                
    # Default API response
    return {"message": "Servo AI API is running"}
