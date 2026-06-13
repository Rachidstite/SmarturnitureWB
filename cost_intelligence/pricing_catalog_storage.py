import json
from pathlib import Path

from cost_intelligence.pricing_catalog import PricingCatalog


class PricingCatalogStorage:
    """
    Persists supplier pricing catalogs as JSON files.
    """

    def load(
        self,
        path,
    ):
        path = Path(path)

        if not path.exists():
            return PricingCatalog()

        with path.open(
            encoding="utf-8",
        ) as catalog_file:
            prices = json.load(
                catalog_file,
            )

        return PricingCatalog(
            prices,
        )

    def save(
        self,
        path,
        catalog,
    ):
        path = Path(path)

        with path.open(
            "w",
            encoding="utf-8",
        ) as catalog_file:
            json.dump(
                catalog.prices,
                catalog_file,
                indent=4,
            )
