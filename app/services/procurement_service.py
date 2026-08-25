"""
Canteen Pulse - Procurement & Recipe Ratio Service
Translates predicted meal counts into exact raw ingredient quantities (kg, litres, units) with safety buffers.
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.database import RecipeRatio

class ProcurementService:
    def calculate_procurement_for_meals(
        self,
        db: Session,
        station_counts: Dict[str, int],
        safety_buffer_pct: float = 5.0
    ) -> Dict[str, Any]:
        """
        Calculates grocery and pantry procurement list from station meal forecasts.
        """
        b_count = station_counts.get("breakfast", 0)
        l_count = station_counts.get("lunch", 0)
        s_count = station_counts.get("snacks", 0)
        d_count = station_counts.get("dinner", 0)
        
        main_meals = l_count + d_count
        total_meals = b_count + l_count + s_count + d_count
        
        buffer_mult = 1.0 + (safety_buffer_pct / 100.0)
        
        ratios = db.query(RecipeRatio).all()
        
        items = []
        total_estimated_cost = 0.0
        
        for r in ratios:
            # Determine relevant meal base
            if r.category == "lunch_dinner":
                base_count = main_meals
            elif r.category == "breakfast":
                base_count = b_count
            elif r.category == "snacks":
                base_count = s_count
            elif r.category == "beverage":
                # Beverages consumed across breakfast + snacks + meals
                base_count = int(b_count * 0.8 + s_count * 1.2 + main_meals * 0.3)
            else:
                base_count = total_meals
                
            raw_qty = (base_count / 100.0) * r.qty_per_100_meals
            buffered_qty = round(raw_qty * buffer_mult, 1)
            cost = round(buffered_qty * r.current_unit_price, 2)
            total_estimated_cost += cost
            
            items.append({
                "id": r.id,
                "category": r.category,
                "ingredient_name": r.ingredient_name,
                "unit": r.unit,
                "qty_per_100_meals": r.qty_per_100_meals,
                "base_quantity": round(raw_qty, 1),
                "buffered_quantity": buffered_qty,
                "safety_buffer_pct": safety_buffer_pct,
                "unit_price": r.current_unit_price,
                "estimated_cost": cost,
                "notes": r.notes
            })
            
        return {
            "total_meals": total_meals,
            "main_meals_count": main_meals,
            "station_counts": station_counts,
            "safety_buffer_pct": safety_buffer_pct,
            "total_estimated_cost": round(total_estimated_cost, 2),
            "items_count": len(items),
            "items": items
        }

procurement_service = ProcurementService()
