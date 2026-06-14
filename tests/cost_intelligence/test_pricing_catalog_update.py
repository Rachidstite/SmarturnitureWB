import unittest


class TestPricingCatalogUpdate(unittest.TestCase):

    def test_has_price_returns_true_and_false(self):

        from cost_intelligence.pricing_catalog import PricingCatalog

        catalog = PricingCatalog(
            {
                "MDF_18MM": {
                    "price_per_sheet": 280,
                    "currency": "MAD",
                }
            }
        )

        self.assertTrue(catalog.has_price("MDF_18MM"))
        self.assertFalse(catalog.has_price("HDF_3MM"))

    def test_list_stock_keys_preserves_insertion_order(self):

        from cost_intelligence.pricing_catalog import PricingCatalog

        catalog = PricingCatalog()
        catalog.set_price("MDF_18MM", {"price_per_sheet": 280})
        catalog.set_price("HDF_3MM", {"price_per_sheet": 120})
        catalog.set_price("MDF_8MM", {"price_per_sheet": 180})

        self.assertEqual(
            catalog.list_stock_keys(),
            ["MDF_18MM", "HDF_3MM", "MDF_8MM"],
        )

    def test_remove_price_removes_existing_price(self):

        from cost_intelligence.pricing_catalog import PricingCatalog

        catalog = PricingCatalog(
            {
                "MDF_18MM": {
                    "price_per_sheet": 280,
                    "currency": "MAD",
                }
            }
        )

        catalog.remove_price("MDF_18MM")

        self.assertFalse(catalog.has_price("MDF_18MM"))
        self.assertIsNone(catalog.get("MDF_18MM"))

    def test_remove_price_raises_key_error_when_missing(self):

        from cost_intelligence.pricing_catalog import PricingCatalog

        catalog = PricingCatalog()

        with self.assertRaises(KeyError):
            catalog.remove_price("MISSING")

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
