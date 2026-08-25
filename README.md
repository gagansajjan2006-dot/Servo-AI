# 🔥 Servo AI — Steam & Ledger Campus Dining Forecaster

Servo AI is an intelligent demand prediction and kitchen operations platform for campus dining facilities. It uses machine learning to forecast meal demand across dayparts (Breakfast, Lunch, Snacks, Dinner), optimize raw ingredient procurement, prevent food waste, and deliver actionable operational intelligence.

---

## ✨ Features

- **🤖 AI/ML Demand Forecasting:** Multi-factor regression models (Gradient Boosting / Random Forest / Ridge) integrating academic calendars, exam schedules, holidays, and live weather conditions.
- **📊 Real-Time Operations Dashboard:** Interactive visualization of today's live meal counts, station breakdown, capacity gauges, and confidence intervals.
- **📈 Historical Analysis & Heatmaps:** Deep dive into dining trends, variance analysis, and weekday-by-hour dining density heatmaps.
- **🥦 Smart Procurement Calculator:** Converts projected meal demand into precise raw ingredient procurement orders with safety buffers and cost estimation.
- **📋 Menu Planning & Item-Level Forecasting:** Station-wise recipe ratios and item popularity modeling.
- **💬 Conversational Dining Assistant:** In-app operational copilot answering queries about prep lists, rush hours, weather impacts, and anomaly detection.
- **⚡ WebSocket Telemetry:** Live dining hall telemetry simulation and real-time updates.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, FastAPI, Uvicorn, SQLAlchemy, Pydantic
- **Machine Learning:** scikit-learn, pandas, numpy, joblib
- **Frontend:** Vanilla JS, CSS3 Design System, Chart.js, Glassmorphism UI
- **Database:** SQLite (with automatic schema creation & synthetic historical seed data)

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <YOUR_REPO_URL>
cd "servo AI"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python run.py
```
Open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 🧪 Running Tests

Execute the automated test suite with `pytest`:
```bash
python -m pytest
```

---

## 📁 Project Structure

```
├── app/
│   ├── config.py              # Configuration & constants
│   ├── database.py            # SQLAlchemy models & database session
│   ├── main.py                # FastAPI endpoints & WebSocket router
│   ├── seed_data.py           # Historical dataset generator & seeder
│   ├── ml/
│   │   ├── features.py        # Feature engineering pipeline
│   │   ├── model.py           # Demand forecasting ML model
│   │   └── explainability.py  # Feature importance & attribution
│   ├── services/
│   │   ├── assistant_service.py   # AI Assistant conversational logic
│   │   ├── menu_service.py        # Menu & recipe management
│   │   ├── prediction_service.py  # Inference orchestration
│   │   ├── procurement_service.py # Ingredient order calculator
│   │   └── weather_service.py     # Weather simulation & integration
│   └── static/                # Frontend UI, CSS, and JS modules
├── data/                      # Local database & trained model storage
├── tests/                     # Pytest automated test suite
├── requirements.txt           # Python package dependencies
├── run.py                     # Application startup entry point
└── README.md
```

---

## 📄 License

MIT License.
