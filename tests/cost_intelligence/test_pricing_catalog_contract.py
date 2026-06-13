import unittest


class TestPricingCatalogContract(unittest.TestCase):

    def test_pricing_catalog_exists(self):

        try:
            from cost_intelligence.pricing_catalog import (
                PricingCatalog,
            )
        except ImportError:
            self.fail(
                "PricingCatalog does not exist"
            )



    def test_pricing_catalog_returns_price_by_stock_key(self):

        from cost_intelligence.pricing_catalog import (
            PricingCatalog,
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

        price = catalog.get(
            "MDF_18MM",
        )

        self.assertEqual(
            price["price_per_sheet"],
            280,
        )

        self.assertEqual(
            price["currency"],
            "MAD",
        )

if __name__ == "__main__":
    unittest.main()
