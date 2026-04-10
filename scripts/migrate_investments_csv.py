#!/usr/bin/env python3
"""
One-time migration for Investments_and_Cash.csv:
  1. Insert an Account_ID row (after row index 1 / Bank_Account_Type row)
  2. Append 18 new account columns (all data cells empty)

The file uses a transposed multi-row header format:
  Row 0: Bank, <col values...>
  Row 1: Bank_Account_Type, <col values...>
  Row 2: Status, <col values...>
  Row 3: Owner, <col values...>
  Row 4+: date/data rows

After migration:
  Row 0: Bank
  Row 1: Bank_Account_Type
  Row 2: Account_ID  <- NEW
  Row 3: Status
  Row 4: Owner
  Row 5+: data rows
"""
import csv
import os

PATH = r"z:\Projects\data\assets\Investments_and_Cash.csv"

# Account IDs for the 11 EXISTING columns (in column order as they appear in the CSV)
EXISTING_IDS = [
    "CASH-001",  # Wealthfront — Joint Cash Account
    "INV-001",   # Fidelity — Joint FIRE
    "INV-002",   # Primearica — UTMA/PA
    "INV-003",   # Morgan Stanley — Access Direct Stock Plan
    "INV-007",   # Robinhood — Roth IRA (Chris)
    "INV-008",   # Robinhood — Traditional IRA (Chris)
    "INV-009",   # Alight — GSK 401(k) Plan
    "INV-005",   # Fidelity — Merck US Salaried Pension Plan
    "INV-012",   # Fidelity — 403b (Kim)
    "INV-014",   # Robinhood — Roth IRA (Kim)
    "INV-015",   # Fidelity — UNIQUE College Investing Plan (Jonah)
]

# 18 new accounts to append: (Bank, Account_Type, Account_ID, Status, Owner)
NEW_ACCOUNTS = [
    ("Wealthfront", "Individual Cash Account",          "CASH-002", "Open",          "Chris"),
    ("Wealthfront", "Individual Cash Account",          "CASH-003", "Open",          "Kim"),
    ("SoFi",        "Checking",                         "CASH-004", "Open",          "Chris"),
    ("SoFi",        "Savings",                          "CASH-005", "Open",          "Chris"),
    ("SoFi",        "Checking",                         "CASH-006", "Open",          "Kim"),
    ("SoFi",        "Savings",                          "CASH-007", "Open",          "Kim"),
    ("Ally",        "Spending Account",                 "CASH-008", "Open",          "Chris"),
    ("Ally",        "Ally Savings",                     "CASH-009", "Open",          "Joint"),
    ("Fidelity",    "Individual - TOD",                 "INV-004",  "Open",          "Chris"),
    ("Robinhood",   "Individual",                       "INV-006",  "Open",          "Chris"),
    ("Fidelity",    "Individual - TOD",                 "INV-010",  "Open",          "Kim"),
    ("Fidelity",    "Roth IRA",                         "INV-011",  "Open",          "Kim"),
    ("Robinhood",   "Individual",                       "INV-013",  "Open",          "Kim"),
    ("Fidelity",    "UNIQUE College Investing Plan",    "INV-016",  "To be opened",  "Chris"),
    ("Venmo",       "Custodial Wallet BTC",             "CRYPT-001","Open",          "Chris"),
    ("Venmo",       "Custodial Wallet ETH",             "CRYPT-002","Open",          "Chris"),
    ("Ledger",      "Nano S Plus BTC",                  "CRYPT-003","Open",          "Chris"),
    ("Ledger",      "Nano S Plus ETH",                  "CRYPT-004","Open",          "Chris"),
]

with open(PATH, newline="", encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    rows = list(reader)

# Validate: first column of rows 0..3 should be Bank, Bank_Account_Type, Status, Owner
expected_labels = ["Bank", "Bank_Account_Type", "Status", "Owner"]
actual_labels = [rows[i][0] for i in range(4)]
if actual_labels != expected_labels:
    raise ValueError(
        f"Unexpected header row labels. Expected {expected_labels}, got {actual_labels}. "
        "Has migration already been run?"
    )

n_new = len(NEW_ACCOUNTS)

# Step 1: Extend existing header rows with new account values
rows[0] += [acc[0] for acc in NEW_ACCOUNTS]  # Bank
rows[1] += [acc[1] for acc in NEW_ACCOUNTS]  # Bank_Account_Type
rows[2] += [acc[3] for acc in NEW_ACCOUNTS]  # Status
rows[3] += [acc[4] for acc in NEW_ACCOUNTS]  # Owner

# Step 2: Build and insert Account_ID row after Bank_Account_Type (index 1)
id_row = ["Account_ID"] + EXISTING_IDS + [acc[2] for acc in NEW_ACCOUNTS]
rows.insert(2, id_row)
# After insert: 0=Bank, 1=Bank_Account_Type, 2=Account_ID, 3=Status, 4=Owner

# Step 3: Extend all data rows with empty cells for new columns
for i in range(5, len(rows)):
    rows[i] += [""] * n_new

# Write back
with open(PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print(f"Done. Updated {PATH}")
print(f"  Account_ID row inserted: {len(EXISTING_IDS)} existing + {n_new} new IDs")
print(f"  New columns appended: {n_new}")
print(f"  Data rows extended: {len(rows) - 5}")
