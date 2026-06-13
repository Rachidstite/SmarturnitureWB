from cost_intelligence.offcut import Offcut


class OffcutAdapter:

    @staticmethod
    def from_region(
        region,
        material,
        thickness,
    ):
        return Offcut(
            id=region.id,
            material=material,
            thickness=thickness,
            width=region.width,
            height=region.height,
            source_sheet=region.source_sheet,
        )
