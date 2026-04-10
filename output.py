"""
Write pipeline output: assets.csv, assets.json, summary.json, dashboard.html.
All files go to config["paths"]["output_dir"].
"""

import csv
import json
import os
from datetime import datetime

from pipeline import ALL_COLUMNS


def write_all(rows: list[dict], config: dict) -> None:
    out_dir = config["paths"]["output_dir"]
    os.makedirs(out_dir, exist_ok=True)

    _write_csv(rows, out_dir)
    _write_json(rows, out_dir)
    _write_summary(rows, out_dir)
    _write_dashboard(rows, out_dir)

    print(f"[output] Wrote 4 files to {out_dir}")


# ------------------------------------------------------------------
# Individual writers
# ------------------------------------------------------------------

def _write_csv(rows: list[dict], out_dir: str) -> None:
    path = os.path.join(out_dir, "assets.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ALL_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: ("" if v is None else v) for k, v in row.items()})
    print(f"[output] Wrote {path}")


def _write_json(rows: list[dict], out_dir: str) -> None:
    path = os.path.join(out_dir, "assets.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, default=_json_default)
    print(f"[output] Wrote {path}")


def _write_summary(rows: list[dict], out_dir: str) -> None:
    if not rows:
        return

    latest = rows[-1]

    asset_cols = [
        "home_value", "car_tesla_model_y", "car_2018_honda_accord",
        "car_2010_honda_accord", "car_2007_honda_civic",
    ]
    liability_cols = [
        "debt_mortgage", "debt_student_loan", "debt_car_tesla",
        "debt_car_2018_accord", "debt_car_2010_accord", "debt_car_2007_civic",
    ]
    equity_cols = ["home_equity", "equity_tesla", "equity_2018_accord"]

    summary = {
        "as_of": latest["date"],
        "net_worth": latest.get("net_worth"),
        "total_assets": latest.get("total_assets"),
        "total_liabilities": latest.get("total_liabilities"),
        "assets": {c: latest.get(c) for c in asset_cols},
        "liabilities": {c: latest.get(c) for c in liability_cols},
        "equity": {c: latest.get(c) for c in equity_cols},
        "last_run": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }

    path = os.path.join(out_dir, "summary.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=_json_default)
    print(f"[output] Wrote {path}")


def _write_dashboard(rows: list[dict], out_dir: str) -> None:
    template_path = os.path.join(os.path.dirname(__file__), "dashboard_template.html")
    with open(template_path, encoding="utf-8") as f:
        template = f.read()

    data_json = json.dumps(rows, default=_json_default)
    html = template.replace("/*PIPELINE_DATA_PLACEHOLDER*/", data_json)

    path = os.path.join(out_dir, "dashboard.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[output] Wrote {path}")


def _json_default(obj):
    # Fallback serializer — shouldn't be needed but guards against surprises
    return str(obj)
