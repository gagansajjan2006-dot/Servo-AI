from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database import RecipeRatio

DEFAULT_RECIPE_RATIOS = [
    {"id": 1, "category": "lunch_dinner", "ingredient_name": "Premium Sona Masoori Rice", "unit": "kg", "qty_per_100_meals": 14.0, "current_unit_price": 58.0, "notes": "Standard 140g per meal"},
    {"id": 2, "category": "lunch_dinner", "ingredient_name": "Toor Dal & Moong Pulses", "unit": "kg", "qty_per_100_meals": 5.5, "current_unit_price": 145.0, "notes": "55g dry dal per meal"},
    {"id": 3, "category": "lunch_dinner", "ingredient_name": "Fresh Mixed Vegetables", "unit": "kg", "qty_per_100_meals": 12.0, "current_unit_price": 42.0, "notes": "Seasonal greens, carrots, beans"},
    {"id": 4, "category": "lunch_dinner", "ingredient_name": "Paneer / Farm Fresh Chicken", "unit": "kg", "qty_per_100_meals": 8.5, "current_unit_price": 280.0, "notes": "High-protein mains"},
    {"id": 5, "category": "lunch_dinner", "ingredient_name": "Whole Wheat Flour (Atta)", "unit": "kg", "qty_per_100_meals": 7.5, "current_unit_price": 40.0, "notes": "For fresh Phulkas & Rotis"},
    {"id": 6, "category": "lunch_dinner", "ingredient_name": "Refined Sunflower Oil & Ghee", "unit": "litres", "qty_per_100_meals": 3.2, "current_unit_price": 135.0, "notes": "Cooking medium & seasoning"},
    {"id": 7, "category": "breakfast", "ingredient_name": "Idli / Dosa Rice & Urad Batter", "unit": "kg", "qty_per_100_meals": 11.0, "current_unit_price": 62.0, "notes": "Fermented batter mix"},
    {"id": 8, "category": "breakfast", "ingredient_name": "Thick Poha & Semolina", "unit": "kg", "qty_per_100_meals": 6.0, "current_unit_price": 48.0, "notes": "Quick morning staples"},
    {"id": 9, "category": "snacks", "ingredient_name": "Potatoes & Sweet Onions", "unit": "kg", "qty_per_100_meals": 9.5, "current_unit_price": 32.0, "notes": "Samosa, Vada Pav, Veg Cutlet filling"},
    {"id": 10, "category": "beverage", "ingredient_name": "Full Cream Dairy Milk", "unit": "litres", "qty_per_100_meals": 14.5, "current_unit_price": 64.0, "notes": "Chai, Filter Coffee & Curd"},
    {"id": 11, "category": "beverage", "ingredient_name": "Assam CTC Tea & Cardamom", "unit": "kg", "qty_per_100_meals": 1.2, "current_unit_price": 360.0, "notes": "Ginger Masala & Strong Chai"},
    {"id": 12, "category": "beverage", "ingredient_name": "Ground Robusta Coffee Beans", "unit": "kg", "qty_per_100_meals": 0.8, "current_unit_price": 520.0, "notes": "South Indian Filter Brew"}
]

class ProcurementService:
    def calculate_procurement_for_meals(
        self,
        db: Optional[Session] = None,
        station_counts: Optional[Dict[str, int]] = None,
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
        
        db_ratios = db.query(RecipeRatio).all() if db else []
        ratios = db_ratios if db_ratios else [type('RecipeObj', (), r)() for r in DEFAULT_RECIPE_RATIOS]
        
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
