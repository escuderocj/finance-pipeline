---
name: Continuous Improvements v1
description: Honda Civic year correction, Account IDs, Investments CSV expansion, Dashboard enhancements (month selector, pie chart, regrouped comparison, to-do list), FIRE cleanup, and documentation
type: project
---

# Continuous Improvements v1 — Design Spec

**Date:** 2026-04-10
**Status:** Approved
**Builds on:** `2026-04-10-finance-pipeline-design.md`

---

## Overview

A set of coordinated improvements to the Finance Pipeline project covering:
1. Correcting the Honda Civic year from 2008 → 2007 across all code and config
2. Adding type-prefixed Account IDs to `Accounts.csv` and disseminating to downstream CSVs
3. Expanding `Investments_and_Cash.csv` with 18 missing account columns
4. Multiple dashboard enhancements (month selector, asset pie chart, regrouped comparison table, financial to-do list)
5. Removing FIRE references from the dashboard scope (reserved for a future separate dashboard)
6. Producing a Lessons Learned doc and Changelog

---

## 1. Honda Civic 2007 Correction

**Problem:** The Honda Civic is a 2007 model. All source CSVs (`Accounts.csv`, `Debt.csv`) already use "2007", but the pipeline code, config, and dashboard still reference "2008". This means `csv_extractor.py` fails silently to match the `Debt.csv` column `2007 Honda Civic` — the debt for this vehicle has never been extracted.

**Changes required:**

| File | Old | New |
|---|---|---|
| `extractors/csv_extractor.py` | `"2008 Honda Civic": "debt_car_2008_civic"` | `"2007 Honda Civic": "debt_car_2007_civic"` |
| `pipeline.py` | `"car_2008_honda_civic"`, `"debt_car_2008_civic"` | `"car_2007_honda_civic"`, `"debt_car_2007_civic"` |
| `output.py` | `"car_2008_honda_civic"`, `"debt_car_2008_civic"` | `"car_2007_honda_civic"`, `"debt_car_2007_civic"` |
| `dashboard_template.html` | `car_2008_honda_civic`, `"Honda Civic 2008"`, `"Civic 2008"` | `car_2007_honda_civic`, `"Honda Civic 2007"`, `"Civic 2007"` |
| `config.example.yaml` | `"2008 HONDA CIVIC": "car_2008_honda_civic"` | `"2007 HONDA CIVIC": "car_2007_honda_civic"` |
| `docs/.../design.md` | All 2008 Civic field name and label references | Updated to 2007 |

`Accounts.csv` and `Debt.csv` already say "2007" — no change needed.

---

## 2. Account IDs

### Format

Type-prefixed sequential codes assigned within each account type:

| Prefix | Account Types Covered |
|---|---|
| `CASH-###` | Cash Management Account, Checking, Savings |
| `INV-###` | Brokerage, IRA (Roth/Traditional), 401k, 403b, 529 Plan, Pension Plan, UTMA |
| `AUTO-###` | Vehicle assets (CarFax) |
| `CRYPT-###` | Cryptocurrency wallets |
| `MORT-###` | Mortgage accounts |
| `LOAN-###` | Student loan, auto loans |

### Accounts.csv

A new `Account_ID` column is inserted as the first column. All rows receive an ID, including closed/sold accounts (for historical completeness).

**Assigned IDs:**

| Account_ID | Bank | Bank_Account_Type |
|---|---|---|
| CASH-001 | Wealthfront | Joint Cash Account |
| CASH-002 | Wealthfront | Individual Cash Account (Chris) |
| CASH-003 | Wealthfront | Individual Cash Account (Kim) |
| CASH-004 | SoFi | Checking (Chris) |
| CASH-005 | SoFi | Savings (Chris) |
| CASH-006 | SoFi | Checking (Kim) |
| CASH-007 | SoFi | Savings (Kim) |
| CASH-008 | Ally | Spending Account |
| CASH-009 | Ally | Ally Savings |
| INV-001 | Fidelity | Joint FIRE Brokerage |
| INV-002 | Primearica | UTMA/PA |
| INV-003 | Morgan Stanley | Access Direct Stock Plan |
| INV-004 | Fidelity | Individual - TOD (Chris) |
| INV-005 | Fidelity | Merck US Salaried Pension Plan |
| INV-006 | Robinhood | Individual (Chris) |
| INV-007 | Robinhood | Roth IRA (Chris) |
| INV-008 | Robinhood | Traditional IRA (Chris) |
| INV-009 | Alight | GSK 401(k) Plan |
| INV-010 | Fidelity | Individual - TOD (Kim) |
| INV-011 | Fidelity | Roth IRA (Kim) |
| INV-012 | Fidelity | 403b (Kim) |
| INV-013 | Robinhood | Individual (Kim) |
| INV-014 | Robinhood | Roth IRA (Kim) |
| INV-015 | Fidelity | UNIQUE 529 (Jonah) |
| INV-016 | Fidelity | UNIQUE 529 (Nico) |
| AUTO-001 | CarFax | 2025 Tesla Model Y |
| AUTO-002 | CarFax | 2018 Honda Accord |
| AUTO-003 | CarFax | 2010 Honda Accord |
| AUTO-004 | CarFax | 2007 Honda Civic |
| CRYPT-001 | Venmo | Custodial Wallet BTC |
| CRYPT-002 | Venmo | Custodial Wallet ETH |
| CRYPT-003 | Ledger | Nano S Plus BTC |
| CRYPT-004 | Ledger | Nano S Plus ETH |
| MORT-001 | Nation One | 2108 N 3rd St. Mortgage (Closed) |
| MORT-002 | Suntrust Bank | 2108 N 3rd St. Mortgage (Closed) |
| MORT-003 | Truist Bank | 2108 N 3rd St. Mortgage (Active) |
| LOAN-001 | SoFi | Student Loan Refi |
| LOAN-002 | Ally | 2025 Tesla MYLR Auto Loan |
| LOAN-003 | Bank of America | 2018 Honda Accord Auto Loan |
| LOAN-004 | American Honda Finance Corp | 2010 Honda Accord Auto Loan |
| LOAN-005 | American Honda Finance Corp | 2007 Honda Civic Auto Loan |

### Investments_and_Cash.csv

Add a new `Account_ID` row as row 3 (after Bank and Bank_Account_Type rows, before Status row). Each column gets its matching `Account_ID` from the table above. The first column (`Bank` header column) gets the label `Account_ID` in that row.

### Debt.csv

Add a new `Account_ID` row as row 2 (after the header row). The `Date` column cell in that row gets the label `Account_ID`. Each debt column gets its matching ID:

| Column | Account_ID |
|---|---|
| 2108 N 3rd | MORT-003 |
| Student Loan | LOAN-001 |
| 2025 Tesla MYLR | LOAN-002 |
| 2018 Honda Accord | LOAN-003 |
| 2007 Honda Civic | LOAN-005 |
| 2010 Honda Accord | LOAN-004 |

---

## 3. Missing Accounts in Investments_and_Cash.csv

18 new columns appended (all data cells empty; values to be filled manually):

| Account_ID | Bank | Bank_Account_Type | Status | Owner |
|---|---|---|---|---|
| CASH-002 | Wealthfront | Individual Cash Account | Open | Chris |
| CASH-003 | Wealthfront | Individual Cash Account | Open | Kim |
| CASH-004 | SoFi | Checking | Open | Chris |
| CASH-005 | SoFi | Savings | Open | Chris |
| CASH-006 | SoFi | Checking | Open | Kim |
| CASH-007 | SoFi | Savings | Open | Kim |
| CASH-008 | Ally | Spending Account | Open | Chris |
| CASH-009 | Ally | Ally Savings | Open | Joint |
| INV-004 | Fidelity | Individual - TOD | Open | Chris |
| INV-006 | Robinhood | Individual | Open | Chris |
| INV-010 | Fidelity | Individual - TOD | Open | Kim |
| INV-011 | Fidelity | Roth IRA | Open | Kim |
| INV-013 | Robinhood | Individual | Open | Kim |
| INV-016 | Fidelity | UNIQUE College Investing Plan | To be opened | Chris |
| CRYPT-001 | Venmo | Custodial Wallet BTC | Open | Chris |
| CRYPT-002 | Venmo | Custodial Wallet ETH | Open | Chris |
| CRYPT-003 | Ledger | Nano S Plus BTC | Open | Chris |
| CRYPT-004 | Ledger | Nano S Plus ETH | Open | Chris |

---

## 4. Dashboard Changes

### 4.1 Layout Order (top → bottom)

1. Title + subtitle
2. Month selector *(new)*
3. Snapshot cards — driven by selected month
4. Asset pie chart — driven by selected month *(new)*
5. Net Worth chart (full history)
6. Asset Breakdown chart (full history)
7. Liability Breakdown chart (full history)
8. Month Comparison table *(moved from above charts to bottom)*
9. Financial To-Do List *(new)*

### 4.2 Month Selector

- Dropdown positioned inline with the subtitle ("As of …")
- Populated with all months that have at least one non-null metric (same `hasData` filter as comparison dropdowns)
- Options displayed as `Mon YYYY` (e.g., "Mar 2026"), newest first
- Default: last entry in dataset (current behavior for snapshot cards preserved)
- On change: re-renders snapshot cards and asset pie chart

### 4.3 Snapshot Cards — Month-Aware

Cards already read from `latest`. Change: read from `selectedRow` (the month chosen by the selector) instead of hardcoding `DATA[DATA.length - 1]`. Default remains the last row, so behavior is identical until the user changes the selector.

### 4.4 Asset Pie Chart (Selected Month)

- Chart type: Doughnut
- Data: asset column values for the selected month
- Segments: Home Value, Tesla Model Y, Honda Accord 2018, Honda Accord 2010, Honda Civic 2007
- Segments with value `null` or `0` are excluded from the doughnut
- Displayed in a new `chart-box` in its own full-width row between snapshot cards and the timeline charts
- Legend shown; tooltips show dollar value and percentage of total

### 4.5 Asset Breakdown Chart — Zero Filtering

Before building the `datasets` array, each candidate dataset is checked: if every value is `null` or `0`, the dataset is excluded. This prevents zero-balance assets (e.g., sold vehicles) from appearing in the legend.

### 4.6 Month Comparison Table — Regrouped

Old granular rows (individual vehicles) replaced with aggregated rows:

| Section | Row | Key / Formula |
|---|---|---|
| Summary | Net Worth | `net_worth` |
| Summary | Total Assets | `total_assets` |
| Summary | Total Liabilities | `total_liabilities` |
| Assets | Home Value | `home_value` |
| Assets | Vehicle Value | sum of all `car_*` columns for that month |
| Liabilities | Mortgage | `debt_mortgage` |
| Liabilities | Auto Loans | sum of all `debt_car_*` columns for that month |
| Equity | Home Equity | `home_equity` |
| Equity | Vehicle Equity | Vehicle Value − Auto Loans (computed inline) |

"Vehicle Value" and "Auto Loans" are computed client-side from the row data; no pipeline changes needed.

### 4.7 Financial To-Do List

Static block rendered at the bottom of the dashboard (below the comparison table). Styled to match the dark card aesthetic. Content (hardcoded in template):

1. **Open Fidelity UNIQUE 529 for Nico** — account marked "To be opened" in Accounts.csv
2. **Complete missing account numbers** — Wealthfront (Kim), SoFi (Kim), Fidelity (Kim), Robinhood (Kim), Ledger wallets all show `<to be inserted>` in Accounts.csv
3. **Rollover Robinhood Traditional IRA → Alight 401k** — Robinhood 5-year match timer expires 3/3/2029; must complete before then
4. **Move Robinhood Roth IRA → Fidelity Roth IRA** — same 5-year timer, expires 3/3/2029
5. **Add crypto wallet balances to pipeline** — Venmo (BTC/ETH) and Ledger (BTC/ETH) are tracked in Accounts.csv but have no historical data in Investments_and_Cash.csv and no pipeline extractor
6. **Set up automated investment account balance tracking** — future pipeline extractor to replace manual updates to Investments_and_Cash.csv

---

## 5. FIRE Reference Handling

The `FIRE_Net_Worth` column in `Accounts.csv` is **retained** — it marks which accounts count toward the FIRE net worth calculation, which is needed for a future FIRE dashboard.

The pipeline does not read or output this field. No code changes required. The design spec is updated to document that `FIRE_Net_Worth` is out of scope for the Finance Dashboard and reserved for a future FIRE-specific dashboard.

---

## 6. Documentation Deliverables

| File | Action |
|---|---|
| `docs/LESSONS_LEARNED.md` | New — silent extractor bug from year mismatch, data model naming conventions, CSV header structure risks |
| `docs/CHANGELOG.md` | New — structured changelog with this release as v1.1.0 |
| `docs/superpowers/specs/2026-04-10-finance-pipeline-design.md` | Updated — corrected field names (2007), FIRE note added |
| `docs/superpowers/specs/2026-04-10-continuous-improvements-v1-design.md` | This file |

---

## Out of Scope

- Automated data ingestion for Investments_and_Cash.csv (future improvement)
- FIRE net worth dashboard (separate project)
- Crypto price feeds or balance APIs
- Changes to the Docker/deployment setup
