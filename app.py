"""
Servo AI - Application Startup Launcher (alias for run.py)
"""
import sys
import uvicorn

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    print("Launching Servo AI - Steam & Ledger Campus Dining Forecaster...")
    print("URL: http://127.0.0.1:8000")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
