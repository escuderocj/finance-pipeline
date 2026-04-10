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
