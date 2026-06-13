import unittest


class TestOffcutAdapter(unittest.TestCase):

    def test_remaining_region_can_be_converted_to_offcut(self):

        from cost_intelligence.offcut import Offcut
        from cost_intelligence.offcut_adapter import OffcutAdapter
        from cost_intelligence.remaining_region import RemainingRegion

        region = RemainingRegion(
            id="REGION-001",
            x=100,
            y=200,
            width=600,
            height=400,
            source_sheet="SHEET-001",
        )

        offcut = OffcutAdapter.from_region(
            region,
            material="MDF",
            thickness=18,
        )

        self.assertIsInstance(
            offcut,
            Offcut,
        )
        self.assertEqual(
            offcut.material,
            "MDF",
        )
        self.assertEqual(
            offcut.thickness,
            18,
        )
        self.assertEqual(
            offcut.width,
            region.width,
        )
        self.assertEqual(
            offcut.height,
            region.height,
        )
        self.assertEqual(
            offcut.area,
            region.area,
        )
        self.assertEqual(
            offcut.source_sheet,
            region.source_sheet,
        )


if __name__ == "__main__":
    unittest.main()
