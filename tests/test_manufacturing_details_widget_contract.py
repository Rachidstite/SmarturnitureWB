import unittest


class TestManufacturingDetailsWidgetContract(
    unittest.TestCase
):

    def test_widget_has_update_report(self):

        with open(
            "ui/manufacturing_intelligence_details_widget.py",
            "r",
            encoding="utf-8",
        ) as f:
            source = f.read()

        self.assertIn(
            "def update_report",
            source,
        )


if __name__ == "__main__":
    unittest.main()
