"""
Finance pipeline entry point.

Run order:
  1. Load config + .env
  2. Extract from all sources (CSV, Paperless)
  3. Merge, align, forward-fill, compute (pipeline)
  4. Write outputs (CSV, JSON, summary, dashboard)
  5. Git commit + push
"""

import os
import subprocess
import sys
from datetime import datetime

import yaml

from extractors.csv_extractor import CsvExtractor
from extractors.paperless_extractor import PaperlessExtractor
import pipeline
import output


# ---------------------------------------------------------------------------
# Config + environment
# ---------------------------------------------------------------------------

def load_config(path: str = None) -> dict:
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "config.yaml")
    if not os.path.exists(path):
        sys.exit(
            f"[main] config.yaml not found at {path}. "
            "Copy config.example.yaml and fill in your values."
        )
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_dotenv(path: str = None) -> None:
    """Load KEY=VALUE pairs from .env into os.environ (if file exists)."""
    if path is None:
        path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())


# ---------------------------------------------------------------------------
# Git
# ---------------------------------------------------------------------------

def git_commit_and_push() -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    token = os.environ.get("GITHUB_TOKEN", "")
    try:
        # Inject token into remote URL so push works without interactive auth
        if token:
            remote_url = f"https://{token}@github.com/escuderocj/finance-pipeline.git"
            subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)

        subprocess.run(["git", "add", "-A"], check=True)
        result = subprocess.run(["git", "diff", "--staged", "--quiet"])
        if result.returncode == 0:
            print("[git] Nothing to commit.")
            return
        subprocess.run(
            ["git", "commit", "-m", f"Daily update {today}"],
            check=True,
        )
        subprocess.run(["git", "push", "--set-upstream", "origin", "HEAD"], check=True)
        print(f"[git] Committed and pushed: Daily update {today}")
    except subprocess.CalledProcessError as e:
        print(f"[git] Warning: git operation failed: {e}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    load_dotenv()
    config = load_config()

    print("[main] Starting finance pipeline...")

    # --- Extract ---
    extractors = [
        CsvExtractor(config),
        PaperlessExtractor(config),
    ]

    all_records: list[dict] = []
    for ext in extractors:
        name = type(ext).__name__
        print(f"[main] Running {name}...")
        try:
            records = ext.extract()
            print(f"[main]   {len(records)} records")
            all_records.extend(records)
        except Exception as e:
            print(f"[main] Warning: {name} failed: {e}", file=sys.stderr)

    if not all_records:
        sys.exit("[main] No records extracted. Aborting.")

    # --- Pipeline ---
    print(f"[main] Processing {len(all_records)} total records...")
    disposals = config.get("asset_disposals", {})
    rows = pipeline.run(all_records, disposals=disposals)
    print(f"[main] {len(rows)} monthly rows produced.")

    # --- Output ---
    output.write_all(rows, config)

    # --- Git ---
    git_commit_and_push()

    print("[main] Done.")


if __name__ == "__main__":
    main()
