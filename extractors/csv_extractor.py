import csv
import os
from datetime import datetime

from .base import BaseExtractor

# Debt.csv column name -> data model field name
# Values in Debt.csv are stored as negatives; we return absolute values.
DEBT_COLUMN_MAP = {
    "2108 N 3rd": "debt_mortgage",
    "Student Loan": "debt_student_loan",
    "2025 Tesla MYLR": "debt_car_tesla",
    "2018 Honda Accord": "debt_car_2018_accord",
    "2010 Honda Accord": "debt_car_2010_accord",
    "2007 Honda Civic": "debt_car_2007_civic",
}


def _normalize_date(raw: str) -> str | None:
    """Return YYYY-MM-01 from a variety of date string formats, or None on failure."""
    raw = raw.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%B %Y", "%b %Y", "%Y-%m"):
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.strftime("%Y-%m-01")
        except ValueError:
            continue
    return None


class CsvExtractor(BaseExtractor):
    def __init__(self, config: dict):
        input_dir = config["paths"]["input_dir"]
        self.zillow_path = os.path.join(input_dir, config["csv_files"]["zillow"])
        self.debt_path = os.path.join(input_dir, config["csv_files"]["debt"])

    def extract(self) -> list[dict]:
        records = []
        records.extend(self._extract_zillow())
        records.extend(self._extract_debt())
        return records

    def _extract_zillow(self) -> list[dict]:
        records = []
        if not os.path.exists(self.zillow_path):
            print(f"[csv_extractor] Warning: Zillow CSV not found at {self.zillow_path}")
            return records

        with open(self.zillow_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Strip whitespace from keys (CSV headers often have extra spaces)
                row = {k.strip(): v for k, v in row.items()}

                date = _normalize_date(row.get("Date", ""))
                if not date:
                    continue

                # Prefer "Estimated Home Value" (full numeric) over "Zestimate" (may be abbreviated e.g. $491.5K)
                raw_value = row.get("Estimated Home Value") or row.get("Zestimate") or ""
                raw_value = raw_value.strip().replace("$", "").replace(",", "")
                if not raw_value:
                    continue

                # Handle K/M suffix (e.g. "491.5K" -> 491500)
                multiplier = 1
                if raw_value.upper().endswith("K"):
                    raw_value, multiplier = raw_value[:-1], 1_000
                elif raw_value.upper().endswith("M"):
                    raw_value, multiplier = raw_value[:-1], 1_000_000

                try:
                    value = float(raw_value) * multiplier
                except ValueError:
                    continue

                records.append({"date": date, "field": "home_value", "value": value})

        return records

    def _extract_debt(self) -> list[dict]:
        records = []
        if not os.path.exists(self.debt_path):
            print(f"[csv_extractor] Warning: Debt CSV not found at {self.debt_path}")
            return records

        with open(self.debt_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                date = _normalize_date(row.get("Date", ""))
                if not date:
                    continue

                for csv_col, field in DEBT_COLUMN_MAP.items():
                    raw_value = row.get(csv_col, "").strip().replace("$", "").replace(",", "")
                    if not raw_value:
                        continue
                    try:
                        value = float(raw_value)
                    except ValueError:
                        continue

                    # Debt.csv stores liabilities as negatives; model uses positives
                    records.append({"date": date, "field": field, "value": abs(value)})

        return records
