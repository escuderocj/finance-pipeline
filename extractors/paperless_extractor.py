import re
from datetime import datetime

import requests

from .base import BaseExtractor

# Regex for primary vehicle value (History-Based Value by CARFAX)
_PRIMARY_VALUE_RE = re.compile(r"History-Based Value by CARFAX \$([0-9,]+)")

# Regex for secondary vehicle name + value in the "Other Cars in Your Garage" section
_SECONDARY_VEHICLE_RE = re.compile(
    r"(\d{4} [A-Z][A-Z0-9 ]+?) Estimated Mileage.*?CARFAX Value - \$([0-9,]+)",
    re.DOTALL,
)

# Regex for primary vehicle name (before "Other Cars" section)
_PRIMARY_NAME_RE = re.compile(r"(\d{4} [A-Z][A-Z0-9 ]+?) Estimated Mileage")

# Mortgage principal balance
_MORTGAGE_RE = re.compile(r"Principal balance \$([0-9,]+(?:\.[0-9]+)?)")

# Date embedded in CARFAX email body: "Car Care Dashboard March 2026"
_CARFAX_DATE_RE = re.compile(r"Car Care Dashboard (\w+ \d{4})")


def _to_month(date_str: str) -> str:
    """Convert 'YYYY-MM-DD' (or 'YYYY-MM-DDThh:mm:ss...') to 'YYYY-MM-01'."""
    return date_str[:7] + "-01"


def _date_from_content(content: str) -> str | None:
    """Extract 'YYYY-MM-01' from 'Car Care Dashboard March 2026' in CARFAX email body."""
    m = _CARFAX_DATE_RE.search(content)
    if not m:
        return None
    try:
        dt = datetime.strptime(m.group(1), "%B %Y")
        return dt.strftime("%Y-%m-01")
    except ValueError:
        return None


def _resolve_date(doc: dict) -> str:
    """
    Return the best YYYY-MM-01 date for a CARFAX document.
    Priority: content body > created (if year >= 2010) > added.
    """
    content_date = _date_from_content(doc.get("content", ""))
    if content_date:
        return content_date

    created = doc.get("created", "")
    if created and int(created[:4]) >= 2010:
        return _to_month(created)

    # Fall back to the date Paperless ingested the document
    return _to_month(doc.get("added", "2000-01-01"))


def _parse_amount(raw: str) -> float:
    return float(raw.replace(",", ""))


class PaperlessExtractor(BaseExtractor):
    def __init__(self, config: dict):
        self.base_url = config["paperless"]["url"].rstrip("/")
        self.token = config["paperless"]["token"]
        self.vehicle_doc_type = config["document_types"]["vehicle_update"]
        self.mortgage_doc_type = config["document_types"]["mortgage"]
        self.vehicle_map: dict[str, str] = config.get("vehicle_map", {})

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def extract(self) -> list[dict]:
        records = []
        records.extend(self._extract_vehicles())
        records.extend(self._extract_mortgage())
        return records

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self) -> dict:
        return {"Authorization": f"Token {self.token}"}

    def _fetch_documents(self, doc_type_id: int) -> list[dict]:
        """Fetch all documents of the given type, handling pagination."""
        url = f"{self.base_url}/api/documents/"
        params = {"document_type__id": doc_type_id, "page_size": 100}
        docs = []

        while url:
            resp = requests.get(url, params=params, headers=self._headers(), timeout=30)
            resp.raise_for_status()
            data = resp.json()
            docs.extend(data.get("results", []))
            url = data.get("next")
            params = {}  # next URL already encodes params

        return docs

    def _extract_vehicles(self) -> list[dict]:
        records = []
        docs = self._fetch_documents(self.vehicle_doc_type)

        for doc in docs:
            date = _resolve_date(doc)
            content = doc.get("content", "")
            records.extend(self._parse_vehicle_content(content, date))

        return records

    def _parse_vehicle_content(self, content: str, date: str) -> list[dict]:
        records = []

        # Split at the "Other Cars in Your Garage" divider
        parts = content.split("Other Cars in Your Garage")
        primary_section = parts[0]
        secondary_section = parts[1] if len(parts) > 1 else ""

        # Primary vehicle
        name_match = _PRIMARY_NAME_RE.search(primary_section)
        value_match = _PRIMARY_VALUE_RE.search(primary_section)
        if name_match and value_match:
            vehicle_name = name_match.group(1).strip()
            field = self.vehicle_map.get(vehicle_name)
            if field:
                records.append({
                    "date": date,
                    "field": field,
                    "value": _parse_amount(value_match.group(1)),
                })
            else:
                print(f"[paperless_extractor] Unknown primary vehicle: '{vehicle_name}'")

        # Secondary vehicles
        for m in _SECONDARY_VEHICLE_RE.finditer(secondary_section):
            vehicle_name = m.group(1).strip()
            field = self.vehicle_map.get(vehicle_name)
            if field:
                records.append({
                    "date": date,
                    "field": field,
                    "value": _parse_amount(m.group(2)),
                })
            else:
                print(f"[paperless_extractor] Unknown secondary vehicle: '{vehicle_name}'")

        return records

    def _extract_mortgage(self) -> list[dict]:
        records = []
        docs = self._fetch_documents(self.mortgage_doc_type)

        for doc in docs:
            date = _to_month(doc["created"])
            content = doc.get("content", "")
            m = _MORTGAGE_RE.search(content)
            if m:
                records.append({
                    "date": date,
                    "field": "debt_mortgage",
                    "value": _parse_amount(m.group(1)),
                })

        return records
