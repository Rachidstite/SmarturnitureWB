import unittest


class TestCostImpactWidgetMappingContract(
    unittest.TestCase
):

    def test_widget_uses_description_field(self):

        with open(
            "ui/manufacturing_intelligence_details_widget.py",
            "r",
            encoding="utf-8",
        ) as f:
            source = f.read()

        self.assertIn(
            "item.description",
            source,
        )


if __name__ == "__main__":
    unittest.main()
