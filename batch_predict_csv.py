"""
Servo AI — Batch CSV Forecaster & Kitchen Procurement CLI
Accepts input CSV files containing dates, weather, and campus event conditions,
executes the GBDT Quantile ML model, and outputs predictions, confidence intervals,
station breakdowns, and grocery requisitions to a structured output CSV file.
"""
import argparse
import sys
from pathlib import Path

# Ensure console supports UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.database import init_db
from app.services.csv_service import csv_batch_forecaster, generate_sample_csv_content


def print_banner():
    print("=" * 80)
    print("  SERVO AI: BATCH CSV DEMAND FORECASTER & KITCHEN REQUISITION ENGINE")
    print("  Model: HistGradientBoostingRegressor (95% Quantile Bounds) | 'Steam & Ledger'")
    print("=" * 80)


def format_table_row(date_str, day_name, meals, bounds, b, l, s, d, reason):
    return f"  {date_str:<10} | {day_name:<9} | {meals:>5} meals | {bounds:<12} | B:{b:<3} L:{l:<3} S:{s:<3} D:{d:<3} | {reason[:26]}"


def run_batch_prediction(input_path: Path, output_path: Path, buffer_pct: float = 5.0):
    init_db()

    if not input_path.exists():
        print(f"\n[!] Input file not found: {input_path}")
        print(f"[*] Generating realistic sample input file at: {input_path} ...")
        input_path.parent.mkdir(parents=True, exist_ok=True)
        with open(input_path, "w", encoding="utf-8") as f:
            f.write(generate_sample_csv_content())
        print(f"[+] Created sample input CSV with 14 days of campus conditions.")

    print(f"\n[*] Ingesting CSV file: {input_path}")
    print(f"[*] Running Machine Learning Forecasting Pipeline (Safety Buffer: {buffer_pct}%)...")

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            csv_content = f.read()

        results = csv_batch_forecaster.process_csv(
            csv_source=csv_content,
            safety_buffer_pct=buffer_pct
        )

        output_df = results["output_dataframe"]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_df.to_csv(output_path, index=False)

        summary = results["summary"]
        predictions = results["predictions"]

        print_banner()
        print(f"\n  Summary of Forecast Results:")
        print(f"  * Processed Days            : {summary['total_rows_processed']} days")
        print(f"  * Total Projected Meals     : {summary['total_predicted_meals']:,} covers")
        print(f"  * Daily Average Load        : {summary['average_daily_meals']} covers/day")
        print(f"  * Estimated Ingredient Cost : INR {summary['total_estimated_procurement_cost']:,.2f}")
        print(f"  * Safety Buffer Applied     : +{summary['safety_buffer_pct']}%")
        print("\n" + "-" * 80)
        print(f"  {'DATE':<10} | {'DAY':<9} | {'PREDICTED':<11} | {'95% BOUNDS':<12} | {'STATION COVERS':<19} | {'PRIMARY REASON'}")
        print("-" * 80)

        for p in predictions:
            bounds_str = f"[{p['lower_bound_95ci']} - {p['upper_bound_95ci']}]"
            print(format_table_row(
                p["date"],
                p["day_name"][:9],
                p["predicted_meals"],
                bounds_str,
                p["breakfast_covers"],
                p["lunch_covers"],
                p["snacks_covers"],
                p["dinner_covers"],
                p["primary_reason"]
            ))

        print("-" * 80)
        print(f"\n[+] SUCCESS: Full enriched predictions and ingredient matrix saved to:")
        print(f"    -> {output_path.resolve()}\n")

    except Exception as err:
        print(f"\n[ERROR] Failed to process CSV: {err}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Servo AI: Batch CSV Demand Forecaster & Kitchen Procurement Engine"
    )
    parser.add_argument(
        "-i", "--input",
        type=str,
        default="data/sample_canteen_forecast_input.csv",
        help="Path to input CSV file containing dates, weather, and calendar flags (default: data/sample_canteen_forecast_input.csv)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="data/predicted_canteen_forecast_output.csv",
        help="Path to output destination CSV file (default: data/predicted_canteen_forecast_output.csv)"
    )
    parser.add_argument(
        "-b", "--buffer",
        type=float,
        default=5.0,
        help="Safety buffer percentage for ingredient procurement (default: 5.0%%)"
    )
    parser.add_argument(
        "--generate-template",
        type=str,
        metavar="PATH",
        help="Generate a blank/sample input CSV template and exit"
    )

    args = parser.parse_args()

    if args.generate_template:
        template_path = Path(args.generate_template)
        template_path.parent.mkdir(parents=True, exist_ok=True)
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(generate_sample_csv_content())
        print(f"[+] Sample CSV template generated at: {template_path.resolve()}")
        return

    run_batch_prediction(
        input_path=Path(args.input),
        output_path=Path(args.output),
        buffer_pct=args.buffer
    )


if __name__ == "__main__":
    main()
