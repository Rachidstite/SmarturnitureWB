import json
import tempfile
import unittest
from pathlib import Path


class TestPricingCatalogStorage(unittest.TestCase):

    def test_catalog_can_load_from_json_file(self):

        from cost_intelligence.pricing_catalog_storage import (
            PricingCatalogStorage,
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "pricing_catalog.json"
            path.write_text(
                json.dumps(
                    {
                        "MDF_18MM": {
                            "price_per_sheet": 280,
                            "price_per_m2": 94.08,
                            "currency": "MAD",
                        }
                    }
                ),
                encoding="utf-8",
            )

            catalog = PricingCatalogStorage().load(
                path,
            )

        self.assertEqual(
            catalog.get("MDF_18MM")["price_per_sheet"],
            280,
        )

    def test_catalog_can_save_to_json_file(self):

        from cost_intelligence.pricing_catalog import PricingCatalog
        from cost_intelligence.pricing_catalog_storage import (
            PricingCatalogStorage,
        )

        catalog = PricingCatalog(
            {
                "MDF_18MM": {
                    "price_per_sheet": 280,
                    "price_per_m2": 94.08,
                    "currency": "MAD",
                }
            }
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "pricing_catalog.json"

            PricingCatalogStorage().save(
                path,
                catalog,
            )

            saved_prices = json.loads(
                path.read_text(
                    encoding="utf-8",
                )
            )

        self.assertEqual(
            saved_prices,
            catalog.prices,
        )

    def test_missing_file_returns_empty_catalog(self):

        from cost_intelligence.pricing_catalog_storage import (
            PricingCatalogStorage,
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "missing.json"

            catalog = PricingCatalogStorage().load(
                path,
            )

        self.assertEqual(
            catalog.prices,
            {},
        )


if __name__ == "__main__":
    unittest.main()
