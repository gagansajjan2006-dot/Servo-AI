# 🍽️ Servo-AI – AI-Powered Campus Canteen Demand Forecasting System

Servo-AI is a high-performance demand forecasting backend engine engineered with **Python FastAPI, SQLAlchemy, SQLite, Pandas, Scikit-learn (RandomForest), and Joblib**. It accurately forecasts dish-level and station-level meal requirements across campus canteen meal shifts (Breakfast, Lunch, Snacks, Dinner), drastically minimizing food wastage and optimizing procurement.

---

## 🌟 Key Features

- **Multi-Station Forecasting**: Predicts exact portion volumes across 4 campus stations (*Breakfast Rush*, *Midday Lunch Line*, *Evening Snacks*, *Hostel Dinner*).
- **Machine Learning Pipeline**: Trained `RandomForestRegressor` incorporating calendar signals (day of week, month, holidays, weekends), weather features (temperature, conditions), campus attendance metrics, and lag features.
- **Dynamic Confidence Intervals**: Configurable statistical confidence intervals (80% - 99%) calculated using normal distribution critical z-scores and residual standard error.
- **Automated Food Waste Tracking**: Automatic computation of wasted quantities and waste percentages with top-wasted analytics.
- **Real-Time Analytics Command Center**: Dashboard aggregates, 7-day trend series, month-over-month summaries, and station/menu-item level performance.
- **Data-Driven AI Recommendations**: Heuristic and predictive advice based on recent demand variances, station peak loads, and waste alerts.
- **Bulk CSV Data Ingestion**: Robust historical data ingestion with schema validation.
- **Serverless & Multi-Platform Ready**: Seamless deployment across Windows, Linux, Docker, and Vercel Serverless (using `/tmp/servo_ai_data`).

---

## 🏗️ Project Architecture

```text
d:/Servo-AI/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application, lifespan & router registration
│   ├── config.py            # Centralized settings & path portability
│   ├── database.py          # SQLAlchemy SQLite engine & session management
│   ├── models.py            # Database schema models
│   ├── schemas.py           # Typed Pydantic request & response models
│   ├── crud.py              # Database query operations layer
│   ├── seed.py              # Realistic demo dataset seeder
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── train.py         # RandomForest training pipeline
│   │   ├── predict.py       # Demand inference engine & confidence bounds
│   │   └── model_manager.py # Model caching, loading & fallback manager
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py        # /api/health
│   │   ├── predictions.py   # /api/predictions/predict, /api/predictions/daily
│   │   ├── meals.py         # /api/meals, /api/meals/{station}, /api/meals/{station}/menu
│   │   ├── demand.py        # /api/demand, /api/demand/{date}, /api/demand/upload
│   │   ├── waste.py         # /api/waste, /api/waste/summary
│   │   ├── analytics.py     # /api/analytics/dashboard, /weekly, /monthly, etc.
│   │   ├── recommendations.py # /api/recommendations
│   │   ├── ml.py            # /api/ml/train, /api/ml/status
│   │   └── settings.py      # /api/settings
│   └── utils/
│       ├── __init__.py
│       └── helpers.py       # Z-score lookup, confidence intervals, CSV parser
├── api/
│   └── index.py             # Vercel serverless entrypoint
├── data/
│   ├── servo_ai.db          # SQLite database
│   └── models/              # Persisted joblib models
├── requirements.txt
├── vercel.json
└── run.py                   # Development server runner
```

---

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Clone and enter directory
cd Servo-AI

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file (or copy `.env.example`):
```env
PORT=8000
ENVIRONMENT=development
FRONTEND_URL=http://localhost:3000,http://localhost:5173
```

### 3. Seed Realistic Demo Data
```bash
python -m app.seed
```

### 4. Train the ML Model
You can train the model via the CLI or via the `/api/ml/train` API endpoint.
```bash
python -c "from app.database import SessionLocal; from app.ml.model_manager import model_manager; db = SessionLocal(); print(model_manager.retrain(db)); db.close()"
```

### 5. Launch the Server
```bash
python run.py
```
The API server will start at `http://127.0.0.1:8000`. Interactive documentation is available at:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

---

## 📡 REST API Reference

| Tag | Method | Endpoint | Description |
|---|---|---|---|
| **Health** | `GET` | `/api/health` | System health check (DB & ML model status) |
| **Predictions** | `POST` | `/api/predictions/predict` | Predict demand for specific item with confidence bounds |
| | `GET` | `/api/predictions/daily` | Full 4-station daily meal forecast |
| | `POST` | `/api/predictions/batch-csv` | Ingest input CSV and return batch predictions & pantry matrix |
| | `POST` | `/api/predictions/batch-csv/download` | Ingest CSV and stream back enriched output CSV file |
| | `GET` | `/api/predictions/sample-csv` | Download pre-formatted sample input CSV template |
| **Meals** | `GET` | `/api/meals` | List all 4 meal stations & schedules |
| | `GET` | `/api/meals/{station}` | Details for a specific station |
| | `GET` | `/api/meals/{station}/menu` | Menu catalog for a station |
| **Demand** | `POST` | `/api/demand` | Record single demand entry |
| | `GET` | `/api/demand` | List historical demand records (paginated) |
| | `GET` | `/api/demand/{date}` | Get demand records for a specific date |
| | `POST` | `/api/demand/upload` | Upload demand CSV file |
| **Waste** | `POST` | `/api/waste` | Log food waste (auto-calculates wasted qty & %) |
| | `GET` | `/api/waste` | List waste records |
| | `GET` | `/api/waste/summary` | Aggregate waste totals & top 5 wasted items |
| **Analytics** | `GET` | `/api/analytics/dashboard` | Aggregated command center KPIs |
| | `GET` | `/api/analytics/weekly` | 7-day trend series |
| | `GET` | `/api/analytics/monthly` | Month-over-month breakdown |
| | `GET` | `/api/analytics/stations` | Per-station load and waste analytics |
| | `GET` | `/api/analytics/menu-items` | Per-dish demand, waste, and ratings |
| **Recommendations** | `GET` | `/api/recommendations` | AI-generated operational recommendations |
| **Machine Learning** | `POST` | `/api/ml/train` | Retrain RandomForest on historical demand |
| | `GET` | `/api/ml/status` | Model status, metrics (MAE, RMSE, R²), features |
| **Settings** | `GET` | `/api/settings` | Canteen settings & station configurations |

---

## 📊 Batch CSV Demand Forecaster & Kitchen Procurement CLI

Servo-AI provides a dedicated batch pipeline that ingests any input CSV containing dates, weather, and campus events, and outputs full quantile meal forecasts, station breakdowns (Breakfast, Lunch, Snacks, Dinner), and grocery pantry requisitions:

```bash
# 1. Run batch forecasting on an input CSV and export to output CSV
python batch_predict_csv.py -i data/sample_canteen_forecast_input.csv -o data/predicted_canteen_forecast_output.csv -b 5.0

# 2. Generate a fresh 14-day sample input CSV template
python batch_predict_csv.py --generate-template my_template.csv
```

### Supported CSV Input Columns
- `date` (YYYY-MM-DD)
- `temperature_c` (e.g. 28.5)
- `rainfall_mm` (e.g. 15.0)
- `humidity_pct` (e.g. 65)
- `is_holiday` (1/0, true/false)
- `is_exam` (1/0, true/false)
- `is_special` (1/0, true/false)
- `rolling_avg_7d` (e.g. 410)

### Enriched CSV Output Columns
- All original input columns +
- `PREDICTED_MEALS` (Total forecasted meal covers)
- `CONFIDENCE_LOWER_95` & `CONFIDENCE_UPPER_95` (95% CI bounds)
- `DEMAND_TREND` (SURGING, STEADY, COOLING)
- `BREAKFAST_MEALS`, `LUNCH_MEALS`, `SNACKS_MEALS`, `DINNER_MEALS`
- `RICE_REQUISITION`, `DAL_REQUISITION`, `VEGETABLES_REQUISITION`, `DAIRY_MILK_REQUISITION`
- `ESTIMATED_GROCERY_COST` (Total ₹ cost with safety buffer)
- `EXPLAINABILITY_REASON` (Dominant operational/causal factor)


---

## 🧪 Testing

Run comprehensive automated API tests:
```bash
python -m pytest
```

---

## 🌐 Vercel Deployment

Servo-AI is configured for Vercel Serverless out-of-the-box using `@vercel/python`.
- `vercel.json` routes all requests to `api/index.py`.
- Ephemeral writable storage (`/tmp/servo_ai_data`) is automatically used in serverless environments.
- Read-only pre-trained models bundled in `data/models/` are used as fallback.
