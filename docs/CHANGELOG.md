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
