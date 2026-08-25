"""
Servo AI - Menu Service & Dish Portioning Engine
"""
from typing import Dict, List, Optional
from datetime import date
from sqlalchemy.orm import Session
from app.database import MenuItem, DailyRecord
from app.services.prediction_service import prediction_service

class MenuService:
    async def get_today_menu(self, db: Session, target_date: Optional[date] = None) -> Dict:
        """Returns the full menu catalog for all shifts with AI predicted portion demand"""
        if target_date is None:
            target_date = date.today()

        # Fetch day's prediction breakdown
        pred_data = await prediction_service.get_today_forecast(db, target_date)
        stations = pred_data.get("raw_station_counts", {})  # {"breakfast": 88, "lunch": 182, "snacks": 78, "dinner": 70}

        # Query all active menu items
        items = db.query(MenuItem).filter(MenuItem.is_active == True).all()

        shifts_map = {
            "breakfast": {
                "name": "Breakfast Rush",
                "time_slot": "07:30 - 10:00",
                "predicted_covers": stations.get("breakfast", 88),
                "items": []
            },
            "lunch": {
                "name": "Midday Lunch Line",
                "time_slot": "12:00 - 14:30",
                "predicted_covers": stations.get("lunch", 182),
                "items": []
            },
            "snacks": {
                "name": "Evening Tea & Snacks",
                "time_slot": "16:00 - 18:00",
                "predicted_covers": stations.get("snacks", 78),
                "items": []
            },
            "dinner": {
                "name": "Hostel Dinner",
                "time_slot": "19:30 - 22:00",
                "predicted_covers": stations.get("dinner", 70),
                "items": []
            }
        }

        total_menu_revenue = 0.0
        total_menu_cost = 0.0
        total_dishes_count = 0

        for it in items:
            shift_key = it.shift.lower()
            if shift_key not in shifts_map:
                continue

            shift_covers = shifts_map[shift_key]["predicted_covers"]
            predicted_portions = max(5, round(shift_covers * it.portion_share_pct))
            
            dish_revenue = round(predicted_portions * it.price, 2)
            dish_cost = round(predicted_portions * it.cost_per_portion, 2)
            margin_pct = round(((it.price - it.cost_per_portion) / it.price) * 100, 1) if it.price > 0 else 0

            total_menu_revenue += dish_revenue
            total_menu_cost += dish_cost
            total_dishes_count += 1

            dish_obj = {
                "id": it.id,
                "dish_name": it.dish_name,
                "shift": it.shift,
                "category": it.category,
                "price": it.price,
                "cost_per_portion": it.cost_per_portion,
                "portion_share_pct": round(it.portion_share_pct * 100, 1),
                "predicted_portions": predicted_portions,
                "chef_station": it.chef_station,
                "dietary": it.dietary,
                "calories": it.calories,
                "allergens": it.allergens,
                "status": it.status,
                "estimated_revenue": dish_revenue,
                "estimated_cost": dish_cost,
                "margin_pct": margin_pct,
            }
            shifts_map[shift_key]["items"].append(dish_obj)

        overall_margin = round(((total_menu_revenue - total_menu_cost) / total_menu_revenue) * 100, 1) if total_menu_revenue > 0 else 0

        return {
            "date": target_date.isoformat(),
            "canteen_name": pred_data["canteen_name"],
            "total_daily_covers": pred_data["hero"]["predicted_count"],
            "total_menu_items": total_dishes_count,
            "total_estimated_revenue": round(total_menu_revenue, 2),
            "total_estimated_cost": round(total_menu_cost, 2),
            "overall_gross_margin_pct": overall_margin,
            "shifts": shifts_map
        }

    def update_dish_status(self, db: Session, item_id: int, status: str) -> Dict:
        """Update live kitchen status of a menu item (ready, preparing, low_stock, sold_out)"""
        item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        if not item:
            raise ValueError("Dish item not found")
        item.status = status
        db.commit()
        db.refresh(item)
        return {
            "id": item.id,
            "dish_name": item.dish_name,
            "status": item.status
        }

    def add_menu_item(self, db: Session, data: Dict) -> MenuItem:
        """Add a new dish to the canteen catalog"""
        new_item = MenuItem(
            dish_name=data["dish_name"],
            shift=data.get("shift", "lunch"),
            category=data.get("category", "Main Course"),
            price=float(data.get("price", 60.0)),
            cost_per_portion=float(data.get("cost_per_portion", 24.0)),
            portion_share_pct=float(data.get("portion_share_pct", 0.30)),
            chef_station=data.get("chef_station", "Main Steam Line"),
            dietary=data.get("dietary", "Veg"),
            calories=int(data.get("calories", 350)),
            allergens=data.get("allergens", "Gluten, Dairy"),
            status=data.get("status", "ready"),
            is_active=True
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

menu_service = MenuService()
