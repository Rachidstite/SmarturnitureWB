import unittest


class TestPricingCatalogUpdate(unittest.TestCase):

    def test_set_price_creates_missing_item(self):

        from cost_intelligence.pricing_catalog import PricingCatalog

        catalog = PricingCatalog()

        catalog.set_price(
            "MDF_18MM",
            {
                "price_per_sheet": 300,
                "price_per_m2": 100,
                "currency": "MAD",
            },
        )

        self.assertEqual(
            catalog.get("MDF_18MM")["price_per_sheet"],
            300,
        )

    def test_set_price_updates_existing_item(self):

        from cost_intelligence.pricing_catalog import PricingCatalog

        catalog = PricingCatalog(
            {
                "MDF_18MM": {
                    "price_per_sheet": 280,
                    "currency": "MAD",
                }
            }
        )

        catalog.set_price(
            "MDF_18MM",
            {
                "price_per_sheet": 300,
                "currency": "MAD",
            },
        )

        self.assertEqual(
            catalog.get("MDF_18MM")["price_per_sheet"],
            300,
        )

    def test_get_still_returns_price_after_set_price(self):

        from cost_intelligence.pricing_catalog import PricingCatalog

        catalog = PricingCatalog()
        price_data = {
            "price_per_sheet": 300,
            "currency": "MAD",
        }

        catalog.set_price(
            "MDF_18MM",
            price_data,
        )

        self.assertEqual(
            catalog.get("MDF_18MM"),
            price_data,
        )


if __name__ == "__main__":
    unittest.main()
