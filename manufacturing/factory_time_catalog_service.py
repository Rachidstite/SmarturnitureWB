import json
from pathlib import Path


class FactoryTimeCatalogService:

    def __init__(self, catalog_path=None):
        self.catalog_path = (
            Path(catalog_path)
            if catalog_path is not None
            else self._default_catalog_path()
        )

    def load(self):
        if not self.catalog_path.exists():
            return {}

        try:
            with self.catalog_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return {}

        return payload if isinstance(payload, dict) else {}

    @staticmethod
    def _default_catalog_path():
        return (
            Path(__file__).resolve().parent.parent
            / "data"
            / "factory"
            / "factory_time_catalog.json"
        )
