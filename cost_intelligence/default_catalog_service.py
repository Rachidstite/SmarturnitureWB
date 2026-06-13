from pathlib import Path

from cost_intelligence.pricing_catalog_storage import PricingCatalogStorage


class DefaultCatalogService:
    """
    Loads the installed default supplier pricing catalog.
    """

    def load_default_catalog(
        self,
    ):
        catalog_path = (
            Path(__file__).resolve().parents[1]
            / "data"
            / "pricing"
            / "default_pricing_catalog.json"
        )

        return PricingCatalogStorage().load(
            catalog_path,
        )
