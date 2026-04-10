# Finance Pipeline — Design Spec
**Date:** 2026-04-10  
**Status:** Approved  
**Repo:** escuderocj/finance-pipeline (private)

---

## Overview

A nightly data pipeline that pulls financial asset and liability data from multiple sources, normalizes it onto a unified monthly timeline, and outputs CSV, JSON, and an HTML dashboard. Runs as a Docker container on Unraid 7.x, scheduled via the User Scripts plugin. Code is backed up nightly to a private GitHub repo.

---

## Goals

- Produce a single monthly timeline covering all family assets and liabilities from 2018 to present
- Compute net worth, per-asset equity, and total assets/liabilities at each point in time
- Output data in formats usable in Excel/Sheets (CSV), programmatic tools (JSON), and a browser (HTML dashboard)
- Survive Unraid OS updates without maintenance (Docker runtime, code on array)
- Be extensible: adding a new data source (crypto, investments) requires only a new extractor file

---

## Non-Goals

- No web server or live API — outputs are static files written to disk
- No real-time data — nightly cadence is sufficient
- No automatic Zillow or KBB scraping in v1 — home values come from manually maintained CSVs; auto-scraping is a future extractor option
- No FIRE (Financial Independence Retire Early) net worth calculations — the `FIRE_Net_Worth` column in `Accounts.csv` is intentionally ignored. FIRE calculations are reserved for a future separate dashboard.

---

## Data Sources

### 1. CSV Files — `/mnt/user/Projects/data/assets/`

| File | Content | Cadence |
|---|---|---|
| `Zillow Estimate, 2108 N 3rd St.csv` | Monthly Zestimate for home at 2108 N 3rd St, Philadelphia | Monthly |
| `Debt.csv` | Balances for mortgage, student loan, and car loans (stored as negative values) | Quarterly |

**Debt.csv columns:** `Date`, `Account_ID` (reference row — skipped by extractor), `2108 N 3rd` (mortgage), `Student Loan`, `2025 Tesla MYLR`, `2018 Honda Accord`, `2007 Honda Civic`, `2010 Honda Accord`

**Zillow CSV columns:** `Date`, `Zestimate`, `Estimated Home Value`, `Notes`

### 2. Paperless-ngx API — `http://192.168.1.19:8000/`

**Authentication:** API token stored in `config.yaml` (gitignored)

| Document Type | ID | Count | Extraction Target |
|---|---|---|---|
| Vehicle Update | 88 | ~100 | CARFAX monthly email — car values via regex on `content` field |
| Mortgage | 111 | 62 | Truist monthly statement — principal balance via regex on `content` field |

**Vehicle Update extraction:**  
Documents are CARFAX monthly dashboard emails. Each email covers all vehicles in the garage — the primary vehicle value appears as `History-Based Value by CARFAX $XX,XXX*` and secondary vehicles appear in an "Other Cars in Your Garage" section as `CARFAX Value - $XX,XXX`. The extractor parses all vehicles from a single email in one pass. Vehicle identity is derived from the vehicle name in the surrounding text (e.g., `2025 TESLA MODEL Y`, `2018 HONDA ACCORD`).

**Mortgage extraction:**  
Pattern: `Principal balance $XXX,XXX.XX` on the line containing account summary.

### 3. Future Sources (not in scope for v1)

The extractor interface is designed so these can be added without touching core pipeline logic:
- Crypto holdings (ETH, BTC) — source TBD
- Investment/brokerage accounts — source TBD

---

## Architecture

### Repository Layout

```
finance-pipeline/
├── extractors/
│   ├── __init__.py
│   ├── base.py                  # BaseExtractor interface
│   ├── csv_extractor.py         # Zillow + Debt CSVs
│   └── paperless_extractor.py  # CARFAX emails + mortgage statements
├── pipeline.py                  # Merge, align, compute
├── output.py                    # Write all output files
├── dashboard_template.html      # Chart.js template; data injected at run time
├── main.py                      # Entry point
├── Dockerfile
├── requirements.txt
├── config.example.yaml          # Template with placeholders — committed to git
├── config.yaml                  # Real config — gitignored, lives on server only
├── .env                         # GITHUB_TOKEN — gitignored
└── .gitignore
```

### Deployment Paths on Unraid

| Purpose | Path |
|---|---|
| Code + config | `/mnt/user/appdata/finance-pipeline/` |
| Input CSVs | `/mnt/user/Projects/data/assets/` |
| Output files | `/mnt/user/Projects/data/assets/output/` |

---

## Extractor Interface

Every extractor — current and future — implements `BaseExtractor`:

```python
class BaseExtractor:
    def extract(self) -> list[dict]:
        """
        Returns a list of normalized records:
        [{"date": "2026-01-01", "field": "car_tesla_model_y", "value": 33910.0}, ...]
        
        - date: always first of month, ISO format (YYYY-MM-DD)
        - field: snake_case column name in unified model
        - value: float, always positive (pipeline negates liabilities)
        """
        raise NotImplementedError
```

Adding a new source = create `extractors/crypto_extractor.py`, subclass `BaseExtractor`, register in `main.py`. No changes to `pipeline.py` or `output.py`.

---

## Data Model

The pipeline produces a unified monthly timeline. Each row represents one month (first of month).

### Asset Columns
| Column | Source |
|---|---|
| `home_value` | Zillow CSV |
| `car_tesla_model_y` | CARFAX (Paperless) |
| `car_2018_honda_accord` | CARFAX (Paperless) |
| `car_2010_honda_accord` | CARFAX (Paperless) |
| `car_2007_honda_civic` | CARFAX (Paperless) |
| `total_assets` | Computed: sum of all asset columns |

### Liability Columns (stored as positive numbers)
| Column | Source |
|---|---|
| `debt_mortgage` | Mortgage statements (Paperless) + Debt.csv |
| `debt_student_loan` | Debt.csv |
| `debt_car_tesla` | Debt.csv |
| `debt_car_2018_accord` | Debt.csv |
| `debt_car_2010_accord` | Debt.csv (all zeros — no loan; included for completeness) |
| `debt_car_2007_civic` | Debt.csv (all zeros — no loan; included for completeness) |
| `total_liabilities` | Computed: sum of all liability columns |

### Computed Columns
| Column | Formula |
|---|---|
| `net_worth` | `total_assets - total_liabilities` |
| `home_equity` | `home_value - debt_mortgage` |
| `equity_tesla` | `car_tesla_model_y - debt_car_tesla` |
| `equity_2018_accord` | `car_2018_honda_accord - debt_car_2018_accord` |

### Temporal Alignment Rules
- All dates normalized to first of month (`YYYY-MM-01`)
- Date range: earliest available data point to present
- **Quarterly data (Debt.csv):** forward-filled to produce a value for every month between quarterly entries
- **CARFAX values:** forward-filled when a month has no email (car value holds until next update)
- **Mortgage from Paperless:** monthly; supplements/overrides Debt.csv mortgage column where available
- Missing values left as `null` / empty (not zero) to distinguish "no data" from "zero balance"

---

## Outputs

All written to `/mnt/user/Projects/data/assets/output/` on each run.

### `assets.csv`
Full monthly timeline as CSV. One row per month, all columns. Excel and Google Sheets ready.

### `assets.json`
Same data as an array of JSON objects. Suitable for n8n workflows, future web dashboards, or any downstream tool.

### `summary.json`
Latest month's snapshot only:
```json
{
  "as_of": "2026-04-01",
  "net_worth": 123456.78,
  "total_assets": 567890.12,
  "total_liabilities": 444433.34,
  "assets": { "home_value": 491500, "car_tesla_model_y": 33910, ... },
  "liabilities": { "debt_mortgage": 345638, ... },
  "equity": { "home_equity": 145862, ... },
  "last_run": "2026-04-10T02:00:00"
}
```

### `dashboard.html`
Self-contained single HTML file. Data embedded as a JSON blob in a `<script>` tag — no server required, openable directly in a browser.

Charts (Chart.js, loaded from CDN):
- **Net worth over time** — line chart, full history
- **Asset breakdown** — stacked area chart showing home value + cars over time
- **Liability breakdown** — stacked area chart showing mortgage + other debts over time
- **Current snapshot cards** — net worth, home equity, total assets, total liabilities

---

## Docker

```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
# Code is mounted from array at runtime — not baked in
```

`git` is installed in the image so the nightly git commit + push runs inside the container alongside the pipeline, keeping the User Scripts wrapper script minimal.

**Runtime invocation (User Scripts):**
```bash
docker run --rm \
  -v /mnt/user/appdata/finance-pipeline:/app \
  -v /mnt/user/Projects/data/assets:/data/assets \
  finance-pipeline python main.py
```

The image provides the Python runtime only. All code and config live on the array and are never baked into the image. Rebuilding the image after a Python version bump requires no code changes.

**Dependencies (requirements.txt):**
- `requests` — Paperless-ngx API calls
- `pyyaml` — config file parsing

No pandas, no heavy dependencies. Standard library handles CSV parsing and JSON.

---

## Scheduling

**Cron schedule:** `0 2 * * *` (2:00am daily — within midnight–6am low-power window)  
**Mechanism:** Unraid User Scripts plugin (already installed)  
**Manual trigger:** User Scripts UI or `docker run ...` via SSH

### Nightly Run Sequence
1. Extract all sources (CSV extractor, Paperless extractor)
2. Merge onto monthly timeline, forward-fill gaps, compute metrics
3. Write `assets.csv`, `assets.json`, `summary.json`, `dashboard.html` to output dir
4. `git add -A && git commit -m "Daily update $(date -I)" && git push`

---

## GitHub Backup

**Repo:** `escuderocj/finance-pipeline` (private)  
**Remote URL:** `https://${GITHUB_TOKEN}@github.com/escuderocj/finance-pipeline.git`  
**Token storage:** `.env` file at `/mnt/user/appdata/finance-pipeline/.env` — gitignored  
**What is committed:** All code, `config.example.yaml`, `dashboard_template.html`, `requirements.txt`, `Dockerfile`, output files (`assets.csv`, `assets.json`, `summary.json`, `dashboard.html`)  
**What is NOT committed:** `config.yaml`, `.env`

---

## Security

- Paperless API token stored in `config.yaml` on server only — never in git
- GitHub PAT stored in `.env` on server only — never in git
- `.gitignore` explicitly excludes both files
- `config.example.yaml` committed with placeholder values as documentation

---

## Extensibility

To add a new data source (e.g., Coinbase for ETH/BTC, or a brokerage CSV):
1. Create `extractors/crypto_extractor.py` subclassing `BaseExtractor`
2. Implement `extract()` returning `[{date, field, value}]` records
3. Register the extractor in `main.py`
4. Add new columns to `config.example.yaml` as documentation

No changes needed to `pipeline.py`, `output.py`, or `dashboard_template.html` (new columns appear automatically).
