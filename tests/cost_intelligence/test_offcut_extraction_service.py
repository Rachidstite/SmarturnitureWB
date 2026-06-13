import unittest


class TestOffcutExtractionService(unittest.TestCase):

    def test_offcut_extraction_service_exists(self):

        try:
            from cost_intelligence.offcut_extraction_service import (
                OffcutExtractionService,
            )
        except ImportError:
            self.fail(
                "OffcutExtractionService does not exist"
            )

        self.assertTrue(
            callable(OffcutExtractionService.extract),
        )

    def test_extract_flattens_remaining_regions_into_offcuts(self):

        from cost_intelligence.offcut import Offcut
        from cost_intelligence.offcut_extraction_service import (
            OffcutExtractionService,
        )
        from cost_intelligence.remaining_region import RemainingRegion
        from exports.strategies import SheetResult

        sheets = [
            SheetResult(
                sheet_id=1,
                material="MDF",
                thickness=18,
                remaining_regions=[
                    RemainingRegion(
                        id="SHEET-1-REGION-1",
                        x=10,
                        y=20,
                        width=600,
                        height=400,
                        source_sheet="SHEET-1",
                    ),
                ],
            ),
            SheetResult(
                sheet_id=2,
                material="MDF",
                thickness=18,
                remaining_regions=[
                    RemainingRegion(
                        id="SHEET-2-REGION-1",
                        x=15,
                        y=25,
                        width=300,
                        height=200,
                        source_sheet="SHEET-2",
                    ),
                ],
            ),
        ]

        offcuts = OffcutExtractionService.extract(sheets)

        self.assertEqual(
            len(offcuts),
            2,
        )
        self.assertIsInstance(
            offcuts[0],
            Offcut,
        )
        self.assertEqual(
            offcuts[0].material,
            "MDF",
        )
        self.assertEqual(
            offcuts[0].thickness,
            18,
        )
        self.assertEqual(
            offcuts[0].source_sheet,
            "SHEET-1",
        )
        self.assertEqual(
            offcuts[1].source_sheet,
            "SHEET-2",
        )

    def test_extract_handles_empty_input(self):

        from cost_intelligence.offcut_extraction_service import (
            OffcutExtractionService,
        )

        self.assertEqual(
            OffcutExtractionService.extract([]),
            [],
        )


if __name__ == "__main__":
    unittest.main()
