import unittest
from dataclasses import fields, is_dataclass


class TestRemainingRegionContract(unittest.TestCase):

    def test_remaining_region_exists_and_is_dataclass(self):

        try:
            from cost_intelligence.remaining_region import (
                RemainingRegion,
            )
        except ImportError:
            self.fail(
                "RemainingRegion does not exist"
            )

        self.assertTrue(
            is_dataclass(RemainingRegion),
        )

    def test_remaining_region_contains_required_fields(self):

        from cost_intelligence.remaining_region import RemainingRegion

        field_names = {
            field.name
            for field in fields(RemainingRegion)
        }

        self.assertEqual(
            field_names,
            {
                "id",
                "x",
                "y",
                "width",
                "height",
                "area",
                "source_sheet",
            },
        )

    def test_remaining_region_calculates_area(self):

        from cost_intelligence.remaining_region import RemainingRegion

        region = RemainingRegion(
            id="REGION-001",
            x=100,
            y=200,
            width=600,
            height=400,
            source_sheet="SHEET-001",
        )

        self.assertEqual(
            region.area,
            region.width * region.height,
        )
        self.assertEqual(
            region.area,
            240000,
        )


if __name__ == "__main__":
    unittest.main()
