"""
Merge extractor records onto a unified monthly timeline, forward-fill gaps,
and compute derived columns (totals, net worth, equity).
"""

from datetime import date

# Ordered list of all data model columns (excluding date and computed columns)
ASSET_COLUMNS = [
    "home_value",
    "car_tesla_model_y",
    "car_2018_honda_accord",
    "car_2010_honda_accord",
    "car_2007_honda_civic",
    "investments_total",
    "cash_total",
]

LIABILITY_COLUMNS = [
    "debt_mortgage",
    "debt_student_loan",
    "debt_car_tesla",
    "debt_car_2018_accord",
    "debt_car_2010_accord",
    "debt_car_2007_civic",
]

SOURCE_COLUMNS = ASSET_COLUMNS + LIABILITY_COLUMNS

COMPUTED_COLUMNS = [
    "total_assets",
    "total_liabilities",
    "net_worth",
    "home_equity",
    "equity_tesla",
    "equity_2018_accord",
]

ALL_COLUMNS = ["date"] + SOURCE_COLUMNS + COMPUTED_COLUMNS


def run(all_records: list[dict], disposals: dict[str, str] | None = None) -> list[dict]:
    """
    all_records: flat list of {"date": "YYYY-MM-01", "field": str, "value": float}
                 from all extractors combined.
    disposals:   optional dict of {field: "YYYY-MM-01"} marking when an asset was
                 sold/disposed. From that month onward the field is set to 0 rather
                 than forward-filled.

    Returns a list of row dicts with ALL_COLUMNS keys, one per month.
    """
    if not all_records:
        return []

    # Normalize disposal dates to "YYYY-MM-DD" strings (YAML may parse them as date objects)
    disposals = {k: str(v) for k, v in (disposals or {}).items()}

    # Build a sparse dict: {date_str: {field: value}}
    # Later records (Paperless) override earlier (CSV) for same date+field because
    # extractors are registered in that order in main.py.
    data_by_date: dict[str, dict[str, float]] = {}
    for rec in all_records:
        d = rec["date"]
        if d not in data_by_date:
            data_by_date[d] = {}
        data_by_date[d][rec["field"]] = rec["value"]

    # Determine full month range
    today = date.today()
    all_dates = sorted(data_by_date.keys())
    start = _parse_month(all_dates[0])
    end = date(today.year, today.month, 1)

    timeline = _month_range(start, end)

    # Forward-fill each source column across the timeline
    last: dict[str, float | None] = {col: None for col in SOURCE_COLUMNS}
    rows = []

    for month_str in timeline:
        if month_str in data_by_date:
            for col in SOURCE_COLUMNS:
                if col in data_by_date[month_str]:
                    last[col] = data_by_date[month_str][col]

        row: dict = {"date": month_str}
        for col in SOURCE_COLUMNS:
            # Zero out disposed assets from their disposal date onward
            if col in disposals and month_str >= disposals[col]:
                row[col] = 0.0
            else:
                row[col] = last[col]

        _compute_derived(row)
        rows.append(row)

    return rows


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _parse_month(date_str: str) -> date:
    """Parse 'YYYY-MM-01' into a date object."""
    parts = date_str.split("-")
    return date(int(parts[0]), int(parts[1]), 1)


def _month_range(start: date, end: date) -> list[str]:
    """Generate sorted list of 'YYYY-MM-01' strings from start to end inclusive."""
    months = []
    current = start
    while current <= end:
        months.append(current.strftime("%Y-%m-%d"))
        # Advance one month
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return months


def _safe_sum(*values) -> float | None:
    valid = [v for v in values if v is not None]
    return sum(valid) if valid else None


def _safe_sub(a, b) -> float | None:
    if a is not None and b is not None:
        return a - b
    return None


def _compute_derived(row: dict) -> None:
    row["total_assets"] = _safe_sum(*(row.get(c) for c in ASSET_COLUMNS))
    row["total_liabilities"] = _safe_sum(*(row.get(c) for c in LIABILITY_COLUMNS))
    row["net_worth"] = _safe_sub(row.get("total_assets"), row.get("total_liabilities"))
    row["home_equity"] = _safe_sub(row.get("home_value"), row.get("debt_mortgage"))
    row["equity_tesla"] = _safe_sub(row.get("car_tesla_model_y"), row.get("debt_car_tesla"))
    row["equity_2018_accord"] = _safe_sub(
        row.get("car_2018_honda_accord"), row.get("debt_car_2018_accord")
    )
