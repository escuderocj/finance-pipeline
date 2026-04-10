class BaseExtractor:
    def extract(self) -> list[dict]:
        """
        Returns a list of normalized records:
        [{"date": "2026-01-01", "field": "car_tesla_model_y", "value": 33910.0}, ...]

        - date: always first of month, ISO format (YYYY-MM-DD)
        - field: snake_case column name in unified data model
        - value: float, always positive (pipeline negates liabilities)
        """
        raise NotImplementedError
