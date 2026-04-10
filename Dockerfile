FROM python:3.12-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code is mounted from the array at runtime — not baked in.
# docker run --rm \
#   -v /mnt/user/appdata/finance-pipeline:/app \
#   -v /mnt/user/Projects/data/assets:/data/assets \
#   finance-pipeline python main.py
