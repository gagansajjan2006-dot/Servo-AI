"""
Canteen Pulse - Weather Service
Handles real-time weather retrieval with caching & realistic high-fidelity simulation fallbacks.
"""
from typing import Dict, Any, Optional
from datetime import date, datetime
import random
import httpx

class WeatherService:
    def __init__(self):
        self.api_key = None  # OpenWeather API Key if configured by admin
        self.city_name = "Bangalore, IN"
        self.cached_weather = {}
        self.simulation_mode = True
        self.current_scenario = "Monsoon Shower"  # Presets: 'Monsoon Shower', 'Sunny Summer', 'Crisp Winter', 'Overcast Cool'

    def set_config(self, api_key: Optional[str] = None, city: Optional[str] = None, scenario: Optional[str] = None):
        if api_key:
            self.api_key = api_key
            self.simulation_mode = False
        if city:
            self.city_name = city
        if scenario:
            self.current_scenario = scenario

    async def get_weather_for_date(self, target_date: date) -> Dict[str, Any]:
        """Returns weather forecast for a given date."""
        date_str = target_date.isoformat()
        
        # Check cache
        if date_str in self.cached_weather:
            return self.cached_weather[date_str]

        # If live API is configured
        if not self.simulation_mode and self.api_key:
            try:
                async with httpx.AsyncClient(timeout=4.0) as client:
                    resp = await client.get(
                        f"https://api.openweathermap.org/data/2.5/weather?q={self.city_name}&appid={self.api_key}&units=metric"
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        w_data = {
                            "condition": data["weather"][0]["main"],
                            "description": data["weather"][0]["description"].capitalize(),
                            "temperature_c": round(data["main"]["temp"], 1),
                            "rainfall_mm": round(data.get("rain", {}).get("1h", 0.0), 1),
                            "humidity_pct": round(data["main"]["humidity"], 1),
                            "icon": self._map_icon(data["weather"][0]["main"]),
                            "canteen_impact": self._calculate_impact(data["weather"][0]["main"], data["main"]["temp"])
                        }
                        self.cached_weather[date_str] = w_data
                        return w_data
            except Exception as e:
                print(f"Weather API error, falling back to simulated engine: {e}")

        # Simulated dynamic scenario weather
        w_data = self._generate_simulated_weather(target_date)
        self.cached_weather[date_str] = w_data
        return w_data

    def _generate_simulated_weather(self, target_date: date) -> Dict[str, Any]:
        """Generates realistic weather based on scenario and target date."""
        today = date.today()
        day_diff = (target_date - today).days
        
        if self.current_scenario == "Monsoon Shower":
            # Rainy today and nearby days
            is_rain = (day_diff % 2 == 0)
            rainfall = 24.5 if is_rain else 4.0
            cond = "Rainy" if is_rain else "Overcast"
            desc = "Moderate Rain Showers" if is_rain else "Cloudy with drizzle threat"
            temp = 24.2 + (day_diff * 0.2)
            humid = 86.0
        elif self.current_scenario == "Sunny Summer":
            rainfall = 0.0
            cond = "Sunny"
            desc = "Clear skies and hot sun"
            temp = 34.5 + (day_diff * 0.1)
            humid = 42.0
        elif self.current_scenario == "Crisp Winter":
            rainfall = 0.0
            cond = "Clear"
            desc = "Breezy and cool mornings"
            temp = 19.5 + (day_diff * 0.1)
            humid = 50.0
        else: # Overcast
            rainfall = 2.0
            cond = "Partly Cloudy"
            desc = "Pleasant mild breeze"
            temp = 27.0
            humid = 62.0

        return {
            "condition": cond,
            "description": desc,
            "temperature_c": round(temp, 1),
            "rainfall_mm": round(rainfall, 1),
            "humidity_pct": round(humid, 1),
            "icon": self._map_icon(cond),
            "canteen_impact": self._calculate_impact(cond, temp)
        }

    def _map_icon(self, condition: str) -> str:
        c = condition.lower()
        if "rain" in c:
            return "cloud-rain"
        elif "thunder" in c or "storm" in c:
            return "cloud-lightning"
        elif "snow" in c or "cold" in c:
            return "snowflake"
        elif "cloud" in c:
            return "cloud"
        elif "clear" in c or "sun" in c:
            return "sun"
        return "sun-medium"

    def _calculate_impact(self, condition: str, temp: float) -> str:
        c = condition.lower()
        if "rain" in c:
            return "🌧️ Rain expected → +8% lunch & +22% hot chai / snack demand"
        elif temp > 32.0:
            return "☀️ High heat → +20% cold beverage & curd rice orders"
        elif temp < 20.0:
            return "❄️ Cool weather → +10% hot breakfast & piping coffee demand"
        return "🌤️ Moderate conditions → Normal station load distribution"

weather_service = WeatherService()
