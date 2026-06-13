from manufacturing.manufacturing_package import ManufacturingPackage


class ManufacturingPackageBuilder:

    def build(
        self,
        panels=None,
        materials=None,
        machining_operations=None,
        edge_operations=None,
        warnings=None,
    ):
        return ManufacturingPackage(
            panels=[] if panels is None else panels,
            materials=[] if materials is None else materials,
            machining_operations=(
                [] if machining_operations is None else machining_operations
            ),
            edge_operations=[] if edge_operations is None else edge_operations,
            warnings=[] if warnings is None else warnings,
        )
