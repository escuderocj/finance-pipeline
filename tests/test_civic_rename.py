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
