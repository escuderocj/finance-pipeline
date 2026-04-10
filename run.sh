#!/bin/bash
# Finance Pipeline — User Scripts entry point
# Schedule: 0 2 * * *  (daily at 2:00 AM)

set -euo pipefail

APP_DIR="/mnt/user/appdata/finance-pipeline"
DATA_DIR="/mnt/user/Projects/data/assets"

# Ensure output directory exists on the host
mkdir -p "${DATA_DIR}/output"

docker run --rm \
  -v "${APP_DIR}:/app" \
  -v "${DATA_DIR}:/data/assets" \
  finance-pipeline \
  python main.py
