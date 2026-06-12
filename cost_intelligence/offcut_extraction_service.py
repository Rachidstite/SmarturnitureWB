from cost_intelligence.offcut_adapter import OffcutAdapter


class OffcutExtractionService:

    @staticmethod
    def extract(
        sheet_results,
    ):
        offcuts = []

        for sheet in sheet_results:
            for region in getattr(sheet, "remaining_regions", []):
                offcuts.append(
                    OffcutAdapter.from_region(
                        region,
                        material=sheet.material,
                        thickness=sheet.thickness,
                    )
                )

        return offcuts
