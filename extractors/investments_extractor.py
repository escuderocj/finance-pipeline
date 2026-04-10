"""Extractor for Investments_and_Cash.csv.

CSV format (5 transposed header rows, then data rows):
  Row 0: Bank names            — first cell: "Bank"
  Row 1: Account type          — first cell: "Bank_Account_Type"
  Row 2: Account IDs           — first cell: "Account_ID"
  Row 3: Account status        — first cell: "Status"
  Row 4: Owners                — first cell: "Owner"
  Rows 5+: date, value per column

Produces two aggregated fields per quarter (forward-filled monthly by pipeline):
  cash_total        — sum of all Open CASH-* account balances
  investments_total — sum of all Open INV-* account balances

CRYPT-* accounts are excluded here; crypto is a separate future extractor.

Staleness check: warns if the most recent entry is older than STALENESS_DAYS.
Deduplication: if two rows share the same normalized date, the later row wins.
"""

import csv
import os
from datetime import date, datetime

from .base import BaseExtractor

# Quarterly data — warn if newest entry is older than this many days
STALENESS_DAYS = 120


def _normalize_date(raw: str) -> str | None:
    """Return YYYY-MM-01 from common date formats, or None on failure."""
    raw = raw.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%B %Y", "%b %Y", "%Y-%m"):
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.strftime("%Y-%m-01")
        except ValueError:
            continue
    return None


class InvestmentsExtractor(BaseExtractor):
    def __init__(self, config: dict):
        input_dir = config["paths"]["input_dir"]
        filename = config["csv_files"].get(
            "investments_and_cash", "Investments_and_Cash.csv"
        )
        self.path = os.path.join(input_dir, filename)

    def extract(self) -> list[dict]:
        if not os.path.exists(self.path):
            print(
                f"[investments_extractor] Warning: CSV not found at {self.path}"
            )
            return []

        with open(self.path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))

        if len(rows) < 6:
            print(
                "[investments_extractor] Warning: CSV has fewer than 6 rows; skipping."
            )
            return []

        # Validate header structure
        expected_labels = [
            "Bank", "Bank_Account_Type", "Account_ID", "Status", "Owner"
        ]
        actual = [rows[i][0] if rows[i] else "" for i in range(5)]
        if actual != expected_labels:
            print(
                f"[investments_extractor] Warning: unexpected header rows "
                f"(expected {expected_labels}, got {actual}). Skipping."
            )
            return []

        account_ids = rows[2][1:]  # skip first-cell label
        statuses = rows[3][1:]     # skip first-cell label

        # Identify which column indices belong to cash vs. investments (Open only)
        cash_cols: list[int] = []
        inv_cols: list[int] = []
        for i, (acct_id, status) in enumerate(zip(account_ids, statuses)):
            if status.strip() != "Open":
                continue
            prefix = acct_id.strip().split("-")[0]
            if prefix == "CASH":
                cash_cols.append(i)
            elif prefix == "INV":
                inv_cols.append(i)
            # CRYPT-* skipped intentionally

        # Parse data rows (rows 5+)
        # Use dicts so later rows overwrite earlier ones on the same normalized date.
        date_cash: dict[str, float] = {}
        date_inv: dict[str, float] = {}

        for row in rows[5:]:
            if not row or not row[0].strip():
                continue
            norm_date = _normalize_date(row[0].strip())
            if not norm_date:
                continue

            values = row[1:]

            def _sum_cols(col_indices: list[int]) -> float:
                total = 0.0
                for i in col_indices:
                    if i >= len(values):
                        continue
                    v = values[i].strip().replace("$", "").replace(",", "")
                    if v:
                        try:
                            total += float(v)
                        except ValueError:
                            pass
                return total

            date_cash[norm_date] = _sum_cols(cash_cols)
            date_inv[norm_date] = _sum_cols(inv_cols)

        if not date_cash and not date_inv:
            print("[investments_extractor] Warning: no data rows parsed.")
            return []

        # Staleness check
        all_dates = sorted(set(date_cash) | set(date_inv))
        most_recent = all_dates[-1]
        try:
            delta = (
                date.today()
                - datetime.strptime(most_recent, "%Y-%m-%d").date()
            ).days
            if delta > STALENESS_DAYS:
                print(
                    f"[investments_extractor] WARNING: most recent entry is "
                    f"{most_recent} ({delta} days ago). "
                    f"Update Investments_and_Cash.csv if balances have changed."
                )
        except ValueError:
            pass

        records: list[dict] = []
        for d, v in date_cash.items():
            records.append({"date": d, "field": "cash_total", "value": v})
        for d, v in date_inv.items():
            records.append({"date": d, "field": "investments_total", "value": v})

        print(
            f"[investments_extractor] {len(date_cash)} cash records, "
            f"{len(date_inv)} investment records (most recent: {most_recent})"
        )
        return records
