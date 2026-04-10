#!/usr/bin/env python3
"""
One-time migration: prepend Account_ID as first column to Accounts.csv.
Run once from the project root: python scripts/migrate_accounts_csv.py
"""
import csv
import os

PATH = r"z:\Projects\data\assets\Accounts.csv"

# IDs assigned in the exact row order of the current Accounts.csv.
# Verify row count matches before writing.
ACCOUNT_IDS = [
    "CASH-001",  # Wealthfront — Joint Cash Account
    "CASH-002",  # Wealthfront — Individual Cash Account (Chris)
    "CASH-003",  # Wealthfront — Individual Cash Account (Kim)
    "CASH-004",  # SoFi — Checking (Chris)
    "CASH-005",  # SoFi — Savings (Chris)
    "CASH-006",  # SoFi — Checking (Kim)
    "CASH-007",  # SoFi — Savings (Kim)
    "CASH-008",  # Ally — Spending Account
    "CASH-009",  # Ally — Ally Savings
    "INV-001",   # Fidelity — Joint FIRE
    "INV-002",   # Primearica — UTMA/PA
    "INV-003",   # Morgan Stanley — Access Direct Stock Plan
    "INV-004",   # Fidelity — Individual - TOD (Chris)
    "INV-005",   # Fidelity — Merck US Salaried Pension Plan
    "INV-006",   # Robinhood — Individual (Chris)
    "INV-007",   # Robinhood — Roth IRA (Chris)
    "INV-008",   # Robinhood — Traditional IRA (Chris)
    "INV-009",   # Alight — GSK 401(k) Plan
    "INV-010",   # Fidelity — Individual - TOD (Kim)
    "INV-011",   # Fidelity — Roth IRA (Kim)
    "INV-012",   # Fidelity — 403b (Kim)
    "INV-013",   # Robinhood — Individual (Kim)
    "INV-014",   # Robinhood — Roth IRA (Kim)
    "INV-015",   # Fidelity — UNIQUE College Investing Plan (Jonah)
    "INV-016",   # Fidelity — UNIQUE College Investing Plan (Nico)
    "AUTO-001",  # CarFax — 2025 Tesla Model Y
    "AUTO-002",  # CarFax — 2018 Honda Accord
    "AUTO-003",  # CarFax — 2010 Honda Accord
    "AUTO-004",  # CarFax — 2007 Honda Civic
    "CRYPT-001", # Venmo — Custodial Wallet BTC
    "CRYPT-002", # Venmo — Custodial Wallet ETH
    "CRYPT-003", # Ledger — Nano S Plus BTC
    "CRYPT-004", # Ledger — Nano S Plus ETH
    "MORT-001",  # Nation One — Mortgage (Closed)
    "MORT-002",  # Suntrust Bank — Mortgage (Closed)
    "MORT-003",  # Truist Bank — Mortgage (Active)
    "LOAN-001",  # SoFi — Student Loan Refi
    "LOAN-002",  # Ally — 2025 Tesla MYLR Auto Loan
    "LOAN-003",  # Bank of America — 2018 Honda Accord Auto Loan
    "LOAN-004",  # American Honda Finance Corp — 2010 Honda Accord Auto Loan
    "LOAN-005",  # American Honda Finance Corp — 2007 Honda Civic Auto Loan
]

with open(PATH, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    fieldnames = list(reader.fieldnames)
    rows = list(reader)

if len(rows) != len(ACCOUNT_IDS):
    raise ValueError(
        f"Row count mismatch: CSV has {len(rows)} data rows, "
        f"ACCOUNT_IDS list has {len(ACCOUNT_IDS)} entries. "
        "Update ACCOUNT_IDS to match the current file."
    )

new_fieldnames = ["Account_ID"] + fieldnames
for i, row in enumerate(rows):
    row["Account_ID"] = ACCOUNT_IDS[i]

with open(PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=new_fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Done. Added Account_ID column to {PATH} ({len(rows)} rows updated).")
