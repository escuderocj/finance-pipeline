# Continuous Improvements v1 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply coordinated improvements to the Finance Pipeline: fix Honda Civic year (2007), add type-prefixed Account IDs to all CSVs, expand Investments_and_Cash.csv with 18 missing accounts, enhance the dashboard with month selector / asset pie chart / regrouped comparison / to-do list, remove FIRE references from dashboard scope, and produce Lessons Learned + Changelog docs.

**Architecture:** Changes flow in dependency order — Python code first (testable in isolation), then source CSV data files, then dashboard template (all HTML/JS), then documentation. CSV data files are modified via one-time migration scripts in `scripts/` to avoid manual error. All dashboard changes are confined to `dashboard_template.html`.

**Tech Stack:** Python 3.12, Chart.js 4 (CDN), vanilla JS, CSV, YAML

---

## File Map

| Action | File | Responsibility |
|---|---|---|
| Create | `tests/__init__.py` | Test package marker |
| Create | `tests/test_civic_rename.py` | Unit tests for 2007 field name correctness |
| Modify | `extractors/csv_extractor.py` | Fix DEBT_COLUMN_MAP key + field name |
| Modify | `pipeline.py` | Rename car_2008 / debt_2008 fields to 2007 |
| Modify | `output.py` | Rename same two field names in summary writer |
| Modify | `config.example.yaml` | Fix vehicle_map key |
| Modify | `dashboard_template.html` | All dashboard enhancements + 2007 label fix |
| Modify | `docs/superpowers/specs/2026-04-10-finance-pipeline-design.md` | Correct field names, add FIRE note |
| Create | `scripts/migrate_accounts_csv.py` | One-time: add Account_ID column to Accounts.csv |
| Create | `scripts/migrate_investments_csv.py` | One-time: add Account_ID row + 18 columns to Investments_and_Cash.csv |
| Modify | `z:/Projects/data/assets/Debt.csv` | Insert Account_ID row (line 2) |
| Create | `docs/LESSONS_LEARNED.md` | Lessons from this release |
| Create | `docs/CHANGELOG.md` | Structured changelog |

---

## Task 1: Create tests + fix Honda Civic 2007 in Python code

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_civic_rename.py`
- Modify: `extractors/csv_extractor.py` (line 15)
- Modify: `pipeline.py` (lines 14, 23)
- Modify: `output.py` (lines 54, 58)

- [ ] **Step 1: Create test package**

Create `tests/__init__.py` as an empty file.

- [ ] **Step 2: Write the failing tests**

Create `tests/test_civic_rename.py`:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from extractors.csv_extractor import DEBT_COLUMN_MAP
import pipeline


def test_debt_column_map_key_is_2007():
    assert "2007 Honda Civic" in DEBT_COLUMN_MAP, \
        "DEBT_COLUMN_MAP must have '2007 Honda Civic' key"
    assert "2008 Honda Civic" not in DEBT_COLUMN_MAP, \
        "DEBT_COLUMN_MAP must not have stale '2008 Honda Civic' key"


def test_debt_field_name_is_2007():
    assert DEBT_COLUMN_MAP.get("2007 Honda Civic") == "debt_car_2007_civic"


def test_pipeline_asset_columns_2007():
    assert "car_2007_honda_civic" in pipeline.ASSET_COLUMNS
    assert "car_2008_honda_civic" not in pipeline.ASSET_COLUMNS


def test_pipeline_liability_columns_2007():
    assert "debt_car_2007_civic" in pipeline.LIABILITY_COLUMNS
    assert "debt_car_2008_civic" not in pipeline.LIABILITY_COLUMNS
```

- [ ] **Step 3: Run tests — expect FAIL**

```
cd "z:/Projects/dev/Assets Tracker"
python -m pytest tests/test_civic_rename.py -v
```

Expected: 4 failures (2008 references still present)

- [ ] **Step 4: Fix `extractors/csv_extractor.py` line 15**

Change:
```python
    "2008 Honda Civic": "debt_car_2008_civic",
```
To:
```python
    "2007 Honda Civic": "debt_car_2007_civic",
```

- [ ] **Step 5: Fix `pipeline.py` — ASSET_COLUMNS and LIABILITY_COLUMNS**

In `ASSET_COLUMNS` (line 14), change:
```python
    "car_2008_honda_civic",
```
To:
```python
    "car_2007_honda_civic",
```

In `LIABILITY_COLUMNS` (line 23), change:
```python
    "debt_car_2008_civic",
```
To:
```python
    "debt_car_2007_civic",
```

- [ ] **Step 6: Fix `output.py` — `_write_summary()` asset and liability lists**

In `_write_summary()`, the `asset_cols` list (line 54), change:
```python
        "car_2008_honda_civic",
```
To:
```python
        "car_2007_honda_civic",
```

In `liability_cols` list (line 58), change:
```python
        "debt_car_2008_civic",
```
To:
```python
        "debt_car_2007_civic",
```

- [ ] **Step 7: Run tests — expect PASS**

```
python -m pytest tests/test_civic_rename.py -v
```

Expected output:
```
tests/test_civic_rename.py::test_debt_column_map_key_is_2007 PASSED
tests/test_civic_rename.py::test_debt_field_name_is_2007 PASSED
tests/test_civic_rename.py::test_pipeline_asset_columns_2007 PASSED
tests/test_civic_rename.py::test_pipeline_liability_columns_2007 PASSED
4 passed
```

- [ ] **Step 8: Commit**

```bash
git add tests/__init__.py tests/test_civic_rename.py extractors/csv_extractor.py pipeline.py output.py
git commit -m "fix: rename Honda Civic field names from 2008 to 2007"
```

---

## Task 2: Fix Honda Civic 2007 in config and dashboard template

**Files:**
- Modify: `config.example.yaml` (line 15)
- Modify: `dashboard_template.html` (lines 269, 270, 402)

- [ ] **Step 1: Fix `config.example.yaml` vehicle_map**

Change:
```yaml
  "2008 HONDA CIVIC": "car_2008_honda_civic"
```
To:
```yaml
  "2007 HONDA CIVIC": "car_2007_honda_civic"
```

- [ ] **Step 2: Fix `dashboard_template.html` — COMPARE_ROWS entry (line 269-270)**

Change:
```javascript
  { label: "Honda Civic 2008",   key: "car_2008_honda_civic",  good: "up" },
```
To:
```javascript
  { label: "Honda Civic 2007",   key: "car_2007_honda_civic",  good: "up" },
```

- [ ] **Step 3: Fix `dashboard_template.html` — asset chart dataset (line 402)**

Change:
```javascript
      { label: "Civic 2008",   data: col(DATA, "car_2008_honda_civic"),  borderColor: "#facc15", backgroundColor: "rgba(250,204,21,0.15)",  fill: true, tension: 0.3, pointRadius: 0, borderWidth: 1.5, spanGaps: true },
```
To:
```javascript
      { label: "Civic 2007",   data: col(DATA, "car_2007_honda_civic"),  borderColor: "#facc15", backgroundColor: "rgba(250,204,21,0.15)",  fill: true, tension: 0.3, pointRadius: 0, borderWidth: 1.5, spanGaps: true },
```

- [ ] **Step 4: Commit**

```bash
git add config.example.yaml dashboard_template.html
git commit -m "fix: update 2008 Honda Civic labels to 2007 in config and dashboard"
```

---

## Task 3: Add Account_ID column to Accounts.csv

**Files:**
- Create: `scripts/migrate_accounts_csv.py`
- Modify: `z:/Projects/data/assets/Accounts.csv`

- [ ] **Step 1: Create the migration script**

Create `scripts/__init__.py` as an empty file.

Create `scripts/migrate_accounts_csv.py`:

```python
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
```

- [ ] **Step 2: Run the migration**

```
cd "z:/Projects/dev/Assets Tracker"
python scripts/migrate_accounts_csv.py
```

Expected:
```
Done. Added Account_ID column to z:\Projects\data\assets\Accounts.csv (41 rows updated).
```

- [ ] **Step 3: Verify — open Accounts.csv and confirm first column is Account_ID starting with CASH-001**

Check that:
- Row 1 header: `Account_ID,Bank,Bank_Account_Type,...`
- First data row: `CASH-001,Wealthfront,Joint Cash Account,...`
- Last data row: `LOAN-005,American Honda Finance Corp,...`

- [ ] **Step 4: Commit**

```bash
git add scripts/__init__.py scripts/migrate_accounts_csv.py "z:/Projects/data/assets/Accounts.csv"
git commit -m "feat: add type-prefixed Account_ID column to Accounts.csv"
```

---

## Task 4: Add Account_ID row to Debt.csv

**Files:**
- Modify: `z:/Projects/data/assets/Debt.csv`

The `csv_extractor.py` `_extract_debt()` reads by column header and normalizes the `Date` field. A row where `Date` = `"Account_ID"` will return `None` from `_normalize_date()` and be silently skipped — safe to insert.

- [ ] **Step 1: Insert Account_ID row as line 2 of Debt.csv**

The current line 1 is:
```
Date,2108 N 3rd,Student Loan,2025 Tesla MYLR,2018 Honda Accord,2007 Honda Civic,2010 Honda Accord
```

Insert this as line 2 (immediately after the header):
```
Account_ID,MORT-003,LOAN-001,LOAN-002,LOAN-003,LOAN-005,LOAN-004
```

Use the Edit tool, replacing:
```
Date,2108 N 3rd,Student Loan,2025 Tesla MYLR,2018 Honda Accord,2007 Honda Civic,2010 Honda Accord
3/31/2018,
```
With:
```
Date,2108 N 3rd,Student Loan,2025 Tesla MYLR,2018 Honda Accord,2007 Honda Civic,2010 Honda Accord
Account_ID,MORT-003,LOAN-001,LOAN-002,LOAN-003,LOAN-005,LOAN-004
3/31/2018,
```

- [ ] **Step 2: Verify extraction still works**

Run a quick extraction smoke test:
```python
# Run in Python REPL from project root
import yaml
from extractors.csv_extractor import CsvExtractor
cfg = {"paths": {"input_dir": r"z:/Projects/data/assets"}, "csv_files": {"zillow": "Zillow Estimate, 2108 N 3rd St.csv", "debt": "Debt.csv"}}
records = CsvExtractor(cfg)._extract_debt()
# Should return records; Account_ID row should be silently skipped
civic_records = [r for r in records if r["field"] == "debt_car_2007_civic"]
print(f"Civic debt records: {len(civic_records)}")  # Should be > 0 if Debt.csv has 2007 Civic data
```

- [ ] **Step 3: Commit**

```bash
git add "z:/Projects/data/assets/Debt.csv"
git commit -m "feat: add Account_ID reference row to Debt.csv"
```

---

## Task 5: Add Account_ID row and 18 missing columns to Investments_and_Cash.csv

**Files:**
- Create: `scripts/migrate_investments_csv.py`
- Modify: `z:/Projects/data/assets/Investments_and_Cash.csv`

- [ ] **Step 1: Create the migration script**

Create `scripts/migrate_investments_csv.py`:

```python
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
  Row 2: Account_ID  ← NEW
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
```

- [ ] **Step 2: Run the migration**

```
python scripts/migrate_investments_csv.py
```

Expected:
```
Done. Updated z:\Projects\data\assets\Investments_and_Cash.csv
  Account_ID row inserted: 11 existing + 18 new IDs
  New columns appended: 18
  Data rows extended: <N>
```

- [ ] **Step 3: Verify the file structure**

Open `Investments_and_Cash.csv` and confirm:
- Row 1: `Bank,Wealthfront,Fidelity,...,Ledger`
- Row 2: `Bank_Account_Type,Joint Cash Account,...,Nano S Plus ETH`
- Row 3: `Account_ID,CASH-001,INV-001,...,CRYPT-004`
- Row 4: `Status,Open,Open,...,Open`
- Row 5: `Owner,Joint,Joint,...,Chris`
- Data rows have 29 value columns (11 existing + 18 new), all new columns empty

- [ ] **Step 4: Commit**

```bash
git add scripts/migrate_investments_csv.py "z:/Projects/data/assets/Investments_and_Cash.csv"
git commit -m "feat: add Account_ID row and 18 missing account columns to Investments_and_Cash.csv"
```

---

## Task 6: Dashboard — month selector + month-aware snapshot cards

**Files:**
- Modify: `dashboard_template.html`

This task refactors the hardcoded `latest` snapshot to be driven by a month selector dropdown.

- [ ] **Step 1: Add month selector HTML — replace the subtitle line**

Find and replace the `<p class="subtitle">` and cards section:

Old (lines 161-163):
```html
  <h1>Finance Dashboard</h1>
  <p class="subtitle" id="as-of"></p>

  <div class="cards" id="cards"></div>
```

New:
```html
  <h1>Finance Dashboard</h1>
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:24px;flex-wrap:wrap;">
    <p class="subtitle" id="as-of" style="margin:0"></p>
    <select id="sel-month" style="background:#1e2130;border:1px solid #3d4460;border-radius:8px;color:#e2e8f0;font-size:0.875rem;padding:6px 10px;cursor:pointer;outline:none;"></select>
  </div>

  <div class="cards" id="cards"></div>
```

- [ ] **Step 2: Replace the snapshot card JS section**

Find and replace this block (lines 234–255):
```javascript
// ── Snapshot cards ────────────────────────────────────────────────────────────
const latest = DATA[DATA.length - 1] || {};

document.getElementById("as-of").textContent = latest.date
  ? "As of " + new Date(latest.date + "T12:00:00").toLocaleDateString("en-US", { year: "numeric", month: "long" })
  : "";

const cardDefs = [
  { label: "Net Worth",         key: "net_worth",         cls: "positive" },
  { label: "Total Assets",      key: "total_assets",      cls: "neutral"  },
  { label: "Total Liabilities", key: "total_liabilities", cls: "negative" },
  { label: "Home Equity",       key: "home_equity",       cls: "positive" },
];

const cardsEl = document.getElementById("cards");
cardDefs.forEach(({ label, key, cls }) => {
  const v = latest[key];
  const card = document.createElement("div");
  card.className = "card";
  card.innerHTML = `<div class="card-label">${label}</div>`
    + `<div class="card-value ${v != null && v < 0 ? "negative" : cls}">${fmt(v)}</div>`;
  cardsEl.appendChild(card);
});
```

With:
```javascript
// ── Month selector ────────────────────────────────────────────────────────────
const hasData = r => r.net_worth != null || r.total_assets != null;
const dataMonths = DATA.filter(hasData);

const monthSel = document.getElementById("sel-month");
dataMonths.slice().reverse().forEach(r => {
  const opt = document.createElement("option");
  opt.value = r.date;
  opt.textContent = monthLabel(r.date);
  monthSel.appendChild(opt);
});
// Default: most recent month with data
monthSel.selectedIndex = 0;

let selectedRow = dataMonths[dataMonths.length - 1] || {};

monthSel.addEventListener("change", () => {
  selectedRow = DATA.find(r => r.date === monthSel.value) || {};
  document.getElementById("as-of").textContent = selectedRow.date
    ? "As of " + new Date(selectedRow.date + "T12:00:00").toLocaleDateString("en-US", { year: "numeric", month: "long" })
    : "";
  renderCards(selectedRow);
  renderAssetPie(selectedRow);
});

document.getElementById("as-of").textContent = selectedRow.date
  ? "As of " + new Date(selectedRow.date + "T12:00:00").toLocaleDateString("en-US", { year: "numeric", month: "long" })
  : "";

// ── Snapshot cards ────────────────────────────────────────────────────────────
const cardDefs = [
  { label: "Net Worth",         key: "net_worth",         cls: "positive" },
  { label: "Total Assets",      key: "total_assets",      cls: "neutral"  },
  { label: "Total Liabilities", key: "total_liabilities", cls: "negative" },
  { label: "Home Equity",       key: "home_equity",       cls: "positive" },
];

const cardsEl = document.getElementById("cards");

function renderCards(row) {
  cardsEl.innerHTML = "";
  cardDefs.forEach(({ label, key, cls }) => {
    const v = row[key];
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `<div class="card-label">${label}</div>`
      + `<div class="card-value ${v != null && v < 0 ? "negative" : cls}">${fmt(v)}</div>`;
    cardsEl.appendChild(card);
  });
}

renderCards(selectedRow);
```

- [ ] **Step 3: Verify in browser**

Open `z:/Projects/data/assets/output/dashboard.html` in a browser. Confirm:
- Dropdown appears next to "As of …" subtitle
- Changing the month updates all 4 snapshot card values
- Default selection shows the latest month

- [ ] **Step 4: Commit**

```bash
git add dashboard_template.html
git commit -m "feat: add month selector to drive snapshot cards"
```

---

## Task 7: Dashboard — asset pie chart for selected month

**Files:**
- Modify: `dashboard_template.html`

- [ ] **Step 1: Add pie chart HTML — insert a new row between cards and charts sections**

Find:
```html
  <div class="charts">
```

Replace with:
```html
  <!-- Asset pie chart row -->
  <div style="display:grid;grid-template-columns:minmax(300px,480px) 1fr;gap:24px;margin-bottom:24px;align-items:start;">
    <div class="chart-box">
      <div class="chart-title">Asset Breakdown — <span id="pie-month-label"></span></div>
      <canvas id="chart-assets-pie" style="max-height:280px;"></canvas>
    </div>
    <div style="display:flex;flex-direction:column;gap:16px;" id="pie-legend-detail"></div>
  </div>

  <div class="charts">
```

- [ ] **Step 2: Add `renderAssetPie()` function — insert before the Net Worth chart section**

Find:
```javascript
// ── Net worth line chart ──────────────────────────────────────────────────────
```

Insert before it:
```javascript
// ── Asset pie chart (selected month) ─────────────────────────────────────────
const PIE_ASSETS = [
  { label: "Home",       key: "home_value",            color: "#60a5fa" },
  { label: "Tesla MY",   key: "car_tesla_model_y",     color: "#f472b6" },
  { label: "Honda 2018", key: "car_2018_honda_accord", color: "#a78bfa" },
  { label: "Honda 2010", key: "car_2010_honda_accord", color: "#fb923c" },
  { label: "Civic 2007", key: "car_2007_honda_civic",  color: "#facc15" },
];

let pieChart = null;

function renderAssetPie(row) {
  const active = PIE_ASSETS.filter(a => (row[a.key] ?? 0) > 0);
  const labels  = active.map(a => a.label);
  const values  = active.map(a => row[a.key]);
  const colors  = active.map(a => a.color);
  const total   = values.reduce((s, v) => s + v, 0);

  document.getElementById("pie-month-label").textContent =
    row.date ? monthLabel(row.date) : "";

  if (pieChart) pieChart.destroy();
  if (active.length === 0) return;

  pieChart = new Chart(document.getElementById("chart-assets-pie"), {
    type: "doughnut",
    data: { labels, datasets: [{ data: values, backgroundColor: colors, borderWidth: 1, borderColor: "#0f1117" }] },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { labels: { color: "#94a3b8", boxWidth: 12 } },
        tooltip: {
          callbacks: {
            label: ctx => {
              const pct = total > 0 ? ((ctx.raw / total) * 100).toFixed(1) : "0.0";
              return ` ${fmt(ctx.raw)} (${pct}%)`;
            },
          },
        },
      },
    },
  });
}

renderAssetPie(selectedRow);

```

- [ ] **Step 3: Verify in browser**

Regenerate `dashboard.html` by running the pipeline, or manually inject test data. Open in browser and confirm:
- Doughnut chart appears below snapshot cards
- Month label in chart title matches selected month
- Changing the month selector updates the pie chart
- Assets with zero/null value are absent from the chart

- [ ] **Step 4: Commit**

```bash
git add dashboard_template.html
git commit -m "feat: add asset doughnut pie chart for selected month"
```

---

## Task 8: Dashboard — filter zero-value assets from Asset Breakdown chart

**Files:**
- Modify: `dashboard_template.html`

- [ ] **Step 1: Replace the asset stacked area chart section**

Find (lines 393–406):
```javascript
// ── Asset stacked area chart ──────────────────────────────────────────────────
new Chart(document.getElementById("chart-assets"), {
  type: "line",
  data: {
    labels: chartLabels(DATA),
    datasets: [
      { label: "Home",         data: col(DATA, "home_value"),            borderColor: "#60a5fa", backgroundColor: "rgba(96,165,250,0.25)",  fill: true, tension: 0.3, pointRadius: 0, borderWidth: 1.5, spanGaps: true },
      { label: "Tesla MY",     data: col(DATA, "car_tesla_model_y"),     borderColor: "#f472b6", backgroundColor: "rgba(244,114,182,0.25)", fill: true, tension: 0.3, pointRadius: 0, borderWidth: 1.5, spanGaps: true },
      { label: "Honda 2018",   data: col(DATA, "car_2018_honda_accord"), borderColor: "#a78bfa", backgroundColor: "rgba(167,139,250,0.25)", fill: true, tension: 0.3, pointRadius: 0, borderWidth: 1.5, spanGaps: true },
      { label: "Honda 2010",   data: col(DATA, "car_2010_honda_accord"), borderColor: "#fb923c", backgroundColor: "rgba(251,146,60,0.25)",  fill: true, tension: 0.3, pointRadius: 0, borderWidth: 1.5, spanGaps: true },
      { label: "Civic 2007",   data: col(DATA, "car_2007_honda_civic"),  borderColor: "#facc15", backgroundColor: "rgba(250,204,21,0.15)",  fill: true, tension: 0.3, pointRadius: 0, borderWidth: 1.5, spanGaps: true },
    ],
  },
  options: { ...CHART_DEFAULTS, scales: { ...CHART_DEFAULTS.scales, y: { ...CHART_DEFAULTS.scales.y, stacked: true } } },
});
```

With:
```javascript
// ── Asset stacked area chart — zero-value assets excluded from legend ─────────
const ASSET_DATASETS_ALL = [
  { label: "Home",         key: "home_value",            borderColor: "#60a5fa", backgroundColor: "rgba(96,165,250,0.25)"  },
  { label: "Tesla MY",     key: "car_tesla_model_y",     borderColor: "#f472b6", backgroundColor: "rgba(244,114,182,0.25)" },
  { label: "Honda 2018",   key: "car_2018_honda_accord", borderColor: "#a78bfa", backgroundColor: "rgba(167,139,250,0.25)" },
  { label: "Honda 2010",   key: "car_2010_honda_accord", borderColor: "#fb923c", backgroundColor: "rgba(251,146,60,0.25)"  },
  { label: "Civic 2007",   key: "car_2007_honda_civic",  borderColor: "#facc15", backgroundColor: "rgba(250,204,21,0.15)"  },
];

// Only include datasets where at least one month has a non-null, non-zero value
const activeAssetDatasets = ASSET_DATASETS_ALL
  .filter(d => DATA.some(r => (r[d.key] ?? 0) > 0))
  .map(d => ({
    label: d.label,
    data: col(DATA, d.key),
    borderColor: d.borderColor,
    backgroundColor: d.backgroundColor,
    fill: true, tension: 0.3, pointRadius: 0, borderWidth: 1.5, spanGaps: true,
  }));

new Chart(document.getElementById("chart-assets"), {
  type: "line",
  data: { labels: chartLabels(DATA), datasets: activeAssetDatasets },
  options: { ...CHART_DEFAULTS, scales: { ...CHART_DEFAULTS.scales, y: { ...CHART_DEFAULTS.scales.y, stacked: true } } },
});
```

- [ ] **Step 2: Verify in browser**

Open the dashboard. Confirm:
- The 2007 Honda Civic (sold in 2018) no longer appears in the Asset Breakdown legend or chart (all values zero)
- The 2010 Honda Accord (sold in 2025) similarly absent or present depending on whether values exist in the data
- Active assets (Home, Tesla, Honda 2018) still render correctly

- [ ] **Step 3: Commit**

```bash
git add dashboard_template.html
git commit -m "fix: exclude zero-value assets from Asset Breakdown chart legend"
```

---

## Task 9: Dashboard — regroup Month Comparison table + move to bottom

**Files:**
- Modify: `dashboard_template.html`

This task does two things: (1) moves the Month Comparison HTML block from above the charts to below, and (2) replaces the granular per-vehicle `COMPARE_ROWS` with aggregated rows.

- [ ] **Step 1: Remove the Month Comparison HTML block from its current position**

Find and remove this entire block (lines 165–187):
```html
  <!-- Month comparison -->
  <div class="compare-section">
    <div class="compare-controls">
      <h2 style="margin:0">Month Comparison</h2>
      <div style="flex:1"></div>
      <label for="sel-a">Compare</label>
      <select id="sel-a"></select>
      <span class="compare-vs">vs</span>
      <select id="sel-b"></select>
    </div>
    <table class="compare-table">
      <thead>
        <tr>
          <th>Metric</th>
          <th id="col-a-head"></th>
          <th id="col-b-head"></th>
          <th>Change</th>
          <th>Change %</th>
        </tr>
      </thead>
      <tbody id="compare-body"></tbody>
    </table>
  </div>
```

- [ ] **Step 2: Add the Month Comparison HTML block below the charts section (after `</div>` that closes `<div class="charts">`)**

After the closing `</div>` of `<div class="charts">`, add:
```html

  <!-- Month comparison — moved below charts -->
  <div class="compare-section" style="margin-top:24px;">
    <div class="compare-controls">
      <h2 style="margin:0">Month Comparison</h2>
      <div style="flex:1"></div>
      <label for="sel-a">Compare</label>
      <select id="sel-a"></select>
      <span class="compare-vs">vs</span>
      <select id="sel-b"></select>
    </div>
    <table class="compare-table">
      <thead>
        <tr>
          <th>Metric</th>
          <th id="col-a-head"></th>
          <th id="col-b-head"></th>
          <th>Change</th>
          <th>Change %</th>
        </tr>
      </thead>
      <tbody id="compare-body"></tbody>
    </table>
  </div>
```

- [ ] **Step 3: Replace COMPARE_ROWS and renderComparison in JS**

Find the entire `COMPARE_ROWS` block and `renderComparison` function (lines 259–349) and replace with:

```javascript
// ── Month comparison ──────────────────────────────────────────────────────────
// Vehicle value and auto loan totals are computed inline from row data.
// Keys prefixed with "_" are computed; all others are direct row field lookups.

const CAR_KEYS  = ["car_tesla_model_y", "car_2018_honda_accord", "car_2010_honda_accord", "car_2007_honda_civic"];
const LOAN_KEYS = ["debt_car_tesla", "debt_car_2018_accord", "debt_car_2010_accord", "debt_car_2007_civic"];

function getCompareVal(row, key) {
  if (key === "_vehicle_value") {
    const vals = CAR_KEYS.map(k => row[k] ?? 0);
    const sum = vals.reduce((a, b) => a + b, 0);
    return sum > 0 ? sum : null;
  }
  if (key === "_auto_loans") {
    const vals = LOAN_KEYS.map(k => row[k] ?? 0);
    const sum = vals.reduce((a, b) => a + b, 0);
    return sum > 0 ? sum : null;
  }
  if (key === "_vehicle_equity") {
    const vv = getCompareVal(row, "_vehicle_value");
    const al = getCompareVal(row, "_auto_loans");
    return vv != null ? (vv - (al ?? 0)) : null;
  }
  return row[key] ?? null;
}

const COMPARE_ROWS = [
  { section: "Summary" },
  { label: "Net Worth",         key: "net_worth",         good: "up"   },
  { label: "Total Assets",      key: "total_assets",      good: "up"   },
  { label: "Total Liabilities", key: "total_liabilities", good: "down" },
  { section: "Assets" },
  { label: "Home Value",        key: "home_value",        good: "up"   },
  { label: "Vehicle Value",     key: "_vehicle_value",    good: "up"   },
  { section: "Liabilities" },
  { label: "Mortgage",          key: "debt_mortgage",     good: "down" },
  { label: "Auto Loans",        key: "_auto_loans",       good: "down" },
  { section: "Equity" },
  { label: "Home Equity",       key: "home_equity",       good: "up"   },
  { label: "Vehicle Equity",    key: "_vehicle_equity",   good: "up"   },
];

const selA = document.getElementById("sel-a");
const selB = document.getElementById("sel-b");

dataMonths.slice().reverse().forEach(r => {
  [selA, selB].forEach(sel => {
    const opt = document.createElement("option");
    opt.value = r.date;
    opt.textContent = monthLabel(r.date);
    sel.appendChild(opt);
  });
});

selA.selectedIndex = 0;
selB.selectedIndex = Math.min(1, dataMonths.length - 1);

function byDate(dateStr) {
  return DATA.find(r => r.date === dateStr) || {};
}

function renderComparison() {
  const rowA = byDate(selA.value);
  const rowB = byDate(selB.value);

  document.getElementById("col-a-head").textContent = monthLabel(selA.value);
  document.getElementById("col-b-head").textContent = monthLabel(selB.value);

  const tbody = document.getElementById("compare-body");
  tbody.innerHTML = "";

  COMPARE_ROWS.forEach(row => {
    const tr = document.createElement("tr");

    if (row.section !== undefined) {
      tr.className = "section-header";
      tr.innerHTML = `<td colspan="5">${row.section}</td>`;
      tbody.appendChild(tr);
      return;
    }

    const a = getCompareVal(rowA, row.key);
    const b = getCompareVal(rowB, row.key);

    let deltaAmt = null, deltaPct = null, deltaClass = "flat";
    if (a != null && b != null) {
      deltaAmt = a - b;
      deltaPct = b !== 0 ? ((a - b) / Math.abs(b)) * 100 : null;
      if (deltaAmt !== 0) {
        const isUp = deltaAmt > 0;
        deltaClass = (row.good === "up" ? isUp : !isUp) ? "up" : "down";
      }
    }

    tr.innerHTML = `<td>${row.label}</td>`
      + `<td>${fmt(a)}</td>`
      + `<td>${fmt(b)}</td>`
      + `<td class="delta ${deltaClass}">${deltaAmt != null ? (deltaAmt >= 0 ? "+" : "") + fmt(deltaAmt) : "—"}</td>`
      + `<td class="delta ${deltaClass}">${deltaPct != null ? fmtPct(deltaPct) : "—"}</td>`;

    tbody.appendChild(tr);
  });
}

selA.addEventListener("change", renderComparison);
selB.addEventListener("change", renderComparison);
renderComparison();
```

Note: Remove the old `const hasData` and `dataMonths` lines that were part of the original comparison section — they are now defined in the Month Selector section (Task 6). Also remove the old `byDate()` function if it appears separately — it is redefined here.

- [ ] **Step 4: Verify in browser**

Open the dashboard and confirm:
- Month Comparison block appears below all three timeline charts
- Rows show: Summary (3 rows), Assets (Home Value + Vehicle Value), Liabilities (Mortgage + Auto Loans), Equity (Home Equity + Vehicle Equity)
- Vehicle Value = sum of all active car values; Auto Loans = sum of all car debt
- Comparison dropdowns still default to latest vs. previous month

- [ ] **Step 5: Commit**

```bash
git add dashboard_template.html
git commit -m "feat: regroup comparison table by category and move to bottom"
```

---

## Task 10: Dashboard — financial to-do list

**Files:**
- Modify: `dashboard_template.html`

- [ ] **Step 1: Add CSS for the to-do list**

Find the closing `</style>` tag and insert before it:
```css
    /* ── To-do list ── */
    .todo-section {
      background: #1e2130;
      border: 1px solid #2d3348;
      border-radius: 12px;
      padding: 20px;
      margin-top: 24px;
    }

    .todo-list {
      list-style: none;
      margin-top: 12px;
    }

    .todo-list li {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      padding: 10px 0;
      border-bottom: 1px solid #1a1f30;
      font-size: 0.875rem;
      color: #cbd5e1;
      line-height: 1.5;
    }

    .todo-list li:last-child { border-bottom: none; }

    .todo-badge {
      flex-shrink: 0;
      width: 20px;
      height: 20px;
      border: 1.5px solid #3d4460;
      border-radius: 4px;
      margin-top: 2px;
    }

    .todo-list strong { color: #e2e8f0; }
```

- [ ] **Step 2: Add to-do list HTML — after the Month Comparison `</div>` (before `</body>`)**

Find `</body>` and insert before it:
```html
  <!-- Financial To-Do List -->
  <div class="todo-section">
    <h2>Financial To-Do</h2>
    <ul class="todo-list">
      <li>
        <div class="todo-badge"></div>
        <span><strong>Open Fidelity UNIQUE 529 for Nico</strong> — account is listed in Accounts.csv as "To be opened"; no historical data tracked yet.</span>
      </li>
      <li>
        <div class="todo-badge"></div>
        <span><strong>Complete missing account numbers</strong> — Wealthfront (Kim), SoFi (Kim), Fidelity (Kim), Robinhood (Kim), and Ledger wallets all show &lt;to be inserted&gt; in Accounts.csv.</span>
      </li>
      <li>
        <div class="todo-badge"></div>
        <span><strong>Rollover Robinhood Traditional IRA → Alight 401k</strong> — Robinhood 5-year match timer expires 3/3/2029. Must complete rollover before that date to avoid forfeiting matched funds.</span>
      </li>
      <li>
        <div class="todo-badge"></div>
        <span><strong>Move Robinhood Roth IRA → Fidelity Roth IRA</strong> — same Robinhood 5-year timer, expires 3/3/2029.</span>
      </li>
      <li>
        <div class="todo-badge"></div>
        <span><strong>Add crypto wallet balances to pipeline</strong> — Venmo (BTC/ETH) and Ledger (BTC/ETH) wallets tracked in Accounts.csv but have no balance history and no pipeline extractor yet.</span>
      </li>
      <li>
        <div class="todo-badge"></div>
        <span><strong>Set up automated investment account balance tracking</strong> — Investments_and_Cash.csv is currently updated manually; a future extractor would automate this.</span>
      </li>
    </ul>
  </div>

```

- [ ] **Step 3: Verify in browser**

Open the dashboard and confirm:
- To-Do section appears at the very bottom of the page
- All 6 items render with checkbox placeholder boxes and readable text
- Styling matches the dark card aesthetic

- [ ] **Step 4: Commit**

```bash
git add dashboard_template.html
git commit -m "feat: add financial to-do list block to dashboard"
```

---

## Task 11: Write Lessons Learned and Changelog

**Files:**
- Create: `docs/LESSONS_LEARNED.md`
- Create: `docs/CHANGELOG.md`

- [ ] **Step 1: Create `docs/LESSONS_LEARNED.md`**

```markdown
# Lessons Learned

## v1.1.0 — 2026-04-10 Continuous Improvements

### Silent extractor miss from vehicle year mismatch

**What happened:** The Honda Civic was recorded as "2008" in the original pipeline code (`csv_extractor.py` DEBT_COLUMN_MAP key, `pipeline.py` field names, `dashboard_template.html` labels) while the source CSV (`Debt.csv`) always had the correct year "2007". Because `DEBT_COLUMN_MAP` looked for `"2008 Honda Civic"` but the CSV column was named `"2007 Honda Civic"`, `csv_extractor.py` silently produced zero records for that column. No error was raised — the mismatch just meant the data was never extracted.

**Why it was hard to spot:** The pipeline did not validate that every mapped column existed in the source file. It simply iterated over `DEBT_COLUMN_MAP` keys and called `row.get(csv_col, "")`, returning an empty string for a missing column — which was then treated as no data and skipped.

**Lesson:** When building column-name-to-field-name mappings for CSV extractors, add a one-time validation pass that logs a warning (or raises) for any mapped column not found in the file headers. This surfaces year/typo mismatches immediately rather than silently producing missing data for years.

**Fix applied:** Corrected the key in `DEBT_COLUMN_MAP` and all downstream field references to "2007". Added unit tests (`tests/test_civic_rename.py`) to pin the correct year and prevent regression.

---

### Multi-row header CSV format is fragile

**What happened:** `Investments_and_Cash.csv` uses a transposed format where the first few rows are headers (Bank, Bank_Account_Type, Status, Owner) rather than the first row being a column header. This is human-readable in a spreadsheet but requires special handling when parsing programmatically.

**Lesson:** Document the format expectation explicitly (done in spec). When adding new rows to this file (like Account_ID), a migration script that validates the row label order before writing is safer than manual editing. The `scripts/migrate_investments_csv.py` script includes this validation.

---

### CSV column order assumptions in migration scripts

The `migrate_accounts_csv.py` script assigns Account IDs by row index. If rows are ever reordered in `Accounts.csv`, the IDs will be incorrectly reassigned. The script validates row count but not row identity.

**Lesson:** For future migrations, match by a stable key (e.g., Bank + Account_Number combination) rather than row index.
```

- [ ] **Step 2: Create `docs/CHANGELOG.md`**

```markdown
# Changelog

All notable changes to the Finance Pipeline project.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.1.0] — 2026-04-10

### Fixed
- **Honda Civic year correction:** Renamed all `car_2008_honda_civic` and `debt_car_2008_civic` field references to `car_2007_honda_civic` and `debt_car_2007_civic` across `csv_extractor.py`, `pipeline.py`, `output.py`, `config.example.yaml`, and `dashboard_template.html`. The Civic is a 2007 model. This bug caused the Debt.csv column `2007 Honda Civic` to never be extracted (silent miss). Source CSVs were already correct.

### Added
- **Account IDs:** Added type-prefixed `Account_ID` column to `Accounts.csv` (CASH-###, INV-###, AUTO-###, CRYPT-###, MORT-###, LOAN-###). Added matching `Account_ID` reference rows to `Investments_and_Cash.csv` and `Debt.csv` for standardized cross-file references.
- **Investments_and_Cash.csv expansion:** Added 18 missing account columns (Wealthfront individual accounts, SoFi accounts, Ally accounts, additional Fidelity/Robinhood accounts, crypto wallets). All new columns initialized empty; values to be filled manually.
- **Dashboard month selector:** Dropdown to change the "current" month view. Drives snapshot cards and asset pie chart. Defaults to the most recent month with data.
- **Asset pie chart:** Doughnut chart showing asset distribution for the selected month. Zero-value assets excluded. Displays below snapshot cards.
- **Zero-value asset filtering:** Asset Breakdown stacked area chart now excludes datasets where all values are null or zero (removes sold vehicles from legend).
- **Regrouped Month Comparison:** Comparison table rows consolidated from per-vehicle granularity to category-level: Assets (Home Value, Vehicle Value), Liabilities (Mortgage, Auto Loans), Equity (Home Equity, Vehicle Equity). Vehicle Value and Auto Loans are computed client-side.
- **Month Comparison moved:** Comparison block relocated from above charts to below all three timeline charts.
- **Financial To-Do list:** Static block at the bottom of the dashboard listing 6 actionable financial items.
- **Unit tests:** `tests/test_civic_rename.py` pins correct 2007 field names in DEBT_COLUMN_MAP and pipeline column lists.
- **Documentation:** `docs/LESSONS_LEARNED.md` and `docs/CHANGELOG.md` added.

### Notes
- `FIRE_Net_Worth` column in `Accounts.csv` is intentionally retained. It is not consumed by this pipeline. It is reserved for a future FIRE-specific dashboard.
- `Investments_and_Cash.csv` is manually maintained. Automated extraction is a future improvement.

---

## [1.0.0] — 2026-04-10

Initial release. See `docs/superpowers/specs/2026-04-10-finance-pipeline-design.md` for full architecture.
```

- [ ] **Step 3: Commit**

```bash
git add docs/LESSONS_LEARNED.md docs/CHANGELOG.md
git commit -m "docs: add Lessons Learned and Changelog for v1.1.0"
```

---

## Task 12: Update pipeline design spec and run end-to-end smoke test

**Files:**
- Modify: `docs/superpowers/specs/2026-04-10-finance-pipeline-design.md`

- [ ] **Step 1: Update field names in the spec — Data Model section**

In the Asset Columns table, change:
```
| `car_2008_honda_civic` | CARFAX (Paperless) |
```
To:
```
| `car_2007_honda_civic` | CARFAX (Paperless) |
```

In the Liability Columns table, change:
```
| `debt_car_2008_civic` | Debt.csv (all zeros — no loan; included for completeness) |
```
To:
```
| `debt_car_2007_civic` | Debt.csv (all zeros — no loan; included for completeness) |
```

- [ ] **Step 2: Update the Debt.csv column reference in Data Sources section (line 41)**

Change:
```
**Debt.csv columns:** `Date`, `2108 N 3rd` (mortgage), `Student Loan`, `2025 Tesla MYLR`, `2018 Honda Accord`, `2008 Honda Civic`, `2010 Honda Accord`
```
To:
```
**Debt.csv columns:** `Date`, `Account_ID` (reference row — skipped by extractor), `2108 N 3rd` (mortgage), `Student Loan`, `2025 Tesla MYLR`, `2018 Honda Accord`, `2007 Honda Civic`, `2010 Honda Accord`
```

- [ ] **Step 3: Add FIRE note to Non-Goals section**

Add to the Non-Goals section:
```markdown
- No FIRE (Financial Independence Retire Early) net worth calculations — the `FIRE_Net_Worth` column in `Accounts.csv` is intentionally ignored. FIRE calculations are reserved for a future separate dashboard.
```

- [ ] **Step 4: Run end-to-end smoke test**

Verify the pipeline runs cleanly with the updated code. If running locally (no Paperless access), test just the CSV extractor path:

```python
# Run from z:/Projects/dev/Assets Tracker
# Quick smoke: verify pipeline processes debt records with corrected 2007 field
import yaml
from extractors.csv_extractor import CsvExtractor
import pipeline

cfg = {
    "paths": {"input_dir": r"z:/Projects/data/assets"},
    "csv_files": {
        "zillow": "Zillow Estimate, 2108 N 3rd St.csv",
        "debt": "Debt.csv"
    }
}
ext = CsvExtractor(cfg)
records = ext.extract()
civic_recs = [r for r in records if r["field"] == "debt_car_2007_civic"]
print(f"Total records: {len(records)}")
print(f"2007 Civic debt records: {len(civic_recs)}")
# Expected: 0 (sold in 2018, no debt was ever recorded for this car)
# But if Debt.csv has values in the 2007 Honda Civic column, you'll see them here

rows = pipeline.run(records)
print(f"Monthly rows produced: {len(rows)}")
last = rows[-1]
print(f"Latest month: {last['date']}, net_worth: {last.get('net_worth')}, car_2007_honda_civic: {last.get('car_2007_honda_civic')}")
```

Expected: No errors, row count matches history, 2007 field present (0.0 or null for sold car).

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/specs/2026-04-10-finance-pipeline-design.md
git commit -m "docs: update pipeline spec with 2007 Civic field names, Account_ID note, FIRE non-goal"
```

---

## Self-Review Checklist

**Spec coverage:**
- [x] Honda Civic 2007 correction — Tasks 1 and 2
- [x] Account_ID type-prefixed format — Tasks 3, 4, 5
- [x] Investments_and_Cash.csv 18 missing columns — Task 5
- [x] Dashboard month selector — Task 6
- [x] Asset pie chart — Task 7
- [x] Zero-value asset filtering — Task 8
- [x] Comparison table regrouped + moved to bottom — Task 9
- [x] Financial to-do list — Task 10
- [x] FIRE reference handled (non-goal in spec, note in changelog) — Tasks 11, 12
- [x] Lessons Learned — Task 11
- [x] Changelog — Task 11
- [x] Pipeline spec updated — Task 12
- [x] End-to-end smoke test — Task 12

**Placeholder scan:** No TBD, TODO, or vague steps found.

**Type consistency:**
- `selectedRow` defined in Task 6, used in Task 7 (`renderAssetPie(selectedRow)`) — consistent
- `dataMonths` defined in Task 6's month selector block; Task 9 comparison section uses `dataMonths.slice().reverse()` to populate dropdowns — consistent; the old duplicate `const hasData`/`dataMonths` block from the original comparison code must be removed in Task 9 Step 3
- `getCompareVal()` defined and used only in Task 9 — consistent
- `byDate()` appears in old code (line 300) and is redefined in Task 9; the old definition must be removed — called out in Task 9 Step 3
- `car_2007_honda_civic` used in Tasks 1, 2, 7, 8, 9 — consistent throughout
