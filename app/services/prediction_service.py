"""
Canteen Pulse - Central Prediction Service
Coordinates forecasts for Today, 7-14 day outlooks, scenario simulations, and station breakdowns.
"""
from datetime import date, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.database import DailyRecord, AcademicCalendar
from app.config import STATIONS, CANTEEN_SETTINGS
from app.ml.model import forecaster
from app.services.weather_service import weather_service

class PredictionService:
    async def get_today_forecast(self, db: Session, target_date: Optional[date] = None) -> Dict[str, Any]:
        """Returns the high-fidelity Kitchen Command Center forecast for today (or specified date)."""
        if target_date is None:
            target_date = date.today()
            
        # 1. Fetch DB record if exists
        record = db.query(DailyRecord).filter(DailyRecord.record_date == target_date).first()
        
        # 2. Fetch live weather
        weather = await weather_service.get_weather_for_date(target_date)
        
        # 3. Fetch academic event
        event = db.query(AcademicCalendar).filter(AcademicCalendar.event_date == target_date).first()
        is_hol = (event.event_type == "holiday") if event else (record.is_holiday if record else False)
        is_ex = (event.event_type == "exam") if event else (record.is_exam_period if record else False)
        is_sp = (event.event_type in ["fest", "placement", "sports"]) if event else (record.is_special_event if record else False)
        event_title = event.title if event else (record.holiday_name or record.exam_name or record.event_name if record else None)
        
        # 4. Fetch 7d rolling average baseline from past records
        past_records = (
            db.query(DailyRecord)
            .filter(DailyRecord.record_date < target_date)
            .order_by(DailyRecord.record_date.desc())
            .limit(28)
            .all()
        )
        if past_records:
            recent_actuals = [r.actual_meals or r.predicted_meals or 380 for r in past_records[:7]]
            roll7 = sum(recent_actuals) / len(recent_actuals)
            all_actuals = [r.actual_meals or r.predicted_meals or 380 for r in past_records]
            roll28 = sum(all_actuals) / len(all_actuals)
        else:
            roll7 = 395.0
            roll28 = 390.0
            
        # 5. Generate forecast
        pred_res = forecaster.predict(
            target_date=target_date,
            is_holiday=is_hol,
            is_exam=is_ex,
            is_special=is_sp,
            temp_c=weather["temperature_c"],
            rainfall_mm=weather["rainfall_mm"],
            humidity_pct=weather["humidity_pct"],
            rolling_avg_7d=roll7,
            rolling_avg_28d=roll28
        )
        
        # 6. Format Stations with rich operational metadata
        station_cards = []
        station_counts = pred_res["stations"]
        
        for st in STATIONS:
            s_id = st["id"]
            count = station_counts.get(s_id, 0)
            
            # Simulated readiness & load status
            if s_id == "breakfast":
                status = "Service Active" if 7 <= 9 <= 10 else "Prepped & Ready"
                prep_note = "Dosa batter 35kg ready; Sambar simmering at 85°C"
            elif s_id == "lunch":
                status = "Prep in Progress"
                prep_note = f"Steamers loaded for {count} thali portions; Rice boiling"
            elif s_id == "snacks":
                status = "Afternoon Prep"
                prep_note = "Samosa rolling batch 1 starts 15:00; Ginger tea decoction set"
            else:
                status = "Scheduled"
                prep_note = "Dinner grains soaked; Chef shift handoff at 18:30"
                
            station_cards.append({
                "id": s_id,
                "name": st["name"],
                "time_slot": st["time_slot"],
                "predicted_count": count,
                "percentage_of_day": round((count / max(1, pred_res["predicted_meals"])) * 100, 1),
                "peak_window": st["peak_window"],
                "key_items": st["key_items"],
                "status": status,
                "prep_note": prep_note,
                "icon": st["icon"]
            })
            
        return {
            "date": target_date.isoformat(),
            "day_name": target_date.strftime("%A"),
            "formatted_date": target_date.strftime("%b %d, %Y"),
            "canteen_name": CANTEEN_SETTINGS["canteen_name"],
            "campus": CANTEEN_SETTINGS["campus"],
            "hero": {
                "predicted_count": pred_res["predicted_meals"],
                "confidence_lower": pred_res["confidence_interval"]["lower"],
                "confidence_upper": pred_res["confidence_interval"]["upper"],
                "trend": pred_res["trend"],  # 'surging', 'cooling', 'steady'
                "baseline_diff_pct": round(((pred_res["predicted_meals"] - roll7) / roll7) * 100, 1),
                "capacity_utilization_pct": round((pred_res["predicted_meals"] / CANTEEN_SETTINGS["default_capacity"]) * 100, 1)
            },
            "weather": weather,
            "event": {
                "has_event": bool(event_title),
                "event_type": event.event_type if event else None,
                "title": event_title
            },
            "reason_chips": pred_res["reason_chips"],
            "stations": station_cards,
            "raw_station_counts": station_counts,
            "actual_record": {
                "actual_meals": record.actual_meals if record else None,
                "manager_notes": record.manager_notes if record else None,
                "anomaly_flag": record.anomaly_flag if record else False,
                "anomaly_reason": record.anomaly_reason if record else None
            } if record else None
        }

    async def get_range_forecast(self, db: Session, days: int = 14) -> List[Dict[str, Any]]:
        """Returns timeline outlook for the next N days with mini cards, weather, and event badges."""
        today = date.today()
        outlook = []
        
        for i in range(days):
            target_date = today + timedelta(days=i)
            day_data = await self.get_today_forecast(db, target_date=target_date)
            outlook.append({
                "date": target_date.isoformat(),
                "day_name": target_date.strftime("%a"),
                "formatted_date": target_date.strftime("%d %b"),
                "is_today": (i == 0),
                "predicted_meals": day_data["hero"]["predicted_count"],
                "confidence_lower": day_data["hero"]["confidence_lower"],
                "confidence_upper": day_data["hero"]["confidence_upper"],
                "trend": day_data["hero"]["trend"],
                "weather_icon": day_data["weather"]["icon"],
                "weather_temp": day_data["weather"]["temperature_c"],
                "weather_cond": day_data["weather"]["condition"],
                "event": day_data["event"],
                "station_counts": day_data["raw_station_counts"],
                "top_reason": day_data["reason_chips"][0]["text"] if day_data["reason_chips"] else ""
            })
            
        return outlook

    async def run_scenario_simulation(
        self,
        db: Session,
        day_of_week: int,
        weather_condition: str,
        temperature_c: float,
        rainfall_mm: float,
        is_holiday: bool,
        is_exam: bool,
        is_fest: bool
    ) -> Dict[str, Any]:
        """Runs interactive what-if simulation for the Kitchen Command Center."""
        today = date.today()
        # Find next occurrence of chosen DOW
        days_ahead = (day_of_week - today.weekday()) % 7
        target_date = today + timedelta(days=days_ahead)
        
        pred_res = forecaster.predict(
            target_date=target_date,
            is_holiday=is_holiday,
            is_exam=is_exam,
            is_special=is_fest,
            temp_c=temperature_c,
            rainfall_mm=rainfall_mm,
            humidity_pct=80.0 if rainfall_mm > 5.0 else 55.0,
            rolling_avg_7d=395.0,
            rolling_avg_28d=390.0
        )
        
        return {
            "simulated_date": target_date.isoformat(),
            "day_name": target_date.strftime("%A"),
            "predicted_meals": pred_res["predicted_meals"],
            "confidence_lower": pred_res["confidence_interval"]["lower"],
            "confidence_upper": pred_res["confidence_interval"]["upper"],
            "trend": pred_res["trend"],
            "stations": pred_res["stations"],
            "reason_chips": pred_res["reason_chips"]
        }

prediction_service = PredictionService()
